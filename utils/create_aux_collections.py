#!/usr/bin/env python
__author__ = 'Danilo S. Carvalho <danilo@jaist.ac.jp>'

import sys
import os
import re
import pymongo
from datetime import datetime
from pymongo import MongoClient

RGX_IPCCLASS = re.compile(r"^(?P<code>[A-Z0-9]{1,14})\s+(?P<descr>.*)$")
RGX_IPCCODE = re.compile(r"(?P<cl>[A-Z]([0-9]{2})?[A-Z]?)(?P<subgr>[0-9]{10})?")

def main(argv):

    conn = MongoClient()
    db = conn.epo
    patcoll = db.patents

    create_ipcmap_collection(db, patcoll)
    #create_ipcclass_collection(db, argv[1])


def create_ipcmap_collection(db, patcoll):
    ipc_map = dict()
    proc_patents = set()

    granted_patents = patcoll.find({"$or": [{"kind": "B1"}, {"kind": "B2"}, {"kind": "B"}]})
    applied_patents = patcoll.find({"$or": [{"kind": "A1"}, {"kind": "A2"}, {"kind": "A"}]})

    print "Reading docs..."
    count = 0

    # Adds first the granted documents, having the final IPC markings.
    # Patent application docs will only be added if there is no grant.
    for patdocs in [granted_patents, applied_patents]:
        for patent in patdocs:
            pat_id = (patent["country"], patent["number"])
            if (pat_id not in proc_patents):
                ipc_subcls = dict()
                for ipc_cls in set([(ipc_info["subclass"], tuple(ipc_info["subgroup"])) for ipc_info in patent["class_ipcr"]]):
                    if (ipc_cls[0] not in ipc_map):
                        ipc_map[ipc_cls[0]] = set()
                    if (ipc_cls[0] not in ipc_subcls):
                        ipc_subcls[ipc_cls[0]] = set()

                    ipc_subcls[ipc_cls[0]].add(ipc_cls[1])

                for cls in ipc_subcls:
                    ipc_map[cls].add((patent["country"], patent["number"], patent["kind"], tuple(sorted(list(ipc_subcls[cls])))))
                
                proc_patents.add(pat_id)

            if (count % 1000 == 0):
                print count
            count += 1

    print "Inserting IPC map entries..."

    ipccoll = db.ipc_map

    for cls in ipc_map:
        ipccoll.insert_one({"class_ipcr": cls, "patent_list": list(ipc_map[cls])})

    ipccoll.create_index("class_ipcr")


def create_ipcclass_collection(db, basedir):
    ipc_classes = ipc_read(basedir)
    ipcclscoll = db.ipc_classes
    
    for cls in ipc_classes:
        print cls
        mo = RGX_IPCCODE.search(cls)
        fields = mo.groupdict()

        class_reg = {"class_ipcr": fields["cl"], "descr": ipc_classes[cls]}
        
        if (fields["subgr"] is not None):
            subgr2 = fields["subgr"][5:].rstrip("0")
            class_reg["subgroup"] = (fields["subgr"][0:5].lstrip("0"), subgr2 if (subgr2 != "") else "00")

        ipcclscoll.insert_one(class_reg)

    ipcclscoll.create_index([("class_ipcr", pymongo.ASCENDING), ("subgroup.0", pymongo.ASCENDING), ("subgroup.1", pymongo.ASCENDING)], unique=True, sparse=True)


def ipc_read(basedir):
    ipc_classes = dict()

    for filename in os.listdir(basedir):
        with open(os.path.join(basedir, filename)) as title_list_file:
            print "Reading %s ..." % filename
            for line in title_list_file:
                mo = RGX_IPCCLASS.search(line)
                if (mo):
                    cls = mo.group("code")
                    descr = mo.group("descr")

                    ipc_classes[cls] = descr

    return ipc_classes






if __name__ == "__main__":
    main(sys.argv)
 
