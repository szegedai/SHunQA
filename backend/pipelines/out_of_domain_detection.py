from backend.exceptions import CheckFailError, PipelineFailError
from backend.pipelines.pipeline_steps import PipelineSteps

from sklearn.linear_model import LogisticRegression
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast, AutoModel


class OutOfDomainDetection(PipelineSteps):
    def __init__(
        self,
        contriever_model: AutoModel,
        contriever_tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast,
        ood_model: LogisticRegression,
        ood_class: int,
    ):
        self.contriever_model = contriever_model
        self.contriever_tokenizer = contriever_tokenizer
        self.ood_model = ood_model
        self.ood_class = ood_class

    def run(self, data: dict) -> dict | PipelineFailError:
        """Runs the OOD detection pipeline step.

        Args:
            data (dict): The input data as a dictionary.

        Raises:
            PipelineFailError: If the pipeline step fails.

        Returns:
            dict: The modified data after executing the pipeline step.
        """
        predicted_class = self.ood_model.predict(
            self.get_contriever_vector([data["query"]]).detach().numpy()
        )[0].item()

        data["ood_class"] = predicted_class

        if predicted_class != self.ood_class:
            raise PipelineFailError(
                "out_of_domain",
                f"Out of domain: class is {predicted_class} instead of {self.ood_class}",
                data,
            )

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
            raise CheckFailError("missing_query", "Missing query", data)
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
