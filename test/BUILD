py_test(
    name = "main",
    srcs = glob(["*.py"]),
    deps = select(
        {
            "//:python2_runtime": [
                "@pip2//isort",
                "@pip2//pathlib2",
                "@pip2//pytest",
                "@pip2//pytest_mock",
                "@pip2//pyyaml",
            ],
            "//:python3_runtime": [
                "@pip3//isort",
                "@pip3//pytest",
                "@pip3//pytest_mock",
                "@pip3//pyyaml",
            ],
        },
        no_match_error = "No Python runtime selected",
    ),
)
