#!/usr/bin/env python

import os
import sys
import subprocess

CHECK_COMMAND = "ping -q -n -c 3 -w 3 %(hostname)s"

def error(msg, *args):
    sys.stderr.write((msg % args) + '\n')

def main(args=None):
    try:
        hostname = args.pop(0)
    except:
        error("Usage: check_host <hostname>")
        return 2

    try:
        cmd = (CHECK_COMMAND % {"hostname": hostname}).split()
        # we don't use a with statement here to stay Python 2.5 compatible
        fnull = open(os.devnull, "w")
        subprocess.check_call(cmd, stdout=fnull, stderr=fnull)
    except subprocess.CalledProcessError:
        error("Host '%s' did not respond to PING.", hostname)
        return 1
    finally:
        fnull.close()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
