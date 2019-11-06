#!/usr/bin/python
"""Extract binary file embedded into a C header."""

import sys
import re


DATA_RX = re.compile(r'^\s*(0x[0-9a-f]+\s*,\s*)+', re.I)


def main(args=None):
    if args:
        infn = args.pop(0)
    else:
        return "Usage: h2file.py <file>.h [output]"

    with open(infn) as infile:
        data = []
        for line in infile:
            match = DATA_RX.match(line)

            if match:
                data.extend([int(n, 16) for n in line.split(',') if n.strip()])

    data = bytes(data)

    if args:
        outfn = args.pop(0)

        with open(outfn, "wb") as outfile:
            outfile.write(data)
    else:
        print(data.decode())


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
