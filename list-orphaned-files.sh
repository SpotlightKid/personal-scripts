#!/bin/sh
#
# list-orphaned-files.sh
#
# List files on the system (under /etc, /opt and /usr), which are not 
# not owned by any package in the Arch packaging system

tmp=${TMPDIR-/tmp}/pacman-disowned-$UID-$$
db=$tmp/db
fs=$tmp/fs

mkdir "$tmp"
trap 'rm -rf "$tmp"' EXIT

echo "Querying package database..."
pacman -Qlq | sort -u > "$db"

echo "Collecting file system listing..."
sudo find /etc /opt /usr \! -name lost+found \
    \( -type d -printf '%p/\n' -o -print \) | \
    sort > "$fs"

comm -23 "$fs" "$db" | less
