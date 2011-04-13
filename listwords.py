#!/usr/bin/env python

import sys
from nltk.corpus import WordNetCorpusReader

dict_dir = sys.argv[1]

wn = WordNetCorpusReader(dict_dir)

for synset in wn.all_synsets():
    for lem in synset.lemmas:
        print lem.name, synset.lexname


