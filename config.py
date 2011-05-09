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
# set to false if you don't wanna use the web for initial vector enrichment.
SHOULD_USE_WEB_FOR_INIT_VEC_ENRICHMENT=True
# set to True if you wanna scrape sites to get the initially enriched vector; set
# to False if you want to use search engine Descriptions.
SHOULD_ENRICH_BY_SCRAPING=True
# which wordnet version should we use?
WORDNET_DIR = 'wordnet/1.6/'

## ---------- SEARCHENGINECORPUS PARAMETERS ----------
APPID = '335CBE48CCCAF4A34652A3DDE7D2CE78FD3390DC'

SHOULD_SCRAPE_SITES = True
NUM_PAGES_TO_SCRAPE = 50
CONTEXT_WORD_WIDTH = 20

WEB_DB_FILENAME = '/tmp/webcorpus-%s.sqlite' % (SHOULD_SCRAPE_SITES and "scrape" or "bing")

URLLIB_TIMEOUT = 3

## ---------- PARALLELISM PARAMETERS ----------
NUM_PROCESSES = N
NUM_FETCH_PROCESSES = NUM_PAGES_TO_SCRAPE

## ---------- PRINT SETTINGS ----------

def print_settings():
    settings = dict(globals())
    todel = []
    for k in sorted(settings.keys()):
        if k.upper() == k:
            print "%s: %s" % (k,settings[k])

if __name__ == '__main__':
    print_settings()

