#!/bin/bash
for dir in lib include local bin share parts; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
    fi
done

PY=$1
if [ "$PY" == "" ]; then
    PY=python2
fi

virtualenv -p $PY .
./bin/pip install --upgrade pip setuptools zc.buildout
./bin/buildout -N
