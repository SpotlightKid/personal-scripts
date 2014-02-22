#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import optparse
import os
import sys


def warn(msg, *args):
    sys.stderr.write((msg % args) + '\n')

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

        sections = list(set(db1.sections() + db2.sections()))

        for section in sorted(sections, key=lambda x: x.upper()):
            if db1.has_section(section) and not db2.has_section(section):
                warn("Section '%s' exists only in file 1.", section)
                self.print_section(db1, section)
            elif db2.has_section(section) and not db1.has_section(section):
                warn("Section '%s' exists only in file 2.", section)
                self.print_section(db2, section)
            else:
                warn("Section '%s' exists in file 1 and 2.", section)
                if self.compare_sections(db1, db2, section):
                    warn("Options in section '%s' differ bewteen file 1 and 2."
                        , section)


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

        db1_options = db1.options(section)
        db2_options = db2.options(section)
        options = list(set(db2_options + db2_options))
        diff = True

        for option in sorted(options):
            if not db1.has_option(section, option):
                value = db2.get(section, option).replace('\n', ' ')
                print("A %s: %s" % (option, value))
            elif not db2.has_option(section, option):
                value = db1.get(section, option).replace('\n', ' ')
                print("D %s: %s" % (option, value))
            elif db1.get(section, option) != db2.get(section, option):
                value = db1.get(section, option).replace('\n', ' ')
                print("- %s: %s" % (option, value))
                value = db2.get(section, option).replace('\n', ' ')
                print("M %s: %s" % (option, value))
            else:
                value = db1.get(section, option).replace('\n', ' ')
                print("%s: %s" % (option, value))
                diff = False

        print("")
        return diff

if __name__ == '__main__':
    ad = AccountDiff()
    sys.exit(ad.main(sys.argv[1:]) or 0)
