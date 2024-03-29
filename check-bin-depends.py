#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hacky script to determine redundant dependencies of an AUR package."""

import sys
from collections import defaultdict
from functools import partial
from subprocess import DEVNULL, PIPE, run, STDOUT
from pprint import pprint

__prog__ = "check-bin-depends"

err = partial(print, file=sys.stderr)


def pipe(cmd, input='', stderr=None, **kwargs):
    kwargs['stdout'] = PIPE
    kwargs['stderr'] = {'redirect': STDOUT, 'capture': PIPE, 'drop': DEVNULL}.get(stderr, stderr)
    kwargs.setdefault('encoding', 'utf-8' if isinstance(input, str) else None)
    res = run(cmd, input=input, **kwargs)
    return (res.stdout, res.stderr) if stderr == 'capture' else res.stdout


def main(args):
    if not args:
        sys.exit("Usage: %s [-e <pkg>] <binary>..." % __prog__)

    excludes = set()
    while True:
        if len(args) >= 3 and args[0] == "-e":
            excludes.add(args[1])
            args.pop(0)
            args.pop(0)
        else:
            break


    depends = set()
    base_devel = set(line.strip() for line in pipe(['pacman', '-Qqg', 'base-devel']).splitlines())
    #err("\n".join(sorted(base_devel)))
    for pkg in base_devel:
        depends.update(p.strip() for p in pipe(['pactree', '-l', pkg]).splitlines())
    depends.update(base_devel)

    for fn in args:
        libs = set()
        for line in pipe(['ldd', fn]).splitlines():
            line = line.strip()
            if line and not (line.startswith('linux-vdso') or 'ld-linux' in line):
                libs.add(line.split()[2])

    #err("\n".join(sorted(libs)))

    err("\nCollecting packages...\n")
    packages = set()
    for path in libs:
        package = pipe(['pkgfile', path]).splitlines()[0].strip()
        if package:
            #err("{} => '{}'".format(lib, package))
            package = package.split('/')[1]

            if package in packages:
                continue

            if package in depends:
                err("Package '{}' in 'base-devel' group (and dependencies).".format(package))
            elif package in excludes:
                err("Package '{}' ignored by exclude list.".format(package))
                continue
            packages.add(package)
        else:
            err("Library file '{}' is not owned by any package.".format(path))

    err("\nCollecting dependencies...\n")
    depends = defaultdict(set)
    for pkg in sorted(packages):
        for dep in set(p.strip() for p in pipe(['pactree', '-l', pkg]).splitlines()):
            if dep != pkg:
                depends[dep].add(pkg)

    #pprint(depends)

    maxcount = 10
    err("\nRemoving indirect dependencies...\n")
    while True:
        toremove = set()
        for pkg in sorted(packages):
            if depends[pkg]:
                toremove.add(pkg)
                err("Dependency '{}' already included by packages '{}'. "
                    "Removing it.".format(pkg, ", ".join(depends[pkg])))

        maxcount -= 1
        if not toremove or not packages or maxcount <= 0:
            break

        packages.difference_update(toremove)

    print("depends: ({})".format(" ".join("'{}'".format(pkg) for pkg in sorted(packages))))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
