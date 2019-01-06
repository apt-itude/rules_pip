#!/bin/sh
read -r firstline < "$1"
e=$(expr "$firstline" : '#!\(.*python.*\)')
if test -n "${e}"; then
    exec $e "$@"
else
    exec /usr/bin/env python3 "$@"
fi
