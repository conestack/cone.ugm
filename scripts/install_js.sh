#!/bin/bash

set -e

if ! which npm &> /dev/null; then
    sudo apt-get install npm
fi

npm --save-dev install \
    qunit \
    karma \
    karma-qunit \
    karma-coverage \
    karma-chrome-launcher \
    karma-viewport \
    karma-module-resolver-preprocessor \
    rollup \
    rollup-plugin-cleanup \
    rollup-plugin-terser \

npm --no-save install \
    ../treibstoff \
    ../cone.app \
    https://github.com/jquery/jquery#main
