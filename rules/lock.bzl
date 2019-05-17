load("@bazel_skylib//lib:paths.bzl", "paths")

def _get_path_relative_to_workspace(path, ctx):
    if paths.is_absolute(path):
        return paths.relativize(path, "/")
    else:
        return paths.join(ctx.label.package, path)

def _pip_lock(ctx):
    requirements_txt_paths = " ".join([
        req_file.path for req_file in ctx.files.requirements
    ])

    requirements_lock_path = _get_path_relative_to_workspace(
        ctx.attr.requirements_lock,
        ctx,
    )

    wheel_dir = _get_path_relative_to_workspace(ctx.attr.wheel_dir, ctx)

    substitutions = {
        "@@LOCK_PIP_REQUIREMENTS_PY2@@": ctx.executable._lock_pip_requirements_py2.short_path,
        "@@LOCK_PIP_REQUIREMENTS_PY3@@": ctx.executable._lock_pip_requirements_py3.short_path,
        "@@WORKSPACE_NAME@@": ctx.workspace_name,
        "@@REQUIREMENTS_TXT_PATHS@@": requirements_txt_paths,
        "@@REQUIREMENTS_LOCK_PATH@@": requirements_lock_path,
        "@@USE_PY2@@": "true" if "2" in ctx.attr.python_version else "false",
        "@@USE_PY3@@": "true" if "3" in ctx.attr.python_version else "false",
        "@@WHEEL_DIRECTORY@@": wheel_dir,
        "@@INDEX_URL@@": ctx.attr.index_url,
    }

    ctx.actions.expand_template(
        template = ctx.file._wrapper_template,
        output = ctx.outputs.executable,
        substitutions = substitutions,
        is_executable = True,
    )

    runfiles = ctx.runfiles(
        files = (
            ctx.files.requirements +
            ctx.attr._lock_pip_requirements_py2.default_runfiles.files.to_list() +
            ctx.attr._lock_pip_requirements_py3.default_runfiles.files.to_list()
        ),
    )

    return [DefaultInfo(
        runfiles = runfiles,
        executable = ctx.outputs.executable,
    )]

pip_lock = rule(
    implementation = _pip_lock,
    attrs = {
        "requirements": attr.label_list(allow_files = True),
        "requirements_lock": attr.string(default = "requirements-lock.json"),
        "python_version": attr.string(
            values = ["PY2", "PY3", "PY2AND3"],
            default = "PY2AND3",
        ),
        "wheel_dir": attr.string(default = "wheels"),
        "index_url": attr.string(default = "https://pypi.org/simple"),
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
        "_wrapper_template": attr.label(
            default = "//src/templates:lock_pip_requirements_wrapper_template.sh",
            allow_single_file = True,
        ),
    },
    executable = True,
)
