from abc import ABC, abstractmethod

from RUFAS.routines.manure_management.abstract_classes.abstract_manure_processor import ManureProcessor


class ManureProcessorFactory(ABC):
    @classmethod
    @abstractmethod
    def get_instance(cls, *args, **kwargs) -> ManureProcessor:
        pass

