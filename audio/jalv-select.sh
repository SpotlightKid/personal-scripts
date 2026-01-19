#!/bin/bash

exec env LV2_PATH="/home/chris/lib/lv2:/home/chris/.lv2:/usr/lib/lv2" jalv.select -H 600 "$@"
