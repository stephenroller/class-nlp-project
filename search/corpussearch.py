
import operator
import os
import sys
import time

class CorpusSearch:

    '''actually half the context size--the lengh in either direction we go'''
    __CONTEXT_SIZE = 10

    __DEFAULT_CORPUS = '../corpora/wsj_untokenized.txt'
    
    def __init__(self):
        pass

    def get_contexts(self, query, corpusfilename=None):
        if not corpusfilename:
            corpusfilename = self.__DEFAULT_CORPUS
        if os.path.isdir(corpusfilename):
            return reduce(operator.concat,
                          [self.get_contexts(query, x)
                           for x in os.listdir(corpusfilename)])
        return reduce(operator.concat,
                      [self.__contexts_in_line(query, line)
                       for line in open(corpusfilename, 'r')])

    def __contexts_in_line(self, query, line):
        '''might mangle the whitespace a bit but that shouldn't matter.
        '''
        lowerq = query.lower()
        words = line.split()
        res = []
        for i in range(len(words)):
            if words[i].lower() == lowerq:
                res.append(self.__get_ind_context(words, i))
        return res
        
    def __get_ind_context(self, words, ind):
        lb = max(0, ind - self.__CONTEXT_SIZE)
        ub = min(len(words), ind + self.__CONTEXT_SIZE)
        return ' '.join(words[lb:ub])

if __name__ == '__main__':
    t = time.time()
    cxts = CorpusSearch().get_contexts('coffee')
    print('Search took %f seconds' % (time.time() - t))
    print('Found %d contexts:' % len(cxts))
    for c in cxts:
        print c

