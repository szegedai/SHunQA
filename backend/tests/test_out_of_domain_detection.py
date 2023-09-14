import pytest
from backend.Pipeline import Pipeline
from backend.pipelines.out_of_domain_detection import OutOfDomainDetection
from backend.exceptions import PipelineFailError, CheckFailError

from transformers import AutoTokenizer, AutoModel
from sklearn.linear_model import LogisticRegression
import pickle


pipeline_step = OutOfDomainDetection(
    AutoModel.from_pretrained("facebook/mcontriever-msmarco"),
    AutoTokenizer.from_pretrained("facebook/mcontriever-msmarco"),
    pickle.load(open("backend/models/ood_model.pkl", "rb")),
    1,
)


def test_in_domain_question():
    data = {"query": "Szabad-e kecskét tartanom az irodámban?"}
    assert pipeline_step.run(data) == data | {"ood_class": 1}


def test_out_of_domain_question():
    data = {"query": "Mikor építették a vízlépcsőket a Duna felső szakaszán?"}
    with pytest.raises(PipelineFailError) as excinfo:
        pipeline_step.run(data)

    assert (
        excinfo.value.data == data | {"ood_class": 0}
        and excinfo.value.error_code == "out_of_domain"
    )


def test_query_missing():
    data = {"query2": "Mikor építették a vízlépcsőket a Duna felső szakaszán?"}
    with pytest.raises(CheckFailError) as excinfo:
        pipeline_step.data_check(data)

    assert excinfo.value.error_code == "missing_query"
