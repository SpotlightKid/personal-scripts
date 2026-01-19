#!/bin/bash

echo "Zenity: " "$@" >> "${TMPDIR:-~/tmp}/zenity.log"
exec /usr/bin/zenity "$@"
