#!/bin/bash

bazel build //src/bin:create_pip_repository.par

WORKSPACE=$(bazel info workspace)
cp $WORKSPACE/bazel-bin/src/bin/create_pip_repository.par $WORKSPACE/tools/create_pip_repository.par
