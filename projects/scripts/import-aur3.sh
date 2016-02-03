#!/bin/bash

AUR4_HOME="$HOME/src/arch/aur"
AUR3_HOME="$HOME/src/arch/aur3"

if [ -z "$1" ]; then
    echo "usage: import-au3 <package>" >/dev/stderr
    exit 1
else
    PKG="$1"
fi

if [ ! -d "$AUR3_HOME/$PKG" ]; then
    cd "$AUR3_HOME" && \
    git clone "https://github.com/aur-archive/$PKG.git" || exit 1
fi

cd "$AUR4_HOME"

if [ ! -d "$PKG" ]; then
    git clone "ssh://aur@aur.archlinux.org/$PKG.git" && \
    cp -i "$AUR3_HOME/$PKG/"* "$PKG" || exit 1
fi

cd "$PKG"

if [ ! -e .gitignore ]; then
    echo pkg/ > .gitignore
    echo src/ >> .gitignore
    echo .AURINFO >> .gitignore
    echo "$PKG/" >> .gitignore
    echo "$PKG"'*.tar.xz' >> .gitignore
    echo "$PKG"'*.tar.gz' >> .gitignore
    echo "$PKG"'*.tar.bz2' >> .gitignore
    echo "$PKG"'*.src.tar.gz' >> .gitignore
fi

makepkg -fc && \
mksrcinfo && \
git add PKGBUILD .SRCINFO .gitignore && \
git status
