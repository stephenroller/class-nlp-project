"""some code to take in english gigaword files and de-sgmlify them.

This is destructive---it modifies the files you pass as args.
"""

import sys
import sgmllib

cur_ps = []

class DeSGMLifier(sgmllib.SGMLParser):
    global cur_ps

    def __init__(self):
        # initialize base class
        sgmllib.SGMLParser.__init__(self)
        self.inp = False

    def newline(self):
        # force newline, if necessary
        if self.flag:
            sys.stdout.write("\n")
        self.flag = 0

    def unknown_starttag(self, tag, attrs):
        # the attrs argument is a list of (attr, value) tuples.
        if tag == 'p':
            self.inp = True
        else:
            self.inp = False

    def handle_data(self, text):
        # called for each text section
        if self.inp:
            cur_ps.append(text)

    def handle_entityref(self, text):
        # called for each entity
        pass
        
    def unknown_endtag(self, tag):
        # called for each end tag
        self.inp = False



def desgmlify(files):
    for f in files:
        desgmlify_file(f)

def desgmlify_file(file):
    global cur_ps
    infile = open(file, 'r')
    t = ''
    for line in infile:
        t += line
    infile.close()
    d = DeSGMLifier()
    d.feed(t)
    d.close()
    out = open(file, 'w')
    for p in cur_ps:
        out.write(p)
    out.close()
    cur_ps = []

if __name__ == '__main__':
    desgmlify(sys.argv[1:])
