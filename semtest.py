#!/usr/bin/env python

from sembuild import * 

def calc_correct(corpus, word):
    wn = WordNetCorpusReader('wordnet/1.6/')
    votes = dict()
    similar_words = corpus.similar_to(word)
    print "Similar words: " + ', '.join(similar_words)
    for near_word in similar_words[1:]:
        for synset in wn.synsets(near_word):
            votes[synset.lexname] = votes.get(synset.lexname, 0) + 1

    ranked = sorted(votes.keys(), key=votes.__getitem__, reverse=True)
    for guess in ranked:
        print votes[guess], guess

    synsets = [ss.lexname for ss in wn.synsets(word)]
    print "correct answer:", ", ".join(synsets)
    guesses = ranked[:len(synsets)]
    numcorrect = len([True for g in guesses if g in synsets])
    print "% correct:", 100*float(numcorrect)/len(synsets)

if __name__ == '__main__':
    word = sys.argv[1]
    corpus = CorpusSimilarityFinder(DEFAULT_CORPUS)
    try:
        corpus.load()
    except IOError:
        print "io error. did you run sembuild.py first?"
        sys.exit(1)
    calc_correct(corpus, word)

