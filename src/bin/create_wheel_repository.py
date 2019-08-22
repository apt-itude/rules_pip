#!/usr/bin/env python
import argparse
import glob
import os
import textwrap
import shutil

_WHEEL_BUILD_FILE_CONTENT = textwrap.dedent("""
    py_library(
        name = "lib",
        srcs = glob(["**/*.py"]),
        data = glob(
            ["**/*"],
            exclude = [
                "**/*.py",
                "**/* *",  # Bazel runfiles cannot have spaces in the name
                "BUILD",
                "WORKSPACE",
                "*.whl.zip",
            ],
        ),
        imports = ["."],
        visibility = ["//visibility:public"],
    )
""")


def main():
    args = parse_args()
    WheelRepositoryGenerator(args.repository_directory).generate()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("repository_directory")
    return parser.parse_args()


class WheelRepositoryGenerator(object):

    def __init__(self, repository_directory):
        self.repository_directory = repository_directory

    @property
    def base_package_build_file_path(self):
        return os.path.join(self.repository_directory, "BUILD")

    @property
    def data_source_pattern(self):
        return os.path.join(self.repository_directory, "*.data", "*")

    def generate(self):
        self._create_base_package_build_file()

        for data_directory in self._find_data_directories():
            self._handle_purelib_and_platlib(data_directory)
            DataPackageGenerator(self.repository_directory, data_directory).generate()

    def _handle_purelib_and_platlib(self, data_directory):
        full_path = os.path.join(self.repository_directory, data_directory)

        try:
            data_contents = os.listdir(full_path)
        except:
            data_contents = []
        
        if 'purelib' in full_path or 'platlib' in full_path:
            source = full_path
        else:
            source = None
        
        if source:
            for f in os.listdir(full_path):
                if 'BUILD' in str(f):
                    continue
                shutil.move(os.path.join(source, f), self.repository_directory)
    
    def _create_base_package_build_file(self):
        with open(self.base_package_build_file_path, mode="w") as build_file:
            build_file.write(_WHEEL_BUILD_FILE_CONTENT)

    def _find_data_directories(self):
        return glob.glob(self.data_source_pattern)


class DataPackageGenerator(object):

    def __init__(self, repository_directory, data_directory):
        self.repository_directory = repository_directory
        self.data_directory = data_directory

    @property
    def package_name(self):
        return os.path.basename(self.data_directory)

    @property
    def package_path(self):
        return os.path.join(self.repository_directory, self.package_name)

    @property
    def symlink_target(self):
        return os.path.relpath(self.data_directory, start=self.repository_directory)

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


if __name__ == "__main__":
    main()
