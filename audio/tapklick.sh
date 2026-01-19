#!/bin/bash
#
# Run klick metronome and tap tempo with enter/return key
#

TEMPO="${1:-120}"

cleanup() {
    stty echo
    oscsend localhost 9001 /klick/metro/stop
    echo "Stop."
    exit
}

klick -o 9001 -s 2 -v 0.5 -P $TEMPO &
echo "Tap tempo with enter/return, Ctrl-C to quit."
sleep 0.2
oscsend localhost 9001 /klick/metro/start
trap cleanup 2
stty -echo
while true; do
   read
   oscsend localhost 9001 /klick/simple/tap
done
