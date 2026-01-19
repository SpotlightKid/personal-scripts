#!/bin/bash
#
# Set up yamaha MODX Audio Input / Output as JACK internal clients
# with 10 output and 4 input channels
#
# Optionally also connect Digitakt output 1/2 ports to system:playback_1/2
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
    echo "Unloading zalsa_in/-out internal JACK clients..." >/dev/stderr
    jack_unload "$NAME Out"
    jack_unload "$NAME In"
else
    echo "Loading zalsa_in/-out internal JACK clients..." >/dev/stderr
    jack_load "$NAME Out" zalsa_in -- "-d hw:$NAME -r $SAMPLERATE -c $INCHANNELS"
    jack_load "$NAME In" zalsa_out -- "-d hw:$NAME -r $SAMPLERATE -c $OUTCHANNELS"

    if [[ $CONNECT -eq 1 ]]; then
        jack-matchmaker "$NAME Out:capture_(?P<ch>1|2)$" "system:playback_{ch}$" &
    fi
fi
