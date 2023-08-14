"""Freedesktop.org Sound Theme Specification support."""

import sys

from dataclasses import dataclass
from functools import partial
from locale import LC_ALL, LC_MESSAGES, getlocale, setlocale
from os.path import exists, isdir, join
from typing import Dict, Optional

from xdg.BaseDirectory import xdg_data_dirs
from xdg.DesktopEntry import IniFile


def _get_locale():
    locale, encoding = getlocale(LC_MESSAGES)

    if locale is None:
        locale = "C"

    if encoding:
        locale += "@" + encoding

    return locale


class SoundThemeNotFoundError(Exception):
    """Raised when theme not found."""
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
                ini = IniFile(index)
                get = partial(ini.get, group="Sound Theme")
                theme = cls(
                    name=name,
                    display_name=get("Name", type="localestring"),
                    comment=get("Comment", type="localestring"),
                    directories={},
                    inherits=get("Inherits", list=True),
                    hidden=get("Hidden", type="boolean"),
                    example=get("Example"),
                )

                for subdir in get("Directories", list=True):
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
                    #print(f"Skipping non-existing {localedir}.", file=sys.stderr)
                    continue

                for fileext in (".disabled", ".oga", ".ogg", ".wav"):
                    filename = join(localedir, basename + fileext)
                    #print(f"Checking {filename}...", file=sys.stderr)

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
        except ThemeNotFoundError as exc:
            return

    if isinstance(theme, SoundTheme):
        subdirs = tuple(theme.directories)

    profiles = [profile]
    if profile != "stereo":
        profiles.append("stereo")

    for profile in profiles + [""]:
        for subdir in subdirs:
            if not theme or theme.dir_matches_profile(subdir, profile):
                themedir = join(theme.name if theme else "", subdir)
                if filename := _search_theme_dirs(basedirs, locales, themedir, name):
                    return filename


def find_sound(soundname, theme="freedesktop", locale=None, profile="stereo"):
    basedirs = (join(d, "sounds") for d in xdg_data_dirs)
    basedirs = (d for d in basedirs if isdir(d))

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
        theme = SoundTheme.load(theme)

    if filename := _lookup_sound(soundname, basedirs, theme, locales, profile):
        return filename

    parents = theme.inherits[:]

    if theme.name != "freedesktop":
        parents.append("freedesktop")

    for parenttheme in parents + [""]:
        if filename := _lookup_sound(soundname, basedirs, parenttheme, locales, profile):
            return filename


if __name__ == "__main__":
    setlocale(LC_ALL, "")
    fn = find_sound(sys.argv[1], profile="stereo", theme="freedesktop")

    if fn:
        print(fn)
