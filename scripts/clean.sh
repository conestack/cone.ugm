#!/bin/bash
#
# Clean development environment.

set -e

to_remove=(
    .coverage .installed.cfg .mr.developer.cfg bin develop-eggs dist htmlcov
    include karma lib64 lib local node_modules package-lock.json parts
    pyvenv.cfg share
)

for item in "${to_remove[@]}"; do
    if [ -e "$item" ]; then
        rm -r "$item"
    fi
done
