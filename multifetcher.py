#!/usr/bin/env python

import sys
import urllib2
from Queue import Queue
import threading
import thread

from config import *

def _fetch(url):
    try:
        f = urllib2.urlopen(url, timeout=URLLIB_TIMEOUT)
        retval = (url, f.read())
        f.close()
        return retval
    except Exception, e:
        sys.stderr.write(str(e) + '\n')
        return (url, "")

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        while True:
            #grabs host from queue
            host = self.queue.get()

            #grabs urls of hosts and then grabs chunk of webpage
            chunk = _fetch(host)
            
            #place chunk into out queue
            self.out_queue.put(chunk)

            #signals to queue job is done
            self.queue.task_done()

class ParallelFetcher(object):
    def __init__(self, urls):
        self.urls = urls
        queue = Queue()
        out_queue = Queue()

        for i in xrange(NUM_FETCH_PROCESSES):
            try:
                t = ThreadUrl(queue, out_queue)
                t.setDaemon(True)
                t.start()
            except thread.error:
                # too many threads. that's okay, just use fewer
                pass

        for url in urls:
            queue.put(url)

        queue.join()
        self.results = dict(r for r in out_queue.queue)


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

