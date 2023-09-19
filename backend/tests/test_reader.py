import os
import pytest
from transformers import pipeline as hf_pipeline
from backend.pipelines.reader import Reader
from backend.exceptions.check_fail import CheckFailError
from backend.exceptions.pipeline_fail import PipelineFailError

# specify cuda gpu
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"] = "2"


pipeline_step = Reader(
    hf_pipeline(
        task="question-answering",
        model="ZTamas/xlm-roberta-large-squad2-qa-milqa-impossible",
        tokenizer="ZTamas/xlm-roberta-large-squad2-qa-milqa-impossible",
        device=0,  # GPU selection, -1 on CPU
        handle_impossible_answer=True,
        max_answer_len=50,  # This can be modified
    )
)
pipeline_fail = Reader(
    hf_pipeline(
        task="text-generation",
        model="ZTamas/xlm-roberta-large-squad2-qa-milqa-impossible",
        tokenizer="ZTamas/xlm-roberta-large-squad2-qa-milqa-impossible",
        device=0,  # GPU selection, -1 on CPU
        handle_impossible_answer=True,
        max_answer_len=50,  # This can be modified
    )
)


def test_in_domain_question():
    data = {
        "query": "Szabad-e kecskét tartanom az irodámban?",
        "context": "Szabad amennyiben az etetést a gazdája végzi el",
    }
    assert "reader" in pipeline_step.run(data).keys()


def test_missing_query():
    data = {"context": "Szabad amennyiben az etetést a gazdája végzi el"}
    with pytest.raises(CheckFailError) as excinfo:
        pipeline_step.data_check(data)

    assert excinfo.value.error_code == "missing_key_reader"


def test_missing_context():
    data = {"query": "Szabad-e kecskét tartanom az irodámban?"}
    with pytest.raises(CheckFailError) as excinfo:
        pipeline_step.data_check(data)

    assert excinfo.value.error_code == "missing_key_reader"


def test_missing_hf_pipeline():
    data = {
        "query": "Szabad-e kecskét tartanom az irodámban?",
        "context": "Szabad amennyiben az etetést a gazdája végzi el",
    }
    with pytest.raises(PipelineFailError) as excinfo:
        pipeline_fail.run(data)
    assert excinfo.value.error_code == "reader_failed"
