#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# prettyplist.py
#
"""Pretty print the contents of a Apple (binary or plain) property list file."""

import sys
from pprint import pprint
from biplist import readPlist

plist = readPlist(sys.argv[1])
pprint(plist)
