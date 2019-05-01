"""
In Python 2, isort requires futures and backports-functools-lru-cache, but in Python 3
it has no dependencies. This import should succeed in both cases.
"""
import isort
