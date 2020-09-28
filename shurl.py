#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  shurl.py
#
#  Copyright 2017 Christopher Arndt <chris@chrisarndt.de>
#
"""Shorten URL via the Google URL shortener API."""

from __future__ import print_function, unicode_literals

import argparse
import re
import sys
import requests

OA
URL_RX = re.compile(r'[^:]+://')
# URL for Google URL shortener API
API_URL = "https://www.googleapis.com/urlshortener/v1/url"
# API key for project "shurlpy"
API_KEY = "XXXXXXXX"


def copy_to_clipboard(data):
    import pyperclip
    pyperclip.copy(data)


def display_notification(url):
    import gi
    gi.require_version('Gtk', '2.0')
    from gi.repository import Gtk
    import notify2

    if not notify2.init('shurl', mainloop='glib'):
        raise RuntimeError("Could not connect to notification service.")

    server_caps = notify2.get_server_caps()
    n = notify2.Notification("Shortened URL:", url, icon="applications-internet")

    if 'actions' in server_caps:
        def open_url(notification, action):
            import webbrowser
            webbrowser.open(url)
            notification.close()

        n.add_action("default", "Open URL", open_url)

    n.connect('closed', lambda *args: Gtk.main_quit())
    n.set_category("network")
    n.set_urgency(notify2.URGENCY_NORMAL)
    n.set_timeout(0)

    if not n.show():
        raise RuntimeError("Failed to send notification.")

    if 'actions' in server_caps:
        Gtk.main()

"""
def display_notification(url):
    import time
    from plyer import notification
    notification.notify("Shortened URL:", url, "shurl", "applications-internet", timeout=10)
"""


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('-c', '--clipboard', action="store_true",
                    help="Copy shortened URL to the clipboard")
    ap.add_argument('-k', '--api-key', metavar="KEY", default=API_KEY, help="Google API key")
    ap.add_argument('-n', '--notify', action="store_true",
                    help="Display shortened URL as a desktop notification (implies '-q')")
    ap.add_argument('-q', '--quiet', action="store_true",
                    help="Do not print shortened URL to standard output")
    ap.add_argument('url',  metavar="URL", nargs='?', help="URL to shorten")
    args = ap.parse_args(args if args is not None else sys.argv[1:])

    if args.url:
        long_url = args.url.strip()
    else:
        import pyperclip
        long_url = pyperclip.paste().strip()

    if not URL_RX.match(long_url):
        return "Invalid or empty URL: '{}'".format(long_url)

    try:
        resp = requests.post(API_URL, params=dict(key=args.api_key),
                             json=dict(longUrl=long_url))

        if resp.status_code != 200:
            raise RuntimeError("unsuccessful API status code: {}".format(resp.status_code))

        rdata = resp.json()
        short_url = rdata['id']
    except Exception as exc:
        return "Could not get shortened URL for '{}': {}".format(args.url, exc)
    else:
        if args.clipboard:
            try:
                copy_to_clipboard(short_url)
            except Exception as exc:
                return "Could not copy URL to clipboard: {}".format(exc)

        if args.notify:
            try:
                display_notification(short_url)
            except Exception as exc:
                return "Could not display notification: {}".format(exc)
        elif not args.quiet:
            print(short_url)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
