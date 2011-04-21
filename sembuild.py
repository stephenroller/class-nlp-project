#!/usr/bin/env python

import sys
import os
import gensim

from nltk.corpus import WordNetCorpusReader

from corpus.indexedcorpus import IndexedCorpus
from corpus.searchenginecorpus import factory as search_engine_factory
from util import StorableDictionary, WordTransformer, STOP_WORDS, context_windows

DEFAULT_CORPUS = '/u/pichotta/penn-wsj-raw-all.txt'
#PREPRO_DIR = 'prepro-corpus/'
PREPRO_DIR = '/tmp/prepro-corpus/'

class VectorCorpus(object):
    """
    A class which takes a corpus object and turns it into
    an iterator of vectors.
    """
    def __init__(self, corpus):
        self.transformer = WordTransformer()
        self.corpus = corpus 
        self.docid2word = StorableDictionary()
        self.word2docid = StorableDictionary()
        self.dictionary = gensim.corpora.dictionary.Dictionary([self._words_iter()])

    def _words_iter(self):
        for word in self.corpus.get_unique_words():
            # words should already be transformed
            #word = self.transformer.transform(word)
            if word:
               yield word

    def _context_to_vector(self, word, large_context, ignore_word=False):
        large_context = self.transformer.tokenize(large_context)
        small_context = []
        for left, mid, right in context_windows(large_context, n=5):
            if mid == word:
                small_context += left + right
                if not ignore_word:
                    small_context.append(mid)

        return small_context

    def _get_word_context_vector(self, word, allowUpdate=False):
        all_contexts = []
        for context in self.corpus.get_contexts(word):
            all_contexts += self._context_to_vector(word, context)
        return self.dictionary.doc2bow(all_contexts, allowUpdate=allowUpdate)

    def __len__(self):
        return len(self.corpus)

    def __getitem__(self, query):
        return self._get_word_context_vector(query)

    def __iter__(self):
        for i, word in enumerate(self._words_iter()):
            self.docid2word[i] = word
            self.word2docid[word] = i
            yield self._get_word_context_vector(word)


class WebVectorCorpus(VectorCorpus):
    def __init__(self, preload_terms):
        search_corpus = search_engine_factory()
        self.terms = preload_terms
        VectorCorpus.__init__(self, search_corpus)
        for term in preload_terms:
            search_corpus.get_contexts(term)

    def _words_iter(self):
        return self.terms

    def _get_word_context_vector(self, word):
        return VectorCorpus._get_word_context_vector(self, word, allowUpdate=True)

    def __len__(self):
        return len(self.terms)


class CorpusSimilarityFinder(object):
    def __init__(self, store_path):
        self.storepath = store_path

    def load(self, vector_corpus):
        self.vector_corpus = vector_corpus
        self.dictionary = gensim.corpora.Dictionary.load(self.storepath + '.dict')
        self.docid2word = StorableDictionary.load(self.storepath + '.id2wrd')
        self.word2docid = StorableDictionary.load(self.storepath + '.wrd2id')
        self.tfidf = gensim.models.TfidfModel.load(self.storepath + '.tfidf')
        self.sim = gensim.similarities.SparseMatrixSimilarity.load(self.storepath + '.sms')

    def create(self, vector_corpus):
        self.vector_corpus = vector_corpus
        # create the dictionary
        self.dictionary = vector_corpus.dictionary
        # ... the corpus
        #gensim.corpora.MmCorpus.serialize(self.storepath + '.corpus', vector_corpus, id2word=self.dictionary)
        # ... the mappings from docids to words
        self.docid2word = vector_corpus.docid2word
        self.word2docid = vector_corpus.word2docid
        # ... the transformation of the corpus
        self.tfidf = gensim.models.TfidfModel(vector_corpus, id2word=self.dictionary, normalize=True)
        # ... and the similarity matrix
        self.sim = gensim.similarities.SparseMatrixSimilarity(self.tfidf[vector_corpus])

    def save(self):
        # save the corpus
        self.dictionary.save(self.storepath + '.dict')
        # ... the corpus
        # ... the mappings from docids to words
        self.docid2word.save(self.storepath + '.id2wrd')
        self.word2docid.save(self.storepath + '.wrd2id')
        # ... the transformation of the corpus
        self.tfidf.save(self.storepath + '.tfidf')
        # ... and the similarity matrix
        self.sim.save(self.storepath + '.sms')
    
    def similar_to(self, word, n=10):
        def _max_dim(vec):
            return max(vec, key=lambda x: x[1])

        def _unvec(vec):
            return dict((self.dictionary[a], b) for a,b in vec)

        wt = WordTransformer()
        word = wt.transform(word)
        self.sim.numBest = n
        vec = self.vector_corpus[word]
        vec = self.tfidf[vec]

        retval = []
        for docid, score in self.sim[vec]:
            docword = self.docid2word[docid]
            retval.append((docword, score))

        return retval

if __name__ == '__main__':
    corpus_path = sys.argv[1]
    if corpus_path.endswith('/'):
        corpus_path = corpus_path[:-1]
    store_path = os.path.join(PREPRO_DIR, os.path.basename(corpus_path))
    offline = IndexedCorpus(store_path + '.sqlite', corpus_path)
    vector_corpus = VectorCorpus(offline)
    corpus = CorpusSimilarityFinder(store_path)
    corpus.create(vector_corpus)
    corpus.save()

