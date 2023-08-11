#!/usr/bin/env python
#
# rofi_timer.py
#
# Requires:
#
# * rofi
# * at
# * python-pytimeparse
#
# Copyright (c) 2023 Christopher Arndt <chris@chrisarndt.de>
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Run custom notification timers from a rofi menu."""

import os
from enum import IntEnum
from os.path import expanduser, join
from subprocess import run

from pytimeparse import parse as timeparse


class Command(IntEnum):
    RunTimer = 0
    DeleteEntry = 10


ENCODING = "UTF-8"
KEYBINDINGS = {
    Command.RunTimer: ("Run Timer", "Return"),
    Command.DeleteEntry: ("Delete Entry", "Ctrl-Return"),
}
ROFI_SELECT_CMD = [
    "rofi",
    "-dmenu",
    "-kb-accept-alt",
    "",
    "-kb-accept-custom",
    "",
    "-kb-accept-custom-alt",
    "",
    "-kb-remove-to-sol",
    "",
    "-i",
    "-p",
    "Timer",
    "-normal-window",
]


def parse_timer(timer):
    if ":" in timer:
        interval, comment = [x.strip() for x in timer.split(":", 1)]
    else:
        interval = timer
        comment = ""

    return interval, comment


def format_history_entry(interval, comment):
    comment = comment.replace("\n", r"\n")
    comment = comment.replace("\r", r"\r")
    return f"{interval}: {comment}\n"


def read_history(fn):
    history = []
    try:
        with open(fn) as fp:
            for line in fp.readlines():
                if line.strip():
                    interval, comment = parse_timer(line)
                    comment = comment.replace(r"\n", "\n")
                    comment = comment.replace(r"\r", "\r")
                    history.append((interval, comment))
    except (IOError, OSError):
        pass

    return reversed(history)


def add_history_entry(fn, interval, comment):
    entry = format_history_entry(interval, comment)

    try:
        with open(fn, "r+") as fp:
            for line in fp.readlines():
                if line == entry:
                    break
            else:
                fp.write(entry)
    except (IOError, OSError):
        pass


def delete_history_entry(fn, timer):
    interval, comment = parse_timer(timer)
    entry = format_history_entry(interval, comment)

    try:
        with open(fn, "r") as fp:
            lines = [line for line in fp.readlines() if line != entry]

        with open(fn, "w") as fp:
            fp.writelines(lines)
    except (IOError, OSError):
        pass


def run_timer(history, timer):
    interval, comment = parse_timer(timer)
    minutes = round(timeparse(interval) / 60)
    notify_cmd = f"notify-send -i timer 'Timer expired' '{comment}'"
    run(["at", f"now + {minutes} minute"], input=notify_cmd, encoding=ENCODING)
    add_history_entry(history, interval, comment)


def select_timer(history, timer=None):
    timers = list(read_history(history))
    rofi_cmd = ROFI_SELECT_CMD[:]
    messages = []

    for cmd in Command:
        try:
            desc, shortcut = KEYBINDINGS[cmd]
        except (ValueError, KeyError):
            continue

        if int(cmd) != 0:
            rofi_cmd.append("-kb-custom-{}".format(cmd.value - 9))
            rofi_cmd.append(shortcut)

        messages.append(f"{shortcut}: {desc}")

    if messages:
        rofi_cmd.append("-mesg")
        rofi_cmd.append(", ".join(messages))

    proc = run(
        rofi_cmd,
        input="\n".join([f"{x[0]}:{x[1]}" for x in timers]),
        capture_output=True,
        encoding=ENCODING,
    )
    timer = proc.stdout.strip()
    actions = {
        Command.RunTimer: (run_timer,),
        Command.DeleteEntry: (delete_history_entry,),
    }
    action = actions.get(proc.returncode)

    if action:
        return action[0](history, timer, *action[1:])


def main(args=None):
    history = join(
        os.environ.get("XDG_CONFIG_HOME", expanduser("~/.config")), "rofi_timer.history"
    )
    cont = None

    while True:
        cont = select_timer(history, cont)

        if not cont:
            break


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
