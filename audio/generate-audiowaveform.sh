#!/bin/bash

WIDTH=${WIDTH:-1920}
HEIGHT=${HEIGHT:-300}

exec audiowaveform \
    -z auto \
    -w $WIDTH \
    -h $HEIGHT \
    --waveform-color ffffffff \
    --background-color 00000000 \
    --no-axis-labels \
    -i "$1" \
    -o "$2"
