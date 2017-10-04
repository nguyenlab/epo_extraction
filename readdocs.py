import sys
import os
import re
from xml.etree import ElementTree
from pymongo import MongoClient

from epo_patdoc import PatentDocument, PatDocMetaRef, PatDocParty, PatentClaim, IPCInfo 


def readdoc(filename):
    patdoc = PatentDocument()

    try:
        doc = ElementTree.parse(filename)
        root_node = doc.getroot()
        print "Processing: ", filename

        patdoc.country = root_node.attrib["country"]
        patdoc.number = root_node.attrib["doc-number"]
        patdoc.kind = root_node.attrib["kind"]
        patdoc.date = datetime.strptime(root_node.attrib["date"], "%Y%m%d")
        patdoc.lang = root_node.attrib["lang"]

        for appl_ref in root_node.findall("./bibliographic-data/application-reference/document-id"):
            patdoc.application_ref.country = appl_ref.find("country").text
            patdoc.application_ref.number = appl_ref.find("doc-number").text
            patdoc.application_ref.kind = appl_ref.find("kind").text
            patdoc.application_ref.date = datetime.strptime(appl_ref.find("date").text, "%Y%m%d")
        
        for publ_ref in root_node.findall("./bibliographic-data/publication-reference/document-id"):
            patdoc.publication_ref.country = publ_ref.find("country").text
            patdoc.publication_ref.number = publ_ref.find("doc-number").text
            patdoc.publication_ref.kind = publ_ref.find("kind").text
            patdoc.publication_ref.date = datetime.strptime(publ_ref.find("date").text, "%Y%m%d")
       
        for pr_claim in root_node.findall("./bibliographic-data/priority-claims/priority-claim"):
            priority_claim = PatDocMetaRef()
            for doc_id in pr_claim.findall("./document-id"):
                try:
                    priority_claim.country = doc_id.find("country").text
                    priority_claim.number = doc_id.find("doc-number").text
                    priority_claim.date = datetime.strptime(doc_id.find("date").text, "%Y%m%d")
                    priority_claim.kind = doc_id.find("kind").text
                except AttributeError:
                    pass

            patdoc.priority_claims.append(priority_claim)

        for title in root_node.findall("./bibliographic-data/technical-data/invention-title"):
            patdoc.title[title.get("lang")] = title.text.strip()

        for cls in root_node.findall("./bibliographic-data/technical-data/classifications-ipcr/classification-ipcr"):
            ipc_info = IPCInfo()
            subclass, subgroup, version, classif_code = tuple([el.strip() for el in cls.text.strip().split() if el.strip() != ""])
            ipc_info.subclass = subclass
            ipc_info.subgroup = subgroup
            ipc_info.version = version
            ipc_info.classif_code = classif_code
            patdoc.class_ipcr.append(ipc_info)

            for appl in root_node.findall("./bibliographic-data/parties/applicants/applicant"):
                applicant = PatDocParty()
                try:
                    applicant.name = appl.find("./addressbook/name").text.strip()
                    applicant.country = appl.find("./addressbook/address/country").text.strip()
                except AttributeError:
                    pass
                
                if (applicant.name != "" and (applicant.name not in [applc.name for applc in patdoc.applicants])):
                    patdoc.applicants.append(applicant)

            for invt in root_node.findall("./bibliographic-data/parties/inventors/inventor"):
                inventor = PatDocParty()
                try:
                    inventor.name = invt.find("./addressbook/name").text.strip()
                    inventor.country = invt.find("./addressbook/address/country").text.strip()
                except AttributeError:
                    pass
                
                if (inventor.name != "" and (inventor.name not in [invtr.name for invtr in patdoc.inventors])):
                    patdoc.inventors.append(inventor)
        
            for agt in root_node.findall("./bibliographic-data/parties/agents/agent"):
                agent = PatDocParty()
                try:
                    agent.name = agt.find("./addressbook/last-name").text.strip()
                    agent.country = agt.find("./addressbook/address/country").text.strip()
                except AttributeError:
                    pass
                
                if (agent.name != "" and (agent.name not in [agnt.name for agnt in patdoc.agents])):
                    patdoc.agents.append(agent)
        

        for country in root_node.findall("./bibliographic-data/international-convention-data/designated-states/ep-contracting-states/country"):
            patdoc.designated_states.append(country.text)

        for abstract in root_node.findall("./abstract"):
            patdoc.abstract[abstract.get("lang")] = []
            
            for paragraph in abstract.itertext():
                if (paragraph):
                    patdoc.abstract[abstract.get("lang")].append(paragraph.strip())

        for description in root_node.findall("./description"):
            patdoc.description[description.get("lang")] = []
            
            for paragraph in description.itertext():
                if (paragraph):
                    patdoc.description[description.get("lang")].append(paragraph.strip().replace("\n", ""))

        

        for claims in root_node.findall("./claims"):
            clm_lang = claims.get("lang")
            patdoc.claims[clm_lang] = []
            patdoc.claims_source = claims.get("load-source")
            claim_count = 1

            if (patdoc.claims_source == "epoque"):
                for paragraph in claims.findall("./claim/claim-text"):
                    add_claim = False
                    if (re.match(r"^CLAIMS", paragraph.text.strip(), re.I)):
                        continue
                    elif (re.match(r"^\d+\.", paragraph.text.strip(), re.I)):
                        add_claim = True
                    else:
                        if (len(patdoc.claims[clm_lang]) > 0):
                            patdoc.claims[clm_lang][-1].text.append(paragraph.text.strip().replace("\n", ""))
                        else:
                            add_claim = True

                    if (add_claim):
                        claim = PatentClaim()
                        claim.number = claim_count
                        claim.text.append(paragraph.text.strip().replace("\n", ""))
                        patdoc.claims[clm_lang].append(claim)
                        claim_count += 1

            else:
                for clm in claims.findall("./claim"):
                    claim = PatentClaim()
                    claim.number = clm.get("num")

                    for paragraph in clm.itertext():
                        if (paragraph):
                            claim.text.append(paragraph.strip().replace("\n", ""))

                    patdoc.claims[clm_lang].append(claim)
    except ElementTree.ParseError as e:
        sys.stderr.write("XML error parsing file: %s" + repr(e))

    return patdoc


def selectdocs(docs_path):
    selected_docs = []

    for filename in os.listdir(docs_path):
        patdoc = readdoc(os.path.join(docs_path, filename))
        if (patdoc.lang == "EN" and len(patdoc.claims["EN"]) > 0):
            selected_docs.append(patdoc.to_dict())

    conn = MongoClient()
    db = conn.epo
    patcoll = db.patents
    patcoll.insert_many(selected_docs)



def main(argv):
    selectdocs(argv[1])


if __name__ == "__main__":
    main(sys.argv)
