#!/usr/bin/env python3

import argparse
import pathlib
import re
import sys


SHEBANG_REGEX = re.compile(r"^#!.*")


def main():
    args = parse_args()

    args.output_path.parent.mkdir(parents=True, exist_ok=True)

    replace_shebang(args.input_path, args.output_path, args.interpreter)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path", type=pathlib.Path)
    parser.add_argument("output_path", type=pathlib.Path)
    parser.add_argument("interpreter")

    return parser.parse_args()


def replace_shebang(input_path, output_path, interpreter):
    input_contents = input_path.read_text()

    output_contents = SHEBANG_REGEX.sub(
        make_shebang(interpreter),
        input_contents,
    )

    output_path.write_text(output_contents)


def make_shebang(interpreter):
    return f"#!/usr/bin/env {interpreter}"


if __name__ == "__main__":
    main()
