#!/usr/bin/env python3
"""Recursively find matching file pairs in each dir under starting dir named
"<name>-L.wav" / "<name>-R.wav" and combine them into a stereo file using sox.
"""

import os
import re
import sys

from os.path import exists, join, splitext
from subprocess import CalledProcessError, run


PROG = "combine-wavs"
WAV_RX = re.compile(r".*-L\.[Ww][Aa][Vv]")
SOX_COMMAND = ["sox", "-M", "{left}", "{right}", "{output}"]


def run_sox(**kw):
    cmd = [item.format(**kw) for item in SOX_COMMAND]
    print(f"Running command: '{' '.join(cmd)}'...")
    return run(cmd, check=True, capture_output=True)


def main():
    if len(sys.argv) > 1:
        startdir = sys.argv[1]
    else:
        sys.exit(f"Usage: {PROG} <start dir>")

    for dirpath, dirname, filenames in os.walk(startdir):
        for filename in filenames:
            match = WAV_RX.match(filename)
            if match:
                # cut off extension and "-L" part
                basename, ext = splitext(filename)
                right = join(dirpath, basename[:-2] + "-R" + ext)
                output = join(dirpath, basename[:-2] + "-stereo" + ext)
                if exists(right):
                    try:
                        run_sox(left=join(dirpath, filename), right=right, output=output)
                    except CalledProcessError as exc:
                        stderr = exc.stderr.decode()
                        print(f"sox command failed: {stderr}", file=sys.stderr)
                else:
                    print(f"Did not find matching file for '{filename}'.", file=sys.stderr)


main()
