from functools import lru_cache as cache
import pandas as pd
from wikidataintegrator import wdi_core

from . import config


@cache
def get_series_qid(session: str, doc_type: str) -> str:
    session_qid = config.sessions[session]
    doc_type_qid = config.doc_types[doc_type]
    query = (
        "SELECT ?item ?itemLabel WHERE {"
        "?item wdt:P17 wd:Q34 ;"
        f"wdt:P361 wd:{session_qid} ;"
        "p:P31 ?st ."
        "?st ps:P31 wd:Q3511132 ;"
        f"pq:P642 wd:{doc_type_qid} ."
        'SERVICE wikibase:label { bd:serviceParam wikibase:language "sv". }}'
    )

    df = wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe=True)
    return df.loc[0, "item"].split("/")[-1]


@cache
def get_series_docs(session: str, doc_type: str) -> pd.DataFrame:
    series_qid = get_series_qid(session, doc_type)
    doc_type_qid = config.doc_types[doc_type]

    query = (
        "SELECT ?item ?itemLabel ?code ?ref WHERE {"
        f"?item wdt:P31/wdt:P279* wd:{doc_type_qid} ;"
        f"wdt:P179 wd:{series_qid} ;"
        "wdt:P8433 ?code ;"
        "wdt:P1031 ?ref ."
        'SERVICE wikibase:label { bd:serviceParam wikibase:language "sv". }}'
    )
    df = wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe=True)
    if df.empty:
        return pd.DataFrame({"item": [], "itemLabel": [], "code": [], "ref": []})
    df["item"] = df["item"].str.split("/", expand=True)[4]
    return df


@cache
def get_people() -> pd.DataFrame:
    query = """SELECT ?item ?itemLabel ?code WHERE {
    ?item wdt:P1214 ?code .
    
    SERVICE wikibase:label { bd:serviceParam wikibase:language "sv". }
    }"""

    df = wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe=True)
    df.item = df.item.str.split("/", expand=True)[4]
    return df
