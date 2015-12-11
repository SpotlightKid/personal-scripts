#!/bin/bash

#echo "$@" >> /tmp/nautilus.log
# strip '--no-default-window --no-desktop' from commadn line
shift 2
exec xdg-open "$@"
