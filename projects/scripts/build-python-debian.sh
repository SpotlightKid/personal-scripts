#!/bin/bash
#
# build-python-debian.sh - Build Python 3 on a vanilla debian system via pyenv
#

sudo apt-get install \
    blt-dev \
    build-essential \
    curl \
    git \
    libbz2-dev \
    libdb5.3-dev \
    libexpat1-dev \
    libfreetype6-dev \
    libgdbm-dev \
    libjpeg-dev \
    liblzma-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libpng12-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    python3 \
    python3-dev \
    python3-pip \
    tk-dev \
    zlib1g-dev

curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
cat >> ~/.bashrc <<__EOF__
export PATH="\$HOME/.pyenv/bin:\$PATH"
eval "\$(pyenv init -)"
eval "\$(pyenv virtualenv-init -)"
__EOF__
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
#export CONFIGURE_OPTS="--enable-optimizations"
export MAKE_OPTS="-j 1"

time pyenv install -v ${1:-3.6.3}
