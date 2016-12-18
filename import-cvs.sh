#!/bin/bash
#
# import-cvs - Import a local CVS repository into a new Git repo
#
# Requires cvs2svn
#

REPO_DIR="$1"
GIT_NAME="$2"

if [ -z "$REPO_DIR" -o -z "$GIT_NAME" ]; then
    echo "usage: import-cvs REPO_DIR GIT_NAME"
    exit 2
fi

WORKDIR="$HOME/tmp/cvs2git"
mkdir -p "$WORKDIR"
cd "$WORKDIR"
rm -rf "$WORKDIR/git-blob.dat" "$WORKDIR/git-dump.dat" "$WORKDIR/git-marks.dat"


cvs2git \
    --blobfile="$WORKDIR/git-blob.dat" \
    --dumpfile="$WORKDIR/git-dump.dat" \
    --username=cvs2git \
    --encoding=UTF-8 \
    "$REPO_DIR" || exit 1

mkdir -p "$WORKDIR/$GIT_NAME"
git init "$WORKDIR/$GIT_NAME"
cd "$WORKDIR/$GIT_NAME"
git fast-import --export-marks="$WORKDIR/git-marks.dat" < "$WORKDIR/git-blob.dat"
git fast-import --import-marks="$WORKDIR/git-marks.dat" < "$WORKDIR/git-dump.dat"
git branch -D TAG.FIXUP
git gc --prune=now
git reset --hard
