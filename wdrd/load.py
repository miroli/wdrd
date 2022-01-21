import os
from wikidataintegrator import wdi_core, wdi_login
from . import riksdagen, transform
from . import models
from . import transform


WD_USERNAME = os.environ.get("WD_USERNAME")
WD_PASSWORD = os.environ.get("WD_PASSWORD")
login_instance = wdi_login.WDLogin(user=WD_USERNAME, pwd=WD_PASSWORD)


def load_collection(session: str, doc_type: str) -> None:
    summary = f"Adding Riksdagen documents with wdrd."
    docs = riksdagen.get_series_docs(session, doc_type)
    collection = models.DocCollection(docs)

    for doc in collection.docs:
        print(f"Loading doc {doc.doc_id}: {doc.title}", end="\n\n")
        wd_item = transform.create_item(doc)
        try:
            wd_item.write(login_instance, bot_account=False, edit_summary=summary)
        except wdi_core.NonUniqueLabelDescriptionPairError:
            print(doc.title)
            continue
