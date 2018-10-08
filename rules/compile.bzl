load("@bazel_skylib//lib:paths.bzl", "paths")


def _get_path_relative_to_workspace(path, ctx):
    if paths.is_absolute(path):
        return paths.relativize(path, "/")
    else:
        return paths.join(ctx.label.package, path)


def _compile_pip_requirements_impl(ctx):
    out_file = ctx.actions.declare_file(ctx.label.name + ".sh")

    output_dir = _get_path_relative_to_workspace(ctx.attr.output_dir, ctx)

    substitutions = {
        "@@REQUIREMENTS_IN_PATH@@": ctx.file.requirements_in.short_path,
        "@@OUTPUT_DIR@@": output_dir,
        "@@PYTHON_INTERPRETER_PATH@@": ctx.attr.python_interpreter,
        "@@GENERATE_REQUIREMENTS_FILE_NAME_BINARY@@": ctx.executable._generate_file_name.short_path,
        "@@PIP_COMPILE_BINARY@@": ctx.executable._pip_compile.short_path,
    }

    ctx.actions.expand_template(
        template = ctx.file._template,
        output = out_file,
        substitutions = substitutions,
        is_executable = True,
    )

    runfiles = ctx.runfiles(
        files = (
            ctx.files.requirements_in +
            ctx.files._generate_file_name +
            ctx.files._pip_compile
        )
    )

    return [DefaultInfo(
        files = depset([out_file]),
        runfiles = runfiles,
        executable = out_file,
    )]


compile_pip_requirements = rule(
    implementation = _compile_pip_requirements_impl,
    attrs = {
        "requirements_in": attr.label(
            allow_single_file = [".in"],
            mandatory = True,
        ),
        "output_dir": attr.string(default = ""),
        "python_interpreter": attr.string(default = "python"),
        "_generate_file_name": attr.label(
            default = "//src/bin:generate_requirements_file_name.par",
            cfg = "host",
            executable = True,
        ),
        "_pip_compile": attr.label(
            default = "//src/bin:compile_pip_requirements.par",
            cfg = "host",
            executable = True,
        ),
        "_template": attr.label(
            default = "//src/templates:compile_pip_requirements_wrapper_template.sh",
            allow_single_file = True,
        )
    },
    executable = True,
)
