from .pipeline_steps import PipelineSteps
from backend.exceptions import CheckFailError, PipelineFailError
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast, AutoModel
from elasticsearch import Elasticsearch
import elastic_transport


class Retriever(PipelineSteps):
    def __init__(
        self,
        es: Elasticsearch,
        elasticsearch_index: str,
        contriever_model: AutoModel,
        contriever_tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast,
        size: int,
        contriever_weight: int,
    ):
        self.es = es
        self.elasticsearch_index = elasticsearch_index
        self.contriever_model = contriever_model
        self.contriever_tokenizer = contriever_tokenizer
        self.size = size
        self.contriever_weight = contriever_weight

    def run(self, data: dict) -> dict | PipelineFailError:
        """Runs the retriever pipeline step.

        Args:
            data (dict): The input data as a dictionary.

        Raises:
            PipelineFailError: If the pipeline step fails.

        Returns:
            dict: The modified data after executing the pipeline step.
        """
        try:
            query_embedding = self.get_contriever_vector(data["query"])

            body = {
                "size": self.size,
                "query": {
                    "script_score": {
                        "querry": {"match": {"document": data["query"]}},
                        "script": {
                            "source": f"_score + {self.contriever_weight} * (cosineSimilarity(params.query_embedding, 'embedding') + 1.0)",
                            "params": {"query_embedding": query_embedding},
                        },
                    }
                },
            }

            s = self.es.search(index=self.elasticsearch_index, body=body)
            contexts = list(s["hits"]["hits"])
            data["official_contexts"] = [
                context["_source"]["official_document"] for context in contexts
            ]
            data["lemmatized_contexts"] = [
                context["_source"]["document"] for context in contexts
            ]
        except elastic_transport.ConnectionError:
            raise PipelineFailError("retriever", "Can't connect to Elastic", data)
        except elastic_transport.ConnectionTimeout:
            raise PipelineFailError("retriever", "ElasticSearch timed out", data)

        return data

    def data_check(self, data: dict) -> dict | CheckFailError:
        """Checks if the data contains the required keys.

        Args:
            data (dict): The input data as a dictionary.

        Raises:
            CheckFailError: If the data does not contain the required keys.

        Returns:
            dict: The unmodified data after checking the keys.
        """
        if "query" not in data.keys():
            raise CheckFailError("missing_query", "Missing query")
        return data

    def get_contriever_vector(self, sentences):
        inputs = self.contriever_tokenizer(
            sentences, padding=True, truncation=True, return_tensors="pt"
        )

        outputs = self.contriever_model(**inputs)  # type: ignore

        def mean_pooling(token_embeddings, mask):
            token_embeddings = token_embeddings.masked_fill(
                ~mask[..., None].bool(), 0.0
            )
            sentence_embeddings = (
                token_embeddings.sum(dim=1) / mask.sum(dim=1)[..., None]
            )
            return sentence_embeddings

        return mean_pooling(outputs[0], inputs["attention_mask"])
