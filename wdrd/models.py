import re
from dataclasses import dataclass
from datetime import datetime
from . import sparql as wd
from . import config as cfg


@dataclass
class Motion:
    doc_id: str
    date: str
    title: str
    session: str
    subtype: str
    committee: str
    ordinal: str
    authors: list
    attachment: dict
    doc_type: str = "mot"

    def __post_init__(self):
        date_fmt = "+%Y-%m-%dT%H:%M:%SZ"
        self.title = self.title.strip()
        self.subtype = cfg.motion_subtypes[self.subtype]
        self.committee = cfg.committees.get(self.committee, None) if self.committee != "" else None
        self.date = datetime.strptime(self.date, "%Y-%m-%d").strftime(date_fmt)
        self.html = f"http://data.riksdagen.se/dokument/{self.doc_id}"
        self.xml = f"http://data.riksdagen.se/dokumentstatus/{self.doc_id}"
        self.pdf = self.extract_pdf()
        self.prop = self.extract_prop()
        self.series = wd.get_series_qid(self.session, "mot")
        self.add_author_qids()

    def extract_pdf(self):
        url = None

        if self.attachment is None:
            return url

        for val in self.attachment["fil"]:
            if val.get("typ", "") == "pdf":
                url = val["url"]
                break
        return url

    def add_author_qids(self):
        id_mapping = wd.get_personal_identifier_mapping()

        for person in self.authors:
            person["qid"] = id_mapping[person["intressent_id"]]

    def extract_prop(self):
        props = wd.get_series_docs(self.session, "prop").copy()
        props.ref = props.ref.str.split(expand=True)[1].str.strip()
        prop_ref = re.search("prop\. (\d+/\d+:\d+)", self.title, re.I)
        if prop_ref:
            match = prop_ref.group(1)
            if match in props.ref.to_list():
                return props[props.ref == match].iloc[0]["item"]
        return None


@dataclass
class Proposition:
    doc_id: str
    date: str
    title: str
    session: str
    subtype: str
    committee: str
    ordinal: str
    attachment: dict
    doc_type: str = "prop"

    def __post_init__(self):
        date_fmt = "+%Y-%m-%dT%H:%M:%SZ"
        self.title = self.title.strip()
        self.committee = cfg.committees.get(self.committee, None) if self.committee != "" else None
        self.date = datetime.strptime(self.date, "%Y-%m-%d").strftime(date_fmt)
        self.html = f"http://data.riksdagen.se/dokument/{self.doc_id}"
        self.xml = f"http://data.riksdagen.se/dokumentstatus/{self.doc_id}"
        self.pdf = self.extract_pdf()
        self.series = wd.get_series_qid(self.session, "prop")

    def extract_pdf(self):
        if self.attachment is None:
            return None
        return self.attachment["fil"]["url"]


class DocCollection:
    def __init__(self, docs: list):
        self.session = self.docs[0].session
        self.doc_type = self.docs[0].doc_type
        docs = self.remove_invalid_docs(docs)
        docs = self.remove_existing_docs(docs)
        self.prepare_docs(docs)

    def prepare_docs(self, docs):
        for doc in docs:
            if self.doc_type == "mot":
                self.docs.append(
                    Motion(
                        doc_id=doc["id"],
                        date=doc["datum"],
                        title=doc["titel"],
                        session=doc["rm"],
                        subtype=doc["subtyp"],
                        committe=doc["organ"],
                        ordinal=doc["beteckning"],
                        authors=doc["dokintressent"]["intressent"],
                        attachment=doc["filbilaga"],
                    )
                )
            elif self.doc_type == "prop":
                self.docs.append(
                    Proposition(
                        doc_id=doc["id"],
                        date=doc["datum"],
                        title=doc["titel"],
                        session=doc["rm"],
                        subtype=doc["subtyp"],
                        committe=doc["organ"],
                        ordinal=doc["beteckning"],
                        attachment=doc["filbilaga"],
                    )
                )

    def remove_invalid_docs(self, docs):
        filtered_docs = []
        for doc in docs:
            if self.doc_type == "mot" and doc["subtyp"] == "":
                continue
            if self.doc_type == "mot" and doc["subtyp"] != "prop":
                continue
            if doc["titel"] == "Motionen utgår":
                continue
            filtered_docs.append(doc)
        return filtered_docs

    def remove_existing_docs(self, docs):
        existing_docs = wd.get_series_docs(self.session, self.doc_type)
        return [x for x in docs if x["id"] not in existing_docs.code.to_list()]
