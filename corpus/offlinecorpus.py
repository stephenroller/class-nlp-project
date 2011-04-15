"""Module to search for all occurrences of a string in a corpus."""

import itertools
import operator
import os
import re
import sys
import time

# actually half the context size--the lengh in either direction we go
CONTEXT_SIZE = 10
DEFAULT_CORPUS = '/u/pichotta/penn-wsj-raw-all.txt'
PREPRO_FILE_DIR = 'prepro-corpus/'

class OfflineCorpus:

    def __init__(self, corpusfilename=DEFAULT_CORPUS):
        self._corpus_name = self._canonicalize_corpus_name(corpusfilename)
        if not self._all_necessary_files_present():
            sys.stderr.write("ERROR! The necessary preprocesed corpus files were not found.\n")
            sys.stderr.write("run offlinecorpuspreprocess.py on the corpus first!\n")
            sys.exit(1)
        self._corpus_files = self._get_corpus_files(corpusfilename)
        self._lines = []
        for f in self._corpus_files:
            for l in open(f, 'r'):
                if not self._should_ignore_line(l):
                    self._lines.append(l)

    def _all_necessary_files_present(self):
        return os.path.isfile(self._get_word_list_filename()) and \
               os.path.isdir(self._get_context_list_dirname())

    def _canonicalize_corpus_name(self, cname):
        return os.path.basename(os.path.normcase(cname))

    def _get_word_list_filename(self):
        return os.path.join(PREPRO_FILE_DIR, self._corpus_name + '_WORDS')

    def _get_context_list_dirname(self):
        return os.path.join(PREPRO_FILE_DIR, self._corpus_name + '_CONTEXTS/')

    def get_contexts(self, query):
        """returns all contexts in which a query appears in a corpus."""
        return itertools.chain(*[self._get_contexts_in_line(query, l)
                                 for l in self._lines])

    def get_unique_words(self):
        """returns a set of unique words. Performs some normalization."""
        print 'getting lines...'
        lines = [l for l in self]
        print 'cleaning and tokenizing...'
        cleanlines = [[self._clean_word(w) for w in l.split()] for l in lines]
        print 'uniquifying...'
        return frozenset().union(*[frozenset(x) for x in cleanlines])

    def _get_corpus_files(self, fname):
        """takes a filename (optionally a dir), returns list of filenames"""
        if os.path.isdir(fname):
            return [x for x in os.walk(fname)]
        return [fname]

    def __iter__(self):
        for l in self._lines:
            yield l
        
    def _get_contexts_in_line(self, query, line):
        """might mangle the whitespace a bit but that shouldn't matter"""
        if self._should_ignore_line(line): return []
        cleanq = self._clean_word(query)
        words = line.split()
        res = []
        for i in range(len(words)):
            if self._clean_word(words[i]) == cleanq:
                res.append(self._get_ind_context(words, i))
        return res

    def _should_ignore_line(self, line):
        return line.strip() == '.START'

    def _clean_word(self, w):
        return re.sub(r'\W', '', w.lower())

    def _get_ind_context(self, words, ind):
        lb = max(0, ind - CONTEXT_SIZE)
        ub = min(len(words), ind + CONTEXT_SIZE)
        #TODO i think there's a performance bottleneck here?
        return ' '.join(words[lb:ub])


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

