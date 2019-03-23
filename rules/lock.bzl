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

    runfiles = ctx.runfiles(
        files = (
            ctx.files.requirements +
            ctx.files._locker
        ),
    )

    return [DefaultInfo(
        files = depset([out_file]),
        runfiles = runfiles,
        executable = out_file,
    )]


pip_lock = rule(
    implementation = _pip_lock,
    attrs = {
        "requirements": attr.label_list(allow_files = True),
        "requirements_lock": attr.string(default = "requirements-lock.json"),
        "python_versions":attr.string_list(),
        "platforms":attr.string_list(),
        "_locker": attr.label(
            default = "//src/bin:lock_pip_requirements",
            cfg = "host",
            executable = True,
        ),
    }
)
