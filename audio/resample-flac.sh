#!/bin/bash
#
# resample-flac.sh

SAMPLERATE=${2:-48000}

# strip path
fn="${1##*/}"
# strip file name extension
bn="${fn%.*}"
# convert to WAV, resample and convert back to FLAC again
flac -d -o "${bn}.wav" "$1" && \
sndfile-resample -to ${SAMPLERATE} -c 0 "${bn}.wav" "${bn}-${SAMPLERATE}.wav" && \
flac --best -o "${bn}-${SAMPLERATE}.flac" "${bn}-${SAMPLERATE}.wav" && \
rm -f "${bn}.wav" "${bn}-${SAMPLERATE}.wav"
