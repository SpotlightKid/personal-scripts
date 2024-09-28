#!/bin/bash
#
# nimpretty-fifo - Run nimpretty on stdin and write formatted code to stdout
#

fifo="$(mktemp -u -t XXXXXXXX.nim)"
mkfifo -m 600 "$fifo"

cleanup() {
    rm -f "$fifo"
}

trap cleanup EXIT
cat > "$fifo"
nimpretty --indent:2 --out:/dev/stdout "$fifo"
