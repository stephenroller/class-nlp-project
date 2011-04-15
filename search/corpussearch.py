
import operator
import os
import sys
import time

# actually half the context size--the lengh in either direction we go
CONTEXT_SIZE = 10
DEFAULT_CORPUS = '../corpora/wsj_untokenized.txt'

def get_contexts(query, corpusfilename=DEFAULT_CORPUS):
    if os.path.isdir(corpusfilename):
        return reduce(operator.concat,
                      [get_contexts(query, x)
                       for x in os.listdir(corpusfilename)])
    return reduce(operator.concat,
                  [__contexts_in_line(query, line)
                   for line in open(corpusfilename, 'r')])

def __contexts_in_line(query, line):
    '''might mangle the whitespace a bit but that shouldn't matter.
    '''
    lowerq = query.lower()
    words = line.split()
    res = []
    for i in range(len(words)):
        if words[i].lower() == lowerq:
            res.append(__get_ind_context(words, i))
    return res
    
def __get_ind_context(words, ind):
    lb = max(0, ind - CONTEXT_SIZE)
    ub = min(len(words), ind + CONTEXT_SIZE)
    return ' '.join(words[lb:ub])

if __name__ == '__main__':
    t = time.time()
    cxts = get_contexts('coffee')
    print('Search took %f seconds' % (time.time() - t))
    print('Found %d contexts:' % len(cxts))
    for c in cxts:
        print c

