load("//rules:compile.bzl", "compile_pip_requirements")
load("//:python.bzl", "PYTHON2")

compile_pip_requirements(
    name = "compile",
    python_interpreter = PYTHON2,
    requirements_in = "//thirdparty/pip:requirements.in",
    requirements_txt = select({
        "//:linux": "requirements-linux.txt",
        "//:osx": "requirements-osx.txt",
    }),
)

exports_files(glob(["requirements*"]))
