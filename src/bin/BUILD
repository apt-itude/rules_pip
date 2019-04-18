load("@subpar//:subpar.bzl", "par_binary")

par_binary(
    name = "compile_pip_requirements",
    srcs = ["compile_pip_requirements.py"],
    visibility = ["//visibility:public"],
    deps = [
        "@pip_click//:lib",
        "@pip_pip//:lib",
        "@pip_pip_tools//:lib",
        "@pip_six//:lib",
    ],
)

par_binary(
    name = "create_pip_repository",
    srcs = ["create_pip_repository.py"],
    visibility = ["//visibility:public"],
    zip_safe = False,
    deps = [
        "//src/piprules",
    ],
)

py_binary(
    name = "replace_shebang",
    srcs = ["replace_shebang.py"],
    visibility = ["//:__subpackages__"],
)
