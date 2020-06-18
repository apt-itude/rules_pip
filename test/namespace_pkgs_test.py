from azure.mgmt import resource, compute


def test_namespace_pkg_import():
    # these not throwing attribute errors will verify that the import was successful
    resource.version
    compute.version
