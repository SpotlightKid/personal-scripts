#!/bin/bash

if [[ "$1" = "-r" ]]; then
    REMOVE_ORIG=1
    shift
fi

for f in "$@"; do
    flac --best --keep-foreign-metadata --silent "$f"

    if [[ "$REMOVE_ORIG" -eq 1 && $? -eq 0 && "$f" != "${f%.*}.flac" ]]; then
        rm -f "$f"
    fi
done
