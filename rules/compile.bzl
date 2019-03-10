load("@bazel_skylib//lib:paths.bzl", "paths")

def _get_path_relative_to_workspace(path, ctx):
    if paths.is_absolute(path):
        return paths.relativize(path, "/")
    else:
        return paths.join(ctx.label.package, path)

def _compile_pip_requirements_impl(ctx):
    out_file = ctx.actions.declare_file(ctx.label.name + ".sh")

    requirements_txt_path = _get_path_relative_to_workspace(
        ctx.attr.requirements_txt,
        ctx,
    )

    substitutions = {
        "@@REQUIREMENTS_IN_PATH@@": ctx.file.requirements_in.short_path,
        "@@REQUIREMENTS_TXT_PATH@@": requirements_txt_path,
        "@@PYTHON_INTERPRETER_PATH@@": ctx.attr.python_interpreter,
        "@@PIP_COMPILE_BINARY@@": ctx.executable._pip_compile.short_path,
        "@@HEADER@@": ctx.attr.header,
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
            ctx.files.data +
            ctx.files._pip_compile
        ),
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
        "data": attr.label_list(allow_files = True),
        "requirements_txt": attr.string(default = "requirements.txt"),
        "python_interpreter": attr.string(default = "python"),
        "header": attr.string(default = "# This file is generated code. DO NOT EDIT."),
        "_pip_compile": attr.label(
            default = "//tools:compile_pip_requirements.par",
            allow_single_file = True,
            cfg = "host",
            executable = True,
        ),
        "_template": attr.label(
            default = "//src/templates:compile_pip_requirements_wrapper_template.sh",
            allow_single_file = True,
        ),
    },
    executable = True,
)
