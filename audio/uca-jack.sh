#!/bin/bash
#
# Set up MODX Audio Input / Output as JACK clients with 10 output and 4 input channels
#

SAMPLE_RATE="${1:-48000}"

if [[ "$1" = "-e" ]]; then
    echo "Killing zita-a2j/j2-a clients..." >/dev/stderr
    killall zita-a2j
    killall zita-j2a
else
    zita-a2j -j "UCA Out" -d hw:CODEC -r $SAMPLE_RATE -c 2 &
    zita-j2a -j "UCA In" -d hw:CODEC -r $SAMPLE_RATE -c 2 &
fi
