from enum import Enum
from typing import Type

from RUFAS.biophysical.manure.digester.anaerobic_digester import AnaerobicDigester
from RUFAS.biophysical.manure.handler.parlor_cleaning import ParlorCleaningHandler
from RUFAS.biophysical.manure.handler.single_stream_handler import SingleStreamHandler
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.biophysical.manure.storage.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.biophysical.manure.storage.slurry_storage_outdoor import SlurryStorageOutdoor
from RUFAS.biophysical.manure.storage.slurry_storage_underfloor import SlurryStorageUnderfloor


class ProcessorType(Enum):
    """
    Enum for different types of manure processors.
    Each member of the enum corresponds to a specific processor class.
    """

    SEPARATOR = Separator
    ROTARY_SCREEN = Separator
    SCREW_PRESS = Separator

    ANAEROBIC_DIGESTER = AnaerobicDigester
    CONTINUOUS_MIX = AnaerobicDigester

    PARLOR_CLEANING = ParlorCleaningHandler

    SINGLE_STREAM_HANDLER = SingleStreamHandler
    ALLEY_SCRAPER = SingleStreamHandler
    MANUAL_SCRAPER = SingleStreamHandler
    FLUSH_SYSTEM = SingleStreamHandler

    ANAEROBIC_LAGOON = AnaerobicLagoon

    SLUURY_STORAGE_OUTDOOR = SlurryStorageOutdoor

    SLURRY_STORAGE_UNDERFLOOR = SlurryStorageUnderfloor

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
            return cls[processor_type.strip().upper().replace(" ", "_").replace("-", "_")].value
        except KeyError:
            raise ValueError(f"Unknown processor type: {processor_type}")
