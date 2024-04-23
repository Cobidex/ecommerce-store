#!/usr/bin/env bash

pycodestyle . | grep -oE '^[^:]+:' | sed 's/:$//' | xargs autopep8 -i -r