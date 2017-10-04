#!/usr/bin/env python
#-*- coding: utf8 -*-
__author__ = "Danilo S. Carvalho <danilo@jaist.ac.jp>"

import web
import json
from pymongo import MongoClient
from bson import json_util

urls = (
    '/epodocs/annot_claims', 'AnnotationClaims',
)
app = web.application(urls, globals())


class AnnotationClaims:
    def GET(self):
        conn = MongoClient()
        db = conn.epo
        annotcoll = db.sample_annot
        patcoll = db.patents

        res = []

        for doc_id in annotcoll.find():
            patdoc = patcoll.find({"country": doc_id["country"], "number": doc_id["number"], "kind": doc_id["kind"]}, 
                                  {"_id": 0, "country": 1, "number": 1, "kind": 1, "claims.EN": 1, "title.EN": 1})[0]
            res.append(patdoc)

        conn.close()

        return json.dumps(res, default=json_util.default)


if __name__ == "__main__":
    app.run()
 
