#!/usr/bin/env python
"""Search Dash/Zeal-compatible docset(s) for given search term."""

import argparse
import os
import pathlib
import plistlib
import sqlite3

IDX_PATH = pathlib.PurePath("Contents", "Resources", "docSet.dsidx")
DOC_PATH = pathlib.PurePath("Contents", "Resources", "Documents")
EXACT_SEARCH_SQL = """\
SELECT name, path
    FROM searchIndex
    WHERE name = ?
    COLLATE UNICODE_NOCASE
    LIMIT {limit:d};
"""
LIKE_SEARCH_SQL = """\
SELECT name, path
    FROM searchIndex
    WHERE name LIKE ? ESCAPE '\\'
    COLLATE UNICODE_NOCASE
    LIMIT {limit:d};
"""


def get_docsets_dir():
    docsets_dir = os.getenv("DASH_DOCSETS_PATH")

    if not docsets_dir:
        data_home = pathlib.Path(os.getenv("XDG_DATA_HOME", pathlib.Path.home() / '.local' / 'share'))
        docsets_dir = data_home / "Zeal" / "Zeal" / "docsets"

    return docsets_dir


def get_docset_indices(name=None):
    result = []
    for p in get_docsets_dir().iterdir():
        if p.is_dir() and p.suffix == ".docset":
            if name:
                info_path = p / "Contents" / "Info.plist"
                with open(info_path, "rb") as fp:
                    info = plistlib.load(fp)

                if not info.get("CFBundleIdentifier") == name.lower():
                    continue

            result.append((p / IDX_PATH, p / DOC_PATH))

    return sorted(result)


def get_docset_index(name):
    return get_docsets_dir() / (name + ".docset") / IDX_PATH


# Custom collation, maybe it is more efficient to store strings
def unicode_nocase_collation(a: str, b: str):
    if a.casefold() == b.casefold():
        return 0
    if a.casefold() < b.casefold():
        return -1
    return 1


def main(args=None):
    ap = argparse.ArgumentParser(usage=__doc__.splitlines()[0])
    ap.add_argument("-l", "--limit", type=int, default=10, metavar="INT",
        help="Set maximum number of search results (default: %(default)i)")
    ap.add_argument("searchphrase", help="Phrase to search for. You can prefix the docset to search in separated by a colon, e.g. 'js:alert'")

    args = ap.parse_args(args)

    try:
        prefix, search = (x.strip() for x in args.searchphrase.split(":", 1))
    except (TypeError, ValueError):
        search = args.searchphrase.strip()
        prefix = None

    indices = get_docset_indices(prefix)
    search = search.replace("\\", r"\\\\")
    search = search.replace("%", "\\%")
    search = search.replace("_", "\\_")
    search = "%" + search + "%"

    for index, docroot in indices:
        with sqlite3.connect(index) as cnx:
            cnx.create_collation("UNICODE_NOCASE", unicode_nocase_collation)
            cur = cnx.cursor()
            cur.execute(EXACT_SEARCH_SQL.format(limit=args.limit), (search,))
            results = {name: path for name,path in cur.fetchall()}
            num_results = len(results)

            if num_results < args.limit:
                cur.execute(LIKE_SEARCH_SQL.format(limit=args.limit), (search,))

                for i, (name, path) in enumerate(cur.fetchall()):
                    if name not in results:
                        results[name] = path

                    if num_results + i + 1 >= args.limit:
                        break

        for i, name in enumerate(results):
            file = path.split("#", 1)[0] if '#' in path else path
            print(f"{i+1} - {name}: {file}")


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)
