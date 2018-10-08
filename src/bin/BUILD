load("@subpar//:subpar.bzl", "par_binary")

par_binary(
    name = "compile_pip_requirements",
    srcs = ["compile_pip_requirements.py"],
    deps = [
        "@pip_click//:lib",
        "@pip_pip_tools//:lib",
        "@pip_six//:lib",
    ],
    visibility = ["//visibility:public"],
)

par_binary(
    name = "create_pip_repository",
    srcs = ["create_pip_repository.py"],
    deps = [
        "//src/piprules",
    ],
    visibility = ["//visibility:public"],
)

par_binary(
    name = "generate_requirements_file_name",
    srcs = ["generate_requirements_file_name.py"],
    deps = [
        "//src/piprules",
    ],
    visibility = ["//visibility:public"],
)
