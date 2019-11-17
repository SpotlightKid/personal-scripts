#!/usr/bin/env python2
"""Scrape Novation Circuit SysEx patch data from HTML saved from Circuit Patch Share site."""

import argparse
import logging
import os
import re
import sys
from os.path import exists, join
from base64 import b64decode


log = logging.getLogger('scrape-circuit-patch-share')


def safe_name(name):
    return "".join(c if re.match(r'\w', c) else '_' for c in name)


def unescape(match):
    return chr(int(match.group(1)))


def scrape_patches(html):
    html = re.sub('&#(\d+);', unescape, html)
    patches = re.findall(r"sendPatchToCircuit\('(.*?)',\s*atob\('(.*?)'\),\s*(\d+)\)", html)

    result = {}
    for name, patch, synth in patches:
        name = name.strip()
        if name in result:
            continue

        result[(name, int(synth))] = bytearray([int(c) for c in b64decode(patch).split(b',')])

    return result


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('-v', '--verbose', action="store_true",
        help="Be verbose")
    ap.add_argument('-o', '--output-dir', metavar='DIR', default=os.getcwd(),
        help="Output directory (default: current directory)")
    ap.add_argument('html', help="HTML input file")
    args = ap.parse_args(args)

    logging.basicConfig(format="%(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO)

    with open(args.html) as fp:
        html = fp.read()

    patches = scrape_patches(html)
    log.info("Found %i patches.", len(patches))


    for i, ((name, synth), data) in enumerate(sorted(patches.items())):
        outdir = join(args.output_dir, "Synth %i" % (synth + 1,))

        if not exists(outdir):
            os.makedirs(outdir)

        outfn = join(outdir, "%s.syx" % safe_name(name))
        log.info("Writing patch '%s' to '%s'...", name, outfn)

        data[7] = synth
        with open(outfn, 'wb') as fp:
            fp.write(patches[(name, synth)])

    log.info("%i patch files written.", i + 1)
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
