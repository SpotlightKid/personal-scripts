#!/bin/bash
#
# Wrapper script for 'xdg-open' to use when Gnome programs want to start the
# Nautilus file manager, but we want the preferred file manager.
#

#echo "$@" >> /tmp/nautilus.log
# strip '--no-default-window --no-desktop' from command line
shift 2
exec xdg-open "$@"
