#!/bin/bash

AUR3DIR="$HOME/src/arch/aur"
AUR4DIR="$HOME/src/arch/aur4"

if [ -z "$1" ]; then
    echo "usage: convaur <project>"
    exit 1
else
    PACKAGE="$1"
    if [ ! -d "$AUR3DIR/$PACKAGE" ]; then
        echo "Package $PACKAGE not found in $AUR3DIR."
        exit 1
    fi
fi

cd "$AUR4DIR"
if [ ! -d "$PACKAGE" ]; then
    git clone ssh://aur@aur.archlinux.org/$PACKAGE.git
fi

cd "$AUR3DIR/$PACKAGE"
for f in PKGBUILD *.install *.patch *.desktop; do
    if [ -e "$f" ]; then
        echo "Copying ${f}..."
        cp -vf "$f" "$AUR4DIR/$PACKAGE/"
    fi
done

svn propget svn:ignore "$AUR3DIR/$PACKAGE" | grep -v '\.SRCINFO' > \
    "$AUR4DIR/$PACKAGE/.gitignore"

cd "$AUR4DIR/$PACKAGE"
git add -A
git stat
