from abc import ABC, abstractmethod


class PipelineSteps(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def run(self):
        pass
