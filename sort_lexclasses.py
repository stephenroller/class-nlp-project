#!/usr/bin/env python

from corpus.offlinecorpus import OfflineCorpus
from nltk.corpus import WordNetCorpusReader

offline = OfflineCorpus()
wn = WordNetCorpusReader('wordnet/1.6/')

for word in offline.get_unique_words():
    synsets = list(wn.synsets(word))
    if len(synsets) == 1 and 'noun' in synsets[0].lexname:
        print word


