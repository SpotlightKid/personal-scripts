#!/bin/bash

[[ -n "$1" ]] || exit 1

SUMMARY="$1"
BODY="$2"
ICON="${3:+--icon=$3}"
SOUND="${4:+--hint=STRING:sound-name:$4}"

notify-send $ICON $SOUND "$SUMMARY" "$BODY"
