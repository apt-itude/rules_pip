load("@bazel_skylib//lib:paths.bzl", "paths")

def _get_path_relative_to_workspace(path, ctx):
    if paths.is_absolute(path):
        return paths.relativize(path, "/")
    else:
        return paths.join(ctx.label.package, path)

def _pip_lock(ctx):
    requirements_lock_path = _get_path_relative_to_workspace(
        ctx.attr.requirements_lock,
        ctx,
    )

    wheel_dir = _get_path_relative_to_workspace(ctx.attr.wheel_dir, ctx)

    req_files = " ".join([req_file.path for req_file in ctx.files.requirements])

    static_args = " --lock-file {lock_file} --wheel-dir {wheel_dir} {req_files} $@".format(
        lock_file = requirements_lock_path,
        wheel_dir = wheel_dir,
        req_files = req_files,
    )

    script_contents = "#!/bin/sh\n"

    if ctx.attr.python_version in ["PY2", "PY2AND3"]:
        executable_path = ctx.attr._lock_pip_requirements_py2.files_to_run.executable.short_path
        script_contents += executable_path + static_args + "\n"

    if ctx.attr.python_version in ["PY3", "PY2AND3"]:
        executable_path = ctx.attr._lock_pip_requirements_py3.files_to_run.executable.short_path
        script_contents += executable_path + static_args + "\n"

    ctx.actions.write(ctx.outputs.executable, script_contents, is_executable=True)

    runfiles = ctx.runfiles(
        files = (
            ctx.files.requirements +
            ctx.attr._lock_pip_requirements_py2.default_runfiles.files.to_list() +
            ctx.attr._lock_pip_requirements_py3.default_runfiles.files.to_list()
        ),
        # collect_data = True,
        # collect_default = True,
    )

    return [DefaultInfo(
        # files = depset([out_file]),
        runfiles = runfiles,
        executable = ctx.outputs.executable,
    )]

pip_lock = rule(
    implementation = _pip_lock,
    attrs = {
        "requirements": attr.label_list(allow_files = True),
        "requirements_lock": attr.string(default = "requirements-lock.json"),
        "wheel_dir": attr.string(default = "wheels"),
        "python_version": attr.string(
            values = ["PY2", "PY3", "PY2AND3"],
            default = "PY2AND3",
        ),
        "platforms": attr.string_list(),
        "_lock_pip_requirements_py2": attr.label(
            default = "//src/bin:lock_pip_requirements_py2",
            cfg = "target",
            executable = True,
        ),
        "_lock_pip_requirements_py3": attr.label(
            default = "//src/bin:lock_pip_requirements_py3",
            cfg = "target",
            executable = True,
        ),
    },
    executable = True,
)
