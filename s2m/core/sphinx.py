import os
from threading import Thread
from pocketsphinx import Pocketsphinx, AudioFile
from s2m.core.utils import nobrackets


class Sphinx(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.ready = False

    def run(self):
        self.config = {
            'verbose': True,
            'hmm': os.path.join('s2m', 'core', 'sphinx', 'fr'),
            'lm': os.path.join('s2m', 'core', 'sphinx', 'fr.lm.dmp'),
            'dict': os.path.join('s2m', 'core', 'sphinx', 's2m.dict'),
            'jsgf': os.path.join('s2m', 'core', 'sphinx', 's2m.jsgf'),
        }
        self.pocketsphinx = Pocketsphinx(**self.config)
        self.ready = True
        
    def to_text(self, filename, erase=False):
        if not self.ready:
            raise EnvironmentError('Initialization of sphinx not finished.')
        FILLER_WORDS = ['<s>', '<sil>', '</s>']
        self.pocketsphinx.decode(filename)
        text = " ".join(
           [s for s in self.pocketsphinx.segments() if s not in FILLER_WORDS])
        text = nobrackets(text)
        nbest = [nobrackets(w[0])
                 for w in self.pocketsphinx.best(count=10)[1:]]
        if erase:
            os.remove(loc)
        return text, nbest

sphinx = Sphinx()
sphinx.start()
