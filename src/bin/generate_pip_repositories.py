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

    @property
    def local_wheels_package(self):
        return self.lock_file["local_wheels_package"]

    def generate(self):
        return textwrap.dedent("""
            load("@{rules_pip_repo}//rules:new_repository.bzl", "local_wheel", "remote_wheel")

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
            if "url" in source:
                yield self._generate_remote_wheel_rule(name, source)
            else:
                yield self._generate_local_wheel_rule(name, source)

    def _generate_remote_wheel_rule(self, name, source):
        return textwrap.dedent("""
            if not native.existing_rule("{name}"):
                remote_wheel(
                    name = "{name}",
                    url = "{url}",
                    sha256 = "{sha256}",
                )
        """).strip().format(
            name=name,
            url=source["url"],
            sha256=source.get("sha256", ""),
        )

    def _generate_local_wheel_rule(self, name, source):
        return textwrap.dedent("""
            if not native.existing_rule("{name}"):
                local_wheel(
                    name = "{name}",
                    wheel = "{package}:{file}",
                )
        """).strip().format(
            name=name,
            package=self.local_wheels_package,
            file=source["file"],
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

    def generate(self):
        return textwrap.dedent("""
            package(default_visibility = ["//visibility:public"])

            {aliases}
        """).strip().format(
            aliases=self._generate_aliases()
        )

    def _generate_aliases(self):
        return "\n".join(self._generate_all_rules())

    def _generate_all_rules(self):
        requirement_tree = self._build_requirement_tree()

        for name, python_subtree in requirement_tree.items():
            for rule in self._generate_rules_for_requirement(name, python_subtree):
                yield rule

    def _build_requirement_tree(self):
        tree = {}

        for environment_name, environment_details in self.environments.items():
            python_version = environment_details["python_version"]
            sys_platform = environment_details["sys_platform"]
            requirements = environment_details["requirements"]

            for requirement_name, requirement_details in requirements.items():
                tree.setdefault(
                    requirement_name, {}
                ).setdefault(
                    python_version, {}
                )[sys_platform] = requirement_details

        return tree

    def _generate_rules_for_requirement(self, requirement_name, python_subtree):
        top_alias = SelectAlias(requirement_name)

        for python_version, platform_subtree in python_subtree.items():
            for sys_platform, requirement_details in platform_subtree.items():
                yield self._generate_py_library(
                    requirement_name,
                    requirement_details,
                    python_version,
                    sys_platform,
                )

            version_alias = self._generate_python_version_alias(
                requirement_name,
                python_version,
                platform_subtree,
            )

            yield str(version_alias)

            python_version_label = _make_python_version_label(python_version)
            top_alias.actual[python_version_label] = version_alias.name

        yield str(top_alias)

    def _generate_py_library(
        self,
        requirement_name,
        requirement_details,
        python_version,
        sys_platform,
    ):
        name = _make_environment_specific_alias(
            requirement_name,
            python_version,
            sys_platform,
        )
        deps = list(self._generate_dependency_labels(requirement_details))

        return textwrap.dedent("""
            py_library(
                name = "{name}",
                deps = {deps},
            )
        """).strip().format(
            name=name,
            deps=deps,
        )

    def _generate_dependency_labels(self, requirement_details):
        yield _make_source_label(requirement_details["source"])
        for dep in requirement_details["dependencies"]:
            yield str(dep)

    def _generate_python_version_alias(
        self,
        requirement_name,
        python_version,
        platform_subtree,
    ):
        alias = SelectAlias(
            _make_python_specific_alias(requirement_name, python_version)
        )

        for sys_platform in platform_subtree:
            bazel_platform = _convert_sys_platform_to_bazel(sys_platform)

            platform_label = _make_platform_label(self.rules_pip_repo, bazel_platform)

            alias.actual[platform_label] = _make_environment_specific_alias(
                requirement_name,
                python_version,
                sys_platform,
            )

        return alias


def _make_python_specific_alias(requirement_name, python_version):
    return "{}__py{}".format(requirement_name, python_version)


def _make_environment_specific_alias(requirement_name, python_version, sys_platform):
    return "{}__py{}_{}".format(requirement_name, python_version, sys_platform)


def _make_python_version_label(version):
    return "@bazel_tools//tools/python:PY{version}".format(version=version)


def _make_platform_label(rules_pip_repo, platform):
    return "@{rules_pip_repo}//platforms:{platform}".format(
        rules_pip_repo=rules_pip_repo,
        platform=platform,
    )


def _make_source_label(source_name):
    return "@{}//:lib".format(source_name)


def _convert_sys_platform_to_bazel(sys_platform):
    if sys_platform == "darwin":
        return "osx"

    if "linux" in sys_platform:
        return "linux"

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
