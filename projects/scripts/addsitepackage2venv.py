#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Make a Python package installed in one of the system-wide site-packages
directories available to the currently active virtual environment by
sym-linking it into its site-packages directory."""

import sys
import os

from os.path import exists, islink, join

__usage__ = "addsitepackage2venv <package>"

venv = os.environ.get('VIRTUAL_ENV')

if not venv:
    print __usage__
    print "No virtualenv active."
    sys.exit(1)
else:
    venvsitedir = join(venv, 'lib', 'python%i.%i' % sys.version_info[:2],
        'site-packages')

if len(sys.argv) > 1:
    pkg = sys.argv[1]
    pkgsitedir = os.path.join(venvsitedir, pkg)
else:
    print __usage__
    sys.exit(2)

if exists(pkgsitedir):
    print "Package %s is already in installed in %s" % (pkg, venvsitedir)
    if islink(pkgsitedir):
        print "Symlinks to: %s" % os.readlink(pkgsitedir)
    sys.exit(1)

for sitedir in sys.path:
    pkgdir = join(sitedir, pkg)

    if sitedir.startswith(venv):
        continue

    if exists(pkgdir):
        try:
            os.symlink(pkgdir, pkgsitedir)
            print "Created symlink %s -> %s." % (pkgdir, pkgsitedir)
        except (IOError, OSError), exc:
            print "Could not created symlink %s -> %s: %s" % (
                pkgdir, pkgsitedir, exc)
        break
else:
    print "No package '%s' found in site-packages directories." % pkg
    sys.exit(1)
