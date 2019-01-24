#!/bin/bash
#
# sendallsyx.sh - Send all MIDI SysEx files in the current directory
# which start with three digits and an underscore to the first hardware
# MIDI output
#

ALSA_RAWMIDI_PORT="${ALSA_RAWMIDI_PORT:-hw:1,0}"

for s in [01][0-9][0-9]_*.syx; do
    echo "Sending $s ..."
    amidi -p $ALSA_RAWMIDI_PORT -s "$s"
    sleep 1
done
