"""Utility functions to discover python package types"""
import glob
import os
import sys
import textwrap


def setup_namespace_pkg_compatibility(wheel_dir):
    """Converts native namespace packages and pkg_resource-style packages to pkgutil-style packages
    Namespace packages can be created in one of three ways. They are detailed here:
    https://packaging.python.org/guides/packaging-namespace-packages/#creating-a-namespace-package
    'pkgutil-style namespace packages' (2) works in Bazel, but 'native namespace packages' (1) and
    'pkg_resources-style namespace packages' (3) do not.
    We ensure compatibility with Bazel of methods 1 and 3 by converting them into method 2.
    Args:
        wheel_dir: the directory of the wheel to convert
    """

    namespace_pkg_dirs = _pkg_resources_style_namespace_packages(wheel_dir)
    if not namespace_pkg_dirs and _native_namespace_packages_supported():
        namespace_pkg_dirs = _implicit_namespace_packages(
            wheel_dir, ignored_dirnames=["%s/bin" % wheel_dir]
        )

    for ns_pkg_dir in namespace_pkg_dirs:
        _add_pkgutil_style_namespace_pkg_init(ns_pkg_dir)


def _pkg_resources_style_namespace_packages(wheel_dir):
    """Discovers namespace packages implemented using the 'pkg_resources-style namespace packages' method.
    "While this approach is no longer recommended, it is widely present in most existing namespace packages." - PyPA
    See https://packaging.python.org/guides/packaging-namespace-packages/#pkg-resources-style-namespace-packages
    """
    namespace_pkg_dirs = set()

    dist_info = _get_dist_info(wheel_dir)
    namespace_packages_record_file = os.path.join(dist_info, "namespace_packages.txt")
    if os.path.exists(namespace_packages_record_file):
        with open(namespace_packages_record_file) as nspkg:
            for line in nspkg.readlines():
                namespace = line.strip().replace(".", os.sep)
                if namespace:
                    namespace_pkg_dirs.add(os.path.join(wheel_dir, namespace))
    return namespace_pkg_dirs


def _get_dist_info(wheel_dir):
    """"Returns the relative path to the dist-info directory if it exists.
    Args:
         wheel_dir: The root of the extracted wheel directory.
    Returns:
        Relative path to the dist-info directory if it exists, else, None.
    """
    dist_info_dirs = glob.glob(os.path.join(wheel_dir, "*.dist-info"))
    if not dist_info_dirs:
        raise ValueError(
            "No *.dist-info directory found. %s is not a valid Wheel." % wheel_dir
        )

    if len(dist_info_dirs) > 1:
        raise ValueError(
            "Found more than 1 *.dist-info directory. %s is not a valid Wheel."
            % wheel_dir
        )

    return dist_info_dirs[0]


def _native_namespace_packages_supported():
    """Returns true if this version of Python supports native namespace packages."""
    return (sys.version_info.major, sys.version_info.minor) >= (3, 3)


def _implicit_namespace_packages(directory, ignored_dirnames):
    """Discovers namespace packages implemented using the 'native namespace packages' method.
    AKA 'implicit namespace packages', which has been supported since Python 3.3.
    See: https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages
    Args:
        directory: The root directory to recursively find packages in.
        ignored_dirnames: A list of directories to exclude from the search
    Returns:
        The set of directories found under root to be packages using the native namespace method.
    """
    namespace_pkg_dirs = set()
    for dirpath, dirnames, filenames in os.walk(directory, topdown=True):
        # We are only interested in dirs with no __init__.py file
        if "__init__.py" in filenames:
            dirnames[:] = []  # Remove dirnames from search
            continue

        for ignored_dir in ignored_dirnames or []:
            if ignored_dir in dirnames:
                dirnames.remove(ignored_dir)

        non_empty_directory = dirnames or filenames
        if (
            non_empty_directory
            and
            # The root of the directory should never be an implicit namespace
            dirpath != directory
        ):
            namespace_pkg_dirs.add(dirpath)

    return namespace_pkg_dirs


def _add_pkgutil_style_namespace_pkg_init(dir_path):
    """Adds 'pkgutil-style namespace packages' init file to the given directory
    See: https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages
    Args:
        dir_path: The directory to create an __init__.py for.
    Raises:
        ValueError: If the directory already contains an __init__.py file
    """
    ns_pkg_init_filepath = os.path.join(dir_path, "__init__.py")

    if os.path.isfile(ns_pkg_init_filepath):
        raise ValueError("%s already contains an __init__.py file." % dir_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(ns_pkg_init_filepath, "w") as ns_pkg_init_f:
        # See https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages
        ns_pkg_init_f.write(
            textwrap.dedent(
                """\
                # __path__ manipulation added by rules_python_external to support namespace pkgs.
                __path__ = __import__('pkgutil').extend_path(__path__, __name__)
                """
            )
        )
