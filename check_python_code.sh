#!/bin/bash

export PYTHONPATH="$PYTHONPATH:$HOME/.pylint.d"
 
echo "======  pep8  ======"
pep8 $1
echo "======  pyflakes  ======"
pyflakes $1
echo "======  pylint  ======"
pylint --output-format=parseable $1

