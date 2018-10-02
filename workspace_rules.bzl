_BUILD_FILE_CONTENT = """
py_library(
    name="lib",
    srcs=glob(["**/*.py"]),
    data = glob(["**/*"], exclude=["**/*.py", "BUILD", "WORKSPACE", "*.whl.zip"]),
    imports=["."],
    visibility=["//visibility:public"],
)
"""

def pip_remote_wheel(name, url, sha256):
    native.new_http_archive(
        name = name,
        url = url,
        sha256 = sha256,
        build_file_content = _BUILD_FILE_CONTENT,
        type = "zip",
    )
