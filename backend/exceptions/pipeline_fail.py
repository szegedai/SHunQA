class PipelineFailError(Exception):
    """Exception raised when a pipeline step fails.

    Args:
        error_code (str): The error code of the error.
        description (str): The description of the error.
        data (dict): Data collected before and in the pipeline.

    Example:
        raise PipelineFailError("elastic_unavailable", "ElasticSearch is not available", {...})
    """
    def __init__(self, error_code: str, description: str, data: dict):
        self.error_code = error_code
        self.description = description
        self.data = data
        super().__init__(self.error_code, self.description, self.data)