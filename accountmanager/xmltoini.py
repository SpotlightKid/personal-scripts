from xml.etree import ElementTree as ET
d = ET.parse('minimax/tb_pw.xml')
entries = d.find('entries')
for el in entries.findall('entry'):
    print "[%s]" % el.get('host')
    print "url: %s" % el.get('host')
    print "user: %s" % el.get('user')
    print "password: %s" % el.get('password')
    print
