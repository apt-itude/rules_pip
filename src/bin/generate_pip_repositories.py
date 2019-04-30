#!/usr/bin/env python2
import argparse
import json
import textwrap


def main():
    args = parse_args()
    lock_file = load_requirements(args.requirements_lock_file)

    bzl_file_contents = BzlFileGenerator(lock_file, args.rules_pip_repo).generate()
    write_file(args.bzl_file_path, bzl_file_contents)

    build_file_contents = BuildFileGenerator(
        lock_file,
        args.rules_pip_repo
    ).generate()
    write_file(args.build_file_path, build_file_contents)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("requirements_lock_file")
    parser.add_argument("bzl_file_path")
    parser.add_argument("build_file_path")
    parser.add_argument("rules_pip_repo")
    return parser.parse_args()


def load_requirements(path):
    with open(path) as requirements_lock_file:
        return json.load(requirements_lock_file)


class BzlFileGenerator(object):

    def __init__(self, lock_file, rules_pip_repo):
        self.lock_file = lock_file
        self.rules_pip_repo = rules_pip_repo

    @property
    def sources(self):
        return self.lock_file["sources"]

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
        for name, source in self.sources.items():
            yield self._generate_pip_repo_rule_for_source(name, source)

    def _generate_pip_repo_rule_for_source(self, name, source):
        return textwrap.dedent("""
            if not native.existing_rule("{name}"):
                pip_repository(
                    name = "{name}",
                    url = "{url}",
                    sha256 = "{sha256}",
                )
        """).strip().format(
            name=name,
            url=source["url"],
            sha256=source.get("sha256", ""),
        )


def indent_block(string, level):
    lines = string.splitlines()
    return "\n".join(indent_line(line, level) for line in lines)


def indent_line(line, level):
    return "{}{}".format((level * 4 * " "), line)


class BuildFileGenerator(object):

    def __init__(self, lock_file, rules_pip_repo):
        self.lock_file = lock_file
        self.rules_pip_repo = rules_pip_repo

    @property
    def environments(self):
        return self.lock_file["environments"]

    @property
    def requirements(self):
        return self.lock_file["requirements"]

    def generate(self):
        return textwrap.dedent("""
            package(default_visibility = ["//visibility:public"])

            {aliases}
        """).strip().format(
            aliases=self._generate_aliases()
        )

    def _generate_aliases(self):
        return "\n".join(self._generate_all_aliases())

    def _generate_all_aliases(self):
        for name, requirement in self.requirements.items():
            source_tree = self._build_source_tree(requirement["source"])
            for alias in self._generate_aliases_for_requirement(name, source_tree):
                yield str(alias)

    def _build_source_tree(self, source_map):
        tree = {}

        for environment_name, environment in self.environments.items():
            python_version = environment["python_version"]
            sys_platform = environment["sys_platform"]
            source = source_map[environment_name]
            tree.setdefault(python_version, {})[sys_platform] = source

        return tree

    def _generate_aliases_for_requirement(self, requirement_name, source_tree):
        top_alias = SelectAlias(requirement_name)

        for python_version, sys_platforms in source_tree.items():
            version_alias = self._generate_python_version_alias(
                requirement_name,
                python_version,
                sys_platforms,
            )

            yield version_alias

            python_version_key = "@bazel_tools//tools/python:PY{}".format(
                python_version
            )
            top_alias.actual[python_version_key] = version_alias.name

        yield top_alias

    def _generate_python_version_alias(
        self,
        requirement_name,
        python_version,
        sys_platforms,
    ):
        alias = SelectAlias("{}__py{}".format(requirement_name, python_version))

        for sys_platform, source in sys_platforms.items():
            bazel_platform = _convert_sys_platform_to_bazel(sys_platform)

            platform_key = "@{rules_pip_repo}//platforms:{platform}".format(
                rules_pip_repo=self.rules_pip_repo,
                platform=bazel_platform,
            )

            alias.actual[platform_key] = "@{}//:lib".format(source)

        return alias


def _convert_sys_platform_to_bazel(sys_platform):
    if sys_platform == "darwin":
        return "osx"

    return sys_platform


class SelectAlias(object):

    def __init__(self, name):
        self.name = name
        self.actual = {}

    def __str__(self):
        return textwrap.dedent("""
            alias(
                name = "{name}",
                actual = select({actual}),
            )
        """).strip().format(
            name=self.name,
            actual=self.actual,
        )


def write_file(path, contents):
    with open(path, mode="w") as bzl_file:
        bzl_file.write(contents)


if __name__ == "__main__":
    main()
