workspace(name = "com_apt_itude_rules_pypi")

git_repository(
    name = "bazel_skylib",
    remote = "https://github.com/bazelbuild/bazel-skylib.git",
    tag = "0.5.0",
)

load("//thirdparty/pip/tools:rules.bzl", "pip_tools_repositories")

pip_tools_repositories()
