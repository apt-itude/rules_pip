"""
In Python 2, isort requires futures, but pkg_resources produces 2 different requirement
instances for that library. This ensures that the duplicate requirements don't cause
duplicate dependencies to be added to the build rule, which is an error.
"""
def test_isort():
    import isort
