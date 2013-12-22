#!/usr/bin/env python

import sys
from xml.dom.minidom import parse

d = parse(sys.argv[1])
sys.stdout.write(d.toprettyxml(indent="  ", encoding="utf-8"))
