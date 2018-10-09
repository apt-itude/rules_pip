import sys

if sys.version_info.major == 2:
    import pathlib2 as pathlib
else:
    import pathlib


def test_pathlib():
    assert pathlib.Path("some/test/file.txt").stem == "file"
