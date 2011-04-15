from pybing.query import WebQuery
import pprint
import sys
import time

class BingSearch:

    __APPID = '335CBE48CCCAF4A34652A3DDE7D2CE78FD3390DC'

    def __init__(self):
        pass

    def get_contexts(self, query):
        results = WebQuery(self.__APPID,
                           query=query).set_offset(0).set_count(50).execute()
        res = []
        for r in results:
            try:
                res.append(r.description)
            except AttributeError:
                pass
        return res

if __name__ == '__main__':
    print "Searching...."
    t = time.time()
    li = BingSearch().get_contexts('coffee')
    print '%d contexts returned.' % len(li)
    #pprint.pprint(li)
    print 'Took %f seconds.' % (time.time() - t)
