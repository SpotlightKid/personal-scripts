#!/bin/bash
#
# aur-check-for-base-devel-dependency
#
# Checks whether the given package(s) is in the base-devel group or a
# dependency of a member of the group.

if [ $# -eq 0 ]; then
    echo "Usage: $0 package..."
    exit 2
fi

for pkg in "$@"; do
    LC_ALL=C pacman -Si $(pactree -rl $pkg | sort) 2>/dev/null | \
        grep -q "^Groups *:.*base-devel"
    if [ $? -eq 0 ]; then
        echo "$pkg"
    fi
done
