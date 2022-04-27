from abc import ABC, abstractmethod

from RUFAS.routines.manure_management.abstract_classes.abstract_manure_process_variables import ManureProcessorVariables


class ManureProcessor(ABC):
    @abstractmethod
    @property
    def daily_vars(self) -> ManureProcessorVariables:
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def reset_daily_variables(self):
        pass
