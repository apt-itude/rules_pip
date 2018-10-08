def _pip_repository_impl(repo_ctx):
    repo_ctx.file("BUILD", "")

    create_repo_exe_path = repo_ctx.path(repo_ctx.attr._create_repo_exe)
    repo_directory = repo_ctx.path("")
    requirements_paths = [
        repo_ctx.path(label)
        for label in repo_ctx.attr.requirements
    ]

    repo_ctx.execute([
        repo_ctx.attr.python_interpreter,
        create_repo_exe_path,
        repo_directory,
    ]+ requirements_paths)


pip_repository = repository_rule(
    implementation = _pip_repository_impl,
    attrs = {
        "requirements": attr.label_list(
            allow_files = [".txt"],
            mandatory = True,
            allow_empty = False,
        ),
        "python_interpreter": attr.string(default = "python"),
        "_create_repo_exe": attr.label(
            default = "//tools:create_pip_repository.par",
            executable = True,
            cfg = "host",
        )
    }
)
