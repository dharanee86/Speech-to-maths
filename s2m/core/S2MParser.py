from s2m.core.parser import Parser
from s2m.core.formulae import *
from s2m.core.utils import listset

class S2MParser():

    def __init__(self):
        self.__parser = Parser()
#        self.__parser.learn(BinaryOperator)
 #       self.__parser.learn(UnaryOperator)
  #      self.__parser.learn(BrackettedBlock)
   #     self.__parser.learn(Variable)
    #    self.__parser.learn(Number)
        BinaryOperator.teach(self.__parser)
        UnaryOperator.teach(self.__parser)
        BrackettedBlock.teach(self.__parser)
        Variable.teach(self.__parser)
        Number.teach(self.__parser)
        
    def parse(self, w):
        #Stupid
        #Modifier le format de token pour séparer formula de data
        parses = self.__parser.cky(w)
        fitf = lambda x: 0.5*x.natural_bracketting_index()+0.1*x.symmetry_index()
        return listset([p.latex() for p in sorted(parses, key=fitf, reverse=True)])

    def __call__(self, w):
        return self.parse(w)

s2m_parser = S2MParser()
