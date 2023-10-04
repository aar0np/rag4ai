# rag4ai and rag4aiLoader
Downloads the SQuAD dataset from HuggingFace and creates vector embeddings using the OpenAI API. Once the data is in RAM, the embeddings are stored in DataStax Astra DB.

Standalone implementation of the [Chatbot Quickstart](https://docs.datastax.com/en/astra-serverless/docs/vector-search/chatbot-quickstart.html) found in DataStax's documentation.

## Requirements
 - A vector-enabled [Astra DB](https://astra.datastax.com) database
 - An Astra DB secure connect bundle
 - An Astra DB application token (with DBA priviliges)
 - An OpenAI account
 - An OpenAI API key
 - Environment variables defined for: `OPENAI_API_KEY`, `ASTRA_DB_APPLICATION_TOKEN`, and `ASTRA_SCB_PATH`

```
export OPENAI_API_KEY=sk-0dfb78089bdud0fBLAHBLAHBLAH20348
export ASTRA_DB_APPLICATION_TOKEN=AstraCS:GgsdfsdQuMtglFHqKZw:SDGSDDSG6a36d8526BLAHBLAHBLAHc18d40
export ASTRA_SCB_PATH=/Users/aaron.ploetz/local/secure-connect-bundle.zip
```

## Functionality

### rag4aiLoader
Queries the user for their Astra DB keyspace name. Then pulls down the SQuAD dataset, generates embeddings, and stores them into Astra DB. Creates all of the schema that it needs. Given the nature of this program, it really only needs to be run once. After that, the **rag4ai** program can be run exclusively.

### rag4ai
Requres the **rag4aiLoader** program to be run first. Queries the user for their Astra DB keyspace name. Starts with the default question, which is "when was the college of engineering in the University of Notre Dame established?"

Once it answers that question, it loops to ask for more questions until the command `exit` is entered.

## Output
```
» python3 rag4ai.py

Your Astra Keyspace name: vsearch
The College of Engineering at the University of Notre Dame was established in 1920. However, courses in civil and mechanical engineering were already being offered as part of the College of Science since the 1870s. Today, the College of Engineering offers various undergraduate and graduate programs in fields such as aerospace and mechanical engineering, chemical and biomolecular engineering, civil engineering and geological sciences, computer science and engineering, and electrical engineering.

Next question?
```