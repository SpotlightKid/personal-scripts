#!/bin/bash
#
# getwheels.sh - Download or build wheels for given package & all dependencies
#
# The package name and optionally a version requirement must be given as the
# first command line argument (be sure to quote it when it contains shell
# special chars, i.e. '>' and '<').
#
# The directory to store the wheel files in should be given as the second
# command line argument. The default is the current working directory.
#
# Idea from: http://lucumr.pocoo.org/2014/1/27/python-on-wheels/
#
# $Id$

if [ $# -ge 1 ]; then
    PACKAGE="$1"
    WHEEL_DIR="${2:-$(pwd)}"
else
    echo "Usage: $0 PACKAGESPEC [DIR]"
    exit 1
fi

DOWNLOAD_CACHE_DIR="$(mktemp -d --tmpdir pip_download_cache.XXXXXX)"

pip wheel --use-wheel -w "$WHEEL_DIR" -f "$WHEEL_DIR" \
  --download-cache "$DOWNLOAD_CACHE_DIR" "$PACKAGE"

for x in "$DOWNLOAD_CACHE_DIR/"*.whl; do
    mv "$x" "$WHEEL_DIR/${x##*%2F}"
done

test -d "$DOWNLOAD_CACHE_DIR" && rm -rf "$DOWNLOAD_CACHE_DIR"