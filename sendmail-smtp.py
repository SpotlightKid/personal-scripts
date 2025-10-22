#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple command line mailer.

Send text-only email via SMTP with message text read from stdin to all email addresses given as
arguments.

"""

import logging
import sys
import socket
import smtplib

from argparse import ArgumentParser
from email.message import EmailMessage


__program__   = "sendmail-smtp.py"
__author__    = "Christopher Arndt"
__version__   = "0.4"
__copyright__ = "MIT license"

__usage__ = "%(prog)s [OPTIONS] <recipient1> [<recipient2> ...]"

log = logging.getLogger(__program__)
options = dict(
   smtp_host = 'localhost',
   smtp_port = None,
   smtp_user = None,
   smtp_pass = None,
   use_ssl = False,
   start_tls = False,
   sender_addr = None,
   from_addr = None,
)



def send_email(from_addr, to_addrs, msg, host='localhost', port=None, user=None, password=None,
               usessl=False, starttls=False, timeout=10.0, verbose=False):
    """Send the email via SMTP."""
    error = None

    if usessl and not starttls:
        smtp_class = smtplib.SMTP_SSL
        if port is None:
            port = 465
    else:
        smtp_class = smtplib.SMTP
        if port is None:
            port = 587

    if verbose:
        print("SMTP conversation:\n")
        smtp_class.debuglevel = 1

    try:
        connected = False
        log.debug("Creating SMTP client instance (%s).", smtp_class.__name__)
        smtp = smtp_class(host, port, timeout=timeout)
        log.debug("Connection established.")
        connected = True

        if starttls:
            log.debug("Requesting STARTTLS.")
            smtp.starttls()
            log.debug("Sending EHLO.")
            smtp.ehlo()

        if user:
            log.debug("Attempting login with Basic Auth (user: '%s', password: '%s')", user, password)
            smtp.login(user, password)

        log.debug("Sending mail from '%s' to: %s", from_addr, ",".join(to_addrs))
        smtp.sendmail(from_addr, to_addrs, msg.as_string())
    except KeyboardInterrupt:
        print("\nInterrupted.")
    else:
        log.debug("Mail sent.")
    finally:
        if connected:
            log.debug("Closing connection.")
            smtp.quit()


def main(args):
    ap = ArgumentParser(prog=__program__, usage=__usage__, description=__doc__)
    ap.set_defaults(**options)
    ap.add_argument("-s", "--subject", help="The mail subject.")
    ap.add_argument("-f", "--from-addr", help="The from address for the mail headers.")
    ap.add_argument("-e", "--sender-addr", help="The sender address for the envelope.")
    ap.add_argument("-H", "--smtp-host", default='localhost',
                    help="The host name of the SMTP server (default: %(default)s).")
    ap.add_argument("-P", "--smtp-port", type=int,
                    help="The port number of the SMTP server (default: 587).")
    ap.add_argument("-S", "--use-ssl", action="store_true",
                    help="Use SSL for the SMTP connection (default: %(default)s).")
    ap.add_argument("-T", "--start-tls", action="store_true",
                    help="Use STARTTLS for the SMTP connection (default: %(default)s).")
    ap.add_argument("-u", "--smtp-user", help="The user name for the SMTP server.")
    ap.add_argument("-p", "--smtp-pass", help="The password for the SMTP server.")
    ap.add_argument("-v", "--verbose", action="store_true", default=False, help="Be more verbose")
    ap.add_argument("--version", action="version", version=__version__, help="Show version number")
    ap.add_argument("recipients", nargs="*", help="The mail recipient(s)")

    args = ap.parse_args(args=args)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(name)s:%(levelname)s:%(asctime)s: %(message)s")

    if args.recipients:
        try:
            text = sys.stdin.read()
        except KeyboardInterrupt:
            return 0

        if text:
            msg = EmailMessage()
            msg.set_content(text)
            msg['To'] = ', '.join(args.recipients)
            msg['From'] = args.from_addr

            if args.subject:
                msg['Subject'] = args.subject

            if args.smtp_user is None and args.smtp_host:
                import netrc
                try:
                    rc = netrc.netrc()
                    user, dummy, passwd = rc.authenticators(args.smtp_host)
                except (IOError, TypeError, netrc.NetrcParseError):
                    pass
                else:
                    args.smtp_user = user
                    args.smtp_pass = passwd

            if args.verbose:
                print("This is the raw message that will be sent:\n")
                print(msg.as_string())
            try:
                send_email(args.sender_addr or args.from_addr, args.recipients, msg,
                           host=args.smtp_host, port=args.smtp_port, user=args.smtp_user,
                           password=args.smtp_pass, usessl=args.use_ssl, starttls=args.start_tls,
                           verbose=args.verbose)
            except smtplib.SMTPException as exc:
                print("An error occured while sending the email via SMTP:", file=sys.stderr)
                print(exc, file=sys.stderr)
                return 1
    else:
        ap.print_help()
        return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
