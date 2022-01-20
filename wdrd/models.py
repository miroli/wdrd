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
    ordinal: int
    authors: list
    attachment: dict

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


class MotionCollection:
    def __init__(self, docs: list):
        self.docs = []
        for doc in docs:
            if doc["subtyp"] == "":
                continue
            if doc["titel"] == "Motionen utgår":
                continue
            motion = Motion(
                doc["id"],
                doc["datum"],
                doc["titel"],
                doc["rm"],
                doc["subtyp"],
                doc["organ"],
                int(doc["beteckning"]),
                doc["dokintressent"]["intressent"],
                doc["filbilaga"],
            )
            self.docs.append(motion)

    def remove_existing_docs(self):
        existing_docs = wd.get_series_docs(self.docs[0].session, "mot")
        self.docs = [x for x in self.docs if x.doc_id not in existing_docs.code.to_list()]
