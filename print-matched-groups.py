#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

if len(sys.argv) < 3:
    sys.exit("usage: print-matched-groups <regex> <file>...")

regex = re.compile(sys.argv[1])
files = sys.argv[2:]

for fn in files:
    matches = set()

    with open(fn) as fp:
        for line in fp:
            for group in regex.findall(line):
                if group:
                    matches.add(group)

        if matches:
            print("%s:\n" % fn)

            for group in sorted(matches):
                print(group)

            print()
