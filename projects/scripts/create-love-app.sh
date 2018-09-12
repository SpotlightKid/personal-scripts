#!/bin/bash

APPDIR="$(mktemp -d ${TMPDIR:-/tmp}/love-XXXXXXX)"
mkdir -p "$APPDIR" && \
xclip -o > "$APPDIR/main.lua" && \
love "$APPDIR"

#xdotool key ctrl+C && \
