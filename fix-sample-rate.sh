#!/bin/bash
#
# Fix WAV files with incorrect sample rate set in header
#
# Pass the target sample rate with the -r RATE option (default: 48000)

if [[ "$1" = "-r" ]]; then
    SAMPLERATE="$2"
    shift 2
else
    SAMPLERATE="48000"
fi

for src in "$@"; do
    path="${src%/*}"
    dn="${path##*/}"
    fn="${src##*/}"
    bn="${fn%.*}"
    dst="$SAMPLERATE/${dn}/${fn}"

    echo "Setting sample rate of ${src} to $SAMPLRATE and saving as ${dst} ..."
    mkdir -p "$SAMPLERATE/${dn}"
    sndfile-convert -override-sample-rate=$SAMPLERATE "$src" "$dst"
done
