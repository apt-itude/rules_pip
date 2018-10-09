workspace(name = "com_apt_itude_rules_pypi")

git_repository(
    name = "bazel_skylib",
    remote = "https://github.com/bazelbuild/bazel-skylib.git",
    tag = "0.5.0",
)

git_repository(
    name = "subpar",
    remote = "https://github.com/google/subpar",
    tag = "1.3.0",
)

http_archive(
    name = "io_bazel_rules_go",
    sha256 = "97cf62bdef33519412167fd1e4b0810a318a7c234f5f8dc4f53e2da86241c492",
    url = "https://github.com/bazelbuild/rules_go/releases/download/0.15.3/rules_go-0.15.3.tar.gz",
)

http_archive(
    name = "com_github_bazelbuild_buildtools",
    strip_prefix = "buildtools-0.15.0",
    url = "https://github.com/bazelbuild/buildtools/archive/0.15.0.zip",
)

# Load buildifier dependencies

load(
    "@io_bazel_rules_go//go:def.bzl",
    "go_register_toolchains",
    "go_rules_dependencies",
)

go_rules_dependencies()

go_register_toolchains()

load(
    "@com_github_bazelbuild_buildtools//buildifier:deps.bzl",
    "buildifier_dependencies",
)

buildifier_dependencies()

# Load PIP repositories

load("//rules:repository.bzl", "pip_repository", "pip_rules_dependencies")

pip_rules_dependencies()

pip_repository(
    name = "pip3",
    python_interpreter = "python3.6",
    requirements_per_platform = {
        "//thirdparty/pip/3:requirements-linux.txt": "linux",
        "//thirdparty/pip/3:requirements-osx.txt": "osx",
    },
)
