#!/bin/sh
#
# sudo-askpass - Use zenity to ask for sudo password
#
# To use, set add this to your shell profile:
#
# export SUDO_ASKPASS=sudo-askpass
#
# and then call sudo with the "-A" option

exec zenity --password --title "Enter password for $USER"
