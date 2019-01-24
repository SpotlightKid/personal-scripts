#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert a Thunderbird password export XML file into an INI style file for accountdb.py."""

import sys
from xml.etree import ElementTree as ET

if len(sys.argv) > 1:
    infile = sys.argv[0]
else:
    infile = 'tb_pw.xml'

d = ET.parse(infile)
entries = d.find('entries')

for el in entries.findall('entry'):
    print("[%s]" % el.get('host'))
    print("url: %s" % el.get('host'))
    print("user: %s" % el.get('user'))
    print("password: %s" % el.get('password'))
    print('')
