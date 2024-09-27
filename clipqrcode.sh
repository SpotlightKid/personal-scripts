#!/bin/bash
#
# Read current selection content and display it fullscreen as a QR code.
#
# By default uses the clipboard selection, you can pass "primary" or
# "secondary" as the first argument to use the XA_PRIMARY or XA_SECONDARY
# selection.
#
# Needs xclip, qrencode and an image viewer, that can read images from stdin,
# for example imv.
#
# Public domain, by Christopher Arndt 2024

SELECTION="${1:-clipboard}"

xclip -o -selection $SELECTION >&/dev/null

if [[ $? -eq 0 ]]; then
  xclip -o -selection $SELECTION -rmlastnl | \
    qrencode -s 10 -t SVG -o - | \
    imv -f -c 'bind <Escape> quit' -
else
  echo "No current $SELECTION selection." >/dev/stderr
fi
