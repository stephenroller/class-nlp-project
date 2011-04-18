#!/usr/bin/env python

import sys
from itertools import tee

senses = dict()

inpta, inptb = tee(sys.stdin)

for line in inpta:
    line = line.strip()
    word, sense = line.split()
    senses[word] = senses.get(word, 0) + 1

for line in inptb:
    line = line.strip()
    word, sense = line.split()
    if senses[word] == 1:
        print word, sense


