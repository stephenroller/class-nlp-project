# Our Little NLP Pony

## Setup

First you'll want to install the Python Natural Language toolkit.

    $ mkdir ~/.pylibs
    $ easy_install-2.6 --install-dir=~/.pylibs dist/nltk-2.0.1rc1-py2.6.egg

We're trying out pybing right now. To install that, do

    $ easy_install-2.6 --install-dir=~/.pylibs dist/pybing-0.1dev_r34-py2.6.egg
or if you're on a system with root access, just

    $ easy_install pybing

should do the trick

## Generating Word lists

    $ python listwords.py wordnet/1.6/ 
