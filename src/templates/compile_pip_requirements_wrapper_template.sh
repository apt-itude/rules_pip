#!/bin/bash
if [ -z ${BUILD_WORKSPACE_DIRECTORY+x} ]; then
    echo "This script must be executed with Bazel"
    exit 1
fi

REQUIREMENTS_IN_PATH="@@REQUIREMENTS_IN_PATH@@"
REQUIREMENTS_TXT_PATH="$BUILD_WORKSPACE_DIRECTORY/@@REQUIREMENTS_TXT_PATH@@"
PYTHON_INTERPRETER_PATH="@@PYTHON_INTERPRETER_PATH@@"
PIP_COMPILE_BINARY="@@PIP_COMPILE_BINARY@@"

echo "Compiling $REQUIREMENTS_TXT_PATH"
$PYTHON_INTERPRETER_PATH $PIP_COMPILE_BINARY \
    --output-file $REQUIREMENTS_TXT_PATH \
    --no-header \
    --no-index \
    --generate-hashes \
    --allow-unsafe \
    "$@" \
    $REQUIREMENTS_IN_PATH
set -x
echo "@@HEADER@@" > requirements.tmp
cat $REQUIREMENTS_TXT_PATH >> requirements.tmp
cp requirements.tmp $REQUIREMENTS_TXT_PATH
