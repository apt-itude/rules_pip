import os
import sys

import pytest


TEST_DIR = os.path.dirname(__file__)


def main():
    args = sys.argv[1:] + [TEST_DIR]
    sys.exit(pytest.main(args))


if __name__ == '__main__':
    main()
