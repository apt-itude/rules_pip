load("//:python.bzl", "PYTHON2", "PYTHON3")
load("//tools/pytest:rules.bzl", "pytest_test")

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
    name = "old_data_test",
    src = "old_data_test.py",
    data = [
        "ietf-yang-metadata.yin",
        ":test-yin-2",
        ":test-yin-3",
    ],
    python_version = 3,
)

py_test(
    name = "conditional_dependencies_test_py2",
    srcs = ["conditional_dependencies_test.py"],
    main = "conditional_dependencies_test.py",
    deps = [
        "@pip//isort",
        "@pip//pathlib2",
    ],
    python_version = "PY2",
    tags = ["new"],
)

py_test(
    name = "conditional_dependencies_test_py3",
    srcs = ["conditional_dependencies_test.py"],
    main = "conditional_dependencies_test.py",
    deps = ["@pip//isort"],
    python_version = "PY3",
    tags = ["new"],
)


py_test(
    name = "local_wheel_test_py2",
    srcs = ["local_wheel_test.py"],
    main = "local_wheel_test.py",
    deps = ["@pip//pyyaml"],
    python_version = "PY2",
    tags = ["new"],
)

py_test(
    name = "local_wheel_test_py3",
    srcs = ["local_wheel_test.py"],
    main = "local_wheel_test.py",
    deps = ["@pip//pyyaml"],
    python_version = "PY3",
    tags = ["new"],
)


py_test(
    name = "multi_platform_multi_python_dep_test_py2",
    srcs = ["multi_platform_multi_python_dep_test.py"],
    main = "multi_platform_multi_python_dep_test.py",
    deps = ["@pip//lxml"],
    python_version = "PY2",
    tags = ["new"],
)

py_test(
    name = "multi_platform_multi_python_dep_test_py3",
    srcs = ["multi_platform_multi_python_dep_test.py"],
    main = "multi_platform_multi_python_dep_test.py",
    deps = ["@pip//lxml"],
    python_version = "PY3",
    tags = ["new"],
)

genrule(
    name = "pyang-main",
    srcs = ["@pip__pyang_1_7_8_py2_py3_none_any//scripts:pyang"],
    outs = ["pyang-main.py"],
    cmd = "cp $< $@",
)

py_binary(
    name = "pyang-exe",
    srcs = [":pyang-main"],
    main = "pyang-main.py",
    deps = ["@pip//pyang"],
    python_version = "PY2",
)

genrule(
    name = "test-yin",
    srcs = ["@pip__pyang_1_7_8_py2_py3_none_any//data/share/yang/modules/ietf:ietf-yang-metadata.yang"],
    outs = ["ietf-yang-metadata-generated.yin"],
    tools = [":pyang-exe"],
    cmd = "$(location :pyang-exe) -f yin -o $@ $<",
)

py_test(
    name = "data_test",
    srcs = ["data_test.py"],
    data = [
        "ietf-yang-metadata.yin",
        ":test-yin",
    ],
    python_version = "PY3",
    tags = ["new"],
)
