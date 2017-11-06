#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os
import re
from urllib.parse import urlparse

from lxml import etree
from os.path import exists, join
from io import open


log = logging.getLogger("ff2pass.py")


def parse(fn, outdir):
    with open(fn, encoding='utf-8') as fp:
        tree = etree.parse(fp)

    root = tree.getroot()
    entries = root.getchildren()[0]
    os.makedirs(outdir, exist_ok=True)

    for entry in entries.getchildren():
        attr = entry.attrib
        host = attr.get('formSubmitURL', '').strip() or attr['host']
        log.debug("Host: %s", host)
        up = urlparse(host)
        host = up.netloc.replace(':', '-')

        if host.startswith('www.'):
            host = host[4:]

        log.debug("Host (mangled): %s", host)

        if not host:
            log.error("Empty host. Skipping entry.")
            continue

#~        user = attr.get('user', '').strip()
#~        if user:
#~            host = '%s@%s' % (user, host)

        i = 2
        outfile = join(outdir, host)

        while exists(outfile):
            log.warning("Output file '%s' exists. Adding prefix '-%i'.", outfile, i)
            outfile = "%s-%i" % (join(outdir, host), i)
            i += 1

        with open(outfile, 'w', encoding='utf-8') as fp:
            log.debug("Writing output file '%s'...\n", outfile)
            fp.write('{}\n'.format(attr['password']))
            fp.write('user: {}\n'.format(attr['user']))
            fp.write('url: {}\n'.format(attr['host']))


def main(args=None):
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(message)s")
    parse(args[0], args[1])


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
