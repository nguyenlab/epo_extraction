import json
import copy

class PatDocMetaRef:
    def __init__(self):
        self.country = ""
        self.number = ""
        self.kind = ""
        self.date = ""


class PatDocParty:
    def __init__(self):
        self.name = ""
        self.country = ""


class PatentClaim:
    def __init__(self):
        self.number = 0
        self.text = []
        self.refs = []


class IPCInfo:
    def __init__(self):
        self.subclass = ""
        self.subgroup = ""
        self.version = ""
        self.classif_code = ""



class PatentDocument:
    def __init__(self):
        self.country = ""
        self.number = ""
        self.kind = ""
        self.date = ""
        self.application_ref = PatDocMetaRef()
        self.publication_ref = PatDocMetaRef()
        self.priority_claims = []
        self.lang = "" 
        self.class_ipcr = []
        self.title = {"EN": ""}
        self.applicants = []
        self.inventors = []
        self.agents = []
        self.designated_states = []
        self.abstract = {"EN": []}
        self.description = {"EN": []}
        self.claims = {"EN": []}
        self.claims_source = ""

    def to_dict(self):
        d_repr = copy.deepcopy(self.__dict__)
        d_repr["application_ref"] = self.application_ref.__dict__
        d_repr["publication_ref"] = self.publication_ref.__dict__
        d_repr["class_ipcr"] = []
        d_repr["priority_claims"] = []

        for ipc_info in self.class_ipcr:
            d_repr["class_ipcr"].append(ipc_info.__dict__)

        for pr_claim in self.priority_claims:
            d_repr["priority_claims"].append(pr_claim.__dict__)
        
        for field in ["applicants", "inventors", "agents"]:
            d_repr[field] = []
            for ent in getattr(self, field):
                d_repr[field].append(ent.__dict__)

        for lang in self.claims:
            d_repr["claims"][lang] = []
            for claim in self.claims[lang]:
                d_repr["claims"][lang].append(claim.__dict__)

        return d_repr

    def to_json(self):
        return json.dumps(self.to_dict())

