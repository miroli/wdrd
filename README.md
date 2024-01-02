## Get started

This repository contains code for importing data from Riksdagen to Wikidata. To run the code in this repo, you need to setup authentication as per https://github.com/SuLab/WikidataIntegrator. See the `test.ipynb` notebook to get started.

There are four main functions:

- `extract_docs` downloads documents from the Riksdagen API.
- `prepare_docs` takes the raw documents and does some basic cleaning, returning a `DocumentCollection`.
- `transform_docs` takes the `DocumentCollection` and returns a list of WikidataIntegrator items ready to be loaded to Wikidata.
- `load_docs` loads the prepared and transformed documents to Wikidata.

## Supported document types
- <s>Motion</s>
- <s>Proposition</s>
- <s>Interpellation</s>
- <s>Skriftlig fråga</s>
- Protokoll
- Utskottsbetänkande
- Utredningsbetänkande
- Kommittédirektiv
- Lag