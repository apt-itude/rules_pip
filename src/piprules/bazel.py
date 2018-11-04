import glob
import logging
import os
import re
import shutil
import sys
import textwrap

from piprules import util


LOG = logging.getLogger(__name__)


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
    def scripts_source_pattern(self):
        return os.path.join(self.base_package_path, "*.data", "scripts", "*")

    @property
    def scripts_package_path(self):
        return os.path.join(self.base_package_path, "scripts")

    @property
    def scripts_package_build_file_path(self):
        return os.path.join(self.scripts_package_path, "BUILD")

    @property
    def library_name(self):
        return self.base_package_name

    @property
    def library_dependency_names(self):
        return set(
            util.normalize_distribution_name(req.project_name)
            for req in self.distribution.requires()
        )

    @property
    def library_dependency_labels(self):
        return ['"//{}"'.format(name) for name in self.library_dependency_names]

    def generate(self):
        self._create_base_package_build_file()
        self._create_scripts_package()

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
            deps=", ".join(self.library_dependency_labels),
        )

        with open(self.base_package_build_file_path, mode="w") as build_file:
            build_file.write(contents)

    def _create_scripts_package(self):
        scripts = self._find_scripts()
        if not scripts:
            return

        try:
            util.ensure_directory_exists(self.scripts_package_path)
        except OSError as err:
            LOG.error("Cannot create scripts package: %s", err)
            return

        for script in scripts:
            script.copy_to_package(self.scripts_package_path)

        build_file_contents = "\n\n".join(
            script.generate_py_binary_rule(self.library_name) for script in scripts
        )

        with open(self.scripts_package_build_file_path, mode="w") as build_file:
            build_file.write(build_file_contents)

    def _find_scripts(self):
        return [_Script(path) for path in glob.glob(self.scripts_source_pattern)]


class _Script(object):

    SHEBANG_REGEX = re.compile(r'^#!.*')

    def __init__(self, original_path):
        self.original_path = original_path

    @property
    def name(self):
        return util.get_path_stem(self.original_path)

    @property
    def package_source_file(self):
        return "{}_script.py".format(self.name)

    def copy_to_package(self, scripts_package_path):
        new_path = os.path.join(scripts_package_path, self.package_source_file)
        shutil.copy(self.original_path, new_path)
        self._replace_shebang(new_path)

    def _replace_shebang(self, path):
        with open(path) as script:
            contents = script.read()

        new_contents = self.SHEBANG_REGEX.sub(
            _make_shebang_for_current_interpreter(),
            contents,
        )

        with open(path, mode="w") as script:
            script.write(new_contents)

    def generate_py_binary_rule(self, library_name):
        return textwrap.dedent("""
            py_binary(
                name = "{name}",
                srcs = ["{source}"],
                main = "{source}",
                deps = ["//{library_name}"],
                default_python_version = "{default_python_version}",
                visibility = ["//visibility:public"],
            )
        """).strip().format(
            name=self.name,
            source=self.package_source_file,
            library_name=library_name,
            default_python_version=_get_default_python_version(),
        )


def _get_default_python_version():
    return "PY3" if sys.version_info.major == 3 else "PY2"


def _make_shebang_for_current_interpreter():
    return "#!/usr/bin/env {}".format(_get_current_interpreter())


def _get_current_interpreter():
    return "python{}.{}".format(sys.version_info.major, sys.version_info.minor)
