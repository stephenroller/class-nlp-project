"""module to ask bing for N<=1000 snippets in which a query appears."""

from pybing.query import WebQuery
import pprint
import sys
import time

from gensim.utils import SaveLoad

APPID = '335CBE48CCCAF4A34652A3DDE7D2CE78FD3390DC'

class SearchEngineCorpus(SaveLoad):
    def __init__(self):
        self.cache = dict()

    def get_contexts(self, query):
        """returns a list of contexts in which a query appears.

        It is entirely possible that the query actually appears multiple
        times in a returned context, or not at all (if a morphologically
        similar form of the word appears, for example).
        """
        if query in self.cache:
            return self.cache[query]

        results = WebQuery(APPID,
                           query=query).set_offset(0).set_count(50).execute()
        res = []
        for r in results:
            try:
                res.append(r.description)
            except AttributeError:
                pass

        self.cache[query] = res
        return res

if __name__ == '__main__':
    q = 'coffee'
    if len(sys.argv) > 1:
        q = sys.argv[1]
    print "Searching...."
    t = time.time()
    li = SearchEngineCorpus().get_contexts(q)
    print 'Took %f seconds.' % (time.time() - t)
    print '%d contexts returned.' % len(li)
    #pprint.pprint(li)
