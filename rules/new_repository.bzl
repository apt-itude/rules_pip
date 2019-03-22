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


def _pip_repositories_impl(repo_ctx):
    # TODO can I get this programatically in case it's named differently?
    repo_name = "com_apt_itude_rules_pip"

    result = repo_ctx.execute([
        repo_ctx.path(repo_ctx.attr._generate_pip_repositories),
        repo_ctx.path(repo_ctx.attr.requirements),
        repo_ctx.path("requirements.bzl"),
        repo_ctx.path("BUILD"),
        repo_name,
    ])
    if result.return_code:
        fail(result.stderr)


pip_repositories = repository_rule(
    implementation = _pip_repositories_impl,
    attrs = {
        "requirements": attr.label(allow_single_file = True),
        "_generate_pip_repositories": attr.label(
            default = "//src/bin:generate_pip_repositories.py",
            executable = True,
            cfg = "host",
        ),
    }
)


def _pip_repository_impl(repo_ctx):
    repo_ctx.download_and_extract(
        url = repo_ctx.attr.url,
        sha256 = repo_ctx.attr.sha256,
        type = "zip" if repo_ctx.attr.is_wheel else "tar.gz"
    )

    if repo_ctx.attr.is_wheel:
        _generate_wheel_build_file(repo_ctx)


def _generate_wheel_build_file(repo_ctx):
    repo_ctx.file(repo_ctx.path("BUILD"), content = _WHEEL_BUILD_FILE_CONTENT)


pip_repository = repository_rule(
    implementation = _pip_repository_impl,
    attrs = {
        "url": attr.string(mandatory = True),
        "sha256": attr.string(),
        "is_wheel": attr.bool(),
    }
)
