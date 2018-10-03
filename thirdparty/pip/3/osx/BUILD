load("//compile:compile.bzl", "compile_requirements")

compile_requirements(
    name = "compile",
    requirements_in = "//thirdparty/pip:requirements.in",
    python_interpreter = "python3",
)

exports_files(["requirements.txt"])
