#!/usr/bin/env python3
"""Display a rofi menu for pass(1) accounts."""

import glob
import os
import re
import sys
from enum import IntEnum
from os.path import basename, expanduser, join, splitext
from subprocess import CalledProcessError, run


class Command(IntEnum):
    CopyPassword = 0
    CopyLogin = 10
    CopyOTP = 11
    CopyURL = 12
    OpenURL = 13
    ViewData = 14


CLIPBOARD_TIMEOUT = 45
ENCODING = "UTF-8"
FIELD_RX = re.compile(r"^(?P<name>\S.*?)\s*[:=]\s*(?P<value>.*)$")
KEYBINDINGS = {
    Command.CopyPassword: ("Copy password", "Return"),
    Command.CopyLogin: ("Copy login", "Ctrl-Return"),
    Command.CopyOTP: ("Copy OTP", "Ctrl-o"),
    Command.CopyURL: ("Copy URL", "Ctrl-u"),
    Command.OpenURL: ("Open URL", "Ctrl-U"),
    Command.ViewData: ("View data", "Alt-e"),
}
LOGIN_NAME_FIELDS = ("login", "username", "user", "id", "email", "emailaddress", "account")
ROFI_SELECT_CMD = [
    "rofi",
    "-dmenu",
    "-no-custom",
    "-kb-accept-custom",
    "",
    "-kb-remove-to-sol",
    "",
    "-i",
    "-p",
    "Account",
    "-normal-window",
]
ROFI_VIEW_CMD = [
    "rofi",
    "-dmenu",
    "-no-custom",
    "-i",
    "-mesg",
    "Enter: Copy field data, ESC: Back",
    "-p",
    "Field",
    "-normal-window",
]
URL_FIELDS = ("url", "homepage", "website")
XCLIP_CMD = ["xclip", "-i", "-selection", "clipboard"]


def copy_password(store, account, mode="show"):
    os.environ["PASSWORD_STORE_DIR"] = store
    os.environ["PASSWORD_STORE_CLIP_TIME"] = str(CLIPBOARD_TIMEOUT)
    proc = run(["pass", mode, "-c", account])

    if proc.returncode == 0:
        show_notification(
            "Secret copied",
            f"Secret for '{account}' copied to clipboard.\n "
            f"Will be cleared in {CLIPBOARD_TIMEOUT} seconds.",
        )


def copy_fieldvalue(store, account, *fieldnames):
    value = get_fieldvalue(store, account, *fieldnames)

    if value:
        run(XCLIP_CMD, input=value, encoding=ENCODING)
    else:
        show_notification(
            "Data not available",
            f"No value set for {', '.join(fieldnames)} in '{account}' data.",
            icon="warning",
        )


def get_pass_accounts(store):
    return sorted(
        splitext(fn)[0] for fn in glob.glob(join("**", "*.gpg"), root_dir=store, recursive=True)
    )


def get_account_data(store, account):
    os.environ["PASSWORD_STORE_DIR"] = store

    try:
        proc = run(["pass", "show", account], capture_output=True, encoding=ENCODING, check=True)
    except CalledProcessError:
        return {}

    data = {}
    for line in proc.stdout.splitlines()[1:]:
        match = FIELD_RX.match(line)
        if match:
            name, value = match.group("name", "value")

        data[name.lower()] = value

    return data


def get_fieldvalue(store, account, *fieldnames):
    data = get_account_data(store, account)

    for name in fieldnames:
        value = data.get(re.sub(r"[-_]", "", name.lower()))

        if value:
            return value

    return None


def open_url(store, account):
    url = get_fieldvalue(store, account, *URL_FIELDS)

    if url:
        run(["xdg-open", url])
    else:
        show_notification("No URL found", f"No URL set for '{account}'.", icon="error")


def select_account(store, account=None):
    accounts = get_pass_accounts(store)
    rofi_cmd = ROFI_SELECT_CMD[:]
    messages = []

    if account:
        rofi_cmd.append("-select")
        rofi_cmd.append(account)

    for cmd in Command:
        try:
            desc, shortcut = KEYBINDINGS[cmd]
        except (ValueError, KeyError):
            continue

        if cmd != Command.CopyPassword:
            rofi_cmd.append("-kb-custom-{}".format(cmd.value - 9))
            rofi_cmd.append(shortcut)

        messages.append(f"{shortcut}: {desc}")

    if messages:
        rofi_cmd.append("-mesg")
        rofi_cmd.append(", ".join(messages))

    proc = run(rofi_cmd, input="\n".join(accounts), capture_output=True, encoding=ENCODING)

    account = proc.stdout.strip()

    if proc.returncode == Command.CopyPassword:
        copy_password(store, account)
    elif proc.returncode == Command.CopyLogin:
        copy_fieldvalue(store, account, *LOGIN_NAME_FIELDS)
    elif proc.returncode == Command.OpenURL:
        open_url(store, account)
    elif proc.returncode == Command.CopyURL:
        copy_fieldvalue(store, account, *URL_FIELDS)
    elif proc.returncode == Command.CopyOTP:
        copy_password(store, account, mode="otp")
    elif proc.returncode == Command.ViewData:
        view_data(store, account)
    else:
        return proc.returncode


def show_notification(summary, body="", icon="info", timeout=10_000):
    run(["notify-send", "-a", "pass", "-t", str(timeout), "-i", icon, summary, body])


def view_data(store, account):
    data = get_account_data(store, account)
    lines = (f"{key}: {value}" for key, value in data.items())
    proc = run(ROFI_VIEW_CMD, input="\n".join(lines), capture_output=True, encoding=ENCODING)

    if proc.returncode == 0:
        value = proc.stdout.split(":", maxsplit=1)[1].strip()
        run(XCLIP_CMD, input=value, encoding=ENCODING)
    elif proc.returncode == 1:
        select_account(store, account)


def main():
    store = os.getenv("PASSWORD_STORE_DIR", expanduser("~/.password-store"))
    return select_account(store)


if __name__ == "__main__":
    sys.exit(main() or 0)
