# Bazel rules for pip requirements

[![Build Status](https://travis-ci.org/apt-itude/rules_pip.svg?branch=master)](https://travis-ci.org/apt-itude/rules_pip)

## Overview
This repository provides rules for the [Bazel build tool](https://www.bazel.build/) that allow your Python code to depend on pip packages using a standard [requirements file](https://pip.pypa.io/en/stable/user_guide/#requirements-files). It utilizes Starlark wherever possible to provide hermetic rules, but uses Python and the `pip` library for dependency resolution and management in order to ensure that the development experience is consistent with that of `pip`.

This repository is designed to be support the use of both Python 2 and Python 3 in a single repo, execution on multiple platforms, and remote execution.

## Getting Started

### Importing the rules

Add the following to your `WORKSPACE` file:

```python
git_repository(
    name = "com_apt_itude_rules_pip",
    commit = "82d3393646982b233c7ed919a5b66ffb471dc649",
    remote = "https://github.com/apt-itude/rules_pip.git",
)

load("@com_apt_itude_rules_pip//rules:dependencies.bzl", "pip_rules_dependencies")

pip_rules_dependencies()
```

### Defining your requirements

All direct external pip dependencies should be defined in a `requirements.txt` file. This file should be located in a Bazel package (typically something like `thirdparty/pip`) and committed to source control.

The same requirements file may be used to define all pip dependencies accross your workspace and shared among Python versions and platforms. To define requirements that only pertain to a particular Python version or platform, you should use [Environment Markers](https://www.python.org/dev/peps/pep-0508/#environment-markers).

_NOTE_: At this time, only the `sys_platform` and `python_version` environment markers are supported. Using additional markers will not cause an error, but the `pip_lock` rule only generates one environment per major Python version per platform, so additional granularity in the `requirements.txt` file will be ignored.

### Locking your requirements

Instantiate the `pip_lock` rule in a `BUILD` file, typically within the same package as the `requirements.txt` file. For example:

`thirdparty/pip/BUILD`
```python
load("@com_apt_itude_rules_pip//rules:lock.bzl", "pip_lock")

pip_lock(
    name = "lock",
    requirements = ["requirements.txt"],
)
```

Next, execute the `pip_lock` binary:

```bash
bazel run //thirdparty/pip:lock
```

This will do two things:
1. Generate a `requirements-lock.json` file alongside the `requirements.txt` file, which locks all direct and transitive dependencies to a specific version
1. Build wheels for any requirement that is not already distributed as a wheel on PyPI and store them in a `wheels` directory alongside the `requirements.txt` file

The `requirements-lock.json` file should be committed to source control.

The wheel files may either be source-controlled or published to a custom Python package index. See [Managing built wheel files](#managing-built-wheel-files) for more information.

### Turning the requirements into Bazel dependencies

Add the following to your `WORKSPACE` file:

```python
load("@com_apt_itude_rules_pip//rules:repository.bzl", "pip_repository")

pip_repository(
    name = "pip",
    requirements = "//thirdparty/pip:requirements-lock.json",
)

load("@pip//:requirements.bzl", "pip_install")

pip_install()
```

This creates an external workspace named `@pip` from which you can access all pip requirements. A `py_library` target is exposed for each requirement via the label `@pip//<distro_name>`, where `<distro_name>` is the canonical name of the Python distribution found in your `requirements.txt` file. The canonical name is all lowercase, with hyphens replaced by underscores. For example, `PyYAML` would become `@pip//pyyaml` and `pytest-mock` would become `@pip//pytest_mock`.

### Using pip dependencies

Simply add `@pip//<distro_name>` labels to the `deps` list of any `py_library`, `py_binary`, or `py_test` rule. For example:

`some/package/BUILD`
```python
py_library(
    name = "dopecode"
    srcs = ["dopecode.py"],
    deps = [
        "@pip//pytest_mock",
        "@pip//pyyaml",
    ]
)
```

When you build these targets, only the pip distributions that are directly or indirectly required by that target will be fetched.

## Updating requirements

To update all requirements simultaneously:
```bash
bazel run <label/of:pip_lock> -- -U
```

To update one or more requirements individually:
```bash
bazel run <label/of:pip_lock> -- -P <package-one> -P <package-two>
```

## Managing built wheel files

There are two options for managing the wheels that are built when executing the `pip_lock` rule:

### Committing them to source control

This is the simplest option. If you simply leave them in the directory in which they were built and commit them to source control, there is nothing more to do. However, this has the downside of bloating your repository with binary files, which can make operations like cloning and pulling take longer if there are large wheels or a large number of wheels. If you choose this option and you are using `git`, you may want to consider using [Git LFS](https://git-lfs.github.com/) for this.

### Publishing them to a custom Python package index

If you have the resources, you can also [create a custom Python package index](https://packaging.python.org/guides/hosting-your-own-index/) in which to host the wheels. Once you publish the wheels to the index, add the index URL as an argument to the `pip_lock` rule. For example:

```python
pip_lock(
    name = "lock",
    requirements = ["requirements.txt"],
    args = ["--index-url", "https://custom.pypi.com"],
)
```

Then, re-run the `pip_lock` binary:

```bash
bazel run //thirdparty/pip:lock
```

This will update the `requirements-lock.json` file to point to the remote wheel files and delete the unused local wheel files. Make sure you commit the updated lock file to source control.

Note that the `--index-url` argument is additive, so you may use it any number of times to expose multiple package indices.

### Why do I need to do this?

__TL;DR__ Pre-building wheels is an unfortunate but necessary compromise to make Bazel and pip play nicely.

PyPI provides two types of distributions: wheels and source distributions.

Wheels are pre-built archives that can simply be extracted onto the `PYTHONPATH` and used out of the box. This makes them ideal for use within Bazel because a repository rule can simply download the wheel file, extract it, and create a static `BUILD` file that globs for all the extracted files as sources to a `py_library` rule.

Source distributions, on the other hand, are archives of the source code, which means that their installation requires a build step. Pure Python code does not require building, but packages that contain C extensions, for example, must be compiled. For various reasons, often due to platform differences, many Python packages are only available as source distributions on PyPI (check out [this website](https://pythonwheels.com/) for availability of many popular distributions as wheels).

Creating `py_library` targets for source distributions can be accomplished in any of the following ways:

#### Let pip do its thing and build them when fetching external dependencies
This is the easiest solution because it's the way pip normally works, which is why the original `rules_pip` rules did it this way. However, there are three major issues with this approach:
1. Bazel provides very little visibility into the fetch process for users, so if a source distribution fails to build for any reason, users are left fumbling around in the dark and figuring out ways of manually executing the `rules_pip` tools in order to reproduce the issue.
1. There is no way to utilize the Bazel Python toolchain at this stage, so in order for the wheels to be built with the correct Python version(s), the system Python interpreter(s) must exactly match your toolchain. This defeats the purpose of using Bazel toolchains in the first place.
1. Fetching external dependencies happens on the host platform (i.e. the platform on which Bazel is running), so this approach will only build the wheels for the host platform. If any wheels are platform-specific, this makes remote execution on a different platform impossible.

#### Build the wheels using Bazel rules
This would be the ideal solution because it's the most Bazel-y solution: start with source code and hermetically build on a target platform. However, this is extremely difficult to accomplish because of how `setuptools` works.

Since all Bazel rules are hermetic, the exact set of input and output files for each rule must be known during the loading phase, before anything has been built. This means that in order for a `py_library`, `py_binary` or `py_test` rule to depend on a source distribution, a complete and explicit list of of the files that would be produced by building that source distribution must be known ahead of time. Unfortunately, a distribution's `setup.py` file may execute arbitrary Python code at build time, which means that it's impossible (or at least way more difficult than I deem worthwhile) to know the outputs it will produce without actually building it.

#### Require all dependencies to be wheels up front
This is the happy(ish) medium between the previous two approaches and is what `rules_pip` now expects. If all external pip dependencies are already wheels, then there is no build step to perform at either fetch time or execution time.

Obviously, it's not practical to expect that everything is distributed as a wheel or that developers will limit themselves to exclusively using packages that are distributed as wheels, so the `pip_lock` rule fills that gap. It provides the mechanism for building wheels in such a way that will both utilize your Python toolchain and work in a remote execution environment.

Although executing the binary produced by `pip_lock` rule is not hermetic, it is consistent with the way pip itself builds wheels because it actually uses the `pip` library.

## Migrating from the original rule set

If you are utilizing the original `compile_pip_requirements` and `pip_repository` rules, you can easily transition to the new ruleset.

### Importing the new rules

In order to keep the original rules functional while migrating to the new ones, import `rules_pip` under a different external repository name and shadow any conflicting rule names. For example:

`WORKSPACE`
```python
git_repository(
    name = "com_apt_itude_rules_pip_new",
    commit = "82d3393646982b233c7ed919a5b66ffb471dc649",
    remote = "https://github.com/apt-itude/rules_pip.git",
)

load(
    "@com_apt_itude_rules_pip_new//rules:dependencies.bzl",
    new_pip_rules_dependencies="pip_rules_dependencies",
)

new_pip_rules_dependencies()
```

### Consolidating your requirements files

If you had separate `requirements.in` files for Python 2 and Python 3, you may continue to keep them separate and simply pass both to the `pip_lock` rule, like so:
```python
load("@com_apt_itude_rules_pip//rules:lock.bzl", "pip_lock")

pip_lock(
    name = "lock",
    requirements = ["requirements-2.in", "requirements-3.in"],
)
```

However, you must add the `python_version < "3.0"` or `python_version >= "3.0"` environment marker to every line of `requirements-2.in` and `requirements-3.in`, respectively, in order to tell the `pip_lock` rule which Python version each requirement belongs to.

If the two lists have a lot of overlap, it may be simpler to combine all requirements into a single `requirements.txt` file and selectively use the `python_version` environment marker only for those requirements that should be limited to one version.

### Locking your requirements and turning them into to Bazel dependencies

Follow the steps outlined in [Locking your requirements](#locking-your-requirements) and [Turning the requirements into Bazel dependencies](#turning-the-requirements-into-Bazel-dependencies).

### Switching to the new dependencies

If you previously instantiated two `pip_repository` rules named `pip2` and `pip3`, simply find and replace all instances of `@pip2` and `@pip3` in your workspace with `@pip`.

### Cleaning up

Delete any usages of the `compile_pip_requirements` rule as well as any `requirements.txt` files that they produced. In addition, remove the `load` statement of the original `com_apt_itude_rules_pip` repo and the associated `pip_rules_dependency` instantiation from your `WORKSPACE` file.

Finally, you may rename `com_apt_itude_rules_pip_new` and `new_pip_rules_dependencies` in your `WORKSPACE` file to the canonical `com_apt_itude_rules_pip` and `pip_rules_dependencies`.
