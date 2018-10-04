def _pip_requirements_impl(repo_ctx):
    create_wheels_repo_path = repo_ctx.path(repo_ctx.attr._create_wheels_repo)
    requirements_path = repo_ctx.path(repo_ctx.attr.requirements)
    repo_directory = repo_ctx.path("")

    repo_ctx.execute([
        repo_ctx.attr.python_interpreter,
        create_wheels_repo_path,
        requirements_path,
        repo_directory,
    ])


pip_requirements = repository_rule(
    implementation = _pip_requirements_impl,
    attrs = {
        "requirements": attr.label(
            allow_single_file = True,
            mandatory = True,
        ),
        "python_interpreter": attr.string(default = "python"),
        "_create_wheels_repo": attr.label(
            default = "//download:create_wheels_repo.py",
        )
    }
)
