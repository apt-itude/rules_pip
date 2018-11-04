load("//:python.bzl", "PYTHON2", "PYTHON3")

def _pytest_main_impl(ctx):
    substitutions = {
        "@@INTERPRETER@@": ctx.attr.interpreter,
        "@@TEST_PATH@@": ctx.file.src.short_path,
    }

    ctx.actions.expand_template(
        template = ctx.file._template,
        output = ctx.outputs.main,
        substitutions = substitutions,
    )

_pytest_main = rule(
    implementation = _pytest_main_impl,
    attrs = {
        "src": attr.label(
            mandatory = True,
            allow_single_file = [".py"],
        ),
        "interpreter": attr.string(mandatory = True),
        "_template": attr.label(
            default = "//tools/pytest:main_template.py",
            allow_single_file = True,
        ),
    },
    outputs = {
        "main": "%{name}.py",
    },
)

def pytest_test(name, src, python_version = 3, **kwargs):
    if python_version == 2:
        interpreter = PYTHON2
        pytest_dep = "@pip2//pytest"
    elif python_version == 3:
        interpreter = PYTHON3
        pytest_dep = "@pip3//pytest"
    else:
        fail("Python version must be 2 or 3")

    main_name = "%s_main" % name
    main_output = ":%s.py" % main_name

    _pytest_main(
        name = main_name,
        src = src,
        interpreter = interpreter,
    )

    deps = kwargs.pop("deps", []) + [pytest_dep]

    native.py_test(
        name = name,
        srcs = [main_output, src],
        main = main_output,
        deps = deps,
        **kwargs
    )
