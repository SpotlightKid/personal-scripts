#!/bin/bash
#
# update-aur-package.sh - Rebuild AUR package and update repository

updpkgsums && \
makepkg -fc && \
makepkg --printsrcinfo > .SRCINFO
git add -A
git diff --cached
pacman -Qlp "$(ls -1tr *pkg.tar.xz | tail -n 1)"

echo -n "Install new package? [Y/n] "
read ret

if [ "x$ret" = "x" -o "x$ret" = "xy" -o "x$ret" = "xY" ]; then
    sudo pacman -U "$(ls -1tr *pkg.tar.xz | tail -n 1)"
fi

echo -n "Commit and push changes to AUR repository? [y/N] "
read ret
if [ "x$ret" = "xy" -o "x$ret" = "xY" ]; then
    git commit && git push
fi
