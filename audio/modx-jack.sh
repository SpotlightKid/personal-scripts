#!/bin/bash
#
# Set up MODX Audio Input / Output as JACK clients with 10 output and 4 input channels
#

zita-a2j -j "MODX Out" -d hw:MODX -r 44100 -c 10 &
zita-j2a -j "MODX In" -d hw:MODX -r 44100 -c 4 &
