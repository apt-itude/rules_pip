from azure.mgmt import resource, compute


def test_namespace_pkg_import():
    resource.version
    compute.version
