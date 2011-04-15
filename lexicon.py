from corpus import offlinecorpus
import gensim
import operator
import re

HALF_CONTEXT_LEN = 9

class Lexicon:
    """a class representing a vector-space based lexicon."""

    def __init__(self, offlinecorp):
        words = set([self._clean_word(w) for w in offlinecorp.get_unique_words()
                                         if self._clean_word(w) != ''])
        self._dict= gensim.corpora.Dictionary()
        for w in words:
            print 'getting contexts for %s' % w
            cxts = offlinecorp.get_contexts(w)
            print 'adding to dict...'
            self._dict.doc2bow(self._contexts_to_token_list(cxts, w),
                               allowUpdate=True)
        print self._dict.token2id

    def _contexts_to_token_list(self, contexts, word):
        """tokenizes a list of contexts, returns a list of normalized tokens.
        
        We tokenize each context and then smash the lists of tokens 
        together. For example,
        ['a b c', 'b d'] will yield ['a', 'b', 'c', 'b', 'd'].

        Two important things: (1) an occurrence of 'word' will be
        removed from each context, and (2) we trim each context to
        at most CONTEXT_LENGTH tokens.
        """
        li = [self._get_cleaned_tokenized_str(c) for c in contexts]
        li = [self._trim_context_and_remove_word(c, word) for x in li]
        return reduce(operator.concat, li)

    def _get_cleaned_tokenized_str(self, line):
        """takes a line, returns a list of the cleaned tokens in that line"""
        return [self._clean_word(w) for w in line.split()
                if len(self._clean_word(w)) > 0]

    def _trim_context_and_remove_word(self, context, word):
        """removes first occurrence of word and trims context around it.

        Note that at this point we expect context to be tokenized and cleaned.
        This has the funny behavior that it modifies "context" in place and
        also returns it so it works in list comprehensions
        """
        word = self._clean_word(word)
        for i in range(len(context)):
            if context[i] == word:
                context.pop(i)
                break
        lb = max(0,i - HALF_CONTEXT_LEN)
        ub = min(len(context), i + HALF_CONTEXT_LEN)
        context = context[lb:ub]
        return context

    def _clean_word(self, word):
        #TODO perhaps apply morphological stemming here?
        return re.sub(r'\W', '', word.lower())

if __name__ == '__main__':
    lex = Lexicon(offlinecorpus.OfflineCorpus())