#!/usr/bin/python
"""Manages an encrypted database holding arbitrary key/value pairs.

Useful for storing account information such as usernames, password, email etc.
"""

__all__ = ['AccountDB', 'db', 'Error']

__script__ = 'accountdb.py'
__version__ = "1.0.1"
__date__ = '2003-09-28'
__license__ = 'GPL'
__author__ = "Christopher Arndt <chris.arndt@web.de>"
__usage__ = """%(__script__)s [OPTIONS] ACTION [ACCOUNTNAME] [FIELDNAME=VALUE ...]
where ACTION is one of: view, edit, delete, dump or list
Version: %(__version__)s
Options:
    -h | --help         show this help
    -d | --database     set filename of account database [~/.accountdb]
    -p | --password     set password for database access
    -c | --create       create new database
"""

import getopt, os, sys, UserDict, zlib
from cPickle import loads, dumps
from getpass import getpass

try:
    from Crypto.Cipher import Blowfish
except ImportError:
    msg = "This %s needs the package 'pycrypto'.\n" + \
      "You can get it at: http://www.amk.ca/python/code/crypto.html"
    if __name__ == '__main__':
        sys.stderr.write(msg % 'script' + '\n')
        sys.exit(1)
    else:
        raise ImportError, msg % 'module'


def _usage(d = vars()):
    sys.stderr.write(__usage__ % d)

def printDict(d, sep=': '):
    s = []
    for i in d.items():
        s.append("%s%s%s" % (i[0], sep, i[1]))
    return "\n".join(s)

def get_homedir():
    return os.environ.get('HOME', os.curdir)

class Error(Exception):
    pass


class AccountDB(UserDict.UserDict):

    def __init__(self, fn=None, key=None):
        if not fn:
            self.fn = db
        else:
            self.fn = fn
        self.key = key
        if self.key != None:
            self.load()
        else:
            self.data = {}

    def load(self):
        if not self.key: raise Error, "Passphrase must not be empty"
        try:
            fo = open(self.fn, 'rb')
        except IOError, x:
            raise Error, "Error loading account database: " + str(x)
        else:
            c = Blowfish.new(self.key)
            dz = c.decrypt(fo.read())
            try:
                try:
                    dp = zlib.decompress(dz)
                except zlib.error, x:
                    raise Error, "Decryption of account database failed: " + str(x)
            finally:
                fo.close()
            self.data = loads(dp)

    def save(self):
        if not self.key: raise Error, "Passphrase must not be empty"
        try:
            if os.path.exists(self.fn):
                os.rename(self.fn, self.fn + '.bak')
            fo = open(self.fn, 'wb')
        except Exception, x:
            raise Error, "Error opening account database for saving: " + str(x)
        else:
            try:
                try:
                    c = Blowfish.new(self.key)
                    dpc = zlib.compress(dumps(self.data, 1))
                    padding = '\0' * (Blowfish.block_size - (len(dpc) % \
                      Blowfish.block_size))
                    dpc = dpc + padding
                    fo.write(c.encrypt(dpc))
                except Exception, x:
                    raise Error, "Encryption of account database failed: " + \
                      str(x)
            finally:
                fo.close()

    def get_account(self, account, fields=[]):
        if fields:
            d = {}
            for i in self[account].keys():
                if i in fields:
                    d[i] = self[account][i]
            return d
        else:
            return self[account]

    def add_account(self, account, **kw):
        if self.has_key(account):
            self[account].update(kw)
        else:
            self[account] = kw

    def list_accounts(self):
        l = self.keys()
        l.sort(lambda x,y: cmp(x.lower(), y.lower()))
        return l

def create_db(db, password):
    if not os.path.exists(db):
        a = AccountDB(fn=db, key=password)
        try:
            a.save()
        except Error, msg:
            sys.stderr.write(str(msg) + '\n')
    else:
        sys.stderr.write("Database '%s' already exists.\n" % db)

def _main(argv):

    action = None
    actions = ['view', 'edit', 'delete', 'list', 'dump']
    key = ''
    options = {
        'db': os.path.join(get_homedir(), '.accountdb'),
        'password': None,
        'create': False
    }

    try:
        opts, args = getopt.getopt(argv, 'hcd:p:',
          ['help', 'password=', 'database='])
    except getopt.GetoptError, x:
        sys.stderr.write(str(x) + \
          "\ntype '%s --help' for usage information.\n" % __script__)
        sys.exit(1)

    for o, a in opts:
        if o in ['-p', '--password']:
            options['password'] = a
        elif o in ['-d', '--database']:
            options['db'] = a
        elif o in ['-h', '--help']:
            _usage()
            sys.exit(0)
        elif o in ['-c', '--create']:
            options['create'] = True
    try:
        action = args.pop(0)
        if action == 'view':
            accounts = args
        elif action not in ('dump', 'list'):
            account = args.pop(0)
    except IndexError, msg:
        sys.stderr.write(str(msg) + '\n')
        _usage()
        sys.exit(1)
    fields = args

    if options.get('password') is None:
        options['password'] = getpass()

    if action in actions:
        try:
            if options.get('create'):
                create_db(options['db'], options['password'])
            a = AccountDB(fn=options['db'], key=options['password'])
        except (Error, KeyboardInterrupt), x:
            sys.stderr.write('Error: ' + str(x) + '\n')
            sys.exit(1)

        if action == 'edit':
            d = {}
            for i in fields:
                k, v = i.split('=', 1)
                d[k] = v
            apply(a.add_account, [account], d)
            try:
                a.save()
            except Error, msg:
                sys.stderr.write(str(msg) + '\n')
        elif action == 'delete':
            if a.has_key(account):
                del a[account]
                try:
                    a.save()
                except Error, msg:
                    sys.stderr.write(str(msg) + '\n')
            else:
                sys.stderr.write("Account '%s' does not exist.\n" % account)
        elif action == 'list':
            print "\n".join(a.list_accounts())
        elif action == 'view':
            for account in accounts:
                if a.has_key(account):
                    print printDict(a.get_account(account, fields))
                    print
                else:
                    sys.stderr.write("Account '%s' does not exist.\n" % account)
        elif action == 'dump':
            print repr(a.data)
    else:
        sys.stderr.write("'%s' is not a valid action.\n" % action)
        _usage()
        sys.exit(1)

if __name__ == '__main__':
    _main(sys.argv[1:])
