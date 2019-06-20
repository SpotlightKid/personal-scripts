#!/bin/bash

if [[ -e "$1" ]]; then
    ABC="$1"
elif [[ -e "$1.abc" ]]; then
    ABC="$1.abc"
fi

INDEX="${2:-1}"

TMP="${TMP:-/tmp}"
BASENAME="${ABC##*/}"
MIDI="${BASENAME%.*}.midi"
abc2midi "$ABC" $INDEX -o "$MIDI"
