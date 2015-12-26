#!/bin/bash

# trailing slashes are important!
SRC="/run/media/chris/UsbStick16G/kurzweil/"
DEST="/home/chris/Dokumente/kurzweil/"

if [[ "$1" = "-f" ]]; then
    DRY_RUN=
    shift
else
    echo "Running in dry mode..."
    DRY_RUN="-n"
fi

if [[ $1 = "-r" ]]; then
    DEST2="$DEST"
    DEST="$SRC"
    SRC="$DEST2"
    shift
fi

echo "Syncing contents of $SRC to $DEST..."

rsync $DRY_RUN -rv --checksum \
    --exclude 00archives \
    --exclude .DS_Store \
    --exclude .boar \
    --exclude .kf-mrulist.dat \
    --exclude "*.png" \
    --exclude "*.rst" \
    --exclude "*.rar" \
    --exclude "*.zip" \
    "$@" \
    "$SRC" "$DEST"
