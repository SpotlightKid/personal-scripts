#!/bin/bash

if [[ -d "$HOME/lib/lv2" ]]; then
    if ! echo $LV2_PATH | grep -q $HOME/lib/lv2; then
        LV2_PATH="$HOME/lib/lv2:$HOME/.lv2:/usr/lib/lv2"
    fi
fi

export LV2_PATH
exec raysession "$@"
