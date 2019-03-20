def _pip_repositories_impl(repo_ctx):
    output_path = repo_ctx.path("requirements.bzl")

    result = repo_ctx.execute([
        repo_ctx.path(repo_ctx.attr._generate_requirements_bzl),
        repo_ctx.path(repo_ctx.attr.requirements),
        output_path,
    ])
    if result.return_code:
        fail(result.stderr)


pip_repositories = repository_rule(
    implementation = _pip_repositories_impl,
    attrs = {
        "requirements": attr.label(allow_single_file=True),
        "_generate_requirements_bzl": attr.label(
            default = "//src/bin:generate_requirements_bzl.py",
            executable = True,
            cfg = "host",
        ),
    }
)
