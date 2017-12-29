__author__ = "Danilo S. Carvalho <danilo@jaist.ac.jp>"

import copy

from saf import Document
from saf import Sentence
from saf import Token
from saf.importers.importer import Importer
from saf.constants import annotation
from nltk.tokenize import word_tokenize

from epo_extraction.annotation import constants


class EPODocumentImporter(Importer):
    def __init__(self):
        self.word_tokenizer = word_tokenize

    def import_document(self, patdoc):
        doc = Document()
        doc.title = u"-".join([patdoc["country"], patdoc["number"], patdoc["kind"]])
        doc.annotations["class_ipcr"] = list(set([(ipc_info["subclass"], tuple(ipc_info["subgroup"])) for ipc_info in patdoc["class_ipcr"]]))

        sentences = []

        #for sent in patdoc["abstract"]["EN"]:
        #    sentences.append({"text": sent, "annotations": {constants.DOC_SECTION: "ABSTR"}})

        #for sent in patdoc["description"]["EN"]:
        #    sentences.append({"text": sent, "annotations": {constants.DOC_SECTION: "DESCR"}})

        for claim in patdoc["claims"]["EN"]:
            claim_txt = u" ".join(claim["text"])
            sentences.append({"text": claim_txt, "annotations": {constants.DOC_SECTION: "CLAIMS",
                                                                 constants.CLAIM_NUM: claim["number"]}})

        for sent in sentences:
            sentence = Sentence()
            sentence.annotations = copy.deepcopy(sent["annotations"])

            for token_raw in self.word_tokenizer(sent["text"]):
                token = Token()
                token.surface = token_raw

                token.annotations[annotation.DEPREL] = u"0"
                sentence.tokens.append(token)

            if (len(sentence.tokens) > 0):
                doc.sentences.append(sentence)

        return doc

