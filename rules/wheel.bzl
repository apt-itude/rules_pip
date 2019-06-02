_COMMON_ATTRS = {
    "_create_wheel_repository": attr.label(
        default = "//src/bin:create_wheel_repository.py",
        executable = True,
        cfg = "host",
    ),
}

def _remote_wheel_impl(repo_ctx):
    repo_ctx.download_and_extract(
        url = repo_ctx.attr.url,
        sha256 = repo_ctx.attr.sha256,
        type = "zip",
    )

    _create_wheel_repository(repo_ctx)


def _create_wheel_repository(repo_ctx):
    result = repo_ctx.execute([
        repo_ctx.path(repo_ctx.attr._create_wheel_repository),
        repo_ctx.path(""),
    ])

    if result.return_code:
        fail(result.stderr)


remote_wheel = repository_rule(
    implementation = _remote_wheel_impl,
    attrs = dict(_COMMON_ATTRS, **{
        "url": attr.string(mandatory = True),
        "sha256": attr.string(),
    })
)


def _local_wheel_impl(repo_ctx):
    # Symlink to the wheel because the "extract" function doesn't know what to do with
    # the .whl extension
    repo_ctx.symlink(repo_ctx.attr.wheel, "wheel.zip")

    repo_ctx.extract(archive = "wheel.zip")

    _create_wheel_repository(repo_ctx)


local_wheel = repository_rule(
    implementation = _local_wheel_impl,
    attrs = dict(_COMMON_ATTRS, **{
        "wheel": attr.label(mandatory = True),
    })
)
