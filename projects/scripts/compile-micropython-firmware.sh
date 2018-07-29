#!/bin/bash -x

BOARD="${1:-BLACK_F407ZG}"
BOARD_REPO_URL="https://github.com/SpotlightKid/$BOARD.git"

if [ -d micropython/.git ]; then
    ( cd micropython; git checkout master; git pull; )
else
    git clone https://github.com/micropython/micropython.git
fi

cd micropython
git submodule update --init

if [ -d ports/stm32/boards/$BOARD ]; then
    if [ -d ports/stm32/boards/$BOARD/.git ]; then
        ( cd ports/stm32/boards/$BOARD; git pull; )
    fi
else
    ( cd ports/stm32/boards; git clone $BOARD_REPO_URL; )
fi

make -C mpy-cross
(cd  ports/stm32; make BOARD=$BOARD clean; make BOARD=$BOARD; )
echo "Done."
