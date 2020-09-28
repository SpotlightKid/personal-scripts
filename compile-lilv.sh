#!/bin/bash

set -e fail
cd ~/tmp
rm -rf lilv
git clone --recursive https://github.com/drobilla/lilv.git
unset CFLAGS CPPCFLAGS CXXFLAGS LDFLAGS MAKEFLAGS
ccache -C
cd lilv
python waf configure \
    --debug \
    --prefix=/usr \
    --configdir=/etc \
    --dyn-manifest \
    --test
python waf
python waf test -v -v -v
