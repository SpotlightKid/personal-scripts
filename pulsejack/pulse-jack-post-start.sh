#!/bin/bash
#
# pulse-jack-post-start.sh
#

pactl load-module module-jack-sink channels=2
pactl load-module module-jack-source channels=2
pacmd set-default-sink jack_out
pacmd set-default-source jack_in
