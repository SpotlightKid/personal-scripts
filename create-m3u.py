#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create an M3U playlist from a directory or list of files."""

from __future__ import print_function, unicode_literals

import argparse
import os
from os.path import abspath, basename, exists, isdir, isfile, join, relpath

import mutagen


def get_first(data, names, default=''):
    if not isinstance(names, (list, tuple)):
        names = [names]

    for name in names:
        val = data.get(name)
        if hasattr(val, 'text'):
            val = val.text
        if val and isinstance(val, (list, tuple)):
            return val[0]
        elif val:
            return val
    return default


def create_m3u(files, output_dir, relative=True):

    m3u_lines = dict()
    artists = set()
    albums = set()
    for filename in files:
        if not isfile(filename):
            continue

        meta = mutagen.File(filename)
        if meta:
            artist = get_first(meta, ('artist', 'TPE1'))
            album = get_first(meta, ('album', 'TALB'))
            title = get_first(meta, ('title', 'TIT2'))
            try:
                tracknum = int(get_first(meta, 'tracknumber', 'TRCK'))
            except:
                tracknum = None

            if artist and title:
                title = "{} - {}".format(artist, title)
            elif artist:
                title = artist

            if artist:
                artists.add(artist)
            if album:
                albums.add(album)

            duration=round(meta.info.length)
            extinf = "#EXTINF:{},{}".format(duration, title)
            path = abspath(filename)
            if relative:
                path = relpath(path, output_dir)

            key = (artist, album, tracknum, title, basename(filename))
            m3u_lines[key] = (extinf, path)

    if m3u_lines:
        if len(albums) == 1 and len(artists) == 1:
            m3u_basename = "{} - {}".format(list(artists)[0], list(albums)[0])
        elif len(artists) == 1:
            m3u_basename = list(artists)[0]
        elif len(albums) == 1:
            m3u_basename = list(albums)[0]
        else:
            m3u_basename = basename(output_dir)

        m3u_filename = join(output_dir, m3u_basename + '.m3u')
        with open(m3u_filename, 'w') as m3u:
            m3u.write('#EXTM3U\n')
            for key in sorted(m3u_lines):
                m3u.write(m3u_lines[key][0] + '\n')
                m3u.write(m3u_lines[key][1] + '\n')


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--directory', metavar="DIR",
        help="Add all supported files in directory DIR to playlist.")
    parser.add_argument('-v', '--verbose', action="store_true",
        help="Be more verbose.")
    parser.add_argument('files', metavar="FILE", nargs='*',
        help="Media files to add to the playlist.")
    args = parser.parse_args(sys.argv[1:] if args is None else args)

    files = []
    if args.directory and isdir(args.directory):
        output_dir = abspath(args.directory).rstrip('/')
        files.extend([join(output_dir, fn) for fn in os.listdir(output_dir)
                      if isfile(join(output_dir, fn))])
    else:
        output_dir = os.getcwd()

    files.extend([fn for f in args.files if isfile(fn)])
    create_m3u(files, output_dir)


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]) or 0)
