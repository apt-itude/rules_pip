load("//rules:compile.bzl", "compile_pip_requirements")

compile_pip_requirements(
    name = "compile3",
    python_interpreter = "python3.6",
    requirements_in = ":requirements.in",
)

exports_files(glob(["requirements*"]))
