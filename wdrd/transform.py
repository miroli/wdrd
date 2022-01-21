from datetime import datetime
import pandas as pd
from wikidataintegrator import wdi_core


def create_item(doc):
    if doc.doc_type == "mot":
        return create_motion(doc)
    elif doc.doc_type == "prop":
        return create_proposition(doc)
    return


def create_motion(doc):
    data = []
    now = datetime.now().strftime("+%Y-%m-%dT00:00:00Z")

    ref = []
    ref.append(
        wdi_core.WDUrl(
            f"http://data.riksdagen.se/dokument/{doc.doc_id}",
            prop_nr="P854",
            is_reference=True,
        )
    )
    ref.append(wdi_core.WDTime(now, prop_nr="P813", is_reference=True))
    ref.append(wdi_core.WDMonolingualText(doc.title, language="sv", prop_nr="P1476", is_reference=True))

    num_qual = wdi_core.WDString(str(doc.ordinal), prop_nr="P1545", is_qualifier=True)
    det_qual = wdi_core.WDItemID("Q80211245", prop_nr="P459", is_qualifier=True)

    instance = wdi_core.WDItemID(doc.subtype, prop_nr="P31", references=[ref])
    jurisdiction = wdi_core.WDItemID("Q34", prop_nr="P1001")
    title = wdi_core.WDMonolingualText(doc.title, language="sv", prop_nr="P1476", references=[ref])
    series = wdi_core.WDItemID(doc.series, prop_nr="P179", qualifiers=[num_qual])
    lang = wdi_core.WDItemID("Q9027", prop_nr="P407")
    date = wdi_core.WDTime(doc.date, prop_nr="P577", references=[ref])
    legal_ref = wdi_core.WDString(f"mot. {doc.session}:{doc.ordinal}", prop_nr="P1031")
    copyright = wdi_core.WDItemID("Q19652", prop_nr="P6216", qualifiers=[det_qual])

    html_qual = wdi_core.WDItemID("Q62626012", prop_nr="P2701", is_qualifier=True)
    available_html = wdi_core.WDUrl(doc.html, prop_nr="P953", qualifiers=[html_qual])

    xml_qual = wdi_core.WDItemID("Q3033641", prop_nr="P2701", is_qualifier=True)
    available_xml = wdi_core.WDUrl(doc.xml, prop_nr="P953", qualifiers=[xml_qual])

    pdf_qual = wdi_core.WDItemID("Q42332", prop_nr="P2701", is_qualifier=True)
    available_pdf = wdi_core.WDUrl(doc.pdf, prop_nr="P953", qualifiers=[pdf_qual])

    if doc.prop:
        prop = wdi_core.WDItemID(doc.prop, prop_nr="P1478")

    if doc.committee:
        committee = wdi_core.WDItemID(doc.committee, prop_nr="P7727", references=[ref])
    else:
        committee = None
    code = wdi_core.WDExternalID(doc.doc_id, "P8433")

    signs = []
    over_one = len(doc.authors) > 1
    sign_codes = []
    for i, person in enumerate(doc.authors):
        if person["qid"] in sign_codes:
            continue
        sign_codes.append(person["qid"])
        if over_one:
            sign_qual = wdi_core.WDString(str(i + 1), prop_nr="P1545", is_qualifier=True)
            obj = wdi_core.WDItemID(person["qid"], prop_nr="P50", references=[ref], qualifiers=[sign_qual])
        else:
            obj = wdi_core.WDItemID(person["qid"], prop_nr="P50", references=[ref])
        signs.append(obj)

    data = [
        instance,
        jurisdiction,
        title,
        series,
        lang,
        date,
        legal_ref,
        copyright,
        available_html,
        available_xml,
        available_pdf,
        code,
    ]

    if not pd.isna(doc.prop):
        data.append(prop)

    if committee:
        data.append(committee)

    data.extend(signs)

    item = wdi_core.WDItemEngine(data=data, new_item=True)
    item.set_label(doc.title, lang="sv")
    label_name = doc.authors[0]["namn"]
    label_date = doc.date[1:5]
    if over_one:
        et_al_sv, et_al_en = " m.fl. ", " et al. "
        label_name = label_name.replace("av ", "")
    else:
        et_al_sv = et_al_en = " "
    item.set_description(f"motion av {label_name}{et_al_sv}från {label_date}", lang="sv")
    item.set_description(f"motion by {label_name}{et_al_en}from {label_date}", lang="en")

    return item


def create_proposition(doc):
    data = []
    now = datetime.now().strftime("+%Y-%m-%dT00:00:00Z")

    ref = []
    ref.append(
        wdi_core.WDUrl(
            f"http://data.riksdagen.se/dokument/{doc.doc_id}",
            prop_nr="P854",
            is_reference=True,
        )
    )
    ref.append(wdi_core.WDTime(now, prop_nr="P813", is_reference=True))
    ref.append(wdi_core.WDMonolingualText(doc.title, language="sv", prop_nr="P1476", is_reference=True))

    num_qual = wdi_core.WDString(str(doc.ordinal), prop_nr="P1545", is_qualifier=True)
    det_qual = wdi_core.WDItemID("Q80211245", prop_nr="P459", is_qualifier=True)

    instance = wdi_core.WDItemID("Q686822", prop_nr="P31", references=[ref])
    jurisdiction = wdi_core.WDItemID("Q34", prop_nr="P1001")
    title = wdi_core.WDMonolingualText(doc.title, language="sv", prop_nr="P1476", references=[ref])
    series = wdi_core.WDItemID(doc.series, prop_nr="P179", qualifiers=[num_qual])
    lang = wdi_core.WDItemID("Q9027", prop_nr="P407")
    date = wdi_core.WDTime(doc.date, prop_nr="P577", references=[ref])
    legal_ref = wdi_core.WDString(f"mot. {doc.session}:{doc.ordinal}", prop_nr="P1031")
    copyright = wdi_core.WDItemID("Q19652", prop_nr="P6216", qualifiers=[det_qual])

    html_qual = wdi_core.WDItemID("Q62626012", prop_nr="P2701", is_qualifier=True)
    available_html = wdi_core.WDUrl(doc.html, prop_nr="P953", qualifiers=[html_qual])

    xml_qual = wdi_core.WDItemID("Q3033641", prop_nr="P2701", is_qualifier=True)
    available_xml = wdi_core.WDUrl(doc.xml, prop_nr="P953", qualifiers=[xml_qual])

    pdf_qual = wdi_core.WDItemID("Q42332", prop_nr="P2701", is_qualifier=True)
    available_pdf = wdi_core.WDUrl(doc.pdf, prop_nr="P953", qualifiers=[pdf_qual])

    if doc.committee:
        committee = wdi_core.WDItemID(doc.committee, prop_nr="P7727", references=[ref])
    else:
        committee = None
    code = wdi_core.WDExternalID(doc.doc_id, "P8433")

    data = [
        instance,
        jurisdiction,
        title,
        series,
        lang,
        date,
        legal_ref,
        copyright,
        available_html,
        available_xml,
        available_pdf,
        code,
    ]

    if committee:
        data.append(committee)

    item = wdi_core.WDItemEngine(data=data, new_item=True)
    item.set_label(doc.title, lang="sv")

    item.set_description(f"proposition i Riksdagen från {doc.date[1:11]}", lang="sv")
    item.set_description(f"proposition in the Riksdag from {doc.date[1:11]}", lang="en")

    return item
