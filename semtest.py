#!/usr/bin/env python

from nltk.corpus import WordNetCorpusReader
import sys

from sembuild import * 

# k = number of web similar words
K = 3
# n = number of small corpus similar words
N = 10
# should we enrich our query vector with web search results?
ENRICH_WITH_WEB = True


_wn = WordNetCorpusReader('wordnet/1.6/')


def get_test_set(r=0.10):
    words = []
    with open('teststs/small-testset') as f:
        for line in f:
            word = line.strip()
            words.append(word)
    return sorted(words)

def calc_correct(corpus, word, exclude_words=[]):
    print "Attempting to classify '%s'" % word
    wn = WordNetCorpusReader('wordnet/1.6/')
    votes = dict()
    word = WordTransformer().transform(word)
    similar_words = _get_similar_nouns(corpus, word)
    print "Similar words: " + ', '.join(similar_words)
    if not similar_words[1:]:
        return None

    print "Fetching online corpuses..."
    wvc = WebVectorCorpus(similar_words)
    webcorp = CorpusSimilarityFinder('/tmp/webcorpus.txt')
    webcorp.create(wvc)

    similar_words = webcorp.similar_to(word, n=K+1)
    print "Web similar words: " + ', '.join(w for w,s in similar_words[1:])

    for near_word, score in similar_words[1:]:
        print near_word
        for synset in wn.synsets(near_word):
            print "\t%s (%s)" % (str(synset), synset.lexname)
        for supersense in set([x.lexname for x in wn.synsets(near_word)]):
            votes[synset.lexname] = votes.get(synset.lexname, 0) + score

    guesses = sorted(votes.keys(), key=votes.__getitem__, reverse=True)
    for guess in guesses:
        print votes[guess], guess
    for g in guesses:
        if 'noun' in g: return g
    return None

def _get_similar_nouns(corpus, word):
    # get sufficiently more than N similar words:
    sims = sorted(corpus.similar_to(word, n=2*N+1, should_enrich_with_web=ENRICH_WITH_WEB),
                  key=lambda x: x[1],
                  reverse=True)
    sims = filter(_has_noun_sense, [w for w,s in sims])
    return sims[:N+1]

def _has_noun_sense(word):
    for synset in list(_wn.synsets(word)):
        if 'noun' in synset.lexname: return True
    return False

def test_categorizer(corpus):
    wn = WordNetCorpusReader('wordnet/1.6/')
    test_words = get_test_set()
    num_correct = 0
    num_guessed = 0
    num_total = 0
    for test_word in test_words:
        try:
            supersenses = list(set([x.lexname for x in wn.synsets(test_word)]))
            if len(supersenses) != 1:
                continue
            correct_answer = supersenses[0]
            print "Looking for '%s'" % test_word
            guess = calc_correct(corpus, test_word, test_words)
            print "%s: %s (correct: %s)" % (test_word, guess or "??", correct_answer)
            print 
            if guess == correct_answer:
                num_correct += 1
            if guess != None:
                num_guessed += 0
            num_total += 1
        except KeyError:
            # wordnet word didn't appear in our corpus
            print "...'%s' not in the corpus" % test_word
            continue

    print "-" * 60
    print "Precision: %.2f%%" % (100 * float(num_correct) / num_guessed)
    print "Recall: %.2f%%" % (100 * float(num_correct) / num_total)



if __name__ == '__main__':
    corpus_path = sys.argv[1]
    if corpus_path.endswith('/'):
        corpus_path = corpus_path[:-1]
    store_path = os.path.join(PREPRO_DIR, os.path.basename(corpus_path))
    corpus = CorpusSimilarityFinder(store_path)
    try:
        offline = IndexedCorpus(store_path + '.sqlite', corpus_path)
        vector_corpus = VectorCorpus(offline)
        corpus.load(vector_corpus)
    except IOError:
        print "io error. did you run sembuild.py first?"
        sys.exit(1)
    if len(sys.argv) == 3:
        print calc_correct(corpus, sys.argv[2])
    else:
        test_categorizer(corpus)

