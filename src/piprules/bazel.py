import os
import textwrap

from piprules import util


def create_build_file(distribution):
    path = os.path.join(distribution.location, "BUILD")

    library_name = util.normalize_distribution_name(distribution.project_name)

    dependency_names = set(
        util.normalize_distribution_name(req.project_name)
        for req in distribution.requires()
    )
    dependencies = ", ".join(
        '"//{}"'.format(name)
        for name in dependency_names
    )

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
