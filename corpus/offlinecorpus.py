"""Module to search for all occurrences of a string in a corpus."""

import operator
import os
import re
import sys
import time

# actually half the context size--the lengh in either direction we go
CONTEXT_SIZE = 10
DEFAULT_CORPUS = '/u/pichotta/penn-wsj-raw-all.txt'

class OfflineCorpus:

    def get_contexts(self, query, corpusfilename=DEFAULT_CORPUS):
        """returns all contexts in which a query appears in a corpus."""
        if os.path.isdir(corpusfilename):
            return reduce(operator.concat,
                          [self.get_contexts(query, x)
                           for x in os.listdir(corpusfilename)])
        return reduce(operator.concat,
                      [self._contexts_in_line(query, line)
                       for line in open(corpusfilename, 'r')])

    def _contexts_in_line(self, query, line):
        """might mangle the whitespace a bit but that shouldn't matter"""
        if self._should_ignore_line(line): return []
        cleanq = self._cleanword(query)
        words = line.split()
        res = []
        for i in range(len(words)):
            if self._cleanword(words[i]) == cleanq:
                res.append(self._get_ind_context(words, i))
        return res

    def _should_ignore_line(self, line):
        return line.strip() == '.START'

    def _cleanword(self, w):
        return re.sub(r'\W', '', w.lower())

    def _get_ind_context(self, words, ind):
        lb = max(0, ind - CONTEXT_SIZE)
        ub = min(len(words), ind + CONTEXT_SIZE)
        return ' '.join(words[lb:ub])

if __name__ == '__main__':
    q = 'coffee'
    if len(sys.argv) > 1:
        q = sys.argv[1]
    t = time.time()
    cxts = OfflineCorpus().get_contexts(q)
    print('Search took %f seconds' % (time.time() - t))
    print('Found %d contexts:' % len(cxts))
    for c in cxts:
        print c
