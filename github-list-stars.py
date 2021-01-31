#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""List all starred repositories in your GitHub account."""

import argparse
import json
import sys
from os.path import exists, join

import requests


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--output", metavar="FILE",
                    help="Save received JSON data to FILE")
    ap.add_argument("token", nargs='?', help="GitHub auth token")
    args = ap.parse_args(args)

    url = "https://api.github.com/user/starred?per_page=100&sort=created"
    headers = {"Accept": "application/vnd.github.v3+json"}

    if args.token:
        headers["Authorization"] = "token " + args.token

    repos = []
    page = 0
    while True:
        req = requests.get(url + "&page=%i" % page, headers=headers)

        if req.status_code == 200:
            data = req.json()

            if not data:
                break

            for repo in data:
                repos.append(repo)
                try:
                    print("Name:", repo["full_name"])
                    print("URL:", repo["html_url"])
                    print("Description:\n")
                    print(repo["description"])
                    print("")
                except KeyError as exc:
                    print("Info not available: %s" % exc)
        else:
            return "Error reponse: {}".format(req.json().get('message'), file=sys.stderr)

        page += 1

    if args.output:
        with open(args.output, 'w') as fp:
            json.dump(repos, fp)


if __name__ == '__main__':
    sys.exit(main() or 0)
