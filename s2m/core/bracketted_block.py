from s2m.core.formulae import Formula

from s2m.core.utils import merge_lists

import random

class BrackettedBlock(Formula):

    def __init__(self, b):

        if not issubclass(b.__class__, Formula):
            raise TypeError('Operand of bracketted block must be a well-formed formula')
        else:
            self.__b = b

    def __getattr__(self, p):

        if p == 'b':
            return self.__b
        elif p == 'priority':
            return 5
        else:
            raise AttributeError

    def __eq__(self, other):
	
        if other and isinstance(other, BrackettedBlock):
            return other.b == self.__b
        return False

    def __hash__(self):

        return hash(self.__b)

    def _latex(self, next_placeholder=1):

        b_tex, next_placeholder, b_level = self.__b._latex(next_placeholder)
        return self.brackets_model(b_level+1) % b_tex, next_placeholder, b_level+1

    def latex(self):

        return self._latex()[0]

    def count_brackets(self):

        y, n = self.__b.count_brackets()
        return y + 1, n

    def a_similarity(self, other):

        return self.__b.a_similarity(other)

    def d_symmetry(self):

        return self.__b.d_symmetry()

    def count_silsdepths(self):
        return self.__b.count_silsdepths()

    def transcription(self):

        return 'ouvrez la parenthèse %s fermez la parenthèse' \
               % self.__b.transcription()

    def replace_placeholder(self, formula, placeholder_id=0, next_placeholder=1, conservative=False):

        return self.__b.replace_placeholder(formula, placeholder_id, next_placeholder, conservative)

    def tree_depth(self):

        return 1 + self.__b.tree_depth()

    def extract_3tree(self):

        return self.__b.extract_3tree()

    @classmethod
    def teach(cls, parser):

        def bracketted_block_complex_expand(words):
            return BrackettedBlock(words[0])            

        bracketted_block_explicit_complex = ('brackettedblock/explicit',
                                             'ouvrez la parenthèse %f fermez la parenthèse',
                                             bracketted_block_complex_expand,
                                             True)

        bracketted_block_implicit_complex = ('brackettedblock/implicit',
                                             'entre parenthèse %f',
                                             bracketted_block_complex_expand,
                                             True)

        tuple_explicit_complex = ('brackettedblock/tupleexplicit',
                                  'nuplet %f fin de nuplet',
                                  bracketted_block_complex_expand,
                                  True)

        tuple_implicit_complex = ('brackettedblock/tupleimplicit',
                                  'nuplet %f',
                                  bracketted_block_complex_expand,
                                  True)

        parser.add_complex_rule(*bracketted_block_explicit_complex)
        parser.add_complex_rule(*bracketted_block_implicit_complex)
        parser.add_complex_rule(*tuple_explicit_complex)
        parser.add_complex_rule(*tuple_implicit_complex)

    @classmethod
    def generate_random(cls, b=None, depth=1):
        """
        Generates a random instance of BrackettedBlock.
        """
        if b == None:
            b = Formula.generate_random(depth=depth-1)           
        return BrackettedBlock(b)
