#!/bin/bash
#
# sudo-askpass - Use yad or zenity to ask for sudo password
#
# To use, add this to your shell profile:
#
# export SUDO_ASKPASS=sudo-askpass
#
# and then call sudo with the "-A" option

PROMPT="Authentication required for $USER"

if which yad &>/dev/null; then
    exec yad --entry --entry-label "Password" --hide-text --image=password --window-icon=dialog-password --text="$PROMPT" --title=Authentication --center
elif which zenity &>/dev/null; then
    exec zenity --password --title "$PROMPT"
elif which kdialog &>/dev/null; then
    exec kdialog --title "Authentication" --password "$PROMPT"
else
    STTY_SAVE="$(stty -g)"

    abort() {
        stty $STTY_SAVE
    }

    trap abort EXIT
    echo -n "Enter password for $USER: " > /dev/stderr
    stty -echo
    read PASSWORD
    echo
    stty $STTY_SAVE
    echo $PASSWORD
fi
