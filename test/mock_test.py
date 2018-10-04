import sys

import pytest


@pytest.fixture
def mock_argv(mocker):
    return mocker.patch.object(sys, "argv", ["fake", "args"])


def test_mock_args(mock_argv):
    assert sys.argv == ["fake", "args"]
