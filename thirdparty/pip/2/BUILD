load("//rules:compile.bzl", "compile_pip_requirements")

compile_pip_requirements(
    name = "compile",
    python_interpreter = "python2.7",
    requirements_in = ":requirements.in",
    requirements_txt = select({
        "//:linux": "requirements-linux.txt",
        "//:osx": "requirements-osx.txt",
    }),
)

exports_files(glob(["requirements*"]))
