#!/usr/bin/env python
"""Wrapper for the pip-tools compile entry point"""

from piptools.scripts import compile as pip_compile


if __name__ == '__main__':
    pip_compile.cli()
