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
    CopyURL = 11
    CopyOTP = 12


CLIPBOARD_TIMEOUT = 45
FIELD_RX = re.compile(r"^(?P<name>\S.*?)\s*[:=]\s*(?P<value>.*)$")
KEYBINDINGS = {
    Command.CopyPassword: ("Copy password", "Return"),
    Command.CopyLogin: ("Copy login", "Ctrl-Return"),
    Command.CopyURL: ("Copy URL", "Ctrl-u"),
    Command.CopyOTP: ("Copy OTP", "Ctrl-o"),
}
LOGIN_NAME_FIELDS = ("login", "username", "user", "id", "email", "emailaddress", "account")
ROFI_CMD = [
    "rofi",
    "-dmenu",
    "-no-custom",
    "-kb-accept-custom",
    "",
    "-kb-remove-to-sol",
    "",
    "-i",
    "-p",
    "Accounts:",
    "-normal-window",
]
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


def copy_fieldvalue(store, account, fieldnames):
    if isinstance(fieldnames, str):
        fieldnames = [fieldnames]

    data = get_account_data(store, account)

    for name in fieldnames:
        value = data.get(re.sub(r"[-_]", "", name.lower()))

        if value:
            run(XCLIP_CMD, input=value, encoding="UTF-8")
            break


def get_pass_accounts(store):
    return sorted(
        splitext(fn)[0] for fn in glob.glob(join("**", "*.gpg"), root_dir=store, recursive=True)
    )


def get_account_data(store, account):
    os.environ["PASSWORD_STORE_DIR"] = store

    try:
        proc = run(["pass", "show", account], capture_output=True, encoding="UTF-8", check=True)
    except CalledProcessError:
        return {}

    data = {}
    for line in proc.stdout.splitlines()[1:]:
        match = FIELD_RX.match(line)
        if match:
            name, value = match.group("name", "value")

        data[name] = value

    return data


def run_rofi(store):
    accounts = get_pass_accounts(store)
    rofi_cmd = ROFI_CMD[:]
    messages = []

    for cmd in Command:
        desc, shortcut = KEYBINDINGS.get(cmd)

        if cmd != Command.CopyPassword:
            rofi_cmd.append("-kb-custom-{}".format(cmd.value - 9))
            rofi_cmd.append(shortcut)

        messages.append(f"{shortcut}: {desc}")

    if messages:
        rofi_cmd.append("-mesg")
        rofi_cmd.append(", ".join(messages))

    proc = run(rofi_cmd, input="\n".join(accounts), capture_output=True, encoding="UTF-8")

    account = proc.stdout.strip()

    if proc.returncode == Command.CopyPassword:
        copy_password(store, account)
    elif proc.returncode == Command.CopyLogin:
        copy_fieldvalue(store, account, LOGIN_NAME_FIELDS)
    elif proc.returncode == Command.CopyURL:
        copy_fieldvalue(store, account, "url")
    elif proc.returncode == Command.CopyOTP:
        copy_password(store, account, mode="otp")
    else:
        return proc.returncode


def show_notification(summary, body="", timeout=10_000):
    run(["notify-send", "-a", "pass", "-t", str(timeout), "-i", "info", summary, body])


def main():
    store = os.getenv("PASSWORD_STORE_DIR", expanduser("~/.password-store"))
    return run_rofi(store)


if __name__ == "__main__":
    sys.exit(main() or 0)
