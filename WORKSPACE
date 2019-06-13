workspace(name = "com_apt_itude_rules_pip")

# Dependencies for this repository

load("//rules:dependencies.bzl", "pip_rules_dependencies")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

pip_rules_dependencies()

# Buildifier repositories

http_archive(
    name = "io_bazel_rules_go",
    sha256 = "7be7dc01f1e0afdba6c8eb2b43d2fa01c743be1b9273ab1eaf6c233df078d705",
    url = "https://github.com/bazelbuild/rules_go/releases/download/0.16.5/rules_go-0.16.5.tar.gz",
)

http_archive(
    name = "com_github_bazelbuild_buildtools",
    strip_prefix = "buildtools-0.15.0",
    url = "https://github.com/bazelbuild/buildtools/archive/0.15.0.zip",
)

load(
    "@io_bazel_rules_go//go:def.bzl",
    "go_register_toolchains",
    "go_rules_dependencies",
)

go_rules_dependencies()

go_register_toolchains()

load(
    "@com_github_bazelbuild_buildtools//buildifier:deps.bzl",
    "buildifier_dependencies",
)

buildifier_dependencies()

# PIP repositories

load("//rules:new_repository.bzl", "pip_repository")

pip_repository(
    name = "pip",
    requirements = "//thirdparty/pip:requirements-lock.json",
)

load("@pip//:requirements.bzl", "pip_install")

pip_install()
