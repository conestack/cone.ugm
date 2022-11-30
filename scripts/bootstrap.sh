#!/bin/bash

set -e

PY=$1
if [ "$PY" == "" ]; then
    PY=python2
fi

virtualenv --clear -p $PY venv
./venv/bin/pip install -U pip setuptools wheel zc.buildout
./venv/bin/buildout -N
