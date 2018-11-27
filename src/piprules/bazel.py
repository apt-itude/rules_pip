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
    def scripts_package_path(self):
        return os.path.join(self.base_package_path, "scripts")

    @property
    def scripts_source_pattern(self):
        return os.path.join(self.base_package_path, "*.data", "scripts", "*")

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

        scripts = self._find_scripts()
        if scripts:
            _ScriptsPackageGenerator(self.scripts_package_path, scripts).generate()

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
            deps=_create_string_list(dep.label for dep in self.library_dependencies),
        )

        with open(self.base_package_build_file_path, mode="w") as build_file:
            build_file.write(contents)

    def _find_scripts(self):
        return [_Script(path) for path in glob.glob(self.scripts_source_pattern)]


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


class _ScriptsPackageGenerator(object):

    def __init__(self, package_path, scripts):
        self.package_path = package_path
        self.scripts = scripts

    @property
    def build_file_path(self):
        return os.path.join(self.package_path, "BUILD")

    def generate(self):
        util.ensure_directory_exists(self.package_path)
        self._copy_scripts_to_package()
        self._create_scripts_package_build_file()

    def _copy_scripts_to_package(self):
        for script in self.scripts:
            shutil.copy(script.original_path, self.package_path)

    def _create_scripts_package_build_file(self):
        contents = textwrap.dedent("""
            exports_files([{script_files}])
        """).lstrip().format(
            script_files=_create_string_list(script.name for script in self.scripts)
        )

        with open(self.build_file_path, mode="w") as build_file:
            build_file.write(contents)


class _Script(object):

    def __init__(self, original_path):
        self.original_path = original_path

    @property
    def name(self):
        return util.get_path_stem(self.original_path)


def _create_string_list(values):
    return ", ".join(_quote(value) for value in values)


def _quote(value):
    return '"{}"'.format(value)
