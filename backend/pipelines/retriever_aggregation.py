from .pipeline_steps import PipelineSteps
from backend.exceptions import CheckFailError, PipelineFailError


class RetrieverAggregation(PipelineSteps):
    """
    A class for aggregating official contexts from retrieved data.

    This class extends `PipelineSteps` and provides functionality for aggregating
    official contexts from retrieved data and preparing the data for further processing.

    Methods:
        run(data: dict) -> dict | PipelineFailError:
            Aggregate official contexts and return the updated data dictionary.

        data_check(data: dict) -> dict | CheckFailError:
            Check the input data for the presence of 'query' and 'official_contexts' keys,
            and return the data dictionary.

    Raises:
        CheckFailError: If the input data lacks 'query' or 'official_contexts' keys.
        PipelineFailError: Raised if the aggregation of official contexts fails during execution
        of the 'run' method.

    """
    def run(self, data: dict) -> dict | PipelineFailError:
        """
        Aggregate official contexts and return the updated data dictionary.

        Args:
            data (dict): A dictionary containing official contexts in the 'official_contexts' field.

        Returns:
            dict | PipelineFailError: A dictionary containing the updated data.

        Raises:
            PipelineFailError: If official context aggregation fails or official_contexts
            are not in the correct format (a list of strings).

        """
        try:
            data["context"] = "\n".join(data["official_contexts"])
        except Exception:
            raise PipelineFailError(
                "context_aggregation_failed",
                "Make sure the official contexts are present and in the correct format. "
                "It should be a list of strings.",
                data,
            )
        return data

    def data_check(self, data: dict) -> dict | CheckFailError:
        """
       Check the input data for the presence of 'query' and 'official_contexts' keys,
       and return the data dictionary.

       Args:
           data (dict): A dictionary containing input data.

       Returns:
           dict | CheckFailError: The input data dictionary.

       Raises:
           CheckFailError: If 'query' or 'official_contexts' keys are missing.

       """
        if "query" not in data.keys() or "official_contexts" not in data.keys():
            raise CheckFailError(
                "missing_query_or_official_contexts",
                "Missing query or official_contexts not passed correctly from retriever",
                data
            )
        return data
