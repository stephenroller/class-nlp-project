#!/usr/bin/env python

import sys
import os
import gensim

from nltk.corpus import WordNetCorpusReader
from nltk.stem.porter import PorterStemmer

from corpus.offlinecorpus import clean_word, OfflineCorpus

DEFAULT_CORPUS = '/u/pichotta/penn-wsj-raw-all.txt'
PREPRO_DIR = 'prepro-corpus/'
STOP_WORDS = ['the', 'an', 'a', '.start', 'to', 'of', 'and']


class WordTransformer(object):
    def __init__(self):
        self.stemmer = PorterStemmer()

    def transform(self, word):
        # stems, lowercases and checks if stopword
        # returns None if the word should be ignored.
        w = word.lower().strip()
        w = clean_word(w)
        #w = self.stemmer.stem(w)
        if w in STOP_WORDS:
            return None
        return w


class StorableDictionary(dict, gensim.utils.SaveLoad):
    pass


class PennCorpus(object):
    def __init__(self, offline):
        self.transformer = WordTransformer()
        self.offline = offline
        self.docid2word = StorableDictionary()
        self.word2docid = StorableDictionary()
        self.dictionary = gensim.corpora.dictionary.Dictionary([self._words_iter()])

    def _words_iter(self):
        for word in self.offline.get_unique_words():
            word = self.transformer.transform(word)
            if word:
               yield word

    def _context_to_vector(self, word, context, ignore_word=False):
        context = context.lower().strip().split(' ')
        context = [clean_word(w) for w in context]
        if ignore_word:
            # optionally, we can exclude the word itself from the context
            # vector
            context = [w for w in context if w != word]
        context = [self.transformer.transform(w) for w in context]
        # filter out words we're supposed to ignore
        context = [w for w in context if w]
        return context


    def _get_word_context_vector(self, word):
        all_contexts = []
        for context in self.offline.get_contexts(word):
            all_contexts += self._context_to_vector(word, context)
        return self.dictionary.doc2bow(all_contexts)

    def __iter__(self):
        for i, word in enumerate(self._words_iter()):
            self.docid2word[i] = word
            self.word2docid[word] = i
            yield self._get_word_context_vector(word)

def create_index(filename, savedir=PREPRO_DIR):
    basename = os.path.basename(filename)

class CorpusSimilarityFinder(object):
    def __init__(self, filename, store_dir=PREPRO_DIR):
        self.filename = filename
        basename = os.path.basename(filename)
        self.storepath = os.path.join(store_dir, basename)

    def load(self):
        self.dictionary = gensim.corpora.Dictionary.load(self.storepath + '.dict')
        self.corpus = gensim.corpora.MmCorpus(self.storepath + '.corpus')
        self.docid2word = StorableDictionary.load(self.storepath + '.id2wrd')
        self.word2docid = StorableDictionary.load(self.storepath + '.wrd2id')
        self.tfidf = gensim.models.TfidfModel.load(self.storepath + '.tfidf')
        self.sim = gensim.similarities.SparseMatrixSimilarity.load(self.storepath + '.sms')

    def save(self):
        # create the corpus
        offline = OfflineCorpus()
        corpus_reader = PennCorpus(offline)
        self.dictionary = corpus_reader.dictionary
        self.dictionary.save(self.storepath + '.dict')
        print self.dictionary
        # ... of the corpus
        gensim.corpora.MmCorpus.serialize(self.storepath + '.corpus', corpus_reader, id2word=corpus_reader.dictionary)
        self.corpus = gensim.corpora.MmCorpus(self.storepath + '.corpus')
        # ... of the mappings from docids to words
        self.docid2word = corpus_reader.docid2word
        self.docid2word.save(self.storepath + '.id2wrd')
        self.word2docid = corpus_reader.word2docid
        self.word2docid.save(self.storepath + '.wrd2id')
        # ... transformation of the corpus
        self.tfidf = gensim.models.TfidfModel(self.corpus, id2word=self.dictionary, normalize=True)
        self.tfidf.save(self.storepath + '.tfidf')
        # ... and of the similarity matrix
        self.sim = gensim.similarities.SparseMatrixSimilarity(self.tfidf[self.corpus])
        self.sim.save(self.storepath + '.sms')
    
    def similar_to(self, word):
        def _max_dim(vec):
            return max(vec, key=lambda x: x[1])

        def _unvec(vec):
            return dict((self.dictionary[a], b) for a,b in vec)

        if not self.corpus:
            raise Exception("You must load() or save() first.")

        wt = WordTransformer()
        word = wt.transform(word)
        n = 10
        self.sim.numBest = n
        vec = self.corpus[self.word2docid[word]]
        vec = self.tfidf[vec]

        retval = []
        for docid, score in self.sim[vec]:
            doc = self.corpus[docid]
            docword = self.docid2word[docid]
            retval.append(docword)
            #print docid, docword, score
        return retval

if __name__ == '__main__':
    corpus = CorpusSimilarityFinder(DEFAULT_CORPUS)
    corpus.save()

