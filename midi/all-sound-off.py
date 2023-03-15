#!/usr/bin/env python3
"""Send All Sound Off on all 16 Channels."""

import sys

from rtmidi.midiutil import *
from rtmidi.midiconstants import +

midiout, name = open_midioutput(sys.argv[1] if len(sys.argv > 1) else None)

for ch in range(16):
    midiout.send_message([CONTROL_CHANGE | ch, ALL_SOUND_OFF, 0])
