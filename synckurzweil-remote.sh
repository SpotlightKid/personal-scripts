#!/bin/bash

if [[ "$1" = "-f" ]]; then
    DRY_RUN=
    shift
else
    echo "Running in dry mode..."
    DRY_RUN="-n"
fi


KURZWEIL_ROOT_LOCAL="$HOME/Dokumente/kurzweil"
KURZWEIL_ROOT_REMOTE="${1:-chrisarndt.de:/home/www/chrisarndt.de/htdocs/files/kurzweil}"
SRC="$KURZWEIL_ROOT_LOCAL/k2x"
DEST="$KURZWEIL_ROOT_REMOTE/sounds/k2x"

echo "Syncing contents of $SRC to $DEST..."

rsync $DRY_RUN -rv --update --delete --checksum \
    --exclude .boar/ \
    --exclude .kf-mrulist.dat \
    --exclude synckurzweil-remote.sh \
    --exclude cfcard/00FAVS/ \
    --exclude cfcard/ULTIMATE/ \
    --exclude keysolution/ \
    --exclude smpl_lib/MELOTRON/ \
    --exclude pyramid/ \
    "$SRC"/ "$DEST"
