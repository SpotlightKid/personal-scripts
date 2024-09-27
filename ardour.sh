#!/bin/bash
#
# Start Ardour DAW with custom LV2 plugin search path
#

EXTRA_LV2_PATHS=(
    "$HOME/lib/lv2"
)
ARDOUR="ardour8"

for path in "${EXTRA_LV2_PATHS[@]}"; do
    if [[ -d "$path" ]]; then
        if ! echo $LV2_PATH | grep -q "$path"; then
            LV2_PATH="$path:$LV2_PATH"
        fi
    fi
done

export LV2_PATH
exec "$ARDOUR" "$@"
