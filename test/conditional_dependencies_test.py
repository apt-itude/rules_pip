"""
This tests conditional dependencies based on Python runtime.

In Python 2, isort requires futures and backports-functools-lru-cache, but in Python 3
it has no dependencies. The import should succeed in both cases.

The pathlib2 module is only included if running Python 2.
"""
import sys

import isort

if sys.version_info.major == 2:
    import pathlib2 as pathlib
else:
    import pathlib

assert pathlib.Path("some/test/file.txt").stem == "file"
