#!/bin/bash
#
# Change sample rate of WAV files using zresample (from zita-resampler)
#
# Pass the target sample rate with the -r RATE option (default: 48000)

if [[ "$1" = "-r" ]]; then
    SAMPLERATE="$2"
    shift 2
else
    SAMPLERATE="48000"
fi

for src in "$@"; do
    fn="${src##*/}"
    dir="${src%/*}"
    bn="${fn%.*}"
    dst="${SAMPLERATE}/${dir}/${bn}.wav"

    echo "Resampling ${src} at $SAMPLERATE Hz to ${dst} ..."
    mkdir -p "$SAMPLERATE/${dn}"
    sndfile-resample -to $SAMPLERATE -c 0 "${src}" "${dst}"
done
