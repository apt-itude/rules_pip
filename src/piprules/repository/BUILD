load("@subpar//:subpar.bzl", "par_binary")

py_library(
    name = "repository",
    srcs = glob(["*.py"]),
    deps = [
        "@pip3//wheel",
        "//src/piprules/common",
    ],
    imports = ["../../"],
    visibility = ["//visibility:public"],
)
