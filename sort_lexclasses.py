#!/usr/bin/env python

import sys

from corpus.indexedcorpus import IndexedCorpus
from nltk.corpus import WordNetCorpusReader

def yield_single_sense_nouns_in_corpus(corpus):
    wn = WordNetCorpusReader('wordnet/1.6/')
    for word in corpus.get_unique_words():
        synsets = list(wn.synsets(word))
        if len(synsets) == 1 and 'noun' in synsets[0].lexname:
            yield word

if __name__ == '__main__':
    index_file = sys.argv[1]
    indexed_corpus = IndexedCorpus(index_file)
    for word in yield_single_sense_nouns_in_corpus(indexed_corpus):
        print word


