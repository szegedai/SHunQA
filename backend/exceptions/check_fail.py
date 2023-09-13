class CheckFailError(Exception):
    """Exception raised when a check fails.

    Args:
        error_code (str): The error code of the check.
        description (str): The description of the error.

    Example:
        raise CheckFailError("query_missing", "Query is missing")
    """
    def __init__(self, error_code: str, description: str):
        self.error_code = error_code
        self.description = description
        super().__init__(self.error_code, self.description)