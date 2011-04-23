
import random
import sys

TESTSET_SIZE = 100

def is_good(word):
    return word.isalpha()

def select_rand(filename):
    words = filter(is_good, [x.strip() for x in open(filename,'r').readlines()])
    for w in select_testset(words):
        print w

def select_testset(words):
    res = []
    for i in range(TESTSET_SIZE):
        res.append(words.pop(random.randint(0,len(words)-1)))
    return res

if __name__ == '__main__':
    select_rand(sys.argv[1])
