# Bazel rules for pip requirements

## Overview
This repository provides rules for the [Bazel build tool](https://www.bazel.build/) that allow your Python code to depend on pip packages using a standard [requirements file](https://pip.pypa.io/en/stable/user_guide/#requirements-files). It is built in pure Python and uses the `pip` and `wheel` libraries to ensure that the resulting dependency set is the same as it would be by using those tools. 

This repository is designed to be compatible with both Python 2 and 3 in a single repo, as well as support multiple platforms. 

## Setup
Add the following to your `WORKSPACE` file:
```
git_repository(
    name = "com_apt_itude_rules_pypi",
    commit = "6f02f84ee978f8bd31c2d0715e70b2b7a72bc603",
    remote = "https://github.com/apt-itude/rules_pip.git",
)

load("@com_apt_itude_rules_pypi//rules:dependencies.bzl", "pip_rules_dependencies")

pip_rules_dependencies()
```
