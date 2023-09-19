from backend.pipelines.pipeline_steps import PipelineSteps
from backend.pipelines.out_of_domain_detection import OutOfDomainDetection


def handle_error(error: Exception, task_name: str, data: dict) -> dict:
    """
    Handle errors that occur during task execution.

    Args:
        error (Exception): The exception that occurred.
        task_name (str): The name of the task where the error occurred.
        data (dict): input data


    Returns:
        dict: A dictionary containing information about the error.
            - "error_occurred_at" (str): The name of the task where the error occurred.
            - "error" (Exception): The exception that occurred.

    Example:
        try:
            # Code that may raise an exception
            result = some_function()
        except Exception as e:
            error_info = handle_error(e, "some_function", data)
            print(error_info)
    """
    print(f"Error occurred at task: {task_name}")
    return {
        "error_occurred_at": task_name,
        "error": error,
        "data": data
    }


class Pipeline:
    def __init__(self, tasks: list[tuple[str, PipelineSteps]]):
        """
        Initialize a Pipeline object with a list of tasks.

        Args:
            tasks (list[tuple[str, PipelineSteps]]): A list of task tuples where each tuple
                contains a task name (str) and a class inherited from PipelineSteps.

        Raises:
            ValueError: If tasks is None or empty.

        Example:
            tasks = [("task1", PipelineSteps), ("task2", PipelineSteps)]
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
            tasks = [("task1", PipelineSteps), ("task2", PipelineSteps)]
            data = {"query": "value"}
            pipeline = Pipeline(tasks)
            result = pipeline.run(data)
        """

        if not data:
            raise ValueError("data cannot be empty")

        for task_name, task in self.tasks:
            try:
                task.data_check(data)
                data = task.run(data)

            except Exception as e:
                return handle_error(e, task_name, data)
        return data
