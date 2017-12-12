#!/bin/sh
for dir in lib include local bin; do
    if [ -d "$dir" ]; then
        rm -r "$dir"
    fi
done
virtualenv --clear --no-site-packages .
./bin/pip install --upgrade pip setuptools zc.buildout
./bin/buildout -N
