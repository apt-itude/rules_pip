#!/bin/bash

set -e

LOCK_PIP_REQUIREMENTS_PY2="@@LOCK_PIP_REQUIREMENTS_PY2@@"
LOCK_PIP_REQUIREMENTS_PY3="@@LOCK_PIP_REQUIREMENTS_PY3@@"
WORKSPACE_NAME="@@WORKSPACE_NAME@@"
REQUIREMENTS_TXT_PATHS="@@REQUIREMENTS_TXT_PATHS@@"
REQUIREMENTS_LOCK_PATH="@@REQUIREMENTS_LOCK_PATH@@"
USE_PY2=@@USE_PY2@@
USE_PY3=@@USE_PY3@@
WHEEL_DIRECTORY="@@WHEEL_DIRECTORY@@"
INDEX_URL=@@INDEX_URL@@

REQUESTING_HELP=0
for arg in $@; do
    if [ "$arg" = "-h" ] || [ "$arg" = "--help" ]; then
        REQUESTING_HELP=1
    fi
done

if [ "$USE_PY2" = true ]; then
    $LOCK_PIP_REQUIREMENTS_PY2 \
        --lock-file $REQUIREMENTS_LOCK_PATH \
        --wheel-dir $WHEEL_DIRECTORY \
        --index-url $INDEX_URL \
        --workspace-name $WORKSPACE_NAME \
        "$@" \
        $REQUIREMENTS_TXT_PATHS
fi

if [ "$REQUESTING_HELP" -ne 0 ]; then
    exit
fi

if [ "$USE_PY3" = true ]; then
    $LOCK_PIP_REQUIREMENTS_PY3 \
        --lock-file $REQUIREMENTS_LOCK_PATH \
        --wheel-dir $WHEEL_DIRECTORY \
        --index-url $INDEX_URL \
        --workspace-name $WORKSPACE_NAME \
        "$@" \
        $REQUIREMENTS_TXT_PATHS
fi
