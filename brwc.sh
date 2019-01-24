#!/bin/bash
#
# Start the BOSS BR Wave Converter windows program via wine
#

BRWC_HOME="$HOME/lib/BRWC310"

exec wine "$BRWC_HOME/BRWC.exe" "$@"
