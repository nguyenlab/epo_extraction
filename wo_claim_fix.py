__author__ = 'danilo@jaist.ac.jp'

from pymongo import MongoClient

def main():
    wo_claim_fix()

def wo_claim_fix():
    conn = MongoClient(port=27117)
    db = conn.epo
    patcoll = db.patents
    count = 0

    for patent in patcoll.find({"country": "WO"}):
        for lang in patent["claims"]:
            claims = []
            claim_num = 1

            for claim_txt in patent["claims"][lang][0]["text"][1:]:
                fixed_claim = {"text": [claim_txt], "refs": [], "number": str(claim_num)}
                claims.append(fixed_claim)
                claim_num += 1

            patent["claims"][lang] = claims

        patcoll.update_one({"_id": patent["_id"]}, {"$set": {"claims": patent["claims"]}})

        if (count % 1000 == 0):
            print count

        count += 1


if __name__ == "__main__":
    main()
