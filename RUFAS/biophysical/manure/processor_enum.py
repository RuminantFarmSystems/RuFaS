from enum import Enum
from typing import Type
import importlib

from RUFAS.biophysical.manure.processor import Processor


class ProcessorType(Enum):
    SEPARATOR = "separator"
    ANAEROBIC_DIGESTER = "anaerobic_digester"

    @classmethod
    def get_processor_class(cls, processor_type: str) -> Type["Processor"]:
        """
        Dynamically imports the correct Processor subclass based on type.

        Parameters
        ----------
        processor_type : str
            The type of processor as a string.

        Returns
        -------
        Type[Processor]
            The class corresponding to the processor type.

        Raises
        ------
        ValueError
            If the processor type is not recognized.
        """
        processor_mapping = {
            cls.SEPARATOR.value: "RUFAS.biophysical.manure.separator.Separator",
            cls.ANAEROBIC_DIGESTER.value: "RUFAS.biophysical.manure.anaerobic_digester.AnaerobicDigester",
        }

        if processor_type not in processor_mapping:
            raise ValueError(f"Unknown processor type: {processor_type}")

        module_name, class_name = processor_mapping[processor_type].rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
