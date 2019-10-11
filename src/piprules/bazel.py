import glob
import os
import shutil
import textwrap

from piprules import util


def generate_package_for_python_distribution(distribution):
    _PyDistPackageGenerator(distribution).generate()


class _PyDistPackageGenerator(object):

    def __init__(self, distribution):
        self.distribution = distribution

    @property
    def base_package_path(self):
        return self.distribution.location

    @property
    def base_package_build_file_path(self):
        return os.path.join(self.base_package_path, "BUILD")

    @property
    def base_package_name(self):
        return util.normalize_distribution_name(self.distribution.project_name)

    @property
    def data_source_pattern(self):
        return os.path.join(self.base_package_path, "*.data", "*")

    @property
    def library_name(self):
        return self.base_package_name

    @property
    def library_dependencies(self):
        return set(
            _LibraryDependency.from_distribution_requirement(req)
            for req in self.distribution.requires()
        )

    def generate(self):
        self._create_base_package_build_file()

        for data_directory in self._find_data_directories():
            _DataPackageGenerator(self.base_package_path, data_directory).generate()

    def _create_base_package_build_file(self):
        # Files with spaces in the name must be excluded
        # https://github.com/bazelbuild/bazel/issues/374
        contents = textwrap.dedent("""
            py_library(
                name = "{name}",
                srcs = glob(["**/*.py"]),
                data = glob(
                    ["**/*"],
                    exclude = [
                        "**/*.py",
                        "**/* *",  # Bazel runfiles cannot have spaces in the name
                        "**/BUILD",
                    ],
                ),
                deps = [{deps}],
                imports = ["."],
                visibility = ["//visibility:public"],
            )
        """).lstrip().format(
            name=self.library_name,
            deps=_create_string_list(sorted(dep.label for dep in self.library_dependencies)),
        )

        with open(self.base_package_build_file_path, mode="w") as build_file:
            build_file.write(contents)

    def _find_data_directories(self):
        return glob.glob(self.data_source_pattern)


class _LibraryDependency(object):

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    @classmethod
    def from_distribution_requirement(cls, requirement):
        return cls(util.normalize_distribution_name(requirement.project_name))

    @property
    def label(self):
        return "//{}".format(self.name)


class _DataPackageGenerator(object):

    def __init__(self, base_package_path, data_directory):
        self.base_package_path = base_package_path
        self.data_directory = data_directory

    @property
    def package_name(self):
        return os.path.basename(self.data_directory)

    @property
    def package_path(self):
        return os.path.join(self.base_package_path, self.package_name)

    @property
    def symlink_target(self):
        return os.path.relpath(self.data_directory, start=self.base_package_path)

    def generate(self):
        os.symlink(self.symlink_target, self.package_path)
        self._create_build_files()

    def _create_build_files(self):
        for dirpath, dirnames, filenames in os.walk(self.package_path):
            _DataPackageBuildFileGenerator(dirpath, filenames).generate()


class _DataPackageBuildFileGenerator(object):

    def __init__(self, package_path, filenames):
        self.package_path = package_path
        self.filenames = filenames

    @property
    def package_name(self):
        return os.path.basename(self.package_path)

    @property
    def build_file_path(self):
        return os.path.join(self.package_path, "BUILD")

    def generate(self):
        contents = self._get_contents()

        with open(self.build_file_path, mode="w") as build_file:
            build_file.write(contents)

    def _get_contents(self):
        if not self.filenames:
            return ""

        return textwrap.dedent("""
            filegroup(
                name = "{package_name}",
                srcs = glob(["*"]),
            )

            exports_files([{data_files}])
        """).lstrip().format(
            package_name=self.package_name,
            data_files=_create_string_list(self.filenames),
        )


def _create_string_list(values):
    return ", ".join(_quote(value) for value in values)


def _quote(value):
    return '"{}"'.format(value)
