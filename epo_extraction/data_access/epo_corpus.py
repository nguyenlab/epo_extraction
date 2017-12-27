__author__ = "Danilo S. Carvalho <danilo@jaist.ac.jp>"

import os
import datetime
from pymongo import MongoClient
from saf.formatters.conll import CoNLLFormatter
from saf.constants import annotation

from epo_extraction.annotation.document_importer import EPODocumentImporter


class EPOCorpus(object):
    def __init__(self, host=None, port=None):
        self.version = 0.0
        self.date = datetime.datetime.now()

        self.conn = MongoClient(host=host, port=port)
        self.db = self.conn.epo
        self.patcoll = self.db.patents

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def docs_iter(self):
        doc_importer = EPODocumentImporter()

        for patdoc in self.patcoll.find():
            doc = doc_importer.import_document(patdoc)
            yield doc

    def export_conll_files(self, directory):
        conll_formatter = CoNLLFormatter([annotation.UPOS] + ["UNUSED", "UNUSED", "UNUSED",
                                                              annotation.DEPREL,
                                                              "UNUSED", "UNUSED", "UNUSED"])

        for doc in self.docs_iter():
            conll_doc = conll_formatter.dumps(doc)
            with open(os.path.join(directory, doc.title + "_claims.conllu"), "w") as conll_file:
                conll_file.write(conll_doc.encode("utf8"))
            print "Exported: ", os.path.join(directory, doc.title + "_claims.conllu")

    def docs_count(self):
        return self.patcoll.count()
