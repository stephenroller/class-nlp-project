#!/usr/bin/env python

import sys
import os
import sqlite3

from util import WordTransformer
from sembuild import PREPRO_DIR

def walk(path):
    queue = [path]
    while queue:
        filename = queue.pop(0)
        if os.path.isdir(filename):
            subchecks = os.listdir(filename)
            # no hidden files
            subchecks = [p for p in subchecks if not p.startswith(".")]
            # no python files (temp hack)
            subchecks = [p for p in subchecks if ".py" not in p]
            queue += [os.path.join(filename, p) for p in subchecks]
        elif os.path.isfile(filename):
            yield filename
 
def init_index(sqlfile):
    if os.path.exists(sqlfile):
        os.remove(sqlfile)

    conn = sqlite3.connect(sqlfile)
    c = conn.cursor()

    c.execute('''CREATE TABLE words (WORD text)''');
    c.execute('''CREATE UNIQUE INDEX wordlist ON words ( WORD )''')
    c.execute('''CREATE TABLE word_appearances (WORD text, FILE text, POS int )''')
    c.execute('''CREATE INDEX word_appearances_bywords ON word_appearances ( WORD )''')

    return conn, c

def add_context(cursor, word, filename, position):
    cursor.execute('''INSERT OR IGNORE INTO words VALUES (?);''', [word])
    cursor.execute('''INSERT INTO word_appearances VALUES (?,?,?)''', [word, filename, position])

def close_index(conn, cursor):
    cursor.execute('VACUUM')
    conn.commit()
    cursor.close()

def index_database(corpus_file_or_folder, index_file):
    wt = WordTransformer()

    conn, cursor = init_index(index_file)
    
    filenames = list(walk(corpus_file_or_folder))

    for i, filename in enumerate(filenames):
        total_bytes = float(os.stat(filename).st_size)
        offset = 0
        with open(filename) as f:
            for j, line in enumerate(f):
                line_bytes = len(line)
                words = wt.tokenize(line)
                processed = []
                for word in words:
                    if word in processed:
                        # no need to record when a word appears twice
                        # that'll fall out later
                        continue
                    processed.append(word)
                    add_context(cursor, word, filename, offset)
                offset += line_bytes
                if j % 500 == 0:
                    print "processing %s (%d/%d): %.2f%% complete" % (filename, i+1, len(filenames), 100 * offset / total_bytes)
                    conn.commit()
                    c = conn.cursor()

    print "syncing to disk... (almost done!)"
    close_index(conn, cursor)

if __name__ == '__main__':
    path = sys.argv[1]
    indexpath = os.path.join(PREPRO_DIR, os.path.basename(path) + '.sqlite')
    index_database(path, indexpath)


