"""Module to search for all occurrences of a string in a corpus.

Note that if you're calling this directly to test it, you need to call
it from the  project root directory (so it can find prepro-corpus/)
"""

import itertools
import operator
import os
import re
import sys
import time

# actually half the context size--the lengh in either direction we go
HALF_CONTEXT_SIZE = 10
DEFAULT_CORPUS = '/u/pichotta/penn-wsj-raw-all.txt'
PREPRO_FILE_DIR = 'prepro-corpus/'

def canonicalize_corpus_name(cname):
    return os.path.basename(os.path.normcase(cname))

def get_word_list_filename(cname):
    return os.path.join(PREPRO_FILE_DIR, cname + '_WORDS')

def get_context_list_dirname(cname):
    return os.path.join(PREPRO_FILE_DIR, cname + '_CONTEXTS/')

def get_context_list_filename(cname, word):
    return os.path.join(get_context_list_dirname(cname), word[0], word)

def clean_word(w):
    return re.sub(r'\W', '', w.lower())


class OfflineCorpus:
    def __init__(self, corpusfilename=DEFAULT_CORPUS):
        self._corpus_name = canonicalize_corpus_name(corpusfilename)
        if not self._all_necessary_files_present():
            sys.stderr.write("ERROR! The necessary preprocesed corpus files were not found.\n")
            sys.stderr.write("run offlinecorpuspreprocess.py on the corpus first!\n")
            sys.exit(1)

    def _all_necessary_files_present(self):
        return os.path.isfile(get_word_list_filename(self._corpus_name)) and \
               os.path.isdir(get_context_list_dirname(self._corpus_name))

    def get_contexts(self, query):
        """returns all contexts in which a query appears in a corpus."""
        fname = get_context_list_filename(self._corpus_name, clean_word(query))
        if not os.path.isfile(fname):
            return []
        f = open(fname, 'r')
        li = [x.strip() for x in f.readlines()]
        f.close()
        return li

    def get_unique_words(self):
        """returns a set of unique words. Performs some normalization."""
        f = open(get_word_list_filename(self._corpus_name), 'r')
        li = [x.strip() for x in f.readlines()]
        f.close()
        return li

if __name__ == '__main__':
    q = 'coffee'
    if len(sys.argv) > 1:
        q = sys.argv[1]
    t = time.time()
    cxts = OfflineCorpus().get_contexts(q)
    print('Search took %f seconds' % (time.time() - t))
    print('Found %d contexts:' % len(cxts))
    for c in cxts:
        print c

