#!/usr/bin/env python

from nltk.corpus import WordNetCorpusReader
import os
import sys
from corpus.indexedcorpus import IndexedCorpus
from sembuild import PREPRO_DIR

def yield_single_sense_nouns_in_corpus(corpus):
    wn = WordNetCorpusReader('wordnet/1.6/')
    for word in corpus.get_unique_words():
        synsets = list(wn.synsets(word))
        if len(synsets) == 1 and 'noun' in synsets[0].lexname:
            yield word

def yield_single_supersense_nouns_in_corpus(corpus):
    wn = WordNetCorpusReader('wordnet/1.6/')
    for w in corpus.get_unique_words():
        lexclasses = list(set([s.lexname for s in wn.synsets(w)]))
        if len(lexclasses) == 1 and 'noun' in lexclasses[0]:
            yield w

if __name__ == '__main__':
    corpus_path = sys.argv[1]
    store_path = os.path.join(PREPRO_DIR, os.path.basename(corpus_path))
    indexed_corpus = IndexedCorpus(store_path + '.sqlite', corpus_path)
    #for word in yield_single_sense_nouns_in_corpus(indexed_corpus):
    for word in yield_single_supersense_nouns_in_corpus(indexed_corpus):
        print word


