#!/bin/sh
# dynamic entrypoint
# in a posix-compatible way attempt to resolve interpreter path.
# checks:
# - shebang line (requires expr)
# - path to python3
# - path to python
read -r firstline < "$1"
exprpath=$(command -v expr)
if test -n "${exprpath}"; then
    e=$(expr "$firstline" : '#!\(.*python.*\)')
    if test -n "${e}"; then
        exec $e "$@"
    fi
fi
py=$(command -v python3)
if test -n "${py}"; then
    exec $py "$@"
else
    exec $(command -v python) "$@"
fi
