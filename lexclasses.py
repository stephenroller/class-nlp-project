#!/usr/bin/env python

lexclasses = [
    'person',
    'communication',
    'artifact',
    'act',
    'group',
    'food',
    'cognition',
    'posession',
    'location',
    'substance',
    'state',
    'time',
    'attribute',
    'object',
    'process',
    'Tops',
    'phenomenon',
    'event',
    'quantity',
    'motive',
    'animal',
    'body',
    'feeling',
    'shape',
    'plant',
    'relation'
]

from nltk.corpus import WordNetCorpusReader

wn16 = WordNetCorpusReader('/u/roller/working/nlp-project/wordnet/wordnet-1.6/dict/')

def all_hyp(synset):
    yield synset
    for h in synset.hypernyms():
        for h2 in all_hyp(synset):
            yield h2

def find_lexclass(synset):
    for h in all_hyp(synset):
        if h in lexclasses:
            return h
    return None



