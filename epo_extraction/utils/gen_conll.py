__author__ = "Danilo S. Carvalho <danilo@jaist.ac.jp>"

import sys
from data_access.annotation_corpus import AnnotationCorpus

CONLL_DOCS_PATH = "/Users/danilo/research/data/epo/conll_claims"

def main(argv):
    annot_corpus = AnnotationCorpus(host="150.65.242.115", port=27117)

    claim_counter = sum([len(doc.sentences) for doc in annot_corpus.documents.values()])
    print float(claim_counter) / len(annot_corpus.documents)




    #annot_corpus.export_conll_files(CONLL_DOCS_PATH)



if __name__ == "__main__":
    main(sys.argv)