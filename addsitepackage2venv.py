#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Make one ore more Python modules or packages installed in one of the
system-wide site-packages directories available in the currently active
virtual environment by sym-linking it into the virtualenv's site-packages
directory.

"""


__author__ = "Christopher Arndt"
__version__ = "0.3 ($Rev$)"
__license__ = "MIT License"
__usage__ = "Usage: addsitepackage2venv <package>"

import argparse
import distutils.sysconfig
import logging
import glob
import os
import site
import sys

from os.path import basename, dirname, exists, isdir, islink, join

log = logging.getLogger("addsitepackage2venv")
MODULE_EXTENSIONS = ['', '.pth', '.py', '.pyc', '.pyo']

if sys.platform.startswith('win'):
    MODULE_EXTENSIONS += ['.dll', '.pyd', '.pyw']
else:
    MODULE_EXTENSIONS += ['.so']


def main(args=None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--force',
        action="store_true", help="Overwrite existing symlinks")
    argparser.add_argument('-q', '--quiet',
        action="store_true", help="Only print errors")
    argparser.add_argument('-v', '--verbose',
        action="store_true", help="Be more verbose")
    argparser.add_argument('packages', nargs='+',
        help="Name(s) of system package(s) to add to virtual environment.")

    args = argparser.parse_args(args if args is not None else sys.argv[1:])

    if args.quiet:
        loglevel = logging.ERROR
    elif args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(level=loglevel, format="%(message)s")
    venv = os.environ.get('VIRTUAL_ENV')

    if not venv:
        argparser.print_help()
        log.error("No virtual environment active.")
        return 1
    else:
        venvsitedir = distutils.sysconfig.get_python_lib()

    if not exists(join(dirname(venvsitedir), 'no-global-site-packages.txt')):
        log.info("This virtual environment includes system site-packages. "
                 "Nothing to do.")
        return 1

    for package in args.packages:
        venvpackage = join(venvsitedir, package)

        for ext in MODULE_EXTENSIONS:
            venvmodule = venvpackage + ext

            if ((ext == '' and glob.glob(join(venvpackage, '__init__.py*'))) or
                    exists(venvmodule)):
                log.info("Package %s is already present in '%s' as '%s'." %
                         (package, venvsitedir, basename(venvmodule)))

                if islink(venvmodule):
                    log.info("Symlinks to: %s" % os.readlink(venvmodule))

                if not args.force:
                    return 1

    site.virtual_addsitepackages(set(sys.path))

    for package in args.packages:
        venvpackage = join(venvsitedir, package)

        log.debug("Checking for package '%s'..." % package)

        for sitedir in sys.path:
            if (not sitedir or not isdir(sitedir) or sitedir.startswith(venv)
                    or sitedir == dirname(sys.argv[0])):
                continue

            log.debug("Checking directory '%s'..." % sitedir)

            pkgdir = join(sitedir, package)

            found = False
            for ext in MODULE_EXTENSIONS:
                module = pkgdir + ext

                if ((ext == '' and glob.glob(join(pkgdir, '__init__.py*'))) or
                        exists(module)):
                    try:
                        if exists(venvpackage + ext) and args.force:
                            os.unlink(venvpackage + ext)

                        os.symlink(module, venvpackage + ext)
                        log.info("Created symlink: %s -> %s" %
                                 (module, venvpackage + ext))
                    except (IOError, OSError) as exc:
                        log.error("Could not create symlink %s -> %s: %s" %
                                  (module, venvpackage + ext, exc))
                    found = True

            if found:
                break

        else:
            log.error("No package '%s' found in site-packages directories." %
                      package)
            return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
