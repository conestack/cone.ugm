#!/bin/bash

python setup.py extract_messages

cat src/cone/ugm/locale/manual.pot >> src/cone/ugm/locale/cone.ugm.pot

python setup.py update_catalog
