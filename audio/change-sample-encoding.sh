#!/bin/bash
#
# Change sample encoding in audio file(s)
#
# Pass the target encoding name with the -e NAME option (default: pcm16)

if [[ "$1" = "-e" ]]; then
    ENCODING="$2"
    shift 2
else
    ENCODING="pcm16"
fi

for src in "$@"; do
    path="${src%/*}"
    dn="${path##*/}"
    fn="${src##*/}"
    bn="${fn%.*}"
    dst="$ENCODING/${dn}/${fn}"

    echo "Setting sample encoding of ${src} to $ENCODING and saving as ${dst} ..."
    mkdir -p "$ENCODING/${dn}"
    sndfile-convert -$ENCODING "$src" "$dst"
done
