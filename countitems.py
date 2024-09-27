#!/usr/bin/env python3
"""Count occurences of same lines read from standard input.

Outputs a table sorted by descending count.

"""

import sys
from collections import Counter

import natsort
import tabulate

counts = Counter(sys.stdin.read().strip().splitlines())
# sort by item
data = natsort.humansorted(counts.items())
# sort by descending count first
data.sort(reverse=True, key=lambda x: x[1])
print(tabulate.tabulate(data, headers=["Item", "Count"], tablefmt="grid" if len(sys.argv) <= 1 else sys.argv[1]))
