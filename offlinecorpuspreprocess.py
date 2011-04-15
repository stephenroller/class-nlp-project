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
    words = _mkwordset(cname, lines)
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

def _mkwordset(corpname, lines):
    """makes word list, returns frozenset of words"""
    f = open(offlinecorpus.get_word_list_filename(corpname), 'w')
    words = _get_unique_words(lines)
    f.writelines([w + '\n' for w in words])
    f.close()
    return words

def _mkcontextlist(words, corpname, lines):
    ctxdict = dict.fromkeys(words)
    print('reading through corpus and compiling contexts...')
    for line in lines:
        tokenized = line.split()
        for i in range(len(tokenized)):
            if offlinecorpus.clean_word(tokenized[i]) in words:
                _add_ctx_to_dict(tokenized, i, ctxdict)
    print('writing contexts to file...')
    for w in ctxdict.iterkeys():
        _write_contexts(w, corpname, ctxdict[w])

def _add_ctx_to_dict(tokenizedline, index, contextdict):
    lb = max(0, index - offlinecorpus.HALF_CONTEXT_SIZE)
    ub = min(len(tokenizedline), index + offlinecorpus.HALF_CONTEXT_SIZE)
    cleanword = offlinecorpus.clean_word(tokenizedline[index])
    if not contextdict[cleanword]:
        contextdict[cleanword] = []
    contextdict[cleanword].append(' '.join(tokenizedline[lb:ub]))

def _write_contexts(word, corpname, contexts):
    if len(word) == 0 or not word[0].isalpha(): return
    f = open(offlinecorpus.get_context_list_filename(corpname, word), 'w')
    f.writelines([x + '\n' for x in contexts])
    f.close()

def _filter_out_hapax_legomena(words):
    return [w for w in words if words.count(w) > 1]

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
        sys.stderr.write('Usage: python offlinecorpuspreprocess.py corpusname\n')
        sys.exit(1)
    prepro(sys.argv[1])
