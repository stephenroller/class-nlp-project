''' Must take some number of args, which must be output files from semtest.
'''

import re
import sys

def calc_pr(lines):
    cor = 0
    guessed = 0
    tot = 0
    for line in lines:
        is_guessed, is_correct = get_is_guessed_or_correct(line)
        #print '%s\t%s' % (is_guessed, is_correct)
        if is_guessed: guessed += 1
        if is_correct: cor += 1
        tot += 1
    #print cor
    #print guessed
    #print tot
    p = float(cor) / guessed
    a = float(cor) / tot
    r = float(cor) / (cor + (tot - guessed))
    f = 2 * (p * r) / (p + r)
    print 'P: %f (%d/%d)' % (p, cor, guessed)
    print 'R: %f (%d/%d)' % (r, cor, (cor + (tot - guessed)))
    print 'A: %f (%d/%d)' % (a, cor, tot)
    print 'F1: %f' % f

def get_is_guessed_or_correct(line):
    m = re.match(r'\S+: (\S+) \(correct: (\S+)\)', line)
    if not m:
        print 'no match found for %s' % line
        return False, False
    #print m.group(1)
    #print m.group(2)
    return (m.group(1) != '??'), (m.group(1) == m.group(2))
    

def grep_for_cor(files):
    lines = []
    for f in files:
        lines += [x for x in open(f,'r') if 'correct:' in x]
    return lines
    

if __name__ == '__main__':
    calc_pr(grep_for_cor(sys.argv[1:]))
