import argparse
import glob
import os
import pkg_resources
import subprocess
import sys
import textwrap
from wheel import wheelfile


def main():
    args = parse_args()
    download_wheels(args.requirements, args.repository_directory)
    expand_wheels_into_bazel_packages(args.repository_directory)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("requirements")
    parser.add_argument("repository_directory")

    return parser.parse_args()


def download_wheels(requirements_file_path, repository_directory):
    pip("wheel", "-r", requirements_file_path, "-w", repository_directory)


def pip(*args):
    execute_python_module("pip", *args)


def execute_python_module(module_name, *args):
    subprocess.check_call([sys.executable, "-m", module_name] + list(args))


def expand_wheels_into_bazel_packages(repository_directory):
    for wheel_path in find_wheels(repository_directory):
        unpack_wheel_into_bazel_package(wheel_path, repository_directory)


def find_wheels(directory):
    for matching_path in glob.glob("{}/*.whl".format(directory)):
        yield matching_path


def unpack_wheel_into_bazel_package(wheel_path, repository_directory):
    distribution = unpack_wheel(wheel_path, repository_directory)
    create_bazel_build_file(distribution)


def unpack_wheel(wheel_path, repository_directory):
    # TODO(): don't use unsupported wheel library
    with wheelfile.WheelFile(wheel_path) as wheel_file:
        distribution_name = wheel_file.parsed_filename.group("name")
        library_name = normalize_distribution_name(distribution_name)
        package_directory = os.path.join(repository_directory, library_name)
        wheel_file.extractall(package_directory)

    try:
        return next(pkg_resources.find_distributions(package_directory))
    except StopIteration:
        raise DistributionNotFoundError(package_directory)


class DistributionNotFoundError(Exception):

    def __init__(self, package_directory):
        super(DistributionNotFoundError, self).__init__()
        self.package_directory = package_directory

    def __str__(self):
        return "Could not find in Python distribution in directory {}".format(
            self.package_directory
        )


def normalize_distribution_name(name):
    return name.lower().replace("-", "_")


def create_bazel_build_file(distribution):
    path = os.path.join(distribution.location, "BUILD")

    library_name = normalize_distribution_name(distribution.project_name)

    dependencies = ", ".join(
        '"//{}"'.format(normalize_distribution_name(req.project_name))
        for req in distribution.requires()
    )

    contents = textwrap.dedent("""
        py_library(
            name = "{name}",
            srcs = glob(["**/*.py"]),
            data = glob(
                ["**/*"],
                exclude = [
                    "**/*.py",
                    "**/* *",  # Bazel runfiles cannot have spaces in the name
                ],
            ),
            deps = [{deps}],
            imports = ["."],
            visibility = ["//visibility:public"],
        )
    """).lstrip().format(
        name=library_name,
        deps=dependencies,
    )

    with open(path, mode="w") as build_file:
        build_file.write(contents)


if __name__ == "__main__":
    main()
