#!/bin/bash
#
# splitcue.sh
#
# Splits an audio CD image file according to cue-file.
# The input file can be flac, wav, ape, etc. - any format supported by shntool.
# The output files will be FLAC encoded and tagged with Vorbis comments.
#
# Source: https://bbs.archlinux.org/viewtopic.php?id=58766
#
# Changes:
#
# 2014-03-16 chris@chrisarndt.de:
#   * Parse album title and individual track artists/titles with cueprint
#   * Add comment/data/genre tags if present in cue comments
#   * Add variable for flac encoding options
#   * Add variable for filename template
#   * Print out tag information for each track when encoding

FLAC_OPTS="-s -8"
FILENAME_TMPL="%n - %p - %t"

if [ -f "$1" ]; then
    i=0

    for cuefile in *.cue; do
        i=$(($i + 1))
    done

    if [ $i -eq 1 ]; then
        # found exactly one cuesheet
        if grep -q "INDEX 01 00:00:00" *.cue ; then
            nice shntool split -t "$FILENAME_TMPL" -f *.cue "$1"
        else
            echo "The first track has a pre-gap. Shntool will cut that off and put it in a seperate file."
            echo "You don't want that. Please modify the cuesheet from:"
            grep -m1 "INDEX 00" *.cue
            grep -m1 "INDEX 01" *.cue
            echo "to:"
            echo "    INDEX 01 00:00:00"
            exit 1
        fi
    elif [ $i -eq 0 ]; then
        echo "No cuesheet found in the current directory."
        exit 1
    elif [ $i -gt 1 ]; then
        echo "$i cuesheets found in the current directory. Please remove the superfluous cuesheets."
        exit 1
    fi
else
    echo "Split image file (flac, ape, wav, etc.) according to cue-file."
    echo "Output files are in FLAC."
    echo "Usage: `basename $0` <image-file>"
    exit 1
fi

echo
album=`cueprint -d '%T\n' *.cue`
genre=`grep -Em 1 'REM\s+GENRE' *.cue | cut -d\" -f2`
comment=`grep -Em 1 'REM\s+COMMENT' *.cue | cut -d\" -f2`
date=`grep -Em 1 'REM\s+DATE' *.cue | cut -d ' ' -f3`

for file in [0-9]*.wav; do
    if [[ ${file:0:1} == 0 ]] ; then
        tracknr=${file:1:1}
    else
        tracknr=${file:0:2}
    fi

    title=`cueprint -n $tracknr -t '%t\n' *.cue`
    artist=`cueprint -n $tracknr -t '%p\n' *.cue`

    echo "Encoding $file..."
    echo
    echo "File: ${file%.*}.flac"
    echo "Track: $tracknr"
    echo "Title: $title"
    echo "Artist (Performer): $artist"
    echo "Album: $album"
    echo "Genre: $genre"
    echo "Comment (Description): $comment"
    echo "Date (Year): $date"
    echo

    nice flac $FLAC_OPTS \
        -T "ARTIST=$artist" \
        -T "ALBUM=$album" \
        -T "TITLE=$title" \
        -T "TRACKNUMBER=$tracknr" \
        ${genre:+-T "GENRE=$genre"} \
        ${comment:+-T "DESCRIPTION=$comment"} \
        ${date:+-T "DATE=$date"} \
        "$file" && rm "$file"
done
