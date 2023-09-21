from typing import Any
from elasticsearch import Elasticsearch
from alive_progress import alive_bar

import spacy
import pandas as pd


def upload_to_elastic(
    data: pd.DataFrame,
    columns: list,
    es: Elasticsearch,
    index: str,
    properties: list,
    nested_columns: list = list(),
):
    """Uploads the lemmatized context, the official context and the embeddings to ElasticSearch.

    Args:
        data (pd.DataFrame): The dataframe with data.
        columns (list): The columns to upload.
        es (Elasticsearch): The Elastic client.
        index (str): The name of the Elastic index.
        properties (list): The properties of the Elastic index.
        nested_columns (list | None, optional): The nested columns. Defaults to None.
    """

    with alive_bar(len(data), title="Upload to Elastic") as bar:
        for i, row in data.iterrows():
            doc = {prop: row[column] for column, prop in zip(columns, properties)}
            doc.update(
                {
                    prop: item
                    for column in nested_columns
                    for item, prop in zip(row[column], properties[len(columns) :])
                }
            )

            resp = es.index(
                index=index,
                id=str(i),
                document=doc,
            )

            bar()


if __name__ == "__main__":
    from preprocess import preprocess_data
    from read_write_docx import split_docx
    from mcontriever_embedding import embed_contexts

    es = Elasticsearch(
        "http://rgai3.inf.u-szeged.hu:3427/",
        basic_auth=("elastic", ""),
        verify_certs=False,
    )

    nlp = spacy.load("hu_core_news_trf")

    nlp.remove_pipe("experimental_arc_predicter")
    nlp.remove_pipe("experimental_arc_labeler")
    nlp.remove_pipe("ner")

    data, _ = split_docx(nlp)
    data = embed_contexts(data)
    data = preprocess_data(data, nlp)

    upload_to_elastic(
        data,
        ["lemmatized_text", "text", "embedding", "file_names"],
        es,
        "4ig_context_embeddings",
        ["document", "official_document", "embedding", "file_name", "h1", "h2", "h3"],
        ["headers"],
    )
