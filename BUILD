load("@com_github_bazelbuild_buildtools//buildifier:def.bzl", "buildifier")

# Run this target to auto-format all Bazel files
buildifier(name = "format")

config_setting(
    name = "linux",
    constraint_values = ["@bazel_tools//platforms:linux"],
    visibility = ["//visibility:public"],
)

config_setting(
    name = "osx",
    constraint_values = ["@bazel_tools//platforms:osx"],
    visibility = ["//visibility:public"],
)
