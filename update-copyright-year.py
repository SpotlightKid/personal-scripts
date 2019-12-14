#!/usr/bin/env python
"""
Update copyright year in git controlled files to year of their last commit.
"""

import argparse
import re
import sys
from functools import partial
from operator import itemgetter
from subprocess import check_output

from dateutil.parser import parse
from binaryornot.check import is_binary


# Important: using re.VERBOSE, don't use '\' to escape end of line
COPYRIGHT_PTN = re.compile(
    r"""
    (?P<copyright>copyright\s*)
    (?P<marker>\s*(\(c\)|©)\s*)?
    (?P<year1>\d\d\d\d)
    ((?P<dash>\s*-\s*)(?P<year2>\d\d\d\d))?
    """,
    re.IGNORECASE | re.VERBOSE)


def replace_year(year, match):
    """Replace year in regex match.

    :param year: year that is substituted
    :type year: str
    :param match: regex match with groups for for 'copyright', 'marker',
        'year1' and 'year2'
    :type match: re.Match
    :return: replacement string
    :rtype: str

    """
    subst = match.groupdict(default='')

    if subst['year2'] or subst['year1'] != str(year):
        if not subst.get('dash', '').strip():
            subst['dash'] = '-'

        subst['year2'] = str(year)
        return "{copyright}{marker}{year1}{dash}{year2}".format(**subst)
    else:
        subst['year1'] = str(year)
        return "{copyright}{marker}{year1}".format(**subst)


def filter_excluded(files, excluded, getter=None):
    return (item for item in files
            if (item if getter is None else getter(item)) not in excluded)


def main(args=None):
    """Main program entry point,

    :param args: list of string command line arguments
    :type args: list[str]
    :return: program exit code or error string
    :rtype: int|str

    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('-e', '--exclude', metavar='PATH', action='append',
                    help="Exclude given path or filename (can be given more than once)")
    ap.add_argument('-v', '--verbose', action='store_true',
                    help="Report which files are processed and updatzed to stdout")
    ap.add_argument('files', nargs='*',
                    help="Only process given files (default: all versioned files)")

    args = ap.parse_args(args)

    def report(msg):
        if args.verbose:
            print(msg)

    git_files = []
    for path in check_output(['git', 'ls-files'] + args.files).decode().splitlines():
        date = parse(check_output(
            ['git', '--no-pager', 'log', '-1', '--date=iso', '--pretty=format:%ai', '--', path]
        ).decode())
        git_files.append((date, path))

    for date, path in filter_excluded(git_files, args.exclude or [], itemgetter(1)):
        if is_binary(path):
            report("Ignoring binary file '%s'." % path)
            continue

        repl_func = partial(replace_year, date.year)
        try:
            with open(path) as fp:
                file_contents = fp.read()
        except OSError as exc:
            print("Could not read file '%s': %s" % (path, exc), file=sys.stderr)

        match = COPYRIGHT_PTN.search(file_contents)
        if match:
            new_contents, num_subst = COPYRIGHT_PTN.subn(repl_func, file_contents)

            if num_subst > 0 and file_contents.strip() != new_contents.strip():
                report("Updating copyright year in '%s' to %s." % (path, date.year))

                try:
                    with open(path, 'w') as fp:
                        fp.write(new_contents)
                except OSError as exc:
                    print("Could not update file '%s': %s" % (path, exc), file=sys.stderr)
            else:
                report("Copyright statements(s) in '%s' already up to date." % path)
        else:
            report("No copyright statement found in '%s'." % path)


if __name__ == '__main__':
    sys.exit(main() or 0)
