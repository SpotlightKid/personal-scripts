#!/bin/bash
#
# sendallsyx.sh
#

ALSA_RAWMIDI_PORT="${ALSA_RAWMIDI_PORT:-hw:1,0}"

for s in [01][0-9][0-9]_*.syx; do
    echo "Sending $s ..." 
    amidi -p $ALSA_RAWMIDI_PORT -s "$s"
    sleep 1
done
