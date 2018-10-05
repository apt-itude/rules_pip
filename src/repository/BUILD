load("@subpar//:subpar.bzl", "par_binary")

par_binary(
    name = "create_pip_repository",
    srcs = ["create.py"],
    main = "create.py",
    deps = [
        "@pip3//wheel",
    ],
    visibility = ["//visibility:public"],
)
