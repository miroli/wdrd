import os
import time
from wikidataintegrator import wdi_core, wdi_login


WD_USERNAME = os.environ.get("WD_USERNAME")
WD_PASSWORD = os.environ.get("WD_PASSWORD")
login_instance = wdi_login.WDLogin(user=WD_USERNAME, pwd=WD_PASSWORD)


def load_collection(docs) -> None:
    summary = f"Adding Riksdagen documents with wdrd."

    for doc in docs:
        try:
            doc.write(login_instance, bot_account=False, edit_summary=summary)
        except wdi_core.NonUniqueLabelDescriptionPairError:
            print('NULD Error')
        time.sleep(1)
