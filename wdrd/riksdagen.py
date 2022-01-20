import requests


def get_series_docs(session: str, doc_type: str) -> list:
    url = "http://data.riksdagen.se/dokumentlista/"
    params = {"doktyp": doc_type, "rm": session, "utformat": "json"}

    finished = False
    docs = []

    while finished is False:
        resp = requests.get(url, params=params)
        params = {}
        data = resp.json()
        docs.extend(data["dokumentlista"]["dokument"])
        if "@nasta_sida" in data["dokumentlista"]:
            url = data["dokumentlista"]["@nasta_sida"]
        else:
            finished = True

    return docs
