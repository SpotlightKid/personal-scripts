#!/usr/bin/env python
"""Print a random musical scale name to standard output.

Select from all natural, sharp and flat keys and all modes.

"""

import random

notes = list("CDEFGAB")
variant = ["natural", "sharp", "flat"]
mode = ["ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"]


def get_random_scale():
    return " ".join([random.choice(notes), random.choice(variant), random.choice(mode)])


if __name__ == '__main__':
    print(get_random_scale())
