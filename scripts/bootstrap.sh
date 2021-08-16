#!/bin/bash

set -e

PY=$1
if [ "$PY" == "" ]; then
    PY=python2
fi

virtualenv --clear --no-site-packages -p $PY .
./bin/pip install --upgrade pip setuptools zc.buildout
./bin/buildout -N
