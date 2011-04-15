from pybing.query import WebQuery
import pprint
import sys
import time

APPID = '335CBE48CCCAF4A34652A3DDE7D2CE78FD3390DC'

def get_contexts(query):
    results = WebQuery(APPID,
                       query=query).set_offset(0).set_count(50).execute()
    res = []
    for r in results:
        try:
            res.append(r.description)
        except AttributeError:
            pass
    return res

if __name__ == '__main__':
    q = 'coffee'
    if len(sys.argv) > 1:
        q = sys.argv[1]
    print "Searching...."
    t = time.time()
    li = get_contexts(q)
    print 'Took %f seconds.' % (time.time() - t)
    print '%d contexts returned.' % len(li)
    #pprint.pprint(li)
