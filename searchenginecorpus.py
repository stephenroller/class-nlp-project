"""module to ask bing for N<=1000 snippets in which a query appears."""

from dist.BeautifulSoup import BeautifulSoup
from pybing.query import WebQuery
import socket
import sqlite3
import os
import re
import sys
import time
import traceback
from urllib2 import urlopen
from multifetcher import ParallelFetcher
from multiprocessing import Lock

from config import *

search_engine_corpus = None

#set timeout for urllib2 calls
socket.setdefaulttimeout(URLLIB_TIMEOUT)

def factory():
    global search_engine_corpus
    if not search_engine_corpus:
        search_engine_corpus = SearchEngineCorpus()
    return search_engine_corpus

class SearchEngineCorpus(object):
    def __init__(self):
        self._init_conns()
        self._queries_made = 0
        self.lock = Lock()

    def get_contexts(self, query, scrape_override=None):
        """returns a list of contexts in which a query appears.

        This returns either the descriptions from bing or contexts form the
        actual site we scrape ourselves.

        scrape_override is funny. If None, we use the default behavior. If it
        is True, we override default behavior and get contexts by scraping. If
        it's False then we override default behavior and get contexts with
        descriptions.

        IMPORTANTLY, if scrape_override has a non-None value, we'll ignore the
        cache.

        It is entirely possible that the query actually appears multiple
        times in a returned context, or not at all (if a morphologically
        similar form of the word appears, for example).
        """
        if scrape_override:
            should_scrape = scrape_override
        else:
            should_scrape = SHOULD_SCRAPE_SITES
        if should_scrape:
            conn = self._scrape_conn
        else:
            conn = self._descr_conn
        ctxs = self._get_results_from_db(query, conn)
        if len(ctxs) > 0:
            return ctxs
        results = WebQuery(APPID, query=query).set_offset(0).set_count(50).execute()
        if should_scrape:
            text_results = self._scrape_text_from_sites(results, query)
        else:
            text_results = self._get_text_from_descriptions(results)
        self._add_results_to_db(query, conn, text_results)
        return text_results

    def _scrape_text_from_sites(self, results, query):
        res = []
        results = results[:NUM_PAGES_TO_SCRAPE]
        try:
            pf = ParallelFetcher([r.url for r in results])
            for r in results:
                try:
                    txt = pf[r.url]
                    res += self._get_contexts_from_html(txt, query)
                except Exception, e:
                    sys.stderr.write(str(e) + '\n')
        except Exception:
            traceback.print_exc()
        return res

    def _get_contexts_from_html(self, html, query):
        res = []
        text = ' '.join(filter(self._visible,
                               BeautifulSoup(html).findAll(text=True)))
        query = query.lower()
        tokens = text.split()
        half_win_size = CONTEXT_WORD_WIDTH / 2
        for i,t in enumerate(tokens):
            if t.lower() == query:
                lb = max(0,i - half_win_size)
                ub = min(len(tokens), i + half_win_size)
                res.append(' '.join(tokens[lb:ub]))
        return res

    # cribbed from http://bit.ly/mhN0PE
    def _visible(self, element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', str(element)):
            return False
        return True

    def _get_text_from_descriptions(self, bingresults):
        """Takes a BingResultSet, returns a list of strings"""
        res = []
        try:
            for r in bingresults:
                try: res.append(r.description)
                except AttributeError: pass
        except Exception:
            traceback.print_exc()
        return res

    def _get_results_from_db(self, query, conn):
        """returns a (possibly empty) list of results if we've done this query"""
        self.lock.acquire()
        c = conn.cursor()
        c.execute('''SELECT result FROM search_results WHERE word=?''', (query,))
        res = [x[0] for x in c.fetchall()]
        c.close()
        self.lock.release()
        return res

    def _add_results_to_db(self, query, conn, results):
        self.lock.acquire()
        c = conn.cursor()
        results.append('')
        c.executemany('''INSERT INTO search_results VALUES (?,?)''',
                      [(query, r) for r in results])
        c.close()
        conn.commit()
        self.lock.release()

    def _init_conns(self):
        """initialize connections to sqlite, stores as instance vars"""
        self._scrape_conn = self._init_conn(WEB_SCRAPE_DB_FILENAME)
        self._descr_conn = self._init_conn(WEB_DESCR_DB_FILENAME)

    def _init_conn(self, filename):
        if not os.path.exists(filename):
            return self._init_db(filename)
        return sqlite3.connect(filename)

    def _init_db(self, filename):
        print 'Initializing SearchEngineCorpus DB at %s...' % filename
        conn = sqlite3.connect(filename)
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
    li = SearchEngineCorpus().get_contexts(q, SHOULD_ENRICH_BY_SCRAPING)
    print 'Took %f seconds.' % (time.time() - t)
    print '%d contexts returned.' % len(li)
#    for c in li: print c
