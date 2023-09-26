import pytest
from backend.exceptions.check_fail import CheckFailError
from backend.exceptions.pipeline_fail import PipelineFailError
from backend.pipelines.retriever_aggregation import RetrieverAggregation

pipeline_step = RetrieverAggregation()


def test_in_domain_question():
    data = {
        "query": "A havi bérlet árát megtéríti a munkáltató?",
        "lemmatized_contexts": [
            "\nmunka járás általános szabály\nidőbeli hatály\na munkáltató az alábbi menetjegy és havi bérlet ár a fent írt mérték térít meg a munkavállaló számára:\nbármely menetjegy vagy havi bérlet, amely a feltüntetett viszonylat alap megállapítható, hogy alkalmas napi munka járás és hazautazás,\nországos kis területi érvényességű havi bérlet, amely meghatározott terület érvényes, továbbá alkalmas és szükséges a napi munka járás és hazautazás történő felhasználás."
        ],
        "official_contexts": [
            "Munkába járás általános szabályai\nIdőbeli hatály\nA munkáltató az alábbi menetjegyek és havi bérletek árának a fent írt mértékét téríti meg a munkavállaló számára:\nbármely menetjegy vagy havi bérlet, amelyről a feltüntetett viszonylat alapján megállapítható, hogy alkalmas napi munkába járásra és hazautazásra,\nországosnál kisebb területi érvényességű havi bérlet, amely meghatározott területen érvényes, továbbá alkalmas és szükséges a napi munkába járásra és hazautazásra történő felhasználásra.\n\n"
        ],
        "scores": [27.679768],
        "h1": ["Munkába járás általános szabályai"],
        "h2": ["Időbeli hatály"],
        "h3": [None],
        "file_names": [
            "doc_1.docx"
        ],
    }
    assert "context" in pipeline_step.run(data).keys()


def test_missing_query():
    data = {
        "official_contexts": [
            "Munkába járás általános szabályai\nIdőbeli hatály\nA munkáltató az alábbi menetjegyek és havi bérletek árának a fent írt mértékét téríti meg a munkavállaló számára:\nbármely menetjegy vagy havi bérlet, amelyről a feltüntetett viszonylat alapján megállapítható, hogy alkalmas napi munkába járásra és hazautazásra,\nországosnál kisebb területi érvényességű havi bérlet, amely meghatározott területen érvényes, továbbá alkalmas és szükséges a napi munkába járásra és hazautazásra történő felhasználásra.\n\n"
        ]
    }
    with pytest.raises(CheckFailError) as excinfo:
        pipeline_step.data_check(data)

    assert excinfo.value.error_code == "missing_query_or_official_contexts"


def test_missing_context():
    data = {"query": "A havi bérlet árát megtéríti a munkáltató?"}
    with pytest.raises(CheckFailError) as excinfo:
        pipeline_step.data_check(data)

    assert excinfo.value.error_code == "missing_query_or_official_contexts"


def test_missing_context_and_query():
    data = {}
    with pytest.raises(CheckFailError) as excinfo:
        pipeline_step.data_check(data)

    assert excinfo.value.error_code == "missing_query_or_official_contexts"


def test_pipeline_error():
    data = {
        "query": "A havi bérlet árát megtéríti a munkáltató?",
        "context":[
            "Munkába járás általános szabályai\nIdőbeli hatály\nA munkáltató az alábbi menetjegyek és havi bérletek árának a fent írt mértékét téríti meg a munkavállaló számára:\nbármely menetjegy vagy havi bérlet, amelyről a feltüntetett viszonylat alapján megállapítható, hogy alkalmas napi munkába járásra és hazautazásra,\nországosnál kisebb területi érvényességű havi bérlet, amely meghatározott területen érvényes, továbbá alkalmas és szükséges a napi munkába járásra és hazautazásra történő felhasználásra.\n\n"
                   ],
    }
    with pytest.raises(PipelineFailError) as excinfo:
        pipeline_step.run(data)

    assert excinfo.value.error_code == "context_aggregation_failed"
