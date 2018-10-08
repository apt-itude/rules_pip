load("//rules:compile.bzl", "compile_pip_requirements")

compile_pip_requirements(
    name = "compile3",
    requirements_in = ":requirements.in",
    python_interpreter = "python3.6",
)

exports_files(glob(["requirements*"]))
