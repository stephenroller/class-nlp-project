#!/usr/bin/env python

import re
import gensim

STOP_WORDS = ['the', 'an', 'a', 'to', 'of', 'and', 'in']
LARGE_STOP_WORDS = [
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am',
    'an', 'and', 'any', 'are', 'arent', 'as', 'at', 'be', 'because',
    'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'cannot', 'cant', 'could', 'couldnt', 'did', 'didnt', 'do', 'does',
    'doesnt', 'doing', 'dont', 'down', 'during', 'each', 'few', 'for',
    'from', 'further', 'had', 'hadnt', 'has', 'hasnt', 'have', 'havent',
    'having', 'he', 'hed', 'hell', 'her', 'here', 'heres', 'hers',
    'herself', 'hes', 'him', 'himself', 'his', 'how', 'hows', 'i', 'id',
    'if', 'ill', 'im', 'in', 'into', 'is', 'isnt', 'it', 'its',
    'itself', 'ive', 'lets', 'me', 'more', 'most', 'mustnt', 'my',
    'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only',
    'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over',
    'own', 'same', 'shant', 'she', 'shed', 'shell', 'shes', 'should',
    'shouldnt', 'so', 'some', 'such', 'than', 'that', 'thats', 'the',
    'their', 'theirs', 'them', 'themselves', 'then', 'there', 'theres',
    'these', 'they', 'theyd', 'theyll', 'theyre', 'theyve', 'this',
    'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very',
    'was', 'wasnt', 'we', 'wed', 'well', 'were', 'werent', 'weve',
    'what', 'whats', 'when', 'whens', 'where', 'wheres', 'which',
    'while', 'who', 'whom', 'whos', 'why', 'whys', 'with', 'wont',
    'would', 'wouldnt', 'you', 'youd', 'youll', 'your', 'youre',
    'yours', 'yourself', 'yourselves', 'youve'
]
STOP_WORDS = LARGE_STOP_WORDS

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


