load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

_WHEEL_BUILD_FILE_CONTENT = """
py_library(
    name = "lib",
    srcs = glob(["**/*.py"]),
    data = glob(
        ["**/*"],
        exclude = [
            "**/*.py",
            "**/* *",  # Bazel runfiles cannot have spaces in the name
            "BUILD",
            "WORKSPACE",
            "*.whl.zip",
        ],
    ),
    imports = ["."],
    visibility = ["//visibility:public"],
)
"""

def pip_rules_dependencies():
    _remote_wheel(
        name = "pip",
        url = "https://files.pythonhosted.org/packages/c2/d7/90f34cb0d83a6c5631cf71dfe64cc1054598c843a92b400e55675cc2ac37/pip-18.1-py2.py3-none-any.whl",
        sha256 = "7909d0a0932e88ea53a7014dfd14522ffef91a464daaaf5c573343852ef98550",
    )

    _remote_wheel(
        name = "setuptools",
        url = "https://files.pythonhosted.org/packages/96/06/c8ee69628191285ddddffb277bd5abdf769166e7a14b867c2a172f0175b1/setuptools-40.4.3-py2.py3-none-any.whl",
        sha256 = "ce4137d58b444bac11a31d4e0c1805c69d89e8ed4e91fde1999674ecc2f6f9ff",
    )

    _remote_wheel(
        name = "wheel",
        url = "https://files.pythonhosted.org/packages/fc/e9/05316a1eec70c2bfc1c823a259546475bd7636ba6d27ec80575da523bc34/wheel-0.32.1-py2.py3-none-any.whl",
        sha256 = "9fa1f772f1a2df2bd00ddb4fa57e1cc349301e1facb98fbe62329803a9ff1196",
    )

    _remote_wheel(
        name = "pip_tools",
        url = "https://files.pythonhosted.org/packages/f7/58/7a3c61ff7ea45cf0f13f3c58c5261c598a1923efa3327494f70c2d532cba/pip_tools-3.1.0-py2.py3-none-any.whl",
        sha256 = "31b43e5f8d605fc84f7506199025460abcb98a29d12cc99db268f73e39cf55e5",
    )

    _remote_wheel(
        name = "click",
        url = "https://files.pythonhosted.org/packages/fa/37/45185cb5abbc30d7257104c434fe0b07e5a195a6847506c074527aa599ec/Click-7.0-py2.py3-none-any.whl",
        sha256 = "2335065e6395b9e67ca716de5f7526736bfa6ceead690adf616d925bdc622b13",
    )

    _remote_wheel(
        name = "six",
        url = "https://files.pythonhosted.org/packages/67/4b/141a581104b1f6397bfa78ac9d43d8ad29a7ca43ea90a2d863fe3056e86a/six-1.11.0-py2.py3-none-any.whl",
        sha256 = "832dc0e10feb1aa2c68dcc57dbb658f1c7e65b9b61af69048abc87a2db00a0eb",
    )

    _ensure_rule_exists(
        git_repository,
        name = "bazel_skylib",
        remote = "https://github.com/bazelbuild/bazel-skylib.git",
        tag = "0.5.0",
    )

    _ensure_rule_exists(
        git_repository,
        name = "subpar",
        remote = "https://github.com/google/subpar",
        tag = "2.0.0",
    )

def _remote_wheel(name, url, sha256):
    _ensure_rule_exists(
        http_archive,
        name = "pip_%s" % name,
        url = url,
        sha256 = sha256,
        build_file_content = _WHEEL_BUILD_FILE_CONTENT,
        type = "zip",
    )

def _ensure_rule_exists(rule_type, name, **kwargs):
    if name not in native.existing_rules():
        rule_type(name = name, **kwargs)
