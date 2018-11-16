load("//:python.bzl", "PYTHON3")
load("//tools/pytest:rules.bzl", "pytest_test")

pytest_test(
    name = "dependency_deduplication_test_2",
    src = "dependency_deduplication_test.py",
    deps = ["@pip2//isort"],
    python_version = 2,
)

pytest_test(
    name = "dependency_deduplication_test_3",
    src = "dependency_deduplication_test.py",
    deps = ["@pip3//isort"],
    python_version = 3,
)

pytest_test(
    name = "mock_test_2",
    src = "mock_test.py",
    deps = ["@pip2//pytest_mock"],
    python_version = 2,
)

pytest_test(
    name = "mock_test_3",
    src = "mock_test.py",
    deps = ["@pip3//pytest_mock"],
    python_version = 3,
)

pytest_test(
    name = "pathlib_test_2",
    src = "pathlib_test.py",
    deps = ["@pip2//pathlib2"],
    python_version = 2,
)

pytest_test(
    name = "pathlib_test_3",
    src = "pathlib_test.py",
    python_version = 3,
)

pytest_test(
    name = "pyyaml_test_2",
    src = "pyyaml_test.py",
    deps = ["@pip2//pyyaml"],
    python_version = 2,
)

pytest_test(
    name = "pyyaml_test_3",
    src = "pyyaml_test.py",
    deps = ["@pip3//pyyaml"],
    python_version = 3,
)

py_binary(
    name = "pyang2",
    srcs = ["@pip2//pyang:script_pyang.py"],
    main = "@pip2//pyang:script_pyang.py",
    deps = ["@pip2//pyang"],
)

genrule(
    name = "test-yin-2",
    srcs = ["test.yang"],
    outs = ["test-2.yin"],
    tools = [":pyang2"],
    cmd = "$(location :pyang2) -f yin -o $@ $<",
)

py_binary(
    name = "pyang3",
    srcs = ["@pip3//pyang:script_pyang.py"],
    main = "@pip3//pyang:script_pyang.py",
    deps = ["@pip3//pyang"],
)

genrule(
    name = "test-yin-3",
    srcs = ["test.yang"],
    outs = ["test-3.yin"],
    tools = [":pyang3"],
    cmd = "$(location :pyang3) -f yin -o $@ $<",
)

pytest_test(
    name = "script_test",
    src = "script_test.py",
    data = [
        ":test-yin-2",
        ":test-yin-3",
    ],
    python_version = 3,
)
