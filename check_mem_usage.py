#!/usr/bin/env python
"""Print a list of processes of current user with memory usage and total."""

__program__   = "check_mem_usage"
__author__    = "Christopher Arndt"
__version__   = "0.1"
__date__      = "2007-11-18"
__copyright__ = "MIT license"


import os
import re
import sys
import time


from subprocess import Popen, PIPE

def main(args):
    print "Date/Time: %s" % time.asctime()
    print
    #output = Popen(["ps", "-u", os.environ['LOGNAME'], "-o", "pid,rss,args"],
    output = Popen(["ps", "-A", "-o", "pid,rss,args"],
        stdout=PIPE).communicate()[0]
    total_mem = 0

    print "%5s %7s %7s %s" % ('PID', 'RSS', 'RSS (Mb)', 'Command')
    for line in output.split('\n')[1:]:
        line = line.strip()
        if not line: continue
        pid, mem, cmd = re.split(r'\s+', line, 2)
        mem = int(mem)
        total_mem += mem
        print "%5s %7d %5.2f Mb %s" % (pid, mem, mem/1024., cmd[:55])
    print
    print "Total memory usage: %5.2f Mb" % (total_mem/1024.,)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
