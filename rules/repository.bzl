load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def _pip_repository_impl(repo_ctx):
    repo_ctx.file("BUILD", "")

    create_repo_exe_path = repo_ctx.path(repo_ctx.attr._create_repo_exe)
    repo_directory = repo_ctx.path("")
    requirements_paths = [
        repo_ctx.path(label)
        for label in repo_ctx.attr.requirements
    ]

    repo_ctx.execute([
        repo_ctx.attr.python_interpreter,
        create_repo_exe_path,
        repo_directory,
    ] + requirements_paths)

pip_repository = repository_rule(
    implementation = _pip_repository_impl,
    attrs = {
        "requirements": attr.label_list(
            allow_files = [".txt"],
            mandatory = True,
            allow_empty = False,
        ),
        "python_interpreter": attr.string(default = "python"),
        "_create_repo_exe": attr.label(
            default = "//tools:create_pip_repository.par",
            executable = True,
            cfg = "host",
        ),
    },
)

_BUILD_FILE_CONTENT = """
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

def rules_pip_repositories():
    existing_rules = native.existing_rules()

    if "pip_pip" not in existing_rules:
        http_archive(
            name = "pip_pip",
            url = "https://files.pythonhosted.org/packages/c2/d7/90f34cb0d83a6c5631cf71dfe64cc1054598c843a92b400e55675cc2ac37/pip-18.1-py2.py3-none-any.whl",
            sha256 = "7909d0a0932e88ea53a7014dfd14522ffef91a464daaaf5c573343852ef98550",
            build_file_content = _BUILD_FILE_CONTENT,
            type = "zip",
        )

    if "pip_wheel" not in existing_rules:
        http_archive(
            name = "pip_wheel",
            url = "https://files.pythonhosted.org/packages/fc/e9/05316a1eec70c2bfc1c823a259546475bd7636ba6d27ec80575da523bc34/wheel-0.32.1-py2.py3-none-any.whl",
            sha256 = "9fa1f772f1a2df2bd00ddb4fa57e1cc349301e1facb98fbe62329803a9ff1196",
            build_file_content = _BUILD_FILE_CONTENT,
            type = "zip",
        )

    if "pip_pip_tools" not in existing_rules:
        http_archive(
            name = "pip_pip_tools",
            url = "https://files.pythonhosted.org/packages/f7/58/7a3c61ff7ea45cf0f13f3c58c5261c598a1923efa3327494f70c2d532cba/pip_tools-3.1.0-py2.py3-none-any.whl",
            sha256 = "31b43e5f8d605fc84f7506199025460abcb98a29d12cc99db268f73e39cf55e5",
            build_file_content = _BUILD_FILE_CONTENT,
            type = "zip",
        )

    if "pip_click" not in existing_rules:
        http_archive(
            name = "pip_click",
            url = "https://files.pythonhosted.org/packages/fa/37/45185cb5abbc30d7257104c434fe0b07e5a195a6847506c074527aa599ec/Click-7.0-py2.py3-none-any.whl",
            sha256 = "2335065e6395b9e67ca716de5f7526736bfa6ceead690adf616d925bdc622b13",
            build_file_content = _BUILD_FILE_CONTENT,
            type = "zip",
        )

    if "pip_six" not in existing_rules:
        http_archive(
            name = "pip_six",
            url = "https://files.pythonhosted.org/packages/67/4b/141a581104b1f6397bfa78ac9d43d8ad29a7ca43ea90a2d863fe3056e86a/six-1.11.0-py2.py3-none-any.whl",
            sha256 = "832dc0e10feb1aa2c68dcc57dbb658f1c7e65b9b61af69048abc87a2db00a0eb",
            build_file_content = _BUILD_FILE_CONTENT,
            type = "zip",
        )
