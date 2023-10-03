import time
from backend.exceptions.pipeline_fail import PipelineFailError
from backend.pipelines.pipeline_steps import PipelineSteps


class Timer(PipelineSteps):
    def __init__(self):
        pass

    def run(self, data: dict) -> dict | PipelineFailError:
        """Runs the Timer pipeline step.

        Args:
            data (dict): The input data as a dictionary.

        Raises:
            PipelineFailError: If the pipeline step fails.

        Returns:
            dict: The modified data after executing the pipeline step.
        """
        if "start_time" not in data.keys():
            data["start_time"] = time.time()
        else:
            data["end_time"] = time.time()
            data["elapsed_time"] = data["end_time"] - data["start_time"]
        return data

    def data_check(self, data: dict) -> dict:
        """Checks if the data contains the required keys.

        Args:
            data (dict): The input data as a dictionary.

        Returns:
            dict: The unmodified data after checking the keys.
        """
        return data
