#!/usr/bin/env python2
import argparse
import json


def main():
    args = parse_args()
    requirements = load_requirements(args.requirements_file)
    bzl_file_contents = BzlFileGenerator(requirements).generate()
    write_bzl_file(args.output_path, bzl_file_contents)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("requirements_file")
    parser.add_argument("output_path")
    return parser.parse_args()


def load_requirements(path):
    with open(path) as requirements_file:
        return json.load(requirements_file)


class BzlFileGenerator(object):

    def __init__(self, requirements):
        self.requirements = requirements

    @property
    def requirements_list(self):
        return self.requirements["requirements"]

    def generate(self):
        return '\n'.join(
            self._generate_pip_repo_rule(requirement)
            for requirement in self.requirements_list
        )

    def _generate_pip_repo_rule(self, requirement):
        return requirement["name"]


def write_bzl_file(path, contents):
    with open(path, mode='w') as bzl_file:
        bzl_file.write(contents)


if __name__ == '__main__':
    main()
