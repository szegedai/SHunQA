from backend.pipelines.pipeline_steps import PipelineSteps
from backend.pipelines.out_of_domain_detection import OutOfDomainDetection


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

        Example:
            tasks = [("task1", PipelineSteps), ("task2", PipelineSteps)]
            data = {"query": "value"}
            pipeline = Pipeline(tasks)
            result = pipeline.run(data)
        """

        if not data:
            raise ValueError("data cannot be empty")

        for task_name, task in self.tasks:
            task.data_check(data)
            data = task.run(data)

        return data
