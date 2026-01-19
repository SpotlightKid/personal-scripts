#!/bin/bash

if [[ "$1" = "-u" ]]; then
    jack_lsp | grep -q midi-merger

    if [[ $? -eq 0 ]]; then
        exec jack_unload midi-merger
    fi
else
    jack_lsp | grep -q midi-merger

    if [[ $? -ne 0 ]]; then
        exec jack_load midi-merger mod-midi-merger
    fi
fi
