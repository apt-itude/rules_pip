def _pip_repository_impl(repo_ctx):
    repo_ctx.file("BUILD", "")

    create_repo_exe_path = repo_ctx.path(repo_ctx.attr._create_repo_exe)
    requirements_path = repo_ctx.path(repo_ctx.attr.requirements)
    repo_directory = repo_ctx.path("")

    repo_ctx.execute([
        repo_ctx.attr.python_interpreter,
        create_repo_exe_path,
        requirements_path,
        repo_directory,
    ])


pip_repository = repository_rule(
    implementation = _pip_repository_impl,
    attrs = {
        "requirements": attr.label(
            allow_single_file = True,
            mandatory = True,
        ),
        "python_interpreter": attr.string(default = "python"),
        "_create_repo_exe": attr.label(
            default = "//tools:create_pip_repository.par",
            executable = True,
            cfg = "host",
        )
    }
)
