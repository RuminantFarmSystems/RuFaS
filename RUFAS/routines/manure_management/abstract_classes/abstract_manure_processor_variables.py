from abc import ABC, abstractmethod
from typing import Dict, Union


class ManureProcessorVariables(ABC):
    @abstractmethod
    def as_dict(self) -> Dict[str: Union[int, float]]:
        pass
