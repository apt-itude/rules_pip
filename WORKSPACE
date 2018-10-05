workspace(name = "com_apt_itude_rules_pypi")

git_repository(
    name = "bazel_skylib",
    remote = "https://github.com/bazelbuild/bazel-skylib.git",
    tag = "0.5.0",
)

git_repository(
    name = "subpar",
    remote = "https://github.com/google/subpar",
    tag = "1.3.0",
)

load("//rules:repository.bzl", "pip_repository")

pip_repository(
    name = "pip3",
    requirements = "//thirdparty/pip/3/osx:requirements.txt",
    python_interpreter = "python3",
)
