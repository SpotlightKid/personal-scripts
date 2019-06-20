#!/bin/bash

SOUNDFONT="/usr/lib/lv2/gmsynth.lv2/GeneralUser_LV2.sf2"
SAMPLERATE=44100
SAMPLEFORMAT="s16"

if [[ -e "$1" ]]; then
    MIDI="$1"
elif [[ -e "$1.mid" ]]; then
    MIDI="$1.mid"
fi

if [[ -e "${MIDI%.*}.fluid" ]]; then
    OPTS="${MIDI%.*}.fluid"
elif [[ -e "midi2flac.fluid" ]]; then
    OPTS="midi2flac.fluid"
fi

TMP="${TMP:-/tmp}"
AUDIO_TMP="$(mktemp "$TMP/midi2flac-XXXXXX.wav")"
BASENAME="${MIDI##*/}"
FLAC="${BASENAME%.*}.flac"

fluidsynth -nil \
    -r ${SAMPLERATE} \
    -O ${SAMPLEFORMAT} \
    -F "$AUDIO_TMP" \
    ${OPTS:+-f $OPTS} \
    "$SOUNDFONT" \
    "$MIDI" && \
sox "$AUDIO_TMP" --norm "$FLAC" && \
rm -f "$AUDIO_TMP" && \
echo "FLAC output file written to '$FLAC'."
