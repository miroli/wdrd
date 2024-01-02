import re
from datetime import datetime
from . import sparql as wd
from . import config as cfg
from .riksdagen import get_doc_metadata


class Document:
    def __init__(self, doc):
        self._doc = doc

    @property
    def doc_id(self):
        return self._doc["id"]

    @property
    def doc_type(self):
        return self._doc["doktyp"]

    @property
    def date(self):
        date_fmt = "+%Y-%m-%dT%H:%M:%SZ"
        return datetime.strptime(self._doc["datum"], "%Y-%m-%d").strftime(date_fmt)

    @property
    def title(self):
        return self._doc["titel"].replace("\n", "").replace("\t", "").strip()

    @property
    def series(self):
        return wd.get_series_qid(self._doc["rm"], self._doc["doktyp"])

    @property
    def session(self):
        return self._doc["rm"]

    @property
    def subtype(self):
        return cfg.motion_subtypes.get(self._doc["subtyp"], "Q452237")

    @property
    def committee(self):
        organ = self._doc["organ"]
        return cfg.committees.get(organ, None) if organ != "" else None

    @property
    def html(self):
        return f"http://data.riksdagen.se/dokument/{self._doc['id']}"

    @property
    def xml(self):
        return f"http://data.riksdagen.se/dokumentstatus/{self._doc['id']}"

    @property
    def pdf(self):
        url = None

        if self._doc["filbilaga"] is None:
            return url

        if isinstance(self._doc["filbilaga"]["fil"], dict):
            return self._doc["filbilaga"]["fil"]["url"]

        for val in self._doc["filbilaga"]["fil"]:
            if val.get("typ", "") == "pdf":
                url = val["url"]
                break
        return url

    @property
    def ordinal(self):
        return self._doc["beteckning"]

    @property
    def cause(self):
        props = wd.get_series_docs(self._doc["rm"], "prop").copy()
        if props.empty:
            return None
        props.ref = props.ref.str.split(expand=True)[1].str.strip()
        prop_ref = re.search("prop\. (\d+/\d+:\d+)", self.title, re.I)
        if prop_ref:
            match = prop_ref.group(1)
            if match in props.ref.to_list():
                return props[props.ref == match].iloc[0]["item"]
        return None

    @property
    def authors(self):
        if self._doc["dokintressent"] is None:
            metadata = get_doc_metadata(self.doc_id)
            meta_authors = metadata["dokumentstatus"].get("dokintressent")
            if meta_authors is None:
                return None
            else:
                self._doc["dokintressent"] = meta_authors
        authors = []
        people = wd.get_people()
        id_mapping = people.set_index("code")["item"].to_dict()

        for person in self._doc["dokintressent"]["intressent"]:
            if person["roll"] != "undertecknare" and self._doc["typ"] != "prop":
                continue
            try:
                authors.append({"name": person["namn"], "qid": id_mapping[person["intressent_id"]]})
            except KeyError:
                authors.append({"name": person["namn"], "qid": None})

        return authors

    @property
    def respondent(self):
        if self._doc["dokintressent"] is None:
            return None
        respondent = None
        people = wd.get_people()
        id_mapping = people.set_index("code")["item"].to_dict()
        name_mapping = people.set_index("code")["itemLabel"].to_dict()

        for person in self._doc["dokintressent"]["intressent"]:
            if person["roll"] == "stalldtill":
                name = name_mapping[person["intressent_id"]]
                qid = id_mapping[person["intressent_id"]]
                respondent = {"name": name, "qid": qid}
                break

        return respondent

    def __repr__(self):
        return f"<Document doc_id={self.doc_id} title={self.title}>"


class DocumentCollection:
    def __init__(self, docs: list):
        self.session = docs[0]["rm"]
        self.doc_type = docs[0]["doktyp"]
        docs = self._remove_invalid_docs(docs)
        docs = self._remove_existing_docs(docs)
        self.docs = [Document(x) for x in docs]

    def _remove_invalid_docs(self, docs):
        filtered_docs = []
        for doc in docs:
            # if self.doc_type == "mot" and doc["subtyp"] == "":
            #    continue
            if self.doc_type == "prop" and doc["subtyp"] != "prop":
                continue
            if doc["titel"] == "Motionen utgår":
                continue
            filtered_docs.append(doc)
        return filtered_docs

    def _remove_existing_docs(self, docs):
        existing_docs = wd.get_series_docs(self.session, self.doc_type)
        return [x for x in docs if x["id"] not in existing_docs.code.to_list()]
