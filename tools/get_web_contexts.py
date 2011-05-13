
import sqlite3
import sys
from config import *

def get_web_contexts(query):
    scrapeconn = sqlite3.connect(WEB_SCRAPE_DB_FILENAME)
    descrconn = sqlite3.connect(WEB_DESCR_DB_FILENAME)
    print '--------------------------------------'
    print 'descr contexts------------------------'
    print '--------------------------------------'
    print_contexts(scrapeconn, query)
    print '--------------------------------------'
    print 'descr contexts------------------------'
    print '--------------------------------------'
    print_contexts(descrconn, query)

def print_contexts(conn, query):
    c = conn.cursor()
    c.execute('''SELECT result FROM search_results WHERE word=?''', (query,))
    for x in c.fetchall():
        print x
    c.close()
    

if __name__ == '__main__':
    get_web_contexts(sys.argv[1])
