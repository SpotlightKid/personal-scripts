#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rename music files from KVR OSC submissions, replacing alpha-numeric prefix with numeric."""

import os
import re
import string


def conv(m):
    m = m.group(0)
    try:
        v = string.ascii_lowercase.index(m[0])
    except (ValueError, TypeError) as exc:
        v = 0

    if len(m) > 1:
        v += int(m[1:])

    return "%i - " % v

def main(path='.', dryrun=True):
    res = []
    for fn in os.listdir(path):
        new = re.sub(r'^[a-z][0-9]*', conv, fn)
        res.append((fn, new))

    for old, new in res:
        try:
            print("'%s' -> '%s'" % (old, new))
            if not dryrun:
                os.rename(old, new)
        except OSError as exc:
            print("Could not rename '%s' to '%s': %s" % (old, new, exc))


if __name__ == '__main__':
    main(sys.argv[1])
