#!/usr/bin/env python
#
# rofi_timer.py
#
# Requires:
#
# * Python 3.8+
# * rofi
# * a [desktop notification server] like e.g. xfce4-notifyd
# * notify-send (from libnotify)
# * systemd-run (from systemd)
# * [pytimeparse]
#
# [desktop notification server]: https://wiki.archlinux.org/title/Desktop_notifications#Notification_servers
# [pytimeparse]: https://pypi.org/project/pytimeparse/
#
# Copyright (c) 2023 Christopher Arndt <chris@chrisarndt.de>
#
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

import enum
import os
import re
import sys
from dataclasses import dataclass
from os.path import dirname, exists, expanduser, join
from subprocess import run
from typing import Optional

from pytimeparse import parse as timeparse


class Command(enum.IntEnum):
    RunTimer = 0
    DeleteEntry = 10


# Customizable settings
DEFAULT_DESCRIPTION = "Timer interval: {timer.interval_seconds}s"
DEFAULT_ICON = "timer"
DEFAULT_SOUND = None
ENCODING = "UTF-8"
KEYBINDINGS = {
    Command.RunTimer: ("Activate Timer", "Return"),
    Command.DeleteEntry: ("Delete History Entry", "Ctrl-Return"),
}
NOTIFICATION_BODY = "{description}"
NOTIFICATION_COMMAND = "notify-timer"
NOTIFICATION_SUMMARY = "Timer expired"
ROFI_SEARCH_LABEL = "Timer"

# No user-customizable settings below
RX_TIMER = re.compile(r"-?(?P<interval>[^-]+)(\s*-\s*)?((?P<description>.*?)\s*$)?")
RX_ICON_TAG = re.compile(r"\B#(?P<icon>[-_.0-9a-z]+)")
RX_SOUND_TAG = re.compile(r"\B\+(?P<sound>[-_.0-9a-z]+)")
TIMER_SELECT_COMMAND = [
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
    ROFI_SEARCH_LABEL,
    "-normal-window",
]
SYSTEMD_RUN_COMMAND = [
    "systemd-run",
    "--user",
    "--on-active",
    "{interval_seconds}",
    "--timer-property=AccuracySec={accuracy}",
    "--description",
    "{description}",
]


@dataclass
class Timer:
    interval: str
    description: Optional[str] = None
    icon: Optional[str] = None
    sound: Optional[str] = None

    @property
    def interval_seconds(self):
        return abs(timeparse(self.interval))

    def __str__(self):
        desc = []
        if self.description:
            desc.append(self.description.replace("\n", r"\n").replace("\r", r"\r"))

        if self.icon:
            desc.append(f"#{self.icon}")

        if self.sound:
            desc.append(f"+{self.sound}")

        desc = " ".join(desc)
        return f"{self.interval} - {desc}" if desc else f"{self.interval}"

    @classmethod
    def from_string(cls, s):
        icon = sound = None
        match = RX_TIMER.match(s)
        if match:
            interval, description = match.group("interval", "description")
        else:
            raise ValueError("Could not parse timer entry.")

        if description:
            match = RX_ICON_TAG.search(description)
            if match:
                icon = match.group("icon")
                description = RX_ICON_TAG.sub("", description)

            match = RX_SOUND_TAG.search(description)
            if match:
                sound = match.group("sound")
                description = RX_SOUND_TAG.sub("", description)

        inst = cls(
            interval=interval.strip(), description=description.strip(), icon=icon, sound=sound
        )

        if not timeparse(interval):
            raise ValueError("Could not parse timer interval.")

        return inst


def get_history_path():
    return join(
        os.environ.get("XDG_CONFIG_HOME", expanduser("~/.config")), "rofi-timer", "history"
    )


def read_history():
    history_path = get_history_path()
    history = []

    try:
        with open(history_path) as fp:
            entry = 0
            for line in fp.readlines():
                if line.strip():
                    entry += 1
                    try:
                        timer = Timer.from_string(line)
                    except ValueError as exc:
                        print(f"Could not read history entry #{entry}: {exc}", file=sys.stderr)
                    else:
                        history.append(timer)
    except (IOError, OSError):
        pass

    return history


def write_history(timer, delete=False):
    history_path = get_history_path()
    entry = str(timer) + "\n"

    try:
        os.makedirs(dirname(history_path), exist_ok=True)

        try:
            with open(history_path, "r") as fp:
                lines = [line for line in fp.readlines() if line != entry]
        except (IOError, OSError):
            lines = []

        with open(history_path, "w") as fp:
            if not delete:
                fp.write(entry)

            fp.writelines(lines)
    except (IOError, OSError) as exc:
        print(f"Could not write history: {exc}", file=sys.stderr)


def delete_history_entry(timer):
    write_history(timer, delete=True)
    return True


def add_timer_systemd(timer, cmd):
    seconds = timer.interval_seconds
    systemd_cmd = [
        item.format(
            interval_seconds=seconds,
            description=timer.description,
            accuracy="1s" if seconds % 60 else "1m",
        )
        for item in SYSTEMD_RUN_COMMAND
    ]
    systemd_cmd.extend(cmd)
    return run(systemd_cmd)


def activate_timer(timer):
    description = timer.description or DEFAULT_DESCRIPTION.format(timer=timer)
    icon = timer.icon or DEFAULT_ICON
    sound = timer.sound or DEFAULT_SOUND
    body = NOTIFICATION_BODY.format(timer=timer, description=description)
    summary = NOTIFICATION_SUMMARY.format(timer=timer)
    notify_cmd = [NOTIFICATION_COMMAND, summary, body, icon or "", sound or ""]
    add_timer_systemd(timer, notify_cmd)
    write_history(timer)


def select_timer(timer=None):
    timers = read_history()
    rofi_cmd = TIMER_SELECT_COMMAND[:]
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
        input="\n".join([str(timer) for timer in timers]),
        capture_output=True,
        encoding=ENCODING,
    )

    actions = {
        Command.RunTimer: (activate_timer,),
        Command.DeleteEntry: (delete_history_entry,),
    }
    action = actions.get(proc.returncode)

    if action:
        try:
            timer = Timer.from_string(proc.stdout.strip())
        except ValueError as exc:
            show_error("Invalid timer", str(exc))
        else:
            return action[0](timer, *action[1:])


def show_error(title, message):
    run(["notify-send", "-i", "error", title, message])


def main(args=None):
    if args:
        try:
            timer = Timer.from_string(" ".join(args))
        except ValueError as exc:
            return f"Invalid timer: {exc}"

        activate_timer(timer)
    else:
        continue_ = None

        while True:
            continue_ = select_timer(continue_)

            if not continue_:
                break


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) or 0)
