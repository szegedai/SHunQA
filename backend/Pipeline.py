def handle_error(error: Exception, task_name: str) -> dict:
    """
    Handle errors that occur during task execution.

    Args:
        error (Exception): The exception that occurred.
        task_name (str): The name of the task where the error occurred.

    Returns:
        dict: A dictionary containing information about the error.
            - "error_occurred_at" (str): The name of the task where the error occurred.
            - "error" (Exception): The exception that occurred.

    Example:
        try:
            # Code that may raise an exception
            result = some_function()
        except Exception as e:
            error_info = handle_error(e, "some_function")
            print(error_info)
    """
    print(f"Error occurred at task: {task_name}")
    return {
        "error_occurred_at": task_name,
        "error": error,
    }


class Pipeline:
    def __init__(self, tasks: list[tuple[str, callable]]):
        """
        Initialize a Pipeline object with a list of tasks.

        Args:
            tasks (list[tuple[str, callable]]): A list of task tuples where each tuple
                contains a task name (str) and a callable function.

        Raises:
            ValueError: If tasks is None or empty.

        Example:
            tasks = [("task1", function1), ("task2", function2)]
            pipeline = Pipeline(tasks)
        """
        if tasks is None or len(tasks) == 0:
            raise ValueError("tasks cannot be None")
        self.tasks = tasks
        self.task_names = list(zip(*tasks))[0]

    def run(self, data: dict) -> dict:
        """
        Execute the pipeline of tasks on the input data.

        Args:
            data (dict): The input data as a dictionary.

        Returns:
            dict: The modified data after executing all tasks.

        Raises:
            ValueError: If data is empty.

        Example:
            data = {"key": "value"}
            pipeline = Pipeline(tasks)
            result = pipeline.run(data)
        """
        if not data:
            raise ValueError("data cannot be empty")

        for task_name, task_func in self.tasks:
            try:
                data = task_func(data)
            except Exception as e:
                return handle_error(e, task_name)
        return data
