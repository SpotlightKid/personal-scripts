#!/bin/bash

LOG="${TMPDIR:-$HOME/tmp}"/xwininfo.$$.log
xwininfo -all "$@" > "$LOG"
cat "$LOG" | yad --text-info --width 800 --height 600 --fontname="Sans 12"
