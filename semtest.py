#!/usr/bin/env python

from sembuild import * 

def calc_correct(corpus, word):
    wn = WordNetCorpusReader('wordnet/1.6/')
    votes = dict()
    similar_words = corpus.similar_to(word, n=20)
    print "Similar words: " + ', '.join(similar_words)
    print

    print "Fetching online corpuses..."
    wvc = WebVectorCorpus(similar_words)
    webcorp = CorpusSimilarityFinder('/tmp/webcorpus.txt')
    webcorp.create(wvc)

    similar_words = webcorp.similar_to(word, n=5)
    print "Web similar words: " + ', '.join(similar_words)
    print

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
    corpus_path = DEFAULT_CORPUS
    store_path = os.path.join(PREPRO_DIR, os.path.basename(corpus_path))
    corpus = CorpusSimilarityFinder(store_path)
    try:
        corpus.load()
    except IOError:
        print "io error. did you run sembuild.py first?"
        sys.exit(1)
    calc_correct(corpus, word)

