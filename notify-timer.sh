#!/bin/bash
#
# notif-timer - Trigger a desktop notification and, optionally, an event sound
#

[[ -n "$1" ]] || exit 1

SUMMARY="$1"
BODY="$2"
ICON="${3:+--icon=$3}"
SOUND="$4"
SOUNDTHEME="rofi-timer"

#notify-send $ICON ${SOUND:+--hint=STRING:sound-name:$4} "$SUMMARY" "$BODY"

# The notifcation server enables caching of event sounds when using the
# PulseAudio backend, which often causes the sound failing to be played by
# PulseAudio (or just as a faint click). So we trigger the sound playback via
# canberra-gtk-play (from libcanberra) directly instead and disable caching
# explicitly.
notify-send $ICON "$SUMMARY" "$BODY"

if [[ -n "$SOUND" ]] && which canberra-gtk-play >&/dev/null; then
    # canberra-gtk-play does not properly look up sounds from thenes, which
    # inherit from other (user) themes, so we resolve the event sound audio
    # file path ourselves using soundtheme-lookup (included with rofi-timer).
    if [[ ! -e "$SOUND" ]] && which soundtheme-lookup >&/dev/null; then
        SOUND="$(soundtheme-lookup "$SOUND" $SOUNDTHEME)"
    fi

    if [[ -n "$SOUND" && "${SOUND##*.}" != "disabled" ]]; then
        canberra-gtk-play \
            -c never \
            --property canberra.xdg-theme.name=$SOUNDTHEME \
            -f "$SOUND"
    fi
fi
