#!/usr/bin/env python

import os
import sys

import mido

if len(sys.argv) < 3:
    sys.exit("usage: {} <infile> <outfile>".format(os.path.basename(sys.argv[0])))

input_midi = mido.MidiFile(sys.argv[1])
output_midi = mido.MidiFile(type=0)
output_midi.tracks.append(mido.merge_tracks(input_midi.tracks))

output_midi.ticks_per_beat = input_midi.ticks_per_beat
output_midi.save(sys.argv[2])
