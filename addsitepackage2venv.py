#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Make a Python module or package installed in one of the system-wide
site-packages directories available to the currently active virtual environment
by sym-linking it into the virtualenv's site-packages directory.

"""


__author__ = "Christopher Arndt"
__version__ = "0.2 ($Rev$)"
__license__ = "MIT License"
__usage__ = "Usage: addsitepackage2venv <package>"

import argparse
import distutils.sysconfig
import os
import site
import sys

from os.path import basename, exists, isdir, islink, join


MODULE_EXTENSIONS = ['', '.py', '.pyc', '.pyo']

if sys.platform.startswith('win'):
    MODULE_EXTENSIONS += ['.dll', '.pyd']
else:
    MODULE_EXTENSIONS += ['.so']


def main(args=None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--force',
        action="store_true", help="Overwrite existing symlinks")
    argparser.add_argument('-v', '--verbose',
        action="store_true", help="Be more verbose")
    argparser.add_argument('package',
        help="Name of system package to add to virtual environment.")

    args = argparser.parse_args(args if args is not None else sys.argv[1:])

    venv = os.environ.get('VIRTUAL_ENV')

    if not venv:
        argparser.print_help()
        print("No virtual environment active.")
        return 1
    else:
        venvsitedir = distutils.sysconfig.get_python_lib()

    if not exists(join(venvsitedir, 'no-global-site-packages.txt')):
        print("This virtual environment includes system site-packages. "
            "Nothing to do.")
        return 1

    venvpackage = join(venvsitedir, args.package)

    for ext in MODULE_EXTENSIONS:
        venvmodule = venvpackage + ext

        if ((ext == '' and exists(join(venvpackage, '__init__.py'))) or
                exists(venvmodule)):
            print("Package %s is already in installed in '%s' as '%s'." %
                (args.package, venvsitedir, basename(venvpackage + ext)))

            if islink(venvpackage + ext):
                print("Symlinks to: %s" % os.readlink(venvpackage + ext))

            if not args.force:
                return 1

    site.virtual_addsitepackages(set(sys.path))

    for sitedir in sys.path:
        if not sitedir or not isdir(sitedir) or sitedir.startswith(venv):
            continue

        if args.verbose:
            print("Checking directory '%s'..." % sitedir)

        pkgdir = join(sitedir, args.package)

        found = False
        for ext in MODULE_EXTENSIONS:
            module = pkgdir + ext

            if ((ext == '' and exists(join(pkgdir, '__init__.py'))) or
                    exists(module)):
                try:
                    os.symlink(module, venvpackage + ext)
                    print("Created symlink: %s -> %s" %
                        (module, venvpackage + ext))
                except (IOError, OSError) as exc:
                    print("Could not create symlink %s -> %s: %s" %
                        (module, venvpackage + ext, exc))
                found = True

        if found:
            break

    else:
        print("No package '%s' found in site-packages directories." %
            args.package)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
