#!/bin/bash
#
# Start the KurzFiler Java program for creating and editing Kurzweil K2xx sample libraries
#

KURZFILER_HOME="$HOME/lib/kurzfiler"

exec java -jar "$KURZFILER_HOME/KurzFiler.jar" "$@"
