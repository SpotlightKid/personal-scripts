#!/bin/bash
#
# pyenv-copy-version - Copy a pyenv Python version installation from one user to another
#

SRCPYENVROOT="$1"
VERSION="$2"

if [[ -z "$SRCPYENVROOT" || -z "$VERSION" ]]; then
    echo "Usage: pyenv-copy-version <source pyenv root dir> <python version>"
    exit 2
fi

SRCDIR="$SRCPYENVROOT/versions/$VERSION"
PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"

if [[ -d "$SRCDIR" ]]; then
    cp -a "$SRCDIR" "$PYENV_ROOT/versions"

    cp -a "$SRCPYENVROOT/shims/"* "$PYENV_ROOT/shims"

    for f in "$PYENV_ROOT/shims"*; do
        sed -e "s|$SRCPYENVROOT|$PYENVROOT|g" -i "$f"
    done
else
    echo "Source directory $SRCDIR not found."
    exit 1
fi
