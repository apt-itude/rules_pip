import errno
import hashlib
import itertools
import os


def get_path_stem(path):
    return os.path.splitext(os.path.basename(path))[0]


def ensure_directory_exists(path):
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise err


def full_groupby(iterable, key=None):
    """Like itertools.groupby(), but sorts the input on the group key first."""
    return itertools.groupby(sorted(iterable, key=key), key=key)


def compute_file_hash(path, algorithm="sha256"):
    hasher = hashlib.new(algorithm)
    block_size = 4096

    with open(path, mode='rb') as file_:
        buf = file_.read(block_size)
        while buf:
            hasher.update(buf)
            buf = file_.read(block_size)

    return hasher.hexdigest()
