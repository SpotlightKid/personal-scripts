#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# makepalette.py
#
"""Create a Gimp palette from the dominant colors of an image file."""

from __future__ import print_function, unicode_literals

import argparse
import logging
import sys
import time

from operator import itemgetter
from os.path import basename, splitext

import colorthief
from colornames import get_color_name


log = logging.getLogger(__file__)


def luminance(r, g, b):
    """Return an indication (0.0-1.0) of how bright the color appears."""
    return (r * 0.2125 + g * 0.7154 + b + 0.0721) * 0.5


def rgb_to_hsb(r, g, b):
    """Convert the given RGB values to HSB (between 0.0-1.0)."""
    h, s, v = 0, 0, max(r, g, b)
    d = v - min(r, g, b)

    if v != 0:
        s = d / float(v)

    if s != 0:
        if r == v:
            h = 0 + (g - b) / d
        elif g == v:
            h = 2 + (b - r) / d
        else:
            h = 4 + (r - g) / d

    h = h / 6.0 % 1
    return h, s, v


def main(args=None):
    sort_methods = {
        'luminance': ("Sort by luminance", lambda color: luminance(*color)),
        'red': ("Sort by red component", itemgetter(0)),
        'green': ("Sort be green component", itemgetter(1)),
        'blue': ("Sort by blue component", itemgetter(2)),
        'hue': ("Sort by hue", lambda color: rgb_to_hsb(*color)[0]),
        'saturation': ("Sort by saturation", lambda color: rgb_to_hsb(*color)[1]),
        'brightness': ("Sort by brightness", lambda color: rgb_to_hsb(*color)[2]),
        'dominance': ('Sort by dominance', lambda color: color),
    }
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('-a', '--accuracy', type=int, default=10,
                    help="Accuracy of algorithm (1=best/slowest, default: %(default)s)")
    ap.add_argument('-c', '--columns', type=int, default=8,
                    help="Number of colors per row (default: %(default)s)")
    ap.add_argument('-d', '--include-dominant', action='store_true',
                    help="Include dominant color in palette.")
    ap.add_argument('-l', '--find-names', type=int, metavar='DISTANCE',
                    help="Set label of each color to nearest match from a built-in "
                         "list of about 1500 colors. DISTANCE is the maximum allowed "
                         "distance for a match (0 - 255, try 20).")
    ap.add_argument('-m', '--max-colors', type=int, default=10,
                    help="Maximum number of colors in the palette (default: %(default)s)")
    ap.add_argument('-n', '--palette-name',
                    help="Name of new palette (default: image file base name)")
    ap.add_argument('-s', '--sort', metavar='METHOD', default='dominance',
                    choices=list(sort_methods) + ['help'],
                    help="Sort color by given method (default: %(default)s). "
                         "Use '--sort help' to show available methods.")
    ap.add_argument('-v', '--verbose', action="store_true",
                    help="Be verbose about what the script does.")
    ap.add_argument('image_file', metavar='IMAGEFILE', nargs='?',
                    help="Image file name")
    ap.add_argument('palette_file', nargs='?', metavar='PALETTEFILE',
                    help="Palette file name")

    args = ap.parse_args(args if args is not None else sys.argv[1:])

    logging.basicConfig(format="%(levelname)s - %(message)s",
        level=logging.DEBUG if args.verbose else logging.WARNING)

    if args.sort == 'help':
        print("Color sorting methods:\n")
        for name in sorted(sort_methods):
            print("%-15s - %s" % (name, sort_methods[name][0]))

        print()
        print("Suffix method with a '-' to sort in reversed (i.e. descending)")
        print("order, e.g. 'red-'.")
        return

    if not args.image_file:
        ap.print_help()
        return 2

    try:
        log.info("Reading image file '%s'...", args.image_file)
        image = colorthief.ColorThief(args.image_file)
    except Exception as exc:
        return "Could not open image file '%s': %s" % (args.image_file, exc)
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

    filebase = splitext(basename(args.image_file))[0]
    palette_name = args.palette_name if args.palette_name else filebase
    palette_fn = args.palette_file if args.palette_file else filebase + '.gpl'

    if args.sort and args.sort in sort_methods:
        reverse = args.sort.endswith('-')
        method = args.sort.rstrip('-')
        log.info("Sorting colors by '%s' method in %s order.", method,
                 'descending' if reversed else 'ascending')
        palette = sorted(palette, key=sort_methods[method][1], reverse=reverse)

    try:
        log.info("Writing GIMP palette file to '%s'...", palette_fn)
        with open(palette_fn, 'w') as gpl:
            gpl.write('GIMP Palette\n')
            gpl.write('Name: %s\n' % palette_name)
            gpl.write('Columns: %i\n#\n' % args.columns)

            for i, (red, green, blue) in enumerate(palette):
                if args.find_names is not None:
                    color_name = get_color_name(red, green, blue, args.find_names)
                    if not color_name:
                        log.warning("No name match found for color (%i, %i, %i).",
                                    red, green, blue)
                if not args.find_names is not None or not color_name:
                    color_name = "%s No. %i" % (palette_name, i + 1)

                gpl.write("%s %s %s %s\n" % (red, green, blue, color_name))
    except (IOError, OSError) as exc:
        return "Could not write to palette file '%s': %s" % (palette_fn, exc)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
