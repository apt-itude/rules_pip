workspace(name = "com_apt_itude_rules_pip")

# Dependencies for this repository

load("//rules:dependencies.bzl", "pip_rules_dependencies")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

pip_rules_dependencies()

# Buildifier repositories

http_archive(
    name = "io_bazel_rules_go",
    urls = [
        "https://storage.googleapis.com/bazel-mirror/github.com/bazelbuild/rules_go/releases/download/0.19.3/rules_go-0.19.3.tar.gz",
        "https://github.com/bazelbuild/rules_go/releases/download/0.19.3/rules_go-0.19.3.tar.gz",
    ],
    sha256 = "313f2c7a23fecc33023563f082f381a32b9b7254f727a7dd2d6380ccc6dfe09b",
)

load("@io_bazel_rules_go//go:deps.bzl", "go_rules_dependencies", "go_register_toolchains")

go_rules_dependencies()

go_register_toolchains()

http_archive(
    name = "com_github_bazelbuild_buildtools",
    strip_prefix = "buildtools-0.15.0",
    url = "https://github.com/bazelbuild/buildtools/archive/0.15.0.zip",
)

load(
    "@com_github_bazelbuild_buildtools//buildifier:deps.bzl",
    "buildifier_dependencies",
)

buildifier_dependencies()

# PIP repositories

load("//rules:repository.bzl", "pip_repository")

pip_repository(
    name = "pip",
    requirements = "//thirdparty/pip:requirements-lock.json",
)

load("@pip//:requirements.bzl", "pip_install")

pip_install()
