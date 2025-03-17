from enum import Enum
from typing import Type
import importlib

from RUFAS.biophysical.manure.digester.anaerobic_digester import AnaerobicDigester
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.separator.separator import Separator


class ProcessorType(Enum):
    SEPARATOR = Separator
    ANAEROBIC_DIGESTER = AnaerobicDigester

    @classmethod
    def get_processor_class(cls, processor_type: str) -> Type["Processor"]:
        """
        Get the corresponding processor class directly from the Enum.

        Parameters
        ----------
        processor_type : str
            The type of processor as a string (from JSON).

        Returns
        -------
        Type[Processor]
            The class corresponding to the processor type.

        Raises
        ------
        ValueError
            If the processor type is not recognized.
        """
        try:
            return cls[processor_type.upper()].value
        except KeyError:
            raise ValueError(f"Unknown processor type: {processor_type}")
