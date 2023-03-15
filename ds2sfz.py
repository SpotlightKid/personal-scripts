#!/usr/bin/env python
"""Convert DecentSampler .dpreset file to SFZ"""

import argparse
import re
import sys

from xml.etree import ElementTree as ET

GROUP_PARAM_IGNORE = [
    "end",
    "start",
    "tag",
]
PARAM_MAP = {
    "ampVelTrack": "amp_veltrack",
    "attack": "amp_attack",
    "decay": "amp_decay",
    "hiNote": "hikey",
    "hiVel": "hivel",
    "loNote": "lokey",
    "loVel": "lovel",
    "path": "sample",
    "release": "amp_release",
    "rootNote": "pitch_keycenter",
    "sustain": "amp_sustain",
    "tuning": "tune",
}
SAMPLE_PARAM_IGNORE = [
    "end",
    "start",
]
REPLACEMENTS = [
    (re.compile(r"\s?db$", re.I), ""),
]


def convert_value(v):
    if isinstance(v, str):
        for rx, repl in REPLACEMENTS:
            v = rx.sub(repl, v)

    try:
        v = int(v)
    except (TypeError, ValueError):
        try:
            v = float(v)
        except (TypeError, ValueError):
            pass

    return v


class SampleGroup(dict):
    def __init__(self, name, **attr):
        self.name = name
        self.update(attr)
        self._samples = []

    def add_sample(self, **attr):
        self._samples.append(attr)

    @property
    def samples(self):
        return self._samples


class SampleLibrary(dict):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._groups = []

    def __str__(self):
        return self.format()

    def format(self, **options):
        ret = []
        for group in self._groups:
            ret.append(f"// {group}")
            ret.append("<group>")

            sgroup = self[group]

            for key, value in sgroup.items():
                if key in GROUP_PARAM_IGNORE:
                    continue

                key = PARAM_MAP.get(key, key)

                ret.append(f"    {key}={value}")

            ret.append("")

            for sample in sorted(sgroup.samples, key=lambda x: int(x.get("rootNote", 0))):
                ret.append("<region>")
                #ret.append(repr(sample))

                for key, value in sample.items():
                    if key in SAMPLE_PARAM_IGNORE:
                        continue

                    value = convert_value(value)

                    if options.get("transpose") and key in ("rootNote", "hiNote", "loNote"):
                        value = value + options.get("transpose")

                    key = PARAM_MAP.get(key, key)
                    ret.append(f"    {key}={value}")

                ret.append("")

            ret.append("")

        return "\n".join(ret)

    def add_group(self, name, **kw):
        if name in self:
            raise ValueError(f"Group {name} already present.")

        self[name] = SampleGroup(name, **kw)

        if name not in self._groups:
            self._groups.append(name)

    def add_sample(self, group, **sample):
        if group not in self:
            raise ValueError(f"Group {group} not found.")

        self[group].add_sample(**sample)


def parse_ds(filename):
    library = SampleLibrary()

    doc = ET.parse(filename)
    root = doc.getroot()
    groups = root.findall("./groups/*")

    for i, group in enumerate(groups):
        name = group.attrib.get("name", f"Group {i+1}")
        library.add_group(name, **{k:v for k,v in group.attrib.items() if k != "name"})
        samples = group.findall("./sample")

        for sample in samples:
            library.add_sample(name, **sample.attrib)

    return library


def main(args=None):
    ap = argparse.ArgumentParser(usage=__doc__.splitlines()[0])
    ap.add_argument("-o", "--output", help="Output file")
    ap.add_argument("-t", "--transpose", type=int, default=0, metavar="SEMITONES",
                    help="Transpose samples by given number of semitones")
    ap.add_argument("source", help="DecentSampler dpreset source file")
    args = ap.parse_args(args)

    library = parse_ds(args.source)

    if args.output:
        with open(args.output, "w") as fp:
            fp.write(library.format(transpose=args.transpose))
    else:
        print(library.format(transpose=args.transpose))


if __name__ == '__main__':
    sys.exit(main() or 0)
