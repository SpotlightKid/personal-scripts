/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pretty print an XML file."""

from __future__ import print_function

import sys
from xml.dom.minidom import parse

d = parse(sys.argv[1])
print(d.toprettyxml(indent="  ", encoding="utf-8").decode('utf-8'))
