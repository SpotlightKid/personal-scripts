#!/bin/bash
#
# Start Zoom and open meeting with ID set in config section below or instruct running Zoom to open the meeting.
#
# If a meeting window is already open, activate the window.
#
# Requirements (Arch):
#
# * zoom
# * xdg-utils
# * xdotool

# Start config
MEETING_ID="XXXXXXXX"
ZOOM_SERVER="bundesdruckerei.zoom.us"
MEETING_PASSWORD="XXXXXXXX"
# End config


ZOOM_WINDOW_ID="$(xdotool search --name 'Zoom Meeting$')"

if [[ -z "$ZOOM_WINDOW_ID" ]]; then
    exec xdg-open "zoommtg://${ZOOM_SERVER}/join?action=join&confno=${MEETING_ID}&pwd=${MEETING_PASSWORD}"
else
    exec xdotool windowactivate "$ZOOM_WINDOW_ID"
fi
