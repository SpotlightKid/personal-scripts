#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# gh-get.py
#
"""Download a single file from a GitHub repository."""

import shutil

from os.path import expanduser
from posixpath import basename

import requests
import yaml

GITHUB_CONFIG = '~/.config/hub'
ENDPOINT = 'https://api.github.com/repos/{user}/{repo}/contents/{path}'
API_TYPE = 'application/vnd.github.v4.raw'


def main(args=None):
    try:
        user, repo, path = args.pop(0).split('/', 2)
    except (IndexError, ValueError):
        return "Usage: gh-get.py <gh-user>/<repo>/<path/to/file> [<dest>]"
    else:
        destfn = args.pop(0) if args else basename(path)

    try:
        with open(expanduser(GITHUB_CONFIG)) as fp:
            hub_config = yaml.load(fp.read())
            access_token = hub_config['github.com'][0]['oauth_token']
    except OSError as exc:
        return "Could not read configuration file '{}': {}".format(
            GITHUB_CONFIG, exc)
    except (IndexError, KeyError):
        return "Access token not found in configuration file."

    headers = dict(Authorization='token {}'.format(access_token),
                   Accept=API_TYPE)
    url = ENDPOINT.format(path=path, repo=repo, user=user)
    try:
        with requests.get(url, headers=headers, stream=True) as req:
            req.raise_for_status()
            with open(destfn, 'wb') as fp:
                shutil.copyfileobj(req.raw, fp)
    except (requests.HTTPError, OSError) as exc:
        return "Error downloading file: {}".format(exc)


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]) or 0)
