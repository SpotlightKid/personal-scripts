#!/bin/bash

function clean_osx_files() {
    find ${1:-.} -iname .ds_store -print0 | xargs -t -r -0 -n 100 rm -f
}
