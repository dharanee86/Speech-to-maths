from s2m.core.formulae import *

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

    def _latex(self):

        b_tex, b_level = self.__b._latex()
        return self.brackets_model(b_level+1) % b_tex, b_level+1
        
    def latex(self):

        return self._latex()[0]
        
    def count_brackets(self):

        y, n = self.__b.count_brackets()
        return y + 1, n

    def distance(self, f):

        return self.__b.distance(f)

    def symmetry_index(self):

        return self.__b.symmetry_index()

    def teach(parser):

        def bracketted_block_complex_expand(words):
            return BrackettedBlock(words[0])

        bracketted_block_explicit_complex = ('brackettedblock-explicit',
                                             'ouvrez la parenthese %f fermez la parenthese',
                                             bracketted_block_complex_expand,
                                             True)

        bracketted_block_implicit_complex = ('brackettedblock-implicit',
                                             'entre parentheses %f',
                                             bracketted_block_complex_expand,
                                             True)

        parser.add_complex_rule(*bracketted_block_explicit_complex)
        parser.add_complex_rule(*bracketted_block_implicit_complex)

