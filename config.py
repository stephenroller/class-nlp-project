#!/usr/bin/env python

## ---------- SEMBUILD PARAMETERS ----------
# default corpus to process. lolz
DEFAULT_CORPUS = '/u/pichotta/penn-wsj-raw-all.txt'
# preprocess directory
PREPRO_DIR = '/tmp/prepro-corpus/'

## ---------- SEMTEST PARAMETERS ----------
# k = number of web similar words
K = 3
# n = number of small corpus similar words
N = 9
# how much to discount each progressive synset (so the nth vote will be
# discounted by VOTE_DAMPING_COEFF ** n).
VOTE_DAMPING_COEFF = 0.7
# set to false if you don't wanna use the web to go from N -> K vectors
SHOULD_USE_WEB_FOR_PARING=True
SHOULD_USE_WEB_FOR_PARING=False
# set to false if you don't wanna use the web for initial vector enrichment.
SHOULD_USE_WEB_FOR_INIT_VEC_ENRICHMENT=True
# which wordnet version should we use?
WORDNET_DIR = 'wordnet/1.6/'



if __name__ == '__main__':
    import pprint
    pprint.pprint(globals())

