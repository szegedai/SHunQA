from backend.exceptions import PipelineFailError, CheckFailError
from backend.pipelines.pipeline_steps import PipelineSteps


class MetadataMaker(PipelineSteps):
    def __init__(self):
        pass

    def run(self, data: dict) -> dict | PipelineFailError:
        """Runs the MetadataMaker pipeline step.

        Args:
            data (dict): The input data as a dictionary.

        Returns:
            dict: The modified data after executing the pipeline step.

        Raises:
            PipelineFailError: If the pipeline step fails.
        """
        data["metadata"] = list()
        for i in range(len(data["h1"])):
            data["metadata"].append(
                {
                    "title": data["h1"][i] if data["h1"][i] else "",
                    "section": data["h2"][i]
                    if data["h2"][i]
                    else "" + (" > " + data["h3"][i])
                    if data["h3"][i]
                    else "",
                    "file_name": data["file_names"][i],
                }
            )
        return data

    def data_check(self, data: dict) -> dict | CheckFailError:
        """Checks if the data contains the required keys.

        Args:
            data (dict): The input data as a dictionary.

        Returns:
            dict: The unmodified data after checking the keys.

        Raises:
            CheckFailError: If the data does not contain the required keys.
        """
        if (
            "h1" not in data.keys()
            or "h2" not in data.keys()
            or "h3" not in data.keys()
            or "file_names" not in data.keys()
        ):
            raise CheckFailError(
                "missing_metadata_fields",
                "Make sure the h1, h2, h3, and file_names fields are present in the data.",
                data,
            )
        return data
