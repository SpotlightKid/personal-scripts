#!/bin/bash
#
# Start the LTT Lighting talk time PyGame application
#

VENV="${WORKON_HOME:-$HOME/lib/virtualenvs}/pygame"

source "$VENV/bin/activate"

exec "$HOME/work/ltt/main.py" -W 300 -H 200 "$@"
