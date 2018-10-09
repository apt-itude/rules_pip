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

py_runtime(
    name = "python2",
    files = [],
    interpreter_path = select({
        ":linux": "/usr/bin/python2.7",
        ":osx": "/usr/local/bin/python2.7",
    }),
    visibility = ["//visibility:public"],
)

py_runtime(
    name = "python3",
    files = [],
    interpreter_path = select({
        ":linux": "/usr/bin/python3.6",
        ":osx": "/usr/local/bin/python3.6",
    }),
    visibility = ["//visibility:public"],
)

config_setting(
    name = "python2_runtime",
    values = {"python_top": "//:python2"},
    visibility = ["//visibility:public"],
)

config_setting(
    name = "python3_runtime",
    values = {"python_top": "//:python3"},
    visibility = ["//visibility:public"],
)
