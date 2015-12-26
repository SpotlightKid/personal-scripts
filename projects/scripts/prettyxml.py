#!/usr/bin/env python

from __future__ import print_function

import sys
from xml.dom.minidom import parse

d = parse(sys.argv[1])
print(d.toprettyxml(indent="  ", encoding="utf-8").decode('utf-8'))
