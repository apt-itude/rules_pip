#!/usr/bin/env bash
firstline=$(head -n 1 "$1")

if [[ "$firstline" =~ ^#!(.*python.*)$ ]]; then
    exec ${BASH_REMATCH[1]} "$@"
else
    exec /usr/bin/env python3 "$@"
fi
