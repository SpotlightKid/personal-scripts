#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# runpy_venv.py
#
"""Run Python interpreter from virtualenv associated with file or directory
given as first command line argument.

An associated virtualenv is one, where the given directory, or directory
containig the given file, or any of its parent directories is set as its
project directory.

Remaining arguments are passed to the Python interpreter.

"""

from __future__ import print_function

import os
import subprocess
import sys

from os.path import abspath, dirname, exists, expanduser, isdir, isfile, join

workon_home = os.environ.get('WORKON_HOME', expanduser('~/lib/virtualenvs'))
project_home = os.environ.get('PROJECT_HOME', expanduser('~/projects'))
venv_bindir = 'scripts' if sys.platform.startswith('win') else 'bin'
python_bin = 'python'


def get_project_dir(venv):
    """Return project dir for given virtualenv directory.

    If no project is set or it cannot be read, return None.

    """
    try:
        with open(join(venv, '.project')) as f:
            return f.read().strip()
    except (IOError, OSError):
        return None

args = sys.argv[1:]

if not args or not args[0].strip():
    print("Usage: runpy_venv <DIR or FILE> [args...]")
    sys.exit(2)
else:
    working_dir = abspath(args.pop(0))

    if not exists(working_dir):
        print("File or directory does not exist: %s" % working_dir)
        sys.exit(1)
    elif isfile(working_dir):
        working_dir = dirname(working_dir)

# compile dict of all venvs with a project dir set,
# mapping project dir to python binary
project_dirs = {}
if isdir(workon_home):
    for venv in os.listdir(workon_home):
        python_bin = join(workon_home, venv, venv_bindir, 'python')

        if isfile(python_bin):
            project_dir = get_project_dir(join(workon_home, venv))

            if project_dir:
                project_dirs[project_dir] = python_bin

if project_dirs:
    while True:
        if working_dir in project_dirs:
            python_bin = project_dirs[working_dir]
            break
        elif working_dir:
            working_dir = dirname(working_dir)

        if not working_dir or working_dir == '/':
            break

#print("Exec: %s" % " ".join([python_bin] + args))
sys.exit(subprocess.call([python_bin] + args))
