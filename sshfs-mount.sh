#!/bin/bash
#
# sshfs-mount.sh
#
# Mount directory from a filserver via SSHfs and open file manager
#

HOST="${1:-dockstar3}"
REMOTE_DIR="${2:-/mnt/explorer}"
LOCAL_DIR="${3:-${HOME}/mnt/${HOST}-${REMOTE_DIR##*/}}"
SSHFS_OPTS="-o max_readahead=524288"

is_mounted() {
    cat /proc/mounts | cut -d " " -f 1 | grep -q "$1"
    return $?
}

if ! is_mounted "$HOST:$REMOTE_DIR" ; then
    if tty -s ; then
        echo "Mounting $HOST:$REMOTE_DIR at $LOCAL_DIR..."
    fi

    mkdir -p "$LOCAL_DIR" && \
    sshfs $SSHFS_OPTS "$HOST:$REMOTE_DIR" "$LOCAL_DIR"
fi

if [ $? -eq 0 -a -n "$DISPLAY" ]; then
    xdg-open "$LOCAL_DIR"
else
    if [ -n "$DISPLAY" ]; then
        zenity --error --title="Mounting failed" \
            --text="Could not mount $HOST:$REMOTE_DIR."
    fi
fi
