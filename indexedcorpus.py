#!/usr/bin/evn python

import sqlite3
import os

from itertools import groupby
from util import context_windows

class IndexedCorpus(object):
    def __init__(self, indexfile, corpus_directory=''):
        self.indexfile = indexfile
        self.corpus_directory = corpus_directory

        self.conn = sqlite3.connect(indexfile)

    def get_unique_words(self):
        c = self.conn.cursor()
        c.execute('select word from words order by word');
        for row in c:
            yield row[0]
        c.close()

    def get_contexts(self, query):
        c = self.conn.cursor()

        c.execute('''
            SELECT F.filename, WA.pos
            FROM words AS W
            JOIN word_appearances as WA ON (W.id = WA.word)
            JOIN filenames AS F ON (WA.file = F.id)
            WHERE W.word = ?
            ORDER BY WA.file, WA.pos
            ''', 
            [query]
        )

        for filename, positions in groupby(c, lambda x: x[0]):
            f = open(os.path.join(self.corpus_directory, filename))
            for filename, position in positions:
                f.seek(position)
                line = f.readline().strip()
                yield line

            f.close()

        c.close()

    def __len__(self):
        c = self.conn.cursor()
        c.execute('select count(*) from words');
        for row in c:
            count = row[0]
            c.close()
            return count


