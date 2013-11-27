#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# htpasswd.py
#
"""A Python re-implementation of the Apache htpasswd utility.

    htpasswd.py -h
    htpasswd.py [-c|n] [-b] [-d|m|s] filename username [password]
    htpasswd.py -nc [-b] [-d|m|s] username [password]
    htpasswd.py -D [-n] filename username

"""

__author__ = "Christopher Arndt"
__version__ = "1.0 ($Rev$)"
__license__ = "MIT License"

import argparse
import getpass
import os
import sys
import random

from collections import OrderedDict

# Try to import passlib for Apache-compatible MD5 and SHA password hashing
try:
    from passlib.hash import apr_md5_crypt, ldap_sha1
    passlib = True
except ImportError:
    passlib = False

# Try to import different versions of crypt function
try:
    from crypt import crypt
except ImportError:
    try:
        from fcrypt import crypt
    except ImportError:
        if passlib:
            from passlib.hash import des_crypt
            crypt = des_crypt.encrypt
        else:
            crypt = None

def make_salt(length=2):
    """Return string of random letters of given length."""
    letters = ('abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789/.')
    return "".join([random.choice(letters) for i in range(length)])

def crypt_passwd(password, salt=None):
    """Hash password with crypt(1) function."""
    return crypt(password, salt or make_salt())


class HtpasswdFile(OrderedDict):
    """Create, read, update and write htpasswd files.

    Sub-classes ``collections.OrderedDict``, so users and pasword hashes can
    be accessed in a dictionary-like fashion, but order of entries is retained.

    """
    def __init__(self, filename, create=False):
        super(HtpasswdFile, self).__init__()
        self.filename = filename

        if not create:
            if os.path.exists(self.filename):
                self.read()
            else:
                raise IOError("File '%s' does not exist." % self.filename)

    @property
    def users(self):
        """Return list of usernames."""
        return self.keys()

    def get_hash(self, username, default=None):
        """Return password hash for given username or default value."""
        return self.get(username, default)

    def read(self, filename=None):
        """Read htpasswd file into memory.

        If filename is given, read this file instead and set filename attribute
        to it.

        """
        if filename:
            self.filename = filename

        self.clear()

        with open(self.filename, 'r') as htpasswd:
            for line in htpasswd:
                username, pwhash = line.split(':', 1)
                self[username.strip()] = pwwhash.strip()

    def save(self, filename=None):
        """Write htpasswd to file given by filename argument or attribute."""
        with open(filename or self.filename, 'w') as htpasswd:
            htpasswd.write(self.__str__())

    def set_password(self, username, password, hashfunc=crypt_passwd):
        """Set password for the given username, or add entry if new."""
        self[username] = hashfunc(password)

    def delete(self, username):
        """Remove the entry for the given username."""
        del self[username]

    def __str__(self):
        """Return formatted htpasswd file as a string."""
        return "".join("%s:%s\n" % entry for entry in self.items())


def main(args=None):
    """Command line interface compatible with original htpasswd utility.

    Pass options and positional arguments as a list of strings.

    """
    doclines = __doc__.splitlines()
    usage = "\n".join(doclines[1:])
    parser = argparse.ArgumentParser(description=doclines[0], usage=usage)
    parser.add_argument('-c', action='store_true', dest='create',
        help='Create a new htpasswd file, overwriting any existing file.')
    parser.add_argument('-b', action='store_true', dest='batch',
        help='Use password from the command line rather than prompting for it.')
    parser.add_argument('-d', action='store_true', dest='crypt',
        help='Use CRYPT encryption of the password%s.' % (
        ' (default)' if not passlib else ''))
    parser.add_argument('-D', action='store_true', dest='delete_user',
        help='Delete the specified user from the htpasswd file.')
    parser.add_argument('-n', action='store_true', dest='display',
        help="Don't create or update file; display results on stdout.")
    parser.add_argument('filename', help='Path to htpasswd file.')
    parser.add_argument('username', nargs='?', default=None)
    parser.add_argument('password', nargs='?', default=None)

    if passlib:
        # If passlib is available
        parser.add_argument('-m', action='store_true', dest='md5',
            help='Use MD5 encryption of the password (default).')
        parser.add_argument('-s', action='store_true', dest='sha1',
            help='Use SHA-1 encryption of the password.')

    args = parser.parse_args(args if args is not None else sys.argv[1:])

    def syntax_error(msg):
        """Display error messages with usage help on standard error output."""
        sys.stderr.write("Syntax error: " + msg)
        sys.stderr.write(parser.format_help())

    if args.display and args.create:
        if args.password:
            syntax_error("Display mode combined with '-c' (create) takes at "
                "most two arguments.\n")
            return 2
        else:
            # re-assign arguments
            args.password = args.username
            args.username = args.filename
            args.filename = None

    if args.delete_user and args.password:
        syntax_error("Superfluous password argument in delete mode.\n")
        return 2

    if passlib:
        if args.crypt:
            hashfunc = crypt_passwd
        elif args.sha1:
            hashfunc = ldap_sha1.encrypt
        else:
            hashfunc = apr_md5_crypt.encrypt
    else:
        hashfunc = crypt_passwd

    try:
        passwdfile = HtpasswdFile(args.filename, create=args.create)
    except (IOError, OSError) as exc:
        sys.stderr.write(str(exc) + '\n')
        return 1

    if args.password and not args.batch:
        syntax_error("Superfluous password argument (use '-b' option).\n")
        return 2
    elif not args.batch:
        try:
            args.password = getpass.getpass('New password: ')
            pw2 = getpass.getpass('Re-type new password: ')

            if args.password != pw2:
                sys.stderr.write("Password mismatch.")
                return 1
        except (KeyboardInterrupt, EOFError):
            return 1

    if args.delete_user:
        passwdfile.delete(args.username)
    else:
        if not args.password:
            syntax_error("Missing password argument.\n")
            return 2
        else:
            passwdfile.set_password(args.username, args.password, hashfunc)

    if args.display:
        print(passwdfile)
    else:
        passwdfile.save()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
