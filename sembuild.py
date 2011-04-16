#!/usr/bin/env python

import sys
import os
from itertools import islice, count
from gensim import corpora, models, similarities

from corpus.offlinecorpus import clean_word, OfflineCorpus

DEFAULT_CORPUS = '/u/pichotta/penn-wsj-raw-all.txt'
PREPRO_DIR = 'prepro-corpus/'
STOP_WORDS = ['the', 'an', 'a', '.start', 'to', 'of', 'and']

class PennCorpus(object):
    def __init__(self, filename):
        self.basename = os.path.basename(filename)
        self.offline = OfflineCorpus()
        self.corpus = None
        self.docid2word = dict()
        
    def _words_iter(self):
        words_filename = os.path.join(PREPRO_DIR, self.basename + '_WORDS')
        with open(words_filename) as f:
            for line in f:
                line = clean_word(line.strip())
                if not line:
                    continue
                if line in STOP_WORDS:
                    continue
                yield line

    def _get_word_context_vector(self, word):
        all_contexts = []
        for context in self.offline.get_contexts(word):
            context = context.lower().strip().split(' ')
            context = [clean_word(w) for w in context]
            context = [w for w in context if w not in STOP_WORDS]
            all_contexts += context
        return self.dictionary.doc2bow(all_contexts)

    def __iter__(self):
        if self.corpus:
            for context in self.corpus:
                yield context
        else:
            i = count(0)
            for i, word in enumerate(self._words_iter()):
                self.docid2word[i] = word
                yield self._get_word_context_vector(word)

    def load(self, loaddir=PREPRO_DIR):
        load_path = os.path.join(loaddir, self.basename)
        self.dictionary = corpora.Dictionary.load(load_path + '.dict')
        self.corpus = corpora.MmCorpus(load_path + '.corpus')
        self.sim = similarities.SparseMatrixSimilarity.load(load_path + '.sms')

    def save(self, savedir=PREPRO_DIR):
        # create the corpus
        # store copies of the dictionary
        save_path = os.path.join(savedir, self.basename)
        self.dictionary = corpora.Dictionary([self._words_iter()])
        self.dictionary.save(save_path + '.dict')
        # ... of the corpus
        corpora.MmCorpus.serialize(save_path + '.corpus', self, id2word=self.dictionary)
        self.corpus = corpora.MmCorpus(save_path + '.corpus')
        self.sim = similarities.SparseMatrixSimilarity(self.corpus)
        # ... and of the similarity matrix
        self.sim.save(save_path + '.sms')

    def similar_to(self, word):
        def _max_dim(vec):
            return max(vec, key=lambda x: x[1])

        def _unvec(vec):
            return dict((self.dictionary[a], b) for a,b in vec)

        if not self.corpus:
            raise Exception("You must load() or save() first.")

        self.sim.numBest = 10
        vec = self._get_word_context_vector(word)
        n = 10
        retval = []
        for docid, score in islice(self.sim[vec], n):
            doc = self.corpus[docid]
            docword = self.docid2word[docid]
            retval.append(docword)
            print docid, docword, score
        return retval





if __name__ == '__main__':
    corpus = PennCorpus(DEFAULT_CORPUS)
    corpus.save()
    #corpus.load()
    print corpus.similar_to('coffee')

