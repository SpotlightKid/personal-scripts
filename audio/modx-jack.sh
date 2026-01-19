#!/bin/bash -x
#
# Set up Yamaha MODX Audio Input / Output as JACK clients via zita-a2j/-j2a
# with 10 output and 4 input channels
#
# Optionally also connect MODX output 1/2 ports to system:playback_1/2
#

NAME="MODX"
CONNECT=0
INCHANNELS=10
OUTCHANNELS=4

if [[ "$1" = "-c" ]]; then
    CONNECT=1
    shift
fi

SAMPLERATE="${1:-44100}"

if [[ "$1" = "-e" ]]; then
    echo "Killing jack-matchmaker..." >/dev/stderr
    killall jack-matchmaker
    echo "Killing zita-a2j/j2-a clients..." >/dev/stderr
    killall zita-a2j
    killall zita-j2a
else
    zita-a2j -j "$NAME Out" -d hw:$NAME -r $SAMPLERATE -c $INCHANNELS &
    zita-j2a -j "$NAME In" -d hw:$NAME -r $SAMPLERATE -c $OUTCHANNELS &

    if [[ $CONNECT -eq 1 ]]; then
        jack-matchmaker "$NAME Out:capture_(?P<ch>1|2)$" "system:playback_{ch}$" &
    fi
fi
