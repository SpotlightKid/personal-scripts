#!/bin/bash -x

bn="${1%.*}"
ffmpeg -i "$1" -i "$bn"-audio.webm -map 0:v -map 1:a -c copy -y "$1"-combined.webm
