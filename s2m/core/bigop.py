#### EN DÉVELOPPEMENT ####
### 
from functools import reduce

from s2m.core.formulae import Formula
from s2m.core.utils import reverse_dict

import random

class BigOperator(Formula):

# Est-ce qu'on gère le contenu du BigOp ? Normalement oui ! 
    __OPERATORS = {'ITG': {'latex': '\int_{%s}^{%s} %s', 'priority': 1, 'type': 'SUM'},
                   'SUM': {'latex': '\sum_{%s}^{%s} %s', 'priority': 1, 'type': 'SUM'},
                   'PRO': {'latex': '\prod_{%s}^{%s} %s','priority': 2, 'type': 'SUM'},
                   'ITR': {'latex': '\bigcap_{%s}^{%s} %s','priority': 2, 'type': 'SUM'},
                   'UNI': {'latex': '\bigcup_{%s}^{%s} %s','priority': 1, 'type': 'SUM'}}

    __OPERATORS_PARSED = {'intégrale': 'ITG',
                          'somme': 'SUM',
                          'produit': 'PRO',
                          'intersection': 'ITR',
                          'union': 'UNI'}

    __OPERATORS_REVERSE = reverse_dict(__OPERATORS_PARSED)

    def __init__(self, o, *args): ##EN CONSTRUCTION !! ## à adapter avec args  
        if o not in self.operators:
            raise ValueError('Unknown big operator code : %r' % o)
        if self.__OPERATORS[o]['type'] == 'SUM':
            if len(args) > 3 or len(args) == 0:
                raise ValueError('Wrong amout of arguments for operator: %r' % len(args))    
        for form in args: 
            if not isinstance(form, Formula):
                raise ValueError('Input not Formula: %r' % form)
        self.__fl = args
        self.__o = o
            

    def __getattr__(self, p):
        if p == 'o':
            return self.__o
        elif p == 'fl':
            return self.__fl
        elif p == 'priority':
            return self.__OPERATORS[self.__o]['priority']
        elif p == 'latex_model':
            return self.__OPERATORS[self.__o]['latex']
        elif p == 'operator_type':
            return self.__OPERATORS[self.__o]['type']
        elif p == 'arity':
            return len(self.__fl)
        elif p == 'operators':
            return self.__OPERATORS.keys()
        else:
            raise AttributeError

    def __eq__(self, other):
         if other and isinstance(other, BigOperator):
            if other.o == self.__o and other.arity == self.arity:
                for i, form in enumerate(self.__fl):
                    if form != other.fl[i]:
                        return False
                else:
                    return True
         return False

    def __hash__(self):
        return reduce(lambda a, b: a ^ hash(b), self.__fl, 0)

    def _latex(self, next_placeholder=1):
        if self.operator_type == 'SUM':
            c_tex, c_level = '', 0
            d_tex, d_level = '', 0
            u_tex, u_level = '', 0
            if len(self.__fl) == 1:
                c_tex, next_placeholder, c_level = self.__fl[0]._latex(next_placeholder)
            if len(self.__fl) == 2:
                c_tex, next_placeholder, c_level = self.__fl[1]._latex(next_placeholder)
                d_tex, next_placeholder, d_level = self.__fl[0]._latex(next_placeholder)
            if len(self.__fl) == 3:
                c_tex, next_placeholder, c_level = self.__fl[2]._latex(next_placeholder)
                d_tex, next_placeholder, d_level = self.__fl[0]._latex(next_placeholder)
                u_tex, next_placeholder, u_level = self.__fl[1]._latex(next_placeholder)
            return self.latex_model % (d_tex, u_tex, c_tex), next_placeholder, c_level
        else:
            return '', next_placeholder, 0

    def latex(self):
        """Genere le code LaTeX correspondant a self"""
        return self._latex()[0]

    def count_brackets(self):
        return self.__fl[-1].count_brackets()

    def a_similarity(self, other):
        if isinstance(other, BigOperator) \
           and self.__o == other.o \
           and self.arity == other.arity:
            s = 0
            for i in range(self.arity):
                s += (self.__l(i)).a_similarity()
            return s/len(self.__fl)
        else:
            return 0.

    def d_symmetry(self):
        return self.__fl[-1].d_symmetry()

    def replace_placeholder(self, formula, placeholder_id=0, next_placeholder=1):

        from s2m.core.placeholder import PlaceHolder

        for (i,f) in enumerate(self.__fl):
            if isinstance(f, PlaceHolder) \
               and next_placeholder == placeholder_id:
                self.__fl[i] = formula
                return 0
            else:
                next_placeholder = f.replace_placeholder(formula,
                                                         placeholder_id,
                                                         next_placeholder)
                if next_placeholder == 0:
                    return 0
        return next_placeholder

    @classmethod
    def teach(cls, parser):

        big_operator_easy = ('bigoperator-operator',
                             cls.__OPERATORS_PARSED,
                             lambda x: x)

        big_operator_from = ('bigoperator-from',
                             {'de': None, 'pour': None, 'sur': None},
                             lambda x: None)

        big_operator_of = ('bigoperator-of',
                           {'de': None, 'des': None},
                           lambda x: None)

        # Defines op A -> BinaryOperator(op, A)
        def big_operator_expand(formulae):
            return BigOperator(*[f for f in formulae if f is not None])

        big_operator_arity1_complex = ('bigoperator/arity1',
                                       '$bigoperator-operator $bigoperator-of %f',
                                       big_operator_expand,
                                       True)

        # Defines op from A of B -> BinaryOperator(op, A, B)
        big_operator_arity2_complex = ('bigoperator/arity2',
                                       '$bigoperator-operator $bigoperator-from %f $bigoperator-of %f',
                                       big_operator_expand,
                                       True)

        # Defines op from A to B of C -> BinaryOperator(op, A, B, C)
        big_operator_arity3_complex = ('bigoperator/arity3',
                                       '$bigoperator-operator $bigoperator-from %f à %f $bigoperator-of %f',
                                       big_operator_expand,
                                       True)

        parser.add_easy_reduce(*big_operator_easy)
        parser.add_easy_reduce(*big_operator_from)
        parser.add_easy_reduce(*big_operator_of)
        parser.add_complex_rule(*big_operator_arity1_complex)
        parser.add_complex_rule(*big_operator_arity2_complex)
        parser.add_complex_rule(*big_operator_arity3_complex)

    def transcription(self):
        if self.operator_type == 'SUM':
            if self.__o == 'ITG':
                connector = 'de'
            else:
                connector = 'des'
            if len(self.__fl) == 1:
                return '%s %s %s' % (self.__OPERATORS_REVERSE[self.__o],
                                     connector,
                                     self.__fl[0].transcription())
            elif len(self.__fl) == 2:
                return '%s sur %s %s %s' % (self.__OPERATORS_REVERSE[self.__o],
                                            self.__fl[0].transcription(),
                                            connector,
                                            self.__fl[1].transcription())
            else:
                return '%s de %s à %s %s %s' % (self.__OPERATORS_REVERSE[self.__o],
                                                self.__fl[0].transcription(),
                                                self.__fl[1].transcription(),
                                                connector,
                                                self.__fl[2].transcription())
      