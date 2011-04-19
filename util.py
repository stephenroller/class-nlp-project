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

    def tokenize(self, line):
        "Used for converting from a string of text to a list of tokens"
        if line == '.start\n':
            return []
        line = line.strip()
        words = line.split()
        words = [self.transform(w) for w in words]
        words = [w for w in words if w]
        return words

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


def context_windows(wordlist, n=11):
    """
    Produces a 'sliding context window' around each word
    in a wordlist, in n different directions. That is, 
    if wordlist is:

        A B C D E F

    and n = 2, then this method will *yield*:

        (A, [B C])
        (B, [A C D])
        (C, [A B D E])
        (D, [B C E F]),
        (E, [C D F]),
        (F, [D E]).
    """

    # make sure it's actually a list
    wordlist = list(wordlist)

    for i in xrange(len(wordlist)):
        j = i - n
        if j < 0:
            j = 0
        yield (wordlist[j:i], wordlist[i], wordlist[i+1:i+n+1])


