#!/usr/bin/env python
"""Check latest version of a project listed on PyPI."""

import argparse
import sys

import requests


def get_project_json(project):
    url = "https://pypi.org/pypi/{}/json"
    with requests.get(url.format(project)) as resp:
        resp.raise_for_status()
        return resp.json()


def main(args=None):
    ap = argparse.ArgumentParser(usage=__doc__.splitlines()[0])
    ap.add_argument('-v', '--verbose', action="store_true", help="Be more verbose.")
    ap.add_argument('project', help="name of project on PyPI to check.")
    args = ap.parse_args(args)

    try:
        pypi_data = get_project_json(args.project)
    except Exception as exc:
        return f"Could not retrieve info for project '{args.project}' from PyPI: {exc}"
    else:
        info = pypi_data["info"]
        print(f"Project: {info['name']}")
        print(f"Summary: {info['summary']}")
        print(f"Latest version: {info['version']}")


if __name__ == '__main__':
    sys.exit(main() or 0)
