#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import optparse
import os
import sys

class AccountDiff:
    """Print differences between two acount files."""

    name = "accountdiff"
    version = "1.0"
    usage = "%prog file1.ini file2.ini"
    config_filename = "accountmanager.ini"

    def main(self, args=None):
        options, args = self.parse_options(args)

        if len(args) != 2:
            self.optparser.print_help()
            return 2

        db1 = configparser.RawConfigParser()
        db1.optionsxform = str
        db1.read(args[0])
        db2 = configparser.RawConfigParser()
        db2.optionsxform = str
        db2.read(args[1])

        for section in sorted(db2.sections(), key=lambda x: x.upper()):
            if db1.has_section(section):
                self.compare_sections(db1, db2, section)
            else:
                self.print_section(db2, section)

    def parse_options(self, args=None):
        self.optparser = optparse.OptionParser(prog=self.name,
            usage=self.usage, version=self.version, description=self.__doc__)
        self.optparser.add_option('-c', '--config', dest="configpath",
            default=self.config_filename, metavar="PATH",
            help="Path to configuration file (default: %default)")
        self.optparser.add_option("-v", "--verbose",
          action="store_true", default=False, dest="verbose",
          help="Be more verbose.")

        options, args = self.optparser.parse_args(args=args)

        ###try:
            ###self.config = parse_config(options.configpath)
        ###except Exception as exc:
            ###print "Error parsing config: %s" % exc
            ###print "Using default configuration file '%s'." % self.config_filename
            ###self.config = parse_config(self.config_filename)

        return options, args

    def print_section(self, db, section):
        print("[%s]" % section)

        for option in sorted(db.options(section)):
            print("%s: %s" % (option, db.get(section, option)))

        print("")

    def compare_sections(self, db1, db2, section):
        print("[%s]" % section)

        options = list(set(db1.options(section) + db2.options(section)))

        for option in sorted(options):
            if not db1.has_option(section, option):
                print("A %s: %s" % (option, db2.get(section, option)))
            elif not db2.has_option(section, option):
                print("D %s: %s" % (option, db1.get(section, option)))
            elif db1.get(section, option) != db2.get(section, option):
                print("- %s: %s" % (option, db1.get(section, option)))
                print("M %s: %s" % (option, db2.get(section, option)))
            else:
                print("%s: %s" % (option, db1.get(section, option)))

        print("")

if __name__ == '__main__':
    ad = AccountDiff()
    sys.exit(ad.main(sys.argv[1:]) or 0)
