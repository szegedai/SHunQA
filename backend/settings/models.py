import pickle
from pydantic_settings import BaseSettings
import spacy
from transformers import AutoModel, AutoTokenizer, pipeline as hf_pipeline

from backend.Pipeline import Pipeline
from backend.pipelines.context_finder import ContextFinder
from backend.pipelines.mongo_save import MongoSave
from backend.pipelines.out_of_domain_detection import OutOfDomainDetection
from backend.pipelines.retriever import Retriever
from backend.pipelines.retriever_aggregation import RetrieverAggregation
from backend.pipelines.reader import Reader
from backend.pipelines.timer import Timer

from backend.settings.environment import (
    environment,
    elasticsearch_connection,
    mongo_client,
)


class ModelSettings(BaseSettings):
    contriever_model_path: str
    qa_model_path: str
    ood_model_path: str
    ood_model_class: int
    spacy_model: str
    gpu: int = -1


model_settings = ModelSettings()  # type: ignore

contriever_model = AutoModel.from_pretrained(model_settings.contriever_model_path)
contriever_tokenizer = AutoTokenizer.from_pretrained(
    model_settings.contriever_model_path
)

qa_pipeline = hf_pipeline(
    task="question-answering",
    model=model_settings.qa_model_path,
    tokenizer=model_settings.qa_model_path,
    device=model_settings.gpu,
    handle_impossible_answer=True,
    max_answer_len=50,  # This can be modified
)

ood_model = pickle.load(open("backend/models/ood_model.pkl", "rb"))

spacy_model = spacy.load(model_settings.spacy_model)
spacy_model.remove_pipe("experimental_arc_predicter")
spacy_model.remove_pipe("experimental_arc_labeler")
spacy_model.remove_pipe("ner")

pipeline_steps = [
    (
        "timer_start",
        Timer(),
    ),
    (
        "out_of_domain_detection",
        OutOfDomainDetection(
            contriever_model,
            contriever_tokenizer,
            ood_model,
            model_settings.ood_model_class,
        ),
    ),
    (
        "retriever",
        Retriever(
            elasticsearch_connection,
            environment.elastic_index,
            spacy_model,
            contriever_model,
            contriever_tokenizer,
            environment.retriever_size,
            environment.retriever_contriever_weight,
        ),
    ),
    (
        "retriever_aggregator",
        RetrieverAggregation(),
    ),
    (
        "reader",
        Reader(
            qa_pipeline,
        ),
    ),
    (
        "context_finder",
        ContextFinder(),
    ),
]

pipeline = Pipeline(pipeline_steps)

pipeline_steps_end = [
    ("timer_end", Timer()),
    ("mongo_save", MongoSave(mongo_client["shunqa"])),
]

pipeline_end = Pipeline(pipeline_steps_end)
