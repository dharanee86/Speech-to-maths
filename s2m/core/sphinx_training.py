import json
import os
# import re
import subprocess

from threading import Thread

from interface.models import TrainingSample
from s2m.core.utils import args_from_dict, print_important
from s2m.settings import MEDIA_ROOT


class SphinxTraining(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        print_important("Info! Thread sphinx_training started.") 

        # Échantillons
        training_dir = os.path.join(MEDIA_ROOT, "training_data")
        fileids = os.path.join(training_dir, "s2m.fileids")
        transcription = os.path.join(training_dir, "s2m.transcription")

        # Modèle de langue
        sphinx_dir = os.path.join("s2m", "core", "sphinx")
        fr_dir = os.path.join(sphinx_dir, "fr")
        fr_save_dir = os.path.join(sphinx_dir, "fr_save")
        mdef = os.path.join(fr_dir, "mdef")
        mdef_txt = os.path.join(fr_dir, "mdef.txt")
        feat_params = os.path.join(fr_dir, "feat.params")
        s2m_dict = os.path.join(sphinx_dir, "s2m.dict")

        # Exécutables adaptation
        sphinxtrain_dir = os.path.join(sphinx_dir, "training")
        bw = os.path.join(sphinxtrain_dir, "bw")
        map_adapt = os.path.join(sphinxtrain_dir, "map_adapt")
        mk_s2sendump = os.path.join(sphinxtrain_dir, "mk_s2sendump")

        # Extraction des ids et des transcriptions
        with open(fileids, 'w') as i, open(transcription, 'w') as t:
            for sample in TrainingSample.objects.all():
                filepath, _ = os.path.splitext(sample.audio.name)
                _, filename = os.path.split(filepath)
                root_filepath = os.path.join(MEDIA_ROOT, filepath)
                i.write(root_filepath + '\n')
                t.write('<s> %s </s> (%s)\n' % (sample.text, filename))

        # Génération des paramètres acoustiques
        fe_params = {'argfile': feat_params,
                     'samprate': '8000',
                     'c': fileids,
                     'di': '.',
                     'do': '.',
                     'ei': 'wav',
                     'eo': 'mfc',
                     'nchans': '2',
                     'mswav': 'yes'}
        fe_args = args_from_dict(fe_params)
        subprocess.call(['sphinx_fe'] + fe_args)

        # Création de mdef.txt
        subprocess.call(['pocketsphinx_mdef_convert',
                         '-text',
                         mdef,
                         mdef_txt])

        # Collecte des statistiques
        bw_params = {'hmmdir': fr_dir,
                     'moddeffn': mdef_txt,
                     'ts2cbfn': '.ptm.',
                     'feat': '1s_c_d_dd',
                     'svspec': '0-12/13-25/26-38',
                     'cmn': 'current',
                     'agc': 'none',
                     'dictfn': s2m_dict,
                     'ctlfn': fileids,
                     'lsnfn': transcription,
                     'accumdir': training_dir}
        bw_args = args_from_dict(bw_params)
        subprocess.call([bw] + bw_args)

        # Copie
        subprocess.call(['cp', '-a', fr_dir, fr_save_dir])

        # Adaptation du modèle (MAP)
        map_adapt_params = {'moddeffn': mdef_txt,
                            'ts2cbfn': '.ptm.',
                            'meanfn': os.path.join(fr_save_dir, 'means'),
                            'varfn': os.path.join(fr_save_dir, 'variances'),
                            'mixwfn': os.path.join(fr_save_dir, 'mixture_weights'),
                            'tmatfn': os.path.join(fr_save_dir, 'transition_matrices'),
                            'accumdir': training_dir,
                            'mapmeanfn': os.path.join(fr_dir, 'means'),
                            'mapvarfn': os.path.join(fr_dir, 'variances'),
                            'mapmixwfn': os.path.join(fr_dir, 'mixture_weights'),
                            'maptmatfn': os.path.join(fr_dir, 'transition_matrices')}
        map_adapt_args = args_from_dict(map_adapt_params)
        subprocess.call([map_adapt] + map_adapt_args)

        # Génération du fichier sendump
        mk_s2sendump_params = {'pocketsphinx': 'yes',
                               'moddeffn': mdef_txt,
                               'mixwfn': os.path.join(fr_dir, 'mixture_weights'),
                               'sendumpfn': os.path.join(fr_dir, 'sendump')}
        mk_s2sendump_args = args_from_dict(mk_s2sendump_params)
        subprocess.call([mk_s2sendump] + mk_s2sendump_args)

        # Suppression de mdef.txt
        os.remove(mdef_txt)


sphinx_training = SphinxTraining()
sphinx_training.start()
