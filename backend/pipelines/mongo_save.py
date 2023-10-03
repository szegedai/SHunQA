from backend.exceptions import PipelineFailError
from backend.pipelines.pipeline_steps import PipelineSteps

from pymongo.database import Database


class MongoSave(PipelineSteps):
    def __init__(self, database: Database):
        self.database = database

    def run(self, data: dict) -> dict | PipelineFailError:
        """Runs the MongoSave pipeline step.

        Args:
            data (dict): The input data as a dictionary.

        Raises:
            PipelineFailError: If the pipeline step fails.

        Returns:
            dict: The modified data after executing the pipeline step.
        """
        try:
            data["id"] = str(self.database["qa"].insert_one(data).inserted_id)
            del data["_id"]
        except Exception as e:
            raise PipelineFailError("mongo_save", f"mongo failed: {str(e)}", data)
        return data

    def data_check(self, data: dict) -> dict:
        """Checks if the data contains the required keys.

        Args:
            data (dict): The input data as a dictionary.

        Returns:
            dict: The unmodified data after checking the keys.
        """
        return data
