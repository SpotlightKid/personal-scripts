#!/usr/bin/env python
#
# downthemall.py
#
"""Scrape all links from given URL and download all link targets whose URL matches the given regular expression

Requires lxml and requests third-party modules.

"""

import argparse
import os
import re
import sys
import time

from io import StringIO
from posixpath import basename
from subprocess import CalledProcessError, check_output, STDOUT
from urllib.parse import urljoin, urlparse

import requests
from lxml import etree


ap = argparse.ArgumentParser(prog="downthemall", description=__doc__.splitlines()[0])
ap.add_argument("-d", "--delay", type=float, help="Delay in seconds (float) between each download")
ap.add_argument("-f", "--force", action="store_true", help="Overwrite existing files")
ap.add_argument("-x", "--use-dirs", action="store_true", help="Create directory hierarchies")
ap.add_argument("-v", "--verbose", action="store_true", help="Verbose messages")
ap.add_argument("url", help="URL to scrape")
ap.add_argument("regex", help="Python regular expression to match against link URLs")

args = ap.parse_args()


try:
    html = requests.get(args.url).text
except Exception as exc:
    print(f"Failed to retrieve page URL: {exc}")
    sys.exit()

parser = etree.HTMLParser()
tree = etree.parse(StringIO(html), parser)
urls = tree.xpath('//a/@href')

try:
    for url in urls:
        if not re.match(r'^[a-z]+:', url):
            url = urljoin(args.url, url)

        if args.verbose:
            print(f"Checking {url}:")

        if re.match(args.regex, url):
            urlparts = urlparse(url)
            fn = basename(urlparts.path)

            if os.path.exists(fn) and not args.force:
                print(f"File '{fn}' already exists. Skipping.")

                if args.verbose:
                    print("Use -f|--force to overwrite.")

                continue

            try:
                if args.verbose:
                    print(f"Downloading {url}...")

                cmd = ["wget", "-q", "-nc"]

                if args.use_dirs:
                    cmd.append("-x")
                    cmd.append("-nH")

                cmd.append(url)
                proc = check_output(cmd, stderr=STDOUT)
            except CalledProcessError as exc:
                output = exc.output.decode(sys.stderr.encoding)
                print(f"Could not download '{url}' (exit code {exc.returncode}): {output}",
                      file=sys.stderr)

            if args.delay is not None and args.delay > 0.0:
                time.sleep(args.delay)
        else:
            if args.verbose:
                print(f"URL {url} does not match. Skipping.")

    if args.verbose:
        print("Done.")
except KeyboardInterrupt:
    print("\nInterrupted.", file=sys.stderr)
