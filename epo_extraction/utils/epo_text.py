#!/usr/bin/env python
#-*- coding: utf8 -*-
__author__ = "Danilo S. Carvalho <danilo@jaist.ac.jp>"

import sys
from epo_extraction.data_access.epo_corpus import EPOCorpus
from wikt_morphodecomp.annotation import MorphoAnalysisAnnotator


def main(argv):
    op = argv[1]

    w2m_config_filepath = ""
    ensemble_size = 0
    morpho_annotator = None
    if (op == "morphodecomp"):
        w2m_config_filepath = argv[2]
        ensemble_size = int(argv[3])
        morpho_annotator = MorphoAnalysisAnnotator()

    with EPOCorpus("localhost", 27117) as epo_corpus:
        total_patents = epo_corpus.docs_count()
        i = 0
        for patdoc in epo_corpus.docs_iter():
            if (op == "text"):
                for sentence in patdoc.sentences:
                    print " ".join([token.surface for token in sentence.tokens])

            elif (op == "morphodecomp"):
                morpho_annotator.annotate(patdoc, ensemble=True, config_paths=[w2m_config_filepath] * ensemble_size)

                for sentence in patdoc.sentences:
                    print " ".join([" ".join(token.annotations["MORPHO"]["decomp"]) for token in sentence.tokens])

            i += 1
            if (i % 10000 == 0):
                sys.stderr.write("Completed %.2f%%\n" % (float(i) * 100 / total_patents))



if __name__ == '__main__':
    main(sys.argv)