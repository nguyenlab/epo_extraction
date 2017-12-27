#!/usr/bin/env python
#-*- coding: utf8 -*-
__author__ = "Danilo S. Carvalho <danilo@jaist.ac.jp>"


import sys
import math
import random
from collections import Counter 
from pymongo import MongoClient

SAMPLE_COLLNAME = "sample_exp"
ANNOT_COLLNAME = "sample_annot"
MIN_SAMPLE = 10

def main(argv):
    if (argv[1] == "exp"):
        if (len(argv) > 2):
            fraction = float(argv[2])
        else:
            fraction = 0.1

        sample_patents(fraction, SAMPLE_COLLNAME)
    elif (argv[1] == "annot"):
        if (len(argv) > 2):
            size = int(argv[2])
        else:
            size = 10

        sample_annot(size, SAMPLE_COLLNAME, ANNOT_COLLNAME)


def sample_patents(fraction, collname):
    conn = MongoClient()
    db = conn.epo
    ipcmapcoll = db.ipc_map
    ipcclscoll = db.ipc_classes
    samplecoll = db[collname]
    docset = set()

    samplecoll.remove({})

    for cls_map in ipcmapcoll.find():
        num_docs = len(cls_map["patent_list"])
        sample_count = int(math.ceil(num_docs * fraction))

        if (sample_count < MIN_SAMPLE):
            sample_count = min(num_docs, MIN_SAMPLE)

        sample = random.sample(cls_map["patent_list"], sample_count)

        samplecoll.insert({"class_ipcr": cls_map["class_ipcr"], "patent_sample": [(pat[0], pat[1], pat[2]) for pat in sample if ((pat[0], pat[1]) not in docset)]})
        docset.update([(pat[0], pat[1]) for pat in sample])


def sample_annot(size, sample_collname, collname):
    conn = MongoClient()
    db = conn.epo
    samplecoll = db[sample_collname]
    annotcoll = db[collname]

    annotcoll.remove({})

    for cls_sample in samplecoll.find():
        num_docs = len(cls_sample["patent_sample"])
        annot_sample = random.sample(cls_sample["patent_sample"], min(num_docs, size))

        annotcoll.insert_many([{"country": pat[0], "number": pat[1], "kind": pat[2]} for pat in annot_sample])







if __name__ == "__main__":
    main(sys.argv)
 
