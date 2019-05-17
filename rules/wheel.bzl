_WHEEL_BUILD_FILE_CONTENT = """
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
"""


def _generate_wheel_build_file(repo_ctx):
    repo_ctx.file(repo_ctx.path("BUILD"), content = _WHEEL_BUILD_FILE_CONTENT)


def _remote_wheel_impl(repo_ctx):
    repo_ctx.download_and_extract(
        url = repo_ctx.attr.url,
        sha256 = repo_ctx.attr.sha256,
        type = "zip",
    )

    _generate_wheel_build_file(repo_ctx)


remote_wheel = repository_rule(
    implementation = _remote_wheel_impl,
    attrs = {
        "url": attr.string(mandatory = True),
        "sha256": attr.string(),
    }
)


def _local_wheel_impl(repo_ctx):
    # Symlink to the wheel because the "extract" function doesn't know what to do with
    # the .whl extension
    repo_ctx.symlink(repo_ctx.attr.wheel, "wheel.zip")

    repo_ctx.extract(archive = "wheel.zip")

    _generate_wheel_build_file(repo_ctx)


local_wheel = repository_rule(
    implementation = _local_wheel_impl,
    attrs = {
        "wheel": attr.label(mandatory = True),
    }
)
