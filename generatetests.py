#!/usr/bin/env python

import os
import sys
import random
import getopt
from nltk.corpus import WordNetCorpusReader

from indexedcorpus import IndexedCorpus
from sembuild import PREPRO_DIR

DEFAULT_SEED = 31337

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

def yield_17_candidates(corpus):
    wn16 = WordNetCorpusReader('wordnet/1.6/')
    wn17 = WordNetCorpusReader('wordnet/1.7.1/')

    for w in corpus.get_unique_words():
        synsets17 = wn17.synsets(w)
        lexclasses = list(set([s.lexname for s in synsets17]))
        synsets16 = wn16.synsets(w)
        if synsets16:
            continue
        if len(lexclasses) != 1:
            continue
        if 'noun' not in lexclasses[0]:
            continue
        yield w

def help():
    print "python %s [-s seed] [-f %%|-n INT|-a] [-6|-7] corpus_path" % sys.argv[0]

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:67f:n:")
    except Exception, e:
        print e
        help()
        sys.exit(2)

    seed = DEFAULT_SEED
    for o,a in opts:
        if o == "-h":
            help()
            sys.exit(1)
        elif o == "-s":
            seed = int(a)

    random.seed(seed)

    if len(args) != 1:
        help()
        sys.exit(2)

    corpus_path = args[0]
    if corpus_path.endswith('/'):
        corpus_path = corpus_path[:-1]
    store_path = os.path.join(PREPRO_DIR, os.path.basename(corpus_path))
    corpus = IndexedCorpus(store_path + '.sqlite', corpus_path)
    
    word_gen = None
    for o,a in opts:
        if o == '-6':
            word_gen = yield_single_supersense_nouns_in_corpus(corpus)
        elif o == '-7':
            word_gen = yield_17_candidates(corpus)

    if word_gen is None:
        help()
        sys.exit(2)
    word_gen = list(word_gen)

    sampled = word_gen
    for o,a in opts:
        if o == '-a':
            sampled = word_gen
        elif o == '-n':
            sampled = random.sample(word_gen, int(a))
        elif o == '-f':
            t = len(corpus)
            n = int(float(a) * t)
            sampled = random.sample(word_gen, n)

    for w in sorted(sampled):
        print w
     

if __name__ == '__main__':
    main()

