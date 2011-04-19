#!/usr/bin/env python

from sembuild import * 

# k = number of web similar words
K = 5
# n = number of small corpus similar words
N = 20

def get_test_set(r=0.10):
    words = []
    with open('wordnet/single_testset.16') as f:
        for line in f:
            word = line.strip()
            words.append(word)
    return sorted(words)

def calc_correct(corpus, word, exclude_words=[]):
    print "Attempting to classify '%s'" % word
    wn = WordNetCorpusReader('wordnet/1.6/')
    votes = dict()
    word = WordTransformer().transform(word)
    similar_words = corpus.similar_to(word, n=N)
    print "Similar words: " + ', '.join(similar_words)
    if not similar_words:
        return None

    print "Fetching online corpuses..."
    wvc = WebVectorCorpus(similar_words)
    webcorp = CorpusSimilarityFinder('/tmp/webcorpus.txt')
    webcorp.create(wvc)

    similar_words = webcorp.similar_to(word, n=K)
    print "Web similar words: " + ', '.join(similar_words)

    for near_word in similar_words[1:]:
        for synset in wn.synsets(near_word):
            votes[synset.lexname] = votes.get(synset.lexname, 0) + 1

    ranked = sorted(votes.keys(), key=votes.__getitem__, reverse=True)
    for guess in ranked:
        print votes[guess], guess

    synsets = [ss.lexname for ss in wn.synsets(word)]
    guesses = ranked[:len(synsets)]
    return guesses and guesses[0] or None

def test_categorizer(corpus):
    wn = WordNetCorpusReader('wordnet/1.6/')
    test_words = get_test_set()
    num_correct = 0
    num_guessed = 0
    num_total = 0
    for test_word in test_words:
        try:
            synsets = wn.synsets(test_word)
            if len(synsets) != 1:
                continue
            correct_answer = synsets[0].lexname
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
    corpus_path = DEFAULT_CORPUS
    store_path = os.path.join(PREPRO_DIR, os.path.basename(corpus_path))
    corpus = CorpusSimilarityFinder(store_path)
    try:
        corpus.load()
    except IOError:
        print "io error. did you run sembuild.py first?"
        sys.exit(1)
    test_categorizer(corpus)

