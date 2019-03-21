py_runtime(
    name = "dynamic",
    files = [],
    interpreter = "dynamic.sh",
    visibility = ["//visibility:public"],
)

py_runtime(
    name = "version-based",
    interpreter = select({
        "@bazel_tools//tools/python:PY2": "python2.sh",
        "@bazel_tools//tools/python:PY3": "python3.sh",
    }),
    files = [],
    visibility = ["//visibility:public"],
)
