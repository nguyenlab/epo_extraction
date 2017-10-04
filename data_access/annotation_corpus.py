__author__ = 'danilo@jaist.ac.jp'

import os
import datetime
from pymongo import MongoClient
from saf.formatters.conll import CoNLLFormatter
from saf.constants import annotation

from annotation.claim_importer import EpoClaimImporter


class AnnotationCorpus(object):
    def __init__(self, host=None, port=None):
        self.documents = dict()
        self.version = 0.0
        self.date = datetime.datetime.now()

        self.load_annotation_docs(host, port)

    def load_annotation_docs(self, host=None, port=None):
        conn = MongoClient(host=host, port=port)
        db = conn.epo
        annotcoll = db.sample_annot
        patcoll = db.patents

        claim_importer = EpoClaimImporter()

        for doc_id in annotcoll.find():
            patdoc = patcoll.find({"country": doc_id["country"], "number": doc_id["number"], "kind": doc_id["kind"]},
                                  {"_id": 0, "country": 1, "number": 1, "kind": 1, "claims.EN": 1, "title.EN": 1,
                                   "class_ipcr": 1})[0]

            doc = claim_importer.import_document(patdoc)
            self.documents[doc.title] = doc
            print "Imported: ", doc.title

        conn.close()

    def export_conll_files(self, directory):
        conll_formatter = CoNLLFormatter([annotation.UPOS] + ["UNUSED", "UNUSED", "UNUSED",
                                                              annotation.DEPREL,
                                                              "UNUSED", "UNUSED", "UNUSED"])

        for title in self.documents:
            conll_doc = conll_formatter.dumps(self.documents[title])
            with open(os.path.join(directory, title + "_claims.conllu"), "w") as conll_file:
                conll_file.write(conll_doc.encode("utf8"))
            print "Exported: ", os.path.join(directory, title + "_claims.conllu")
