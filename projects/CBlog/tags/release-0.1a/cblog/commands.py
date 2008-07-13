#!/usr/bin/env python

import os
import sys

from os.path import *

import pkg_resources
pkg_resources.require("TurboGears")

import turbogears

def start():
    """Start the CherryPy application server."""

    import cherrypy
    cherrypy.lowercase_api = True

    from cblog.cachecontrol import ExpiresFilter

    curdir = os.getcwd()

    # first look on the command line for a desired config file,
    # if it's not on the command line, then look for setup.py
    # in the current directory. If it's not there, this script is
    # probably installed
    if len(sys.argv) > 1:
        turbogears.update_config(configfile=sys.argv[1],
            modulename="cblog.config")
    elif exists(join(curdir, "setup.py")):
        turbogears.update_config(configfile="dev.cfg",
            modulename="cblog.config")
    else:
        turbogears.update_config(configfile="prod.cfg",
            modulename="cblog.config")

    from cblog.controllers import Root
    root = Root()
    cherrypy.root = root
    cherrypy.root._cp_filters = [ExpiresFilter()]

    turbogears.start_server(root)
