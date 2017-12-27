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
        if (op == "text"):
            for patdoc in epo_corpus.docs_iter():
                for sentence in patdoc.sentences:
                    print " ".join([token.surface.encode("utf8") for token in sentence.tokens])

                i += 1
                print_progress(i, total_patents, 1000)

        elif (op == "morphodecomp"):
            for patdoc in epo_corpus.docs_iter():
                morpho_annotator.annotate(patdoc, ensemble=True, config_paths=[w2m_config_filepath] * ensemble_size)

                for sentence in patdoc.sentences:
                    print " ".join([" ".join([morph.encode("utf8") for morph in token.annotations["MORPHO"]["decomp"]]) for token in sentence.tokens])

                i += 1
                print_progress(i, total_patents, 1000)
                

def print_progress(counter, total, interval):
    if (counter % interval == 0):
        sys.stderr.write("Completed %.2f%%\n" % (float(counter) * 100 / total))


if __name__ == '__main__':
    main(sys.argv)
