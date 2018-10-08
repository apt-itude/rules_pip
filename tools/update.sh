#!/bin/bash

bazel build //src/bin:create_pip_repository.par
cp bazel-bin/src/bin/create_pip_repository.par tools/create_pip_repository.par
