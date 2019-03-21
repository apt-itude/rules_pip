load("//:python.bzl", "PYTHON2", "PYTHON3")
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

genrule(
    name = "pyang2_script",
    srcs = ["@pip2//pyang/scripts:pyang"],
    outs = ["pyang2.py"],
    tools = ["//src/bin:replace_shebang"],
    cmd = "$(location //src/bin:replace_shebang) $< $@ %s" % PYTHON2,
)

py_binary(
    name = "pyang2",
    srcs = [":pyang2_script"],
    deps = ["@pip2//pyang"],
)

genrule(
    name = "test-yin-2",
    srcs = ["@pip2//pyang/data/share/yang/modules/ietf:ietf-yang-metadata.yang"],
    outs = ["ietf-yang-metadata-2.yin"],
    tools = [":pyang2"],
    cmd = "$(location :pyang2) -f yin -o $@ $<",
)

genrule(
    name = "pyang3_script",
    srcs = ["@pip3//pyang/scripts:pyang"],
    outs = ["pyang3.py"],
    tools = ["//src/bin:replace_shebang"],
    cmd = "$(location //src/bin:replace_shebang) $< $@ %s" % PYTHON3,
)

py_binary(
    name = "pyang3",
    srcs = [":pyang3_script"],
    deps = ["@pip3//pyang"],
)

genrule(
    name = "test-yin-3",
    srcs = ["@pip3//pyang/data/share/yang/modules/ietf:ietf-yang-metadata.yang"],
    outs = ["ietf-yang-metadata-3.yin"],
    tools = [":pyang3"],
    cmd = "$(location :pyang3) -f yin -o $@ $<",
)

pytest_test(
    name = "data_test",
    src = "data_test.py",
    data = [
        "ietf-yang-metadata.yin",
        ":test-yin-2",
        ":test-yin-3",
    ],
    python_version = 3,
)

py_test(
    name = "multi_platform_multi_python_dep_test_py2",
    srcs = ["multi_platform_multi_python_dep_test.py"],
    main = "multi_platform_multi_python_dep_test.py",
    deps = ["@pip//:lxml"],
    python_version = "PY2",
)

py_test(
    name = "multi_platform_multi_python_dep_test_py3",
    srcs = ["multi_platform_multi_python_dep_test.py"],
    main = "multi_platform_multi_python_dep_test.py",
    deps = ["@pip//:lxml"],
    python_version = "PY3",
)
