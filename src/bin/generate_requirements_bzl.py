#!/usr/bin/env python2
import argparse
import json
import textwrap


def main():
    args = parse_args()
    requirements = load_requirements(args.requirements_file)

    bzl_file_contents = BzlFileGenerator(requirements, args.rules_pip_repo).generate()
    write_file(args.bzl_file_path, bzl_file_contents)

    build_file_contents = BuildFileGenerator(
        requirements,
        args.rules_pip_repo
    ).generate()
    write_file(args.build_file_path, build_file_contents)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("requirements_file")
    parser.add_argument("bzl_file_path")
    parser.add_argument("build_file_path")
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
        for source in requirement["sources"]:
            name = generate_repo_name(requirement["name"], source)
            yield self._generate_pip_repo_rule_for_source(name, source)

    def _generate_pip_repo_rule_for_source(self, name, source):
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
            sha256=source.get("sha256", ""),
            is_wheel=source.get("is-wheel", False),
        )


def indent_block(string, level):
    lines = string.splitlines()
    return "\n".join(indent_line(line, level) for line in lines)


def indent_line(line, level):
    return "{}{}".format((level * 4 * " "), line)


def generate_repo_name(distro_name, source):
    name = "pip__{}".format(distro_name)

    if "python" in source:
        name += "_py{}".format(source["python"])

    if "platform" in source:
        name += "_{}".format(source["platform"])

    return name


class BuildFileGenerator(object):

    def __init__(self, requirements, rules_pip_repo):
        self.requirements = requirements
        self.rules_pip_repo = rules_pip_repo

    @property
    def python_versions_list(self):
        return self.requirements["python-versions"]

    @property
    def platforms_list(self):
        return self.requirements["platforms"]

    @property
    def requirements_list(self):
        return self.requirements["requirements"]

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
        for requirement in self.requirements_list:
            for alias in self._generate_aliases_for_requirement(requirement):
                yield str(alias)

    def _generate_aliases_for_requirement(self, requirement):
        top_alias = SelectAlias(requirement["name"])

        for python_version in self.python_versions_list:
            version_alias = self._generate_python_version_alias(
                python_version,
                requirement,
            )

            yield version_alias

            python_version_key = "@bazel_tools//tools/python:PY{}".format(
                python_version
            )
            top_alias.actual[python_version_key] = version_alias.name

        yield top_alias

    def _generate_python_version_alias(self, python_version, requirement):
        alias = SelectAlias("{}__py{}".format(requirement["name"], python_version))

        for platform in self.platforms_list:
            source = self._find_matching_source(requirement, python_version, platform)

            platform_key = "@{rules_pip_repo}//platforms:{platform}".format(
                rules_pip_repo=self.rules_pip_repo,
                platform=platform,
            )
            repo_name = generate_repo_name(requirement["name"], source)

            alias.actual[platform_key] = "@{}//:lib".format(repo_name)

        return alias

    def _find_matching_source(self, requirement, python_version, platform):
        for source in requirement["sources"]:
            python_version_matches = source.get("python", python_version) == python_version
            platform_matches = source.get("platform", platform) == platform
            if python_version_matches and platform_matches:
                return source

        # TODO raise better exception
        raise RuntimeError("No source matches target Python version and platform")


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
