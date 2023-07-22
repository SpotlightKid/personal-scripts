#!/usr/bin/env python
"""Examine an RSS feed retrieved from given URL."""

import sys
from xml.dom.minidom import parseString as parse_xml

import feedparser
import requests


if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = "https://lmc.nyxkn.org/rss"

res = requests.get(url)

if res.status_code != 200:
    sys.exit(f"Could not retrieve {url}.")

print("Headers:\n========\n")
for name, val in res.headers.items():
    print(f"{name}: {val}")

feed = feedparser.parse(res.text, response_headers=res.headers)

print("\nFeed:\n=====\n")
for name, val in feed.feed.items():
    print(f"{name}: {val}")

print("\nEntries:\n========\n")
for i, entry in enumerate(feed.entries):
    print(f"Entry {i:02}:\n=========\n")

    for name, val in entry.items():
        print(f"{name}: {val}")

    print()

doc = parse_xml(res.text)
print("Raw RSS XML:\n============\n")
print(doc.toprettyxml())
