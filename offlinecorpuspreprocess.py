"""This is a script to preprocess a corpus so it's usable by OfflineCorpus.

If you want to use a corpus for an OfflineCorpus, you must run this script
first. It's as easy as

python offlinecorpuspreprocess.py /u/pichotta/penn-wsj-raw-all.txt

for example. It puts a bunch of stuff into prepro-corpus/ dir.

IMPORTANT: you have to call this script from the directory it's in. I didn't
make it smart enough to chdir as needed, and didn't want to hardcode the
absolute path of the corpus preprocessing files in.
"""

import sys

# this constant is duplicated in corpus.offlinecorpus. Sorry :C
PREPRO_FILE_DIR = 'prepro-corpus/'

def prepro(corpname):
    mkdirs(corpname)

def mkdirs(corpname):
    try:
        os.mkdir(PREPRO_FILE_DIR)
    except OSError:
        pass
    for letter in string.ascii_lowercase:
        try:
            os.mkdir(os.join(PREPRO_FILE_DIR, letter))
        except OSError:
            pass

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python offlinecorpuspreprocess.py corpusname')
        sys.exit(1)
    prepro(sys.argv[1])
