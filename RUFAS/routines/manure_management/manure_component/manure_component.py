from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional

from RUFAS.routines.manure_management.manure_component_output.manure_component_output import ManureComponentOutput


class ManureComponent(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def daily_update(self, *args, **kwargs) -> ManureComponentOutput:
        pass

    @property
    @abstractmethod
    def all_output(self) -> List[ManureComponentOutput]:
        pass

    @property
    @abstractmethod
    def last_output(self) -> Optional[ManureComponentOutput]:
        return self.all_output[-1] if len(self.all_output) > 0 else None

    @property
    @abstractmethod
    def predecessor(self) -> Optional[ManureComponent]:
        pass
