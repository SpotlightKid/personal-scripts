#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert color values in Löve Lua scripts from 0..255 to 0.0..1.0"""


import os
import re
from pathlib import Path


COLOR_FUNC_RX = re.compile(r'\.(?P<function>(set(Background)?Color(Mask)?|clear))'
                           r'\(\s*(?P<red>\d+)\s*,\s*(?P<green>\d+)\s*,\s*(?P<blue>\d+)(\s*,\s*(?P<alpha>\d+))?\s*\)')
COLOR_TABLE_RX = re.compile(r'{\s*(?P<red>\d+)\s*,\s*(?P<green>\d+)\s*,\s*(?P<blue>\d+)(\s*,\s*(?P<alpha>\d+))?\s*}')


def convert_color_values(match):
    red = int(match.group('red')) / 255
    green = int(match.group('green')) / 255
    blue = int(match.group('blue')) / 255

    if 'function' in match.groupdict():
        func = match.group('function')

        if match.group('alpha') is not None:
            alpha = int(match.group('alpha')) / 255
            return '.{}({:.5}, {:.5}, {:.5}, {:.5})'.format(func, red, green, blue, alpha)
        else:
            return '.{}({:.5}, {:.5}, {:.5})'.format(func, red, green, blue)
    else:
        if match.group('alpha') is not None:
            alpha = int(match.group('alpha')) / 255
            return '{{{:.5}, {:.5}, {:.5}, {:.5}}}'.format(red, green, blue, alpha)
        else:
            return '{{{:.5}, {:.5}, {:.5}}}'.format(red, green, blue)


def main(args=None):
    if '-f' in (args if args is not None else sys.argv[1:]):
        dryrun = False
    else:
        dryrun = True

    for scriptfn in sorted(Path().rglob("*.lua")):
        matches = 0
        lines = []
        print("Reading file '{}'...".format(scriptfn))

        with open(scriptfn) as fp:
            for line in fp:
                for rx in (COLOR_FUNC_RX, COLOR_TABLE_RX):
                    newline, nrepl = rx.subn(convert_color_values, line)

                    if nrepl:
                        line = newline
                        matches += nrepl

                lines.append(line)


        if matches:
            if not dryrun:
                bakfn = str(scriptfn) + '.bak'
                if os.path.exists(bakfn):
                    print("Backup file '{}' already exists. Skipping file.".format(bakfn))
                    continue
                else:
                    os.rename(scriptfn, bakfn)

                with open(scriptfn, 'w') as fp:
                    fp.writelines(lines)

                print("Rewritten file '{}' with {} replacements.".format(scriptfn, matches))
            else:
                print("{} matches in file '{}'.".format(matches, scriptfn))
        else:
            print("No matches in file '{}'.".format(scriptfn))


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)

