#!/usr/bin/env @@INTERPRETER@@

import sys

import pytest


def main():
    args = sys.argv[1:]
    args.append("@@TEST_PATH@@")

    sys.exit(pytest.main(args))


if __name__ == '__main__':
    main()
