#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert a file to a C char array representation.

Writes a C header to standard output or into a new file.

"""

import argparse
import sys
from os.path import basename, isfile


BYTES_PER_LINE = 12
INDENT = 2

# for Python 2 backwards compatibility
if isinstance(b'', str):
    toint = ord
else:
    toint = lambda x: x


def read_file(fobj, chunksize):
    while True:
        chunk = fobj.read(chunksize)
        if not chunk:
            yield None
            break
        yield chunk


def fn2identifier(fname):
    res = []
    for c in basename(fname).lower():
        res.append(c if c.isalnum() else '_')

    if not (res[0].isalpha() or res[0] == '_'):
        res.insert(0, '_')

    return "".join(res)


def process_file(inf, outf, varname, bytes_per_line=BYTES_PER_LINE,
                 indent=INDENT, lenvar=True, guard=True):
    size = 0

    if guard:
        outf.write("#ifndef {}_H\n".format(varname.upper()))
        outf.write("#define {}_H\n".format(varname.upper()))

    outf.write("static const unsigned char {}[] = {{\n".format(varname + '_data'))

    for data in read_file(inf, bytes_per_line):
        if data is not None:
            size = size + len(data)
            outf.write(" " * indent)
            outf.write(", ".join("0x{:02x}".format(toint(i)) for i in data))

        if data is None:
            outf.write('\n')
            break
        else:
            outf.write(',\n')

    outf.write("};\n")

    if lenvar:
        outf.write("const size_t {} = {:d};\n".format(varname + '_len', size))

    if guard:
        outf.write("#endif\n")


def main(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--name", metavar="PREFIX",
                    help="Name prefix für const data in generated code")
    ap.add_argument("infile", help="Input file")
    ap.add_argument("outfile", nargs='?', help="Output file (default: stdout)")

    args = ap.parse_args(args)

    if not isfile(args.infile):
        return "{} is not a file.".format(args.infile)


    varname = (args.name if args.name else fn2identifier(args.infile)).strip()

    with open(args.infile, "rb") as infp:
        with (open(args.outfile, 'w') if args.outfile else sys.stdout) as outfp:
            process_file(infp, outfp, varname)


if __name__ == '__main__':
    sys.exit(main() or 0)
