import pytest


@pytest.mark.parametrize("python_version", [2, 3])
def test_output(python_version):
    path = "test/ietf-yang-metadata-{}.yin".format(python_version)

    with open(path) as yin_file:
        contents = yin_file.read()

    with open("test/ietf-yang-metadata.yin") as expected_yin_file:
        expected_contents = expected_yin_file.read()

    assert contents == expected_contents
