"""This is a script to preprocess a corpus so it's usable by OfflineCorpus.

If you want to use a corpus for an OfflineCorpus, you must run this script
first. It's as easy as

python offlinecorpuspreprocess.py /u/pichotta/penn-wsj-raw-all.txt

for example. It puts a bunch of stuff into prepro-corpus/ dir.

IMPORTANT: you have to call this script from the directory it's in. I didn't
make it smart enough to chdir as needed, and didn't want to hardcode the
absolute path of the corpus preprocessing files in.
"""

from corpus import offlinecorpus
import itertools
import os
import string
import sys


def prepro(corpname):
    _mkdirs(corpname)
    lines = _get_all_lines(_get_corpus_files(corpname))
    cname = offlinecorpus.canonicalize_corpus_name(corpname)
    words = _mkwordlist(cname, lines)
    _mkcontextlist(words, cname, lines)

def _mkdirs(corpname):
    cname = offlinecorpus.canonicalize_corpus_name(corpname)
    try:
        os.mkdir(offlinecorpus.PREPRO_FILE_DIR)
    except OSError:
        pass
    try:
        os.mkdir(offlinecorpus.get_context_list_dirname(cname))
    except OSError:
        pass
    for letter in string.ascii_lowercase:
        try:
            os.mkdir(os.path.join(offlinecorpus.get_context_list_dirname(cname), letter))
        except OSError:
            pass

def _get_corpus_files(fname):
    """takes a filename (optionally a dir), returns list of filenames"""
    if os.path.isdir(fname):
        return [x for x in os.walk(fname)]
    return [fname]

def _mkwordlist(corpname, lines):
    """makes word list, returns list of words"""
    f = open(offlinecorpus.get_word_list_filename(corpname), 'w')
    words = _get_unique_words(lines)
    f.writelines([w + '\n' for w in words])
    f.close()
    return words

def _mkcontextlist(words, corpname, lines):
    for w in words:
        print('getting/writing context for %s' % w)
        ctxs = _get_contexts(w, lines)
        _write_contexts(w, corpname, ctxs)

def _write_contexts(word, corpname, contexts):
    if len(word) == 0 or not word[0].isalpha(): return
    f = open(offlinecorpus.get_context_list_filename(corpname, word), 'w')
    f.writelines([x + '\n' for x in contexts])
    f.close()

def _filter_out_hapax_legomena(words):
    return [w for w in words if words.count(w) > 1]

def _get_contexts(word, lines):
    """returns all contexts in which a word appears."""
    return itertools.chain(*[_get_contexts_in_line(word, l)
                             for l in lines])

def _get_contexts_in_line(word, line):
    """might mangle the whitespace a bit but that shouldn't matter"""
    if _should_ignore_line(line): return []
    cleanw = offlinecorpus.clean_word(word)
    words = line.split()
    res = []
    for i in range(len(words)):
        if offlinecorpus.clean_word(words[i]) == cleanw:
            res.append(_get_ind_context(words, i))
    return res

def _get_ind_context(words, ind):
    lb = max(0, ind - offlinecorpus.CONTEXT_SIZE)
    ub = min(len(words), ind + offlinecorpus.CONTEXT_SIZE)
    #TODO i think there's a performance bottleneck here?
    return ' '.join(words[lb:ub])

def _get_unique_words(lines):
    """returns a set of unique words. Performs some normalization."""
    # clean and tokenize
    cleanlines = [[offlinecorpus.clean_word(w) for w in l.split()]
                  for l in lines]
    # uniquify
    return frozenset().union(*[frozenset(x) for x in cleanlines])

def _get_all_lines(files):
    lines = []
    for f in files:
        for l in open(f, 'r'):
            if not _should_ignore_line(l):
                lines.append(l)
    return lines
    
def _should_ignore_line(line):
    return line.strip() == '.START'



if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python offlinecorpuspreprocess.py corpusname')
        sys.exit(1)
    prepro(sys.argv[1])
