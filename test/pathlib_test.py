"""
This tests conditional dependencies based on Python runtime. The pathlib2
module is only included if running Python 2.
"""

import sys

if sys.version_info.major == 2:
    import pathlib2 as pathlib
else:
    import pathlib


def test_pathlib():
    assert pathlib.Path("some/test/file.txt").stem == "file"
