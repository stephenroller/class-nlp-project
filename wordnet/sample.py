#!/usr/bin/env python

import sys
from random import sample

def get_test_set(r=0.10):
    words = []
    for line in sys.stdin:
        word = line.strip()
        words.append(word)

    return sorted(sample(words, int(r * len(words))))

for word in get_test_set():
    print word
