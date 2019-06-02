def _pip_repositories_impl(repo_ctx):
    result = repo_ctx.execute([
        repo_ctx.path(repo_ctx.attr._generate_pip_repositories),
        repo_ctx.path(repo_ctx.attr.requirements),
        repo_ctx.path("requirements.bzl"),
        repo_ctx.path(""),
        repo_ctx.attr.rules_pip_repo_name,
    ])
    if result.return_code:
        fail(result.stderr)

    repo_ctx.file("BUILD")


pip_repositories = repository_rule(
    implementation = _pip_repositories_impl,
    attrs = {
        "requirements": attr.label(allow_single_file = True),
        "rules_pip_repo_name": attr.string(default = "com_apt_itude_rules_pip"),
        "_generate_pip_repositories": attr.label(
            default = "//src/bin:generate_pip_repositories.py",
            executable = True,
            cfg = "host",
        ),
    }
)
