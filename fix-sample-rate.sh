#!/bin/bash
#
# Fix WAV files with incorrect sampel rate set in header
#

SAMPLERATE="${1:-48000}"

for wav in *.wav; do
  bn="${wav%.*}"
  sndfile-convert -override-sample-rate=$SAMPLERATE "$wav" "${bn}-fixed.wav" && \
    mv "${wav}" "${wav}.bak" && \
    mv "${bn}-fixed.wav" "${wav}"
done
