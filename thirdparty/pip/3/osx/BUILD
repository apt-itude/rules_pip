load("//rules:compile.bzl", "compile_pip_requirements")

compile_pip_requirements(
    name = "compile",
    requirements_in = "//thirdparty/pip:requirements.in",
    python_interpreter = "python3",
)

exports_files(["requirements.txt"])
