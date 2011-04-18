#!/usr/bin/env python

import re
import gensim

STOP_WORDS = ['the', 'an', 'a', 'to', 'of', 'and', 'in']

class WordTransformer(object):
    def __init__(self, stemming=False):
        self.stem_enabled = stemming
        if stemming:
            from nltk.stem.porter import PorterStemmer
            self.stemmer = PorterStemmer()

    def transform(self, word):
        # stems, lowercases and checks if stopword
        # returns None if the word should be ignored.
        w = word.lower().strip()
        w = clean_word(w)
        if self.stem_enabled:
            w = self.stemmer.stem(w)
        if w in STOP_WORDS:
            return None
        return w


class StorableDictionary(dict, gensim.utils.SaveLoad):
    pass


def clean_word(w):
    w = w.replace('-', '_')
    return re.sub(r'\W', '', w.lower())

