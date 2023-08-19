#!/usr/bin/env python3
"""Freedesktop.org Sound Theme Specification support."""

import logging
import sys

from dataclasses import dataclass
from functools import partial
from locale import LC_ALL, LC_MESSAGES, getlocale, setlocale
from os.path import exists, isdir, join
from typing import Dict, Optional

from xdg.BaseDirectory import xdg_data_dirs
from xdg.DesktopEntry import IniFile


log = logging.getLogger(__name__)


def _get_locale():
    locale, encoding = getlocale(LC_MESSAGES)

    if locale is None:
        locale = "C"

    if encoding:
        locale += "@" + encoding

    return locale


class ThemeError(Exception):
    """Base exception for errors concerning theme loading."""

    pass


class SoundThemeNotFoundError(ThemeError):
    """Raised when theme not found."""

    pass


class InvalidThemeError(ThemeError):
    """Raised when loading a theme containing errors."""

    pass


@dataclass
class SoundThemeDirectory:
    output_profile: Optional[str]
    context: Optional[str]


@dataclass
class SoundTheme:
    name: str
    display_name: str
    comment: Optional[str]
    inherits: Optional[str]
    directories: Dict[str, SoundThemeDirectory]
    hidden: bool
    example: Optional[str]

    @classmethod
    def load(cls, name):
        for datadir in xdg_data_dirs:
            index = join(datadir, "sounds", name, "index.theme")

            if exists(index):
                logging.debug("Loading theme %s from %s...", name, index)
                ini = IniFile(index)
                get = partial(ini.get, group="Sound Theme")
                directories = get("Directories", list=True)
                inherits = get("Inherits", list=True)

                if not directories and not inherits:
                    raise InvalidThemeError(
                        "Theme must define a value for either or both the "
                        "'Directories' and the 'Inherits' key."
                    )

                theme = cls(
                    name=name,
                    display_name=get("Name", type="localestring"),
                    comment=get("Comment", type="localestring"),
                    directories={},
                    inherits=inherits,
                    hidden=get("Hidden", type="boolean"),
                    example=get("Example"),
                )

                for subdir in directories:
                    theme.directories[subdir] = SoundThemeDirectory(
                        context=ini.get("Context", group=subdir),
                        output_profile=ini.get("OutputProfile", group=subdir),
                    )

                return theme
        else:
            raise SoundThemeNotFoundError(f"No sound theme named '{name}' found.")

    def dir_matches_profile(self, subdir, profile):
        return subdir in self.directories and self.directories[subdir].output_profile == profile


def _search_theme_dirs(basedirs, locales, themedir, name):
    for basedir in basedirs:
        basename = name

        while True:
            for locale in locales:
                localedir = join(basedir, themedir, locale)

                if not isdir(localedir):
                    log.debug("Skipping non-existing %s.", localedir)
                    continue

                for fileext in (".disabled", ".oga", ".ogg", ".wav"):
                    filename = join(localedir, basename + fileext)
                    log.debug("Checking %s...", filename)

                    if exists(filename):
                        return filename

            try:
                basename, _ = basename.rsplit("-", 1)
            except ValueError:
                break


def _lookup_sound(name, basedirs, theme, locales, profile):
    subdirs = ("",)

    if theme and isinstance(theme, str):
        try:
            theme = SoundTheme.load(theme)
        except ThemeError as exc:
            log.error("Could not load theme %s: %s", theme, exc)

    if isinstance(theme, SoundTheme):
        subdirs = tuple(theme.directories)

    profiles = [profile]
    if profile != "stereo":
        profiles.append("stereo")

    for profile in profiles + [""]:
        for subdir in subdirs:
            if not theme or theme.dir_matches_profile(subdir, profile):
                themedir = join(theme.name if theme else "", subdir)
                log.debug(
                    "Searching theme dir %s (subdir: %s profile: %s) in basedirs.",
                    themedir,
                    subdir,
                    profile,
                )
                if filename := _search_theme_dirs(basedirs, locales, themedir, name):
                    return filename


def find_sound(soundname, theme="freedesktop", locale=None, profile="stereo"):
    basedirs = (join(d, "sounds") for d in xdg_data_dirs)
    basedirs = [d for d in basedirs if isdir(d)]

    if locale is None:
        locale = _get_locale()

    locales = []
    for loc in [
        locale,
        locale.split("@", 1)[0],
        locale.split("_", 1)[0],
        "C",
        "",
    ]:
        if loc not in locales:
            locales.append(loc)

    if isinstance(theme, str):
        try:
            theme = SoundTheme.load(theme)
        except ThemeError as exc:
            log.error("Could not load theme %s: %s", theme, exc)

    if filename := _lookup_sound(soundname, basedirs, theme, locales, profile):
        return filename

    parents = theme.inherits[:]

    if theme.name != "freedesktop":
        parents.append("freedesktop")

    for parenttheme in parents + [""]:
        if filename := _lookup_sound(soundname, basedirs, parenttheme, locales, profile):
            return filename


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    ap.add_argument("soundname", help="Sound name to look up")
    ap.add_argument("theme", nargs="?", help="Sound theme name")

    args = ap.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    setlocale(LC_ALL, "")
    fn = find_sound(args.soundname, profile="stereo", theme=args.theme or "freedesktop")

    if fn:
        print(fn)
