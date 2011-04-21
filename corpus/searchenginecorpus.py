"""module to ask bing for N<=1000 snippets in which a query appears."""

from pybing.query import WebQuery
import sqlite3
import os
import sys
import time

from gensim.utils import SaveLoad

APPID = '335CBE48CCCAF4A34652A3DDE7D2CE78FD3390DC'
DB_FILENAME = '/tmp/webcorpus.sqlite'

search_engine_corpus = None

def factory():
    global search_engine_corpus
    if not search_engine_corpus:
        search_engine_corpus = SearchEngineCorpus()
    return search_engine_corpus

class SearchEngineCorpus(object):
    def __init__(self):
        self._conn = self._init_conn()
        self._queries_made = 0

    def get_contexts(self, query):
        """returns a list of contexts in which a query appears.

        It is entirely possible that the query actually appears multiple
        times in a returned context, or not at all (if a morphologically
        similar form of the word appears, for example).
        """
        ctxs = self._get_results_from_db(query)
        if len(ctxs) > 0:
            return ctxs
        results = WebQuery(APPID, query=query).set_offset(0).set_count(50).execute()
        text_results = self._get_text_from_bing_results(results)
        self._add_results_to_db(query, text_results)
        return text_results

    def _get_text_from_bing_results(self, bingresults):
        """Takes a BingResultSet, returns a list of strings"""
        res = []
        for r in bingresults:
            try: res.append(r.description)
            except AttributeError: pass
        return res

    def _get_results_from_db(self, query):
        """returns a (possibly empty) list of results if we've done this query"""
        c = self._conn.cursor()
        c.execute('''SELECT result FROM search_results WHERE word=?''', (query,))
        res = [x[0] for x in c.fetchall()]
        c.close()
        return res

    def _add_results_to_db(self, query, results):
        c = self._conn.cursor()
        c.executemany('''INSERT INTO search_results VALUES (?,?)''',
                      [(query, r) for r in results])
        c.close()
        self._conn.commit()

    def _init_conn(self):
        """initialize connection to sqlite"""
        if not os.path.exists(DB_FILENAME):
            return self._init_db()
        return sqlite3.connect(DB_FILENAME)

    def _init_db(self):
        print 'Initializing SearchEngineCorpus DB at %s...' % DB_FILENAME
        conn = sqlite3.connect(DB_FILENAME)
        c = conn.cursor()
        # so if a search returns no results we're doomed to repeat it. oh well!
        c.execute('''CREATE TABLE search_results(
                        word INTEGER,
                        result TEXT)''')
        c.execute('''CREATE INDEX resultindex ON search_results(word)''')
        c.close()
        conn.commit()
        return conn


if __name__ == '__main__':
    q = 'coffee'
    if len(sys.argv) > 1:
        q = sys.argv[1]
    print "Searching...."
    t = time.time()
    li = SearchEngineCorpus().get_contexts(q)
    print 'Took %f seconds.' % (time.time() - t)
    print '%d contexts returned.' % len(li)
