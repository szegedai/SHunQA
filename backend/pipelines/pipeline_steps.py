from abc import ABC, abstractmethod


class PipelineSteps(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def run(self, data: dict) -> dict:
        pass

    @abstractmethod
    def data_check(self, data: dict) -> dict:
        pass

