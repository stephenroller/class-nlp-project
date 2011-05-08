#!/usr/bin/env python

from nltk.corpus import WordNetCorpusReader
import sys

from sembuild import * 

# k = number of web similar words
K = 3
# n = number of small corpus similar words
N = 9
# how much to discount each progressive synset (so the nth vote will be
# discounted by VOTE_DAMPING_COEFF ** n).
VOTE_DAMPING_COEFF = 0.7
# set to false if you don't wanna use the web to go from N -> K vectors
SHOULD_USE_WEB_FOR_PARING=True
SHOULD_USE_WEB_FOR_PARING=False
# set to false if you don't wanna use the web for initial vector enrichment.
SHOULD_USE_WEB_FOR_INIT_VEC_ENRICHMENT=True
# which wordnet version should we use?
WORDNET_DIR = 'wordnet/1.6/'

_wn = WordNetCorpusReader(WORDNET_DIR)

def get_test_set(filename):
    words = []
    with open(filename) as f:
        for line in f:
            word = line.strip()
            words.append(word)
    return sorted(words)

def calc_correct(corpus, word, exclude_words=[]):
    print "Attempting to classify '%s'" % word
    wn = _wn
    votes = dict()
    word = WordTransformer().transform(word)
    similar_words = _get_similar_noun_conf_pairs(corpus, word)
    if SHOULD_USE_WEB_FOR_PARING:
        justwords = [x[0] for x in similar_words]
        print "Similar words: " + ', '.join(justwords)
        if not similar_words[1:]:
            return None
        print "Fetching online corpuses..."
        wvc = WebVectorCorpus(justwords)
        webcorp = CorpusSimilarityFinder('/tmp/webcorpus.txt')
        webcorp.create(wvc)
        similar_words = webcorp.similar_to(word, n=K+1)
        print "Web similar words: " + ', '.join(w for w,s in similar_words[1:])
    else:
        similar_words = similar_words[:K+1]

    for near_word, score in similar_words[1:]:
        print near_word
        for synset in wn.synsets(near_word):
            print "\t%s (%s)" % (str(synset), synset.lexname)
        curCoeff = 1.0
        for supersense in filter(_is_noun_synset, wn.synsets(near_word)):
            votes[supersense.lexname] = votes.get(supersense.lexname, 0) + (curCoeff * score)
            curCoeff *= VOTE_DAMPING_COEFF

    guesses = sorted(votes.keys(), key=votes.__getitem__, reverse=True)
    for guess in guesses:
        print votes[guess], guess
    for g in guesses:
        if 'noun' in g: return g
    return None

def _is_noun_synset(synset):
    return 'noun' in synset.lexname

def _get_similar_noun_conf_pairs(corpus, word):
    # if we're using the web, get sufficiently more than N similar words:
    sims = sorted(corpus.similar_to(word,
                                    n=2*N+1,
                                    should_enrich_with_web=SHOULD_USE_WEB_FOR_INIT_VEC_ENRICHMENT),
                  key=lambda x: x[1],
                  reverse=True)
    sims = filter(_has_noun_sense, sims)
    return sims[:N+1]

def _has_noun_sense(word_conf_pair):
    for synset in list(_wn.synsets(word_conf_pair[0])):
        if 'noun' in synset.lexname: return True
    return False

def test_categorizer(corpus, test_filename):
    wn = _wn
    test_words = get_test_set(test_filename)
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
            if guess is not None:
                num_guessed += 1
            num_total += 1
        except KeyError:
            # wordnet word didn't appear in our corpus
            print "...'%s' not in the corpus" % test_word
            continue

    print "-" * 60
    print "Precision: %.2f%% (%d/%d)" % (100 * float(num_correct) / num_guessed, num_correct, num_guessed)
    print "Recall: %.2f%% (%d/%d)" % (100 * float(num_correct) / num_total, num_correct, num_total)



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "We need a test filename as the 2nd command line param."
        sys.exit(2)

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
    test_categorizer(corpus, sys.argv[2])

