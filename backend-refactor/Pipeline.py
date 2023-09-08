import Retriever
import Reader
import OutOfDomainDetection
import RetrieverAgreg


class Pipeline:
    """A data processing pipeline for performing various tasks.

    Args:
        data (dict): The input data as a dict.
        out_of_domain_detection (OutOfDomainDetection): An instance of the OutOfDomainDetection class.
        retriever (Retriever): An instance of the Retriever class.
        retriever_agreg (RetrieverAgreg): An instance of the RetrieverAgreg class.
        reader (Reader): An instance of the Reader class.

    Attributes:
        _data (pd.DataFrame): The input data provided during initialization.
        _out_of_domain_detection (OutOfDomainDetection): The OutOfDomainDetection instance.
        _retriever (Retriever): The Retriever instance.
        _retriever_agreg (RetrieverAgreg): The RetrieverAgreg instance.
        _reader (Reader): The Reader instance.
        _results (dict): A dictionary to store the results or error information.

    Methods:
        run(): Execute the data processing tasks in sequence and store results in _results.
        handle_error(error, task_name, error_code): Handle errors and store error information in _results.

    Returns:
        dict: A dictionary containing the results and error information.

    Note:
        This pipeline processes data by running a sequence of tasks, such as out_of_domain_detection,
        retriever, retriever_agreg, and reader and then returns the answer for the question.
        If an error occurs during any task execution, it is
        handled and recorded in the _results dictionary.

    Example:
        data = pd.DataFrame(...)  # Create a Pandas DataFrame with your data
        out_of_domain = OutOfDomainDetection(...)
        retriever = Retriever(...)
        aggreg = RetrieverAgreg(...)
        reader = Reader(...)
        pipeline = Pipeline(data, out_of_domain, retriever, aggreg, reader)
        results = pipeline.run()
    """

    def __init__(self,
                 data: dict,
                 out_of_domain_detection: OutOfDomainDetection,
                 retriever: Retriever,
                 retriever_agreg: RetrieverAgreg,
                 reader: Reader):
        self._data: dict = data
        self._out_of_domain_detection: OutOfDomainDetection = out_of_domain_detection
        self._retriever: Retriever = retriever
        self._retriever_agreg: RetrieverAgreg = retriever_agreg
        self._reader: Reader = reader
        self._results: dict = dict()

    def run(self) -> dict:
        tasks: list = [
            ("out_of_domain_detection", self._out_of_domain_detection, 24),
            ("retriever", self._retriever, 25),
            ("retriever_agreg", self._retriever_agreg, 26),
            ("reader", self._reader, 27)
        ]

        for task_name, task_func, error_code in tasks:
            try:
                self._data = task_func.run(self._data)
                self._results["results"] = self._data
            except Exception as e:
                self.handle_error(e, task_name, error_code)
                return self._results
        return self._results

    def handle_error(self, error: Exception, task_name: str, error_code: int):
        self._results["error"] = error
        self._results["error_occurred_at"] = task_name
        self._results["error_code"] = error_code

