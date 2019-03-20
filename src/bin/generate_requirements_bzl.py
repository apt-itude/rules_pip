#!/usr/bin/env python2
import argparse
import json
import textwrap


def main():
    args = parse_args()
    requirements = load_requirements(args.requirements_file)
    bzl_file_contents = BzlFileGenerator(requirements, args.rules_pip_repo).generate()
    write_bzl_file(args.output_path, bzl_file_contents)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("requirements_file")
    parser.add_argument("output_path")
    parser.add_argument("rules_pip_repo")
    return parser.parse_args()


def load_requirements(path):
    with open(path) as requirements_file:
        return json.load(requirements_file)


class BzlFileGenerator(object):

    def __init__(self, requirements, rules_pip_repo):
        self.requirements = requirements
        self.rules_pip_repo = rules_pip_repo

    @property
    def requirements_list(self):
        return self.requirements["requirements"]

    def generate(self):
        return textwrap.dedent("""
            load("@{rules_pip_repo}//rules:new_repository.bzl", "pip_repository")

            {pip_install_macro}
        """).strip().format(
            rules_pip_repo=self.rules_pip_repo,
            pip_install_macro=self._generate_pip_install_macro(),
        )

    def _generate_pip_install_macro(self):
        pip_repo_rules = "\n".join(
            indent_block(rule, 1)
            for rule in self._generate_all_pip_repo_rules()
        )

        return textwrap.dedent("""
            def pip_install():
            {rules}
        """).strip().format(
            rules=pip_repo_rules,
        )

    def _generate_all_pip_repo_rules(self):
        for requirement in self.requirements_list:
            for rule in self._generate_pip_repo_rules_for_requirement(requirement):
                yield rule

    def _generate_pip_repo_rules_for_requirement(self, requirement):
        name = "pip__{}".format(requirement["name"])
        for source in requirement["sources"]:
            yield self._generate_pip_repo_rule_for_requirement(name, source)

    def _generate_pip_repo_rule_for_requirement(self, name, source):
        return textwrap.dedent("""
            if not native.existing_rule("{name}"):
                pip_repository(
                    name = "{name}",
                    url = "{url}",
                    sha256 = "{sha256}",
                    is_wheel = {is_wheel},
                )
        """).strip().format(
            name=name,
            url=source["url"],
            sha256=source["sha256"],
            is_wheel=source["is-wheel"],
        )


def indent_block(string, level):
    lines = string.splitlines()
    return "\n".join(indent_line(line, level) for line in lines)


def indent_line(line, level):
    return "{}{}".format((level * 4 * " "), line)


def write_bzl_file(path, contents):
    with open(path, mode="w") as bzl_file:
        bzl_file.write(contents)


if __name__ == "__main__":
    main()
