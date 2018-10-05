workspace(name = "com_apt_itude_rules_pypi")

git_repository(
    name = "bazel_skylib",
    remote = "https://github.com/bazelbuild/bazel-skylib.git",
    tag = "0.5.0",
)

load("//download:rules.bzl", "pip_requirements")

pip_requirements(
    name = "pip3",
    requirements = "//thirdparty/pip/3/osx:requirements.txt",
    python_interpreter = "python3",
)
