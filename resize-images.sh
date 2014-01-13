#!/bin/bash
#
# create resized versions of all JPEG images found in current directory in
# a subdirectory named after size of the longest side (default 1024).

# enable extended filename patterns
shopt -s extglob

SIZE="${1:-1024}"
EXT="${2:-jpg}"

mkdir -p "$SIZE";
for image in *.[jJ][pP]?(e)[gG]; do
    filename="${image##*/}"
    basename="${filename%.*}"
    echo "Converting '"$image"' to '"$SIZE/$basename.$EXT"'..."
    convert "$image" -resize 1024 "$SIZE/$basename.$EXT"
done
