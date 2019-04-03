import errno
import contextlib
import itertools
import os


def normalize_distribution_name(name):
    return name.lower().replace("-", "_")


def get_path_stem(path):
    return os.path.splitext(os.path.basename(path))[0]


def ensure_directory_exists(path):
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise err


def get_import_path_of_module(module):
    return os.path.abspath(os.path.dirname(os.path.dirname(module.__file__)))


@contextlib.contextmanager
def prepend_to_pythonpath(paths):
    original_pythonpath = os.environ.get("PYTHONPATH")
    original_parts = original_pythonpath.split(":") if original_pythonpath else []
    os.environ["PYTHONPATH"] = ":".join(paths + original_parts)

    try:
        yield
    finally:
        if original_pythonpath is None:
            del os.environ["PYTHONPATH"]
        else:
            os.environ["PYTHONPATH"] = original_pythonpath


def full_groupby(iterable, key=None):
    """Like itertools.groupby(), but sorts the input on the group key first."""
    return itertools.groupby(sorted(iterable, key=key), key=key)
