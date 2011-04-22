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

    c.execute('''CREATE TABLE words (id INTEGER PRIMARY KEY, word TEXT)''');
    c.execute('''CREATE UNIQUE INDEX wordlist ON words ( word )''')
    c.execute('''CREATE TABLE word_appearances (word INTEGER, file INTEGER, pos INTEGER )''')
    c.execute('''CREATE INDEX word_appearances_bywords ON word_appearances ( word )''')
    c.execute('''CREATE TABLE filenames (id INTEGER, filename TEXT)''')
    c.execute('''CREATE UNIQUE INDEX filename_id ON filenames ( id )''')

    c.close()

    return conn

def add_file(conn, filename, fileid):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO filenames VALUES (?, ?)''', [fileid, filename])
    cursor.close()

def add_word(conn, word, word_ids):
    if word in word_ids:
        return word_ids[word]
    else:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO words (word) VALUES (?)''', [word])
        word_id = cursor.lastrowid
        word_ids[word] = word_id
        return word_id

def remove_singletons(conn):
    c = conn.cursor()
    c2 = conn.cursor()

    c.execute('''SELECT word, count(*) FROM word_appearances GROUP BY word''')
    for word, count in c:
        if count == 1:
            c2.execute('''DELETE FROM words WHERE id = ?''', [word])
            c2.execute('''DELETE FROM word_appearances WHERE word = ?''', [word])
    c2.close()
    c.close()

def add_context(conn, wordid, fileid, position):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO word_appearances VALUES (?,?,?)''', [wordid, fileid, position])
    cursor.close()

def close_index(conn):
    cursor = conn.cursor()
    cursor.execute('VACUUM')
    conn.commit()
    cursor.close()

def index_database(corpus_file_or_folder, index_file, remove_once=True):
    # if remove once is True, the words that appear in the corpus only
    # once will not be indexed.

    wt = WordTransformer()

    print "Initing database (%s)..." % index_file
    conn = init_index(index_file)
    word_ids = dict()
    
    print "Calculating total corpus size..."
    filenames = list(walk(corpus_file_or_folder))
    total_offset = 0
    total_bytes = sum(float(os.stat(f).st_size) for f in filenames)


    from datetime import datetime
    from terminal import ProgressBar
    pb = ProgressBar(width=20, color='green')
    start = datetime.now()
    

    print "Beginning indexing..."
    for fileid, filename in enumerate(filenames):
        offset = 0
        print "Processing %s..." % filename
        with open(filename) as f:
            add_file(conn, filename, fileid)
            for j, line in enumerate(f):
                line_bytes = len(line)

                if line.strip() == '.START':
                    # special token in the wsj corpus file
                    offset += line_bytes
                    continue

                words = wt.tokenize(line)
                processed = []
                for word in words:
                    if word in processed:
                        # no need to record when a word appears twice
                        # that'll fall out later
                        continue
                    processed.append(word)
                    wordid = add_word(conn, word, word_ids)
                    add_context(conn, wordid, fileid, offset)

                offset += line_bytes
                total_offset += line_bytes
                if j % 5000 == 0:
                    pct = float(total_offset) / total_bytes
                    eta = ((datetime.now() - start) / total_offset) * int(total_bytes - total_offset)
                    msg = "indexing  -  ETA %s" % (str(eta)[:10])
                    pb.render(pct, msg)
        
    msg = "completed in %s" % (datetime.now() - start)
    pb.render(1, msg)
    if remove_once:
        print "filtering words appearing only once..."
        remove_singletons(conn)

    print "syncing to disk... (almost done!)"
    close_index(conn)


if __name__ == '__main__':
    path = sys.argv[1]
    if path.endswith('/'):
        path = path[:-1]
    indexpath = os.path.join(PREPRO_DIR, os.path.basename(path) + '.sqlite')
    index_database(path, indexpath)


