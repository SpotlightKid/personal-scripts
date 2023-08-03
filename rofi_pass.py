#!/usr/bin/env python3
"""Display a rofi menu for pass accounts."""

import glob
import os
import re
import shlex
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
    EditAccount = 15


CLIPBOARD_TIMEOUT = 45
TERMINAL = os.environ.get("TERMINAL", "rofi-sensible-terminal")
ENCODING = "UTF-8"
FIELD_RX = re.compile(r"^(?P<name>\S.*?)\s*[:=]\s*(?P<value>.*)$")
KEYBINDINGS = {
    Command.CopyPassword: ("Copy password", "Return"),
    Command.CopyLogin: ("Copy login", "Ctrl-Return"),
    Command.CopyOTP: ("Copy OTP", "Ctrl-o"),
    Command.CopyURL: ("Copy URL", "Ctrl-u"),
    Command.OpenURL: ("Open URL", "Ctrl-U"),
    Command.ViewData: ("View data", "Shift-Return"),
    Command.EditAccount: ("Edit account", "Control-Shift-Return"),
}
LOGIN_NAME_FIELDS = ("login", "username", "user", "id", "email", "emailaddress", "account")
ROFI_SELECT_CMD = [
    "rofi",
    "-dmenu",
    "-no-custom",
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
    "Account",
    "-normal-window",
]
ROFI_VIEW_CMD = [
    "rofi",
    "-dmenu",
    "-no-custom",
    "-kb-accept-custom",
    "",
    "-kb-accept-alt",
    "",
    "-kb-custom-1",
    "Shift-Return",
    "-kb-custom-2",
    "Control-Return",
    "-i",
    "-mesg",
    "ESC: Back, Return: Copy field value, Shift-Return: Copy &amp; back; Control-Return: Copy &amp; close",
    "-p",
    "Field",
    "-normal-window",
]
RUN_IN_TERMINAL_CMD = ["{terminal}", "-e", "{command_string}", "-T", "{title}"]
URL_FIELDS = ("url", "homepage", "website")
XCLIP_CMD = ["xclip", "-i", "-selection", "clipboard"]


def copy_password(store, account, mode="show"):
    env = os.environ.copy()
    env["PASSWORD_STORE_DIR"] = store
    env["PASSWORD_STORE_CLIP_TIME"] = str(CLIPBOARD_TIMEOUT)
    proc = run(["pass", mode, "-c", account], env=env)

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


def edit_account(store, account):
    env = os.environ.copy()
    env["PASSWORD_STORE_DIR"] = store

    run_in_terminal(["pass", "edit", account], title=f"Edit account: {account}", env=env)


def get_pass_accounts(store):
    return sorted(
        splitext(fn)[0] for fn in glob.glob(join("**", "*.gpg"), root_dir=store, recursive=True)
    )


def get_account_data(store, account):
    env = os.environ.copy()
    env["PASSWORD_STORE_DIR"] = store

    try:
        proc = run(
            ["pass", "show", account], capture_output=True, encoding=ENCODING, check=True, env=env
        )
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


def open_url(store, account, *fieldnames):
    url = get_fieldvalue(store, account, *fieldnames)

    if url:
        run(["xdg-open", url])
    else:
        show_notification("No URL found", f"No URL set for '{account}'.", icon="error")


def run_in_terminal(cmd, title="", env=None):
    subst = {
        "command": cmd,
        "command_string": shlex.join(cmd),
        "title": title,
        "terminal": TERMINAL,
    }
    term_cmd = [item.format(**subst) for item in RUN_IN_TERMINAL_CMD]
    run(term_cmd, env=env)


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
    actions = {
        Command.CopyPassword: (copy_password,),
        Command.CopyLogin: (copy_fieldvalue, *LOGIN_NAME_FIELDS),
        Command.CopyOTP: (copy_password, "otp"),
        Command.CopyURL: (copy_fieldvalue, *URL_FIELDS),
        Command.OpenURL: (open_url, *URL_FIELDS),
        Command.ViewData: (view_data,),
        Command.EditAccount: (edit_account,),
    }
    action = actions.get(proc.returncode)

    if action:
        return action[0](store, account, *action[1:])


def show_notification(summary, body="", icon="info", timeout=10_000):
    run(["notify-send", "-a", "pass", "-t", str(timeout), "-i", icon, summary, body])


def view_data(store, account):
    data = get_account_data(store, account)
    lines = "\n".join((f"{key}: {value}" for key, value in data.items()))

    while True:
        proc = run(ROFI_VIEW_CMD, input=lines, capture_output=True, encoding=ENCODING)

        if proc.returncode in (0, 10, 11):
            match = FIELD_RX.match(proc.stdout.strip())

            if match:
                value = match.group("value")
                run(XCLIP_CMD, input=value, encoding=ENCODING)

        if proc.returncode != 0:
            break

    if proc.returncode == 10:
        return account


def main():
    store = os.getenv("PASSWORD_STORE_DIR", expanduser("~/.password-store"))
    cont = None

    while True:
        cont = select_account(store, cont)

        if not cont:
            break


if __name__ == "__main__":
    sys.exit(main() or 0)
