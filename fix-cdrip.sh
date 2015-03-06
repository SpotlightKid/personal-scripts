#!/bin/bash
#
# fix-cdrip.sh
#
# Organize FLAC, MP3 and Ogg files from a CD rip into sub-directories
#

if [ -n "$1" ]; then
    cd "$1"
fi

perl-rename 'tr/A-Z/a-z/' *.{flac,mp3,ogg}
for type in flac mp3 ogg; do
    mkdir "$type"
    mv *.$type "$type"
done
