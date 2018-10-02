load("//:workspace_rules.bzl", "pip_remote_wheel")


def pip_tools_libs():
    native.py_library(
        name = "click",
        deps = [
            "@pip__click//:lib",
        ],
        visibility = ["//visibility:public"],
    )
    native.py_library(
        name = "pip_tools",
        deps = [
            "@pip__pip_tools//:lib",
            ":click",
            ":six",
        ],
        visibility = ["//visibility:public"],
    )
    native.py_library(
        name = "six",
        deps = [
            "@pip__six//:lib",
        ],
        visibility = ["//visibility:public"],
    )


def pip_tools_repositories():
    existing_rules = native.existing_rules()

    if "pip__click" not in existing_rules:
        pip_remote_wheel(
            name = "pip__click",
            url = "https://files.pythonhosted.org/packages/fa/37/45185cb5abbc30d7257104c434fe0b07e5a195a6847506c074527aa599ec/Click-7.0-py2.py3-none-any.whl",
            sha256 = "2335065e6395b9e67ca716de5f7526736bfa6ceead690adf616d925bdc622b13",
        )

    if "pip__pip_tools" not in existing_rules:
        pip_remote_wheel(
            name = "pip__pip_tools",
            url = "https://files.pythonhosted.org/packages/2c/e5/78ee3b9c4503772fcf71f923a4edbd3d597cb61260f59c495ec54cee794c/pip_tools-3.0.0-py2.py3-none-any.whl",
            sha256 = "e45e5198ce3799068642ebb0e7c9be5520bcff944c0186f79c1199a2759c970a",
        )

    if "pip__six" not in existing_rules:
        pip_remote_wheel(
            name = "pip__six",
            url = "https://files.pythonhosted.org/packages/2c/e5/78ee3b9c4503772fcf71f923a4edbd3d597cb61260f59c495ec54cee794c/pip_tools-3.0.0-py2.py3-none-any.whl",
            sha256 = "832dc0e10feb1aa2c68dcc57dbb658f1c7e65b9b61af69048abc87a2db00a0eb",
        )
