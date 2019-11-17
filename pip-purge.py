#!/usr/bin/env python
"""Uninstall all packages from the current Python virtual environment.

The follwoing packages are excluded, i.e. left installed.

* pip
* pkg-resources
* setuptools
* wheel

"""

from __future__ import print_function

import os
from subprocess import check_call, check_output, CalledProcessError

try:
    input = raw_input
except NameError:
    pass

EXCLUDES = ('setuptools', 'pkg-resources', 'pip', 'wheel', '-e',)


def prompt(msg):
    try:
        resp = input(msg + " (y/N): ")
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    else:
        return resp.lower() in ('y', 'yes')


def excluded(pkg, excludes):
    for exclude in excludes:
        if pkg.startswith(exclude):
            return True


def parse_requirements(requirements, ignore=()):
    """Parse list of Python package requirements and strip off version numbers.

    Returns a set of package names.
    """
    packages = set()
    for line in requirements:
        line = line.strip()
        if line.startswith(('#', '-r', '--')):
            continue
        if '#egg=' in line:
            pkg = line.split('#egg=')[1]
        else:
            pkg = line.split('==')[0]
        if not excluded(pkg, ignore):
            packages.add(pkg)
    return packages


def main(args=None):
    # make sure output of commands is predictable,
    # but keep existing environment (e.g. VIRTUAL_ENV)
    os.environ['LC_ALL'] = 'C'
    # Capture the output of 'pip freeze'.
    try:
        requirements = check_output(['pip', 'freeze'])
    except CalledProcessError as exc:
        return exc.output
    else:
        # XXX: not sure what affects output encoding of pip
        requirements = requirements.decode('utf-8')
        packages = parse_requirements(requirements.splitlines(), EXCLUDES)

    # Alert the user.
    print('Found {0} packages installed:'.format(len(packages)))
    if packages:
        print(", ".join(sorted(packages)))

    if packages and ('-y' in args or prompt("Purge packages?")):
        # Do the de-installing.
        errors = []
        print("Purging...")
        for package in packages:
            try:
                command = ['pip', 'uninstall',  '-y', package]
                check_call(command)
            except CalledProcessError as exc:
                errors.append("'pip uninstall {0}' failed with exit code {1}."
                              .format(package, exc.returncode))

        if errors:
            # Report errors
            return "\n".join(errors)


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]) or 0)
