from .pipeline_steps import PipelineSteps
from backend.exceptions.check_fail import CheckFailError
from backend.exceptions.pipeline_fail import PipelineFailError
from transformers import pipeline


class Reader(PipelineSteps):
    """
    A class for processing text using a huggingface transformers pipeline.

    This class extends `PipelineSteps` and provides functionality for running
    a transformer-based reader pipeline on input data.

    Args:
        pipe (pipeline): The pipeline used for processing.

    Attributes:
        pipeline (pipeline): The pipeline used for processing.

    Methods:
        run(data: dict) -> dict:
            Run the reader pipeline on the provided data.

        data_check(data: dict) -> ict:
            Check if the input data is valid and query, context exists as key.

    Raises:
        CheckFailError: If the input data is missing or empty.
        PipelineFailError: If the reader pipeline encounters an exception.

    """
    def __init__(self, hf_pipeline: pipeline):
        """
        Initialize a Reader object with the provided pipeline.

        Args:
            hf_pipeline (pipeline): The reader pipeline to use for processing.
        """
        self.pipeline = hf_pipeline
        super().__init__()

    def run(self, data: dict) -> dict:
        """
        Run the pipeline on the input data.

        Args:
            data (dict): A dictionary containing the input data, including 'question' and 'context' fields.

        Returns:
            dict: A dictionary containing the input data along with the reader pipeline results.

        Raises:
            CheckFailError: If the input data is missing or empty.
            PipelineFailError: If the reader pipeline encounters an exception.

        """
        data = self.data_check(data)
        try:
            results = self.pipeline(
                question=data['query'],
                context=data['context']
            )
            data["reader"] = results
            return data
        except Exception as e:
            raise PipelineFailError(
                "reader_failed",
                "check if data or pipeline was passed correctly",
                data
            )

    def data_check(self, data: dict) -> dict:
        """
        Check if the input data is valid (query and context in the data keys).

        Args:
            data (dict): A dictionary containing the input data.

        Returns:
            dict: returns the input data if it is valid.

        """
        if "query" not in data.keys() or "context" not in data.keys():
            raise CheckFailError(
                "missing_key_reader",
                "Missing query or context in data dict keys"
            )
        return data

