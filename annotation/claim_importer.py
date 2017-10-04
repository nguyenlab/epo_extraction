__author__ = 'danilo@jaist.ac.jp'

from saf.data_model.document import Document
from saf.data_model.sentence import Sentence
from saf.data_model.token import Token
from saf.importers.importer import Importer
from saf.constants import annotation
from nltk.tokenize import word_tokenize

from annotation import constants


class EpoClaimImporter(Importer):
    def __init__(self):
        self.word_tokenizer = word_tokenize


    def import_document(self, document):
        doc = Document()
        doc.title = u"-".join([document["country"], document["number"], document["kind"]])
        doc.annotations["class_ipcr"] = list(set([(ipc_info["subclass"], tuple(ipc_info["subgroup"])) for ipc_info in document["class_ipcr"]]))

        for claim in document["claims"]["EN"]:
            sentence = Sentence()
            sentence.annotations[constants.CLAIM_NUM] = claim["number"]
            claim_txt = u" ".join(claim["text"])

            for token_raw in self.word_tokenizer(claim_txt):
                token = Token()
                token.surface = token_raw
                token.annotations[annotation.DEPREL] = u"0"
                sentence.tokens.append(token)

            if (len(sentence.tokens) > 0):
                doc.sentences.append(sentence)

        return doc

