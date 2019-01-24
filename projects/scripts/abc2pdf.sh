#!/bin/bash
#
# abc2pdf.sh - Convert an ABC music file into a PDF score
#

if [ -z "$1" ]; then
    echo "Usage: abc2pdf [options] <file.abc>"
    return 2
else
    abc="${@: -1}"
    if [ ! -e "$abc" ]; then
        echo "Input file '"$abc"' does not exists."
        return 1
    fi
fi

# construct output filenames from input options
basefn="${abc##*/}"
basen="${basefn%.*}"
TMP="${TMP:-/tmp}"
PS="$(mktemp "$TMP/abc2pdf-XXXXXX.ps")"
PDF="$basen.pdf"

# generate PostScript with abcm2ps
abcm2ps $ABCM2PS_OPTS -O "$PS" "$@"; ret=$?

if [ $ret -ne 0 ]; then
    echo "Warning: error in conversion of ABC file to PostScript."
    echo "abcm2ps returned $ret."
fi

if [ -e "$PS" ]; then
    ps2pdf "$PS" "$PDF"; ret=$?
    rm -f "$PS"
fi

exit $ret
