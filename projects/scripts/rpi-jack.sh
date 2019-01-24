#!/bin/bash
#
# Start JACK on my Raspberry Pi with a M-Audio Fast Track Pro audio interface
# and run fluidsynth with a General MIDI soundfont or teh one given on the
# command line
#

AUDIODEV="hw:1"
MIDIDEV="FastTrack Pro"
SAMPLERATE=44100
CHANNELS=2
GAIN="0.5"
JACK="true"
SOUNDFONT="${1:-/usr/share/sounds/sf2/FluidR3_GM.sf2}"

if [ "x$JACK" = "xtrue" ]; then
    jackd -R -P95 -p 32 -d dummy -C 0 -P $CHANNELS -r $SAMPLERATE &
    sleep 1
    alsa_out -d "$AUDIODEV" -c $CHANNELS -r $SAMPLERATE >&/dev/null &
    sleep 1
    fluidsynth -s -i -L $(($CHANNELS / 2)) -r $SAMPLERATE -g "$GAIN" \
        -a jack -m alsa_seq -p fluidsynth1 \
        "$SOUNDFONT" &
else
    fluidsynth -s -i -L $(($CHANNELS / 2)) -r $SAMPLERATE -g "$GAIN" \
       -a alsa -o "audio.alsa.device=$AUDIODEV" -m alsa_seq -p fluidsynth1 \
       "$SOUNDFONT" &
fi

sleep 2
aconnect "$MIDIDEV:0" "fluidsynth1:0"
