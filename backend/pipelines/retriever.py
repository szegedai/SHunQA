from backend.pipelines.pipeline_steps import PipelineSteps
from backend.exceptions import CheckFailError, PipelineFailError
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast, AutoModel
from elasticsearch import Elasticsearch, exceptions
from typing import Any


class Retriever(PipelineSteps):
    def __init__(
        self,
        es: Elasticsearch,
        elasticsearch_index: str,
        nlp: Any,
        contriever_model: AutoModel,
        contriever_tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast,
        size: int,
        contriever_weight: int,
    ):
        self.es = es
        self.elasticsearch_index = elasticsearch_index
        self.nlp = nlp
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
            query_embedding = self.get_contriever_vector(data["query"]).tolist()[0]

            clean_query = self.lemmatize_text(data["query"])

            body = {
                "size": self.size,
                "query": {
                    "script_score": {
                        "query": {"match": {"document": clean_query}},
                        "script": {
                            "source": f"_score + {self.contriever_weight} * (cosineSimilarity(params.query_embedding, 'embedding') + 1.0)",
                            "params": {"query_embedding": query_embedding},
                        },
                    }
                },
            }

            s = self.es.search(index=self.elasticsearch_index, body=body)
            contexts = list(s["hits"]["hits"])
            data.update(
                {
                    "official_contexts": [],
                    "lemmatized_contexts": [],
                    "scores": [],
                    "h1": [],
                    "h2": [],
                    "h3": [],
                    "file_names": [],
                }
            )
            for context in contexts:
                data["official_contexts"].append(
                    context["_source"]["official_document"]
                )
                data["lemmatized_contexts"].append(context["_source"]["document"])
                data["scores"].append(context["_score"])
                data["h1"].append(context["_source"].get("h1"))
                data["h2"].append(context["_source"].get("h2"))
                data["h3"].append(context["_source"].get("h3"))
                data["file_names"].append(context["_source"]["file_name"])

        except exceptions.NotFoundError as e:
            raise PipelineFailError(
                "bad_index", "Couldn't find the provided Elastic index", data
            ) from e
        except exceptions.ConnectionError as e:
            raise PipelineFailError(
                "cant_connect_to_elastic", "Can't connect to Elastic", data
            ) from e
        except exceptions.ConnectionTimeout as e:
            raise PipelineFailError(
                "elastic_connection_timeout", "Elastic connection timed out", data
            ) from e

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

    def lemmatize_text(self, text: str) -> str:
        """Lemmatizes the text.

        Args:
            text (str): The text to lemmatize.

        Returns:
            str: The lemmatized text.
        """
        doc = self.nlp(text)
        return " ".join(
            [
                token.lemma_ if token.pos not in ["DET", "ADV", "PRON", "PUNCT"] else ""
                for token in doc
            ]
        )

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
