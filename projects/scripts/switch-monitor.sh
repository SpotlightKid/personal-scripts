#!/bin/bash
#
# Switch enabled screen between external monitor and internal laptop screen
#

IN="LVDS1"
EXT="HDMI1"

if (xrandr | grep "$EXT disconnected"); then
    xrandr --output $EXT --off --output $IN --auto
else
    xrandr --output $IN --off --output $EXT --auto
fi
