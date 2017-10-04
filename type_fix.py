#!/usr/bin/env python

import sys
from datetime import datetime
from pymongo import MongoClient

def main(argv):
    if (argv[1] == "date"):
        date_fix()
    elif (argv[1] == "ipc"):
        ipc_fix()

def date_fix():
    conn = MongoClient()
    db = conn.epo
    patcoll = db.patents
    count = 0

    for patent in patcoll.find():
        patent["date"] = datetime.strptime(patent["date"], "%Y%m%d")
        patent["application_ref"]["date"] = datetime.strptime(patent["application_ref"]["date"], "%Y%m%d")
        patent["publication_ref"]["date"] = datetime.strptime(patent["publication_ref"]["date"], "%Y%m%d")

        for priority_claim in patent["priority_claims"]:
            priority_claim["date"] = datetime.strptime(priority_claim["date"], "%Y%m%d")

        patcoll.update_one({"_id": patent["_id"]}, {"$set": {"date": patent["date"], 
                                                             "application_ref.date": patent["application_ref"]["date"], 
                                                             "publication_ref.date": patent["publication_ref"]["date"],
                                                             "priority_claims": patent["priority_claims"]}})

        if (count % 10000):
            print count

        count += 1


def ipc_fix():
    conn = MongoClient()
    db = conn.epo
    patcoll = db.patents
    count = 0

    for patent in patcoll.find():
        class_ipcr = []

        for ipc_info in patent["class_ipcr"]:
            if (type(ipc_info) == type([])):
                ipc_dict = dict()
                ipc_dict["subclass"] = ipc_info[0]
                ipc_dict["subgroup"] = ipc_info[1].split("/")

                if (len(ipc_info) < 3):
                    if (len(ipc_dict["subgroup"]) > 1):
                        ipc_dict["version"] = ""
                        ipc_dict["classif_code"] = ""
                    else:
                        ipc_dict["subgroup"] = ["0", "00"]
                        ipc_dict["version"] = ipc_info[1][0:9]
                        ipc_dict["classif_code"] = ipc_info[1][9:]
                elif (len(ipc_info) < 4):
                    ipc_dict["version"] = ipc_info[2][0:9]
                    ipc_dict["classif_code"] = ipc_info[2][9:]
                else:
                    ipc_dict["version"] = ipc_info[2]
                    ipc_dict["classif_code"] = ipc_info[3]

                class_ipcr.append(ipc_dict)
            else:
                class_ipcr.append(ipc_info)

        patcoll.update_one({"_id": patent["_id"]}, {"$set": {"class_ipcr": class_ipcr}})

        if (count % 1000 == 0):
            print count

        count += 1





if __name__ == "__main__":
    main(sys.argv)
 
