#!/usr/bin/env python
#
# splitsyx.py
#
"""A quick hack to split up a sysex bulk dump of Yamaha AN1x voices.

The bulk file is split into patches and for each patch a separate file is
written in the current directory  with each filename showing the patch name
and optionally the program number, i.e. "The Voice.syx" or "001_The_Voice.syx".

Uses only minimal error checking and existing files may be overwritten, so
USE AT YOUR OWN RISK!

"""

import sys
import argparse
import os
from os.path import exists, join


__usage__ = "Usage: %(prog)s SYSEXFILE"

PATCHNAME_OFFSET = 9
PATCHNAME_LEN = 10
PATCHSLOT_OFFSET = 7
PY3 = sys.version_info[:2] >= (3, 0)


def is_an1x_voice(data):
    return (data[0] == 0xF0 and data[1] == 0x43 and
        data[3] == 0x5C and data[2] >> 4 == 0 and
        data[6]) == 0x11


def checksum(data, offset=4, end=-2):
    return ~sum(data[offset:end]) + 1 & 0x7F


def escape(s, chars=" /?*:;$\!"):
    for c in chars:
        s = s.replace(c, '_')
    return s


def main(args=None):
    ap = argparse.ArgumentParser(usage=__usage__, description=__doc__)
    ap.add_argument('-s', '--with-slots',
        action="store_true",
        help="Keep the program number stored in each patch.")
    ap.add_argument('-v', '--verbose',
        action="store_true",
        help="Print what's going on to standard out.")
    ap.add_argument('-f', '--force',
        action="store_true",
        help="Overwrite existing output files.")
    ap.add_argument('sysex', help="Input AN1x voice bank sysex file.")
    ap.add_argument('output_dir', nargs='?',
        help="Output directory (created if it doesn't exist).")

    args = ap.parse_args(args if args is not None else sys.argv)

    infile = open(args.sysex, 'rb')
    data = infile.read()
    infile.close()

    # split patches
    patches = [bytearray(p + b'\xF7') for p in data.split(b'\xF7')][:-1]

    for i, patch in enumerate(patches):
        if not is_an1x_voice(patch):
            print (u"Sysex msg. %03i is not a Yamaha AN1x voice dump." % i)
            continue

        patchname = patch[PATCHNAME_OFFSET:PATCHNAME_OFFSET+PATCHNAME_LEN]
        patchname = patchname.decode('latin1')

        if args.verbose:
            print (u"Read voice '%s' (%i bytes)." % (patchname, len(patch)))

        filename = escape(patchname.strip())

        if args.with_slots:
            slot = ord(patch[PATCHSLOT_OFFSET])
            filename = u"%03i_%s.syx" % (slot + 1, filename)
        else:
            filename += ".syx"
            patch = bytearray(patch)
            patch[6:9] = b'\x10\0\0'
            patch[-2] = checksum(patch)

        if args.output_dir:
            if not exists(args.output_dir):
                os.mkdir(args.output_dir)

            filename = join(args.output_dir, filename)

        if exists(filename) and not args.force:
            print (u"Output file '%s' already exists and will not be "
                "overwritten." % filename)
        else:
            if args.verbose:
                print (u"Writing data to file '%s'..." % filename)
            f = open(filename.encode('utf-8'), 'wb')
            f.write(patch)
            f.close()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
