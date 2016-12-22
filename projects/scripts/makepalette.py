#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# makepalette.py
#
"""Create a Gimp palette from the dominant color of an image file."""

from __future__ import print_function, unicode_literals

import argparse
import logging
import sys
import time

from os.path import basename, splitext

import colorthief

log = logging.getLogger(__file__)


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('-a', '--accuracy', type=int, default=10,
                    help="Accuracy of algorithm (1=best/slowest, default: %(default)s)")
    ap.add_argument('-c', '--columns', type=int, default=8,
                    help="Number of colors per row (default: %(default)s)")
    ap.add_argument('-d', '--include-dominant', action='store_true',
                    help="Include dominant color in palette")
    ap.add_argument('-m', '--max-colors', type=int, default=10,
                    help="Maximum number of colors in the palette (default: %(default)s)")
    ap.add_argument('-n', '--name',
                    help="Name of new palette (default: image file base name)")
    ap.add_argument('-v', '--verbose', action="store_true",
                    help="Be verbose")
    ap.add_argument('imagefile', metavar='IMAGEFILE', help="Image file name")
    ap.add_argument('palettefile', nargs='?', metavar='PALETTEFILE',
                    help="Palette file name")

    args = ap.parse_args(args if args is not None else sys.argv[1:])

    logging.basicConfig(format="%(levelname)s - %(message)s",
        level=logging.DEBUG if args.verbose else logging.WARNING)

    try:
        log.info("Reading image file '%s'...", args.imagefile)
        image = colorthief.ColorThief(args.imagefile)
    except Exception as exc:
        return "Could not open image file '%s': %s" % (args.imagefile, exc)
    else:
        start = time.time()
        log.info("Calculating palette of max. %i colors...", args.max_colors)
        palette = image.get_palette(args.max_colors, args.accuracy)
        log.debug("Found %i colors in %.2f seconds." %
                  (len(palette), time.time() - start))
        if args.include_dominant:
            log.info("Looking for dominant color...")
            start = time.time()
            dominant = image.get_color(args.accuracy)
            log.debug("Found dominant color (%s) in %.2f seconds." %
                      (", ".join(map(str, dominant)), time.time() - start))

            if dominant not in palette:
                log.info("Adding dominant color to palette.")
                palette.insert(0, dominant)
            else:
                log.info("Dominant color already included in palette.")

    filebase = splitext(basename(args.imagefile))[0]
    palettename = args.name if args.name else filebase
    palettefn = args.palettefile if args.palettefile else filebase + '.gpl'

    try:
        log.info("Writing GIMP palette file to '%s'...", palettefn)
        with open(palettefn, 'w') as gpl:
            gpl.write('GIMP Palette\n')
            gpl.write('Name: %s\n' % palettename)
            gpl.write('Columns: %i\n#\n' % args.columns)

            for i, (red, green, blue) in enumerate(palette):
                gpl.write("%s %s %s %s Color %i\n" %
                          (red, green, blue, palettename, i + 1))
    except (IOError, OSError) as exc:
        return "Could not write to palette file '%s': %s" % (palettefn, exc)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
