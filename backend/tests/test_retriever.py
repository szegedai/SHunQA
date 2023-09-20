import pytest
import os
from elasticsearch import Elasticsearch
from backend.Pipeline import Pipeline
from backend.pipelines.retriever import Retriever
from backend.exceptions import PipelineFailError, CheckFailError

from transformers import AutoTokenizer, AutoModel
import pickle

es = Elasticsearch(
    "http://rgai3.inf.u-szeged.hu:3427/",
    basic_auth=("elastic", "7ZQhi+zIL357DgjIjyi0"),
    verify_certs=False,
)

pipeline_step = Retriever(
    es,
    "4ig_context_embeddings",
    AutoModel.from_pretrained("facebook/mcontriever-msmarco"),
    AutoTokenizer.from_pretrained("facebook/mcontriever-msmarco"),
    1,
    9,
)


def test_query():
    data = {"query": "A havi bérlet árát megtéríti a munkáltató?"}
    expected_data = {
        "query": "A havi bérlet árát megtéríti a munkáltató?",
        "lemmatized_contexts": [
            "\nmunka járás általános szabály\nidőbeli hatály\na munkáltató az alábbi menetjegy és havi bérlet ár a fent írt mérték térít meg a munkavállaló számára:\nbármely menetjegy vagy havi bérlet, amely a feltüntetett viszonylat alap megállapítható, hogy alkalmas napi munka járás és hazautazás,\nországos kis területi érvényességű havi bérlet, amely meghatározott terület érvényes, továbbá alkalmas és szükséges a napi munka járás és hazautazás történő felhasználás."
        ],
        "official_contexts": [
            "Munkába járás általános szabályai\nIdőbeli hatály\nA munkáltató az alábbi menetjegyek és havi bérletek árának a fent írt mértékét téríti meg a munkavállaló számára:\nbármely menetjegy vagy havi bérlet, amelyről a feltüntetett viszonylat alapján megállapítható, hogy alkalmas napi munkába járásra és hazautazásra,\nországosnál kisebb területi érvényességű havi bérlet, amely meghatározott területen érvényes, továbbá alkalmas és szükséges a napi munkába járásra és hazautazásra történő felhasználásra.\n\n"
        ],
    }
    assert pipeline_step.run(data) == expected_data


def test_empty_query():
    data = {"query": ""}
    expected_data = {"query": "", "official_contexts": [], "lemmatized_contexts": []}
    assert pipeline_step.run(data) == expected_data


def test_missing_query():
    data = {
        "question": "Ha szabad kecskét tartani az irodában, akkor hány éves a kapitány?"
    }
    with pytest.raises(CheckFailError) as e:
        pipeline_step.data_check(data)

    assert e.value.error_code == "missing_query"


def test_bad_index():
    data = {
        "query": "Ha szabad kecskét tartani az irodában, akkor hány éves a kapitány?"
    }
    pipeline_step.elasticsearch_index = "stringified_goats"
    with pytest.raises(PipelineFailError) as e:
        pipeline_step.run(data)

    assert (
        e.value.error_code == "retriever"
        and e.value.description == "index_not_found_exception"
    )
