#!/usr/bin/env python

import sys
import urllib2
from multiprocessing import Pool

NUM_PROCESSES = 10

def _fetch(url):
    try:
        f = urllib2.urlopen(url)
        retval = (url, f.read())
        f.close()
        return retval
    except KeyboardInterrupt, e:
        sys.exit(100)
    except Exception, e:
        sys.stderr.write(str(e) + '\n')
        return (url, "")

class ParallelFetcher(object):
    def __init__(self, urls):
        self.urls = urls
        self.pool = Pool(NUM_PROCESSES)
        self.results = dict(self.pool.map(_fetch, urls))

    def __getitem__(self, url):
        return self.results[url]

if __name__ == '__main__':
    urls = [
        "http://google.com",
        "http://reddit.com",
        "http://stephenroller.com",
        "http://news.ycombinator.com",
        "http://slashdot.org",
        "http://cnn.com",
        "http://news.google.com",
        "http://xkcd.com",
        "http://python.org",
        "http://sourceforge.net",
    ]
    pf = ParallelFetcher(urls)
    for url in urls:
        print url, len(pf[url])

