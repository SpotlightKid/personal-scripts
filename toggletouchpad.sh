#!/bin/bash
#
# toggletouchpad.sh - Enable/Disable touchpad device managed via libinput
#
# Requires 'xinput' program from package 'xorg-xinput', 'bash', 'awk' and 'grep'.
#

export LC_ALL=C
device="$(xinput list --name-only | grep -i touchpad)"
is_enabled=$(xinput list-props "$device" | awk -F : '/Device Enabled/ {print $2}')

if [[ $is_enabled -eq 1 ]]; then
    xinput disable "$device"
else
    xinput enable "$device"
fi
