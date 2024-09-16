#!/bin/bash

SASS_BIN="./node_modules/sass/sass.js"
SASS_DIR="./scss"
TARGET_DIR="./src/cone/ugm/browser/static"

$SASS_BIN --no-source-map=none $SASS_DIR/ugm.scss $TARGET_DIR/cone.ugm.css
