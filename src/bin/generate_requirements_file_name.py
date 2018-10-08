#!/usr/bin/env python
"""
Prints the name of the requirements file that should be generated for the
current environment
"""

from piprules import requirements


if __name__ == '__main__':
    print(requirements.generate_filename())
