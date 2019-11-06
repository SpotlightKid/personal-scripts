#!/bin/bash
#
# Shortcut to install a binary Arch package,
# which has already been built by yay
#
PKG="$(ls -r1 ~/.cache/yay/$1/$1-*.tar.xz | head -n 1)"

if [ -n "$PKG" ]; then
    sudo pacman -U "$PKG"
fi
