#!/usr/bin/env python

import itertools
import sys
import os
import gensim

from nltk.corpus import WordNetCorpusReader

from indexedcorpus import IndexedCorpus
from searchenginecorpus import factory as search_engine_factory
from util import StorableDictionary, WordTransformer, STOP_WORDS, context_windows

from config import *

def _context_to_vector(word, large_context, ignore_word=False):
    large_context = WordTransformer().tokenize(large_context)
    small_context = []
    for left, mid, right in context_windows(large_context, n=5):
        if mid == word:
            small_context += left + right
            if not ignore_word:
                small_context.append(mid)

    return small_context


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
        self.passes = 0

    def _words_iter(self):
        for word in self.corpus.get_unique_words():
            # words should already be transformed
            #word = self.transformer.transform(word)
            if word:
               yield word

    def _get_word_context_vector(self, word, allowUpdate=False):
        all_contexts = []
        for context in self.corpus.get_contexts(word):
            all_contexts += _context_to_vector(word, context)
        return self.dictionary.doc2bow(all_contexts, allowUpdate=allowUpdate)

    def __len__(self):
        return len(self.corpus)

    def __getitem__(self, query):
        return self._get_word_context_vector(query)

    def __iter__(self):
        from datetime import datetime
        from terminal import ProgressBar
        pb = ProgressBar('green', width=20)
        self.passes += 1
        
        start = datetime.now()

        num_docs = float(len(self))
        for i, word in enumerate(self._words_iter()):
            self.docid2word[i] = word
            self.word2docid[word] = i
            if (i+1) % 10 == 0:
                eta = (datetime.now() - start) * int((num_docs - i)) // (i + 1)
                pct = i/num_docs
                msg = "corpus pass #%d / ETA %s" % (self.passes, eta)
                pb.render(pct, msg)

            yield self._get_word_context_vector(word)

        runtime = datetime.now() - start
        msg = "completed pass #%d in %s" % (self.passes, runtime)
        pb.render(1, msg)

search_corpus = None
def parallel_hack(term):
    search_corpus.get_contexts(term)

class WebVectorCorpus(VectorCorpus):
    def __init__(self, preload_terms):
        global search_corpus
        search_corpus = search_engine_factory()
        self.terms = preload_terms
        VectorCorpus.__init__(self, search_corpus)
        from multiprocessing import Pool
        p = Pool(NUM_PROCESSES)
        p.map(parallel_hack, preload_terms)

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
    
    def similar_to(self, word, n=10, should_enrich_with_web=False):
        def _max_dim(vec):
            return max(vec, key=lambda x: x[1])

        def _unvec(vec):
            return dict((self.dictionary[a], b) for a,b in vec)

        wt = WordTransformer()
        word = wt.transform(word)
        self.sim.numBest = n
        vec = self.vector_corpus[word]
        if(should_enrich_with_web): self._enrich_vec_with_web(vec, word)
        vec = self.tfidf[vec]

        retval = []
        for docid, score in self.sim[vec]:
            docword = self.docid2word[docid]
            retval.append((docword, score))

        return retval

    def _enrich_vec_with_web(self, vec, word):
        webctxs = [_context_to_vector(word, c, True)
                   for c in search_engine_factory().get_contexts(word)]
        print 'adding %d contexts from web to query vector.' % len(webctxs)
        webbowvec = self.vector_corpus.dictionary.doc2bow(itertools.chain(*webctxs),
                                                          allowUpdate=False)
        return self._combine_bow_vecs(vec, webbowvec)

    def _combine_bow_vecs(self, v1, v2):
        resdict = dict(v1)
        for w,c in v2:
            if w not in resdict: resdict[w] = 0
            resdict[w] += c
        return resdict.items()
        

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

