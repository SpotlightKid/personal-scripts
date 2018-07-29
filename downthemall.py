#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# downthemall.py - scrape all links from given URL and download all link targets whose URL
#     matches the given regular expression
#

import re
import sys
import requests

from io import StringIO
from lxml import etree
from subprocess import CalledProcessError, check_call, DEVNULL
from urllib.parse import urljoin


if len(sys.argv) != 3:
    sys.exit("usage: downthemall.py <url> <regex>")

page_url = sys.argv[1]
regex = sys.argv[2]

html = requests.get(page_url).text
parser = etree.HTMLParser()
tree = etree.parse(StringIO(html), parser)
urls = tree.xpath('//a/@href')

for url in urls:
    if not re.match(r'^[a-z]+:', url):
        url = urljoin(page_url, url)

    if re.match(regex, url):
        try:
            check_call(['wget', '-q', url], stdout=DEVNULL)
        except CalledProcessError as exc:
            print("Could not download '{}'. wget process exit code: {}".format(url, exc.returncode))
