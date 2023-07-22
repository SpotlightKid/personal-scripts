#!/bin/bash
#
# update-aur-package.sh - Rebuild AUR package and update repository

set -e

updpkgsums && \
makepkg -fc && \
makepkg --printsrcinfo > .SRCINFO
pacman -Qlp "$(ls -1tr *pkg.tar.* | tail -n 1)"

echo -n "Install new package? [Y/n] "
read ret

if [ "x$ret" = "x" -o "x$ret" = "xy" -o "x$ret" = "xY" ]; then
    sudo pacman -U "$(ls -1tr *pkg.tar.* | tail -n 1)"
fi

{git status; git diff; } | less
echo -n "Commit and push changes to AUR repository? [y/N] "
read ret
if [[ "${ret,,}" = "y" ]]; then
    git add -A
    git commit -m "New upstream version" -e && \
    git push
fi

echo -n "Remove build artifacts? [y/N] "
read ret
if [[ "${ret,,}" = "y" ]]; then
    rm -rf src pkg *.tar.*
fi
