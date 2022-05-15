import logging

logging.captureWarnings(True)

from . import document, riksdagen, wd_item, load


def extract_docs(session: str, doc_type: str) -> list:
    return riksdagen.get_series_docs(session, doc_type)


def prepare_docs(docs: list) -> list:
    collection = document.DocumentCollection(docs)
    return collection


def transform_docs(collection: document.DocumentCollection) -> list:
    items = [wd_item.create_item(x) for x in collection.docs]
    return items


def load_docs(items: list) -> None:
    load.load_collection(items)
