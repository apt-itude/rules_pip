load("@bazel_skylib//lib:paths.bzl", "paths")

def _get_path_relative_to_workspace(path, ctx):
    if paths.is_absolute(path):
        return paths.relativize(path, "/")
    else:
        return paths.join(ctx.label.package, path)

def _pip_lock_impl(ctx):
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
    implementation = _pip_lock_impl,
    doc = """
        Defines a binary target that may be executed via `bazel run` in order to compile
        any number of `requirements.txt` files into a single `requirements-lock.json`
        file. This binary should be executed on all supported platforms to add the 
        correct set of requirements to the lock file for each platform. 
    """,
    attrs = {
        "requirements": attr.label_list(
            allow_files = True,
            doc = """
                Files following the standard requirements file format 
                (https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format)

                These should define direct dependencies only, and should not pin
                dependency versions unless necessary.
            """,
        ),
        "requirements_lock": attr.string(
            default = "requirements-lock.json",
            doc = """
                A path relative to the package in which this rule is defined to which
                the compiled lock file should be written. This file should 
                be source-controlled and provided as input to the `pip_repository` rule.
            """,
        ),
        "python_version": attr.string(
            values = ["PY2", "PY3", "PY2AND3"],
            default = "PY2AND3",
            doc = """
                The Python versions for which to compile the requirement set. The
                requirements lock file will contain one environment per Python version 
                per platform. Each environment will define its locked requirement set.
            """,
        ),
        "wheel_dir": attr.string(
            default = "wheels",
            doc = """
                A path to a directory relative to the package in which this rule is
                defined in which built wheels will be stored. If the given directory
                does not already exist, it will be created. 
                
                Wheels will be built for any required distribution that is not already 
                available as a wheel for the given environment. These wheels may be
                committed to source control or published to a custom Python package 
                index. If the latter approach is used, this binary should be run again
                with the `index_url` attribute set to the URL of that index in order to 
                resolve the new locations of those wheels.
            """,
        ),
        "index_url": attr.string(
            default = "https://pypi.org/simple",
            doc = "The URL of a custom Python package index to use instead of PyPI.",
        ),
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
