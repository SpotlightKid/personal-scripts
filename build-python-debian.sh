sudo apt-get install build-essential python3 python3-dev python3-pip git curl libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev blt-dev tk-dev libjpeg-dev libpng12-dev libfreetype6-dev

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

time pyenv install -v 3.6.3
