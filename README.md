# Our Little NLP Pony

## Setup

First you'll want to install the Python Natural Language toolkit.

    $ mkdir ~/.pylibs
    $ easy_install-2.6 --install-dir=~/.pylibs dist/nltk-2.0.1rc1-py2.6.egg

We're trying out pybing and gensim. To install that, do

    $ easy_install-2.6 --install-dir=~/.pylibs dist/pybing-0.1dev_r34-py2.6.egg
    $ easy_install-2.6 --install-dir=~/.pylibs dist/gensim-0.7.8-py2.6.egg

## Generating Word lists

    $ python listwords.py wordnet/1.6/ 
