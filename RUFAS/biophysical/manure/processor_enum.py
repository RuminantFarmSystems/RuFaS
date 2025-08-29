from enum import Enum
from typing import Type

from RUFAS.biophysical.manure.digester.continuous_mix import ContinuousMix
from RUFAS.biophysical.manure.handler.parlor_cleaning import ParlorCleaningHandler
from RUFAS.biophysical.manure.handler.single_stream_handler import SingleStreamHandler
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.biophysical.manure.storage.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.biophysical.manure.storage.bedded_pack import BeddedPack
from RUFAS.biophysical.manure.storage.composting import Composting
from RUFAS.biophysical.manure.storage.daily_spread import DailySpread
from RUFAS.biophysical.manure.storage.open_lot import OpenLot
from RUFAS.biophysical.manure.storage.slurry_storage_outdoor import SlurryStorageOutdoor
from RUFAS.biophysical.manure.storage.slurry_storage_underfloor import SlurryStorageUnderfloor


class ProcessorType(Enum):
    """
    Enum for different types of manure processors.
    Each member of the enum corresponds to a specific processor class.
    """

    RotaryScreen = Separator
    ScrewPress = Separator

    ContinuousMix = ContinuousMix

    ParlorCleaningHandler = ParlorCleaningHandler

    AlleyScraper = SingleStreamHandler
    ManualScraper = SingleStreamHandler
    FlushSystem = SingleStreamHandler

    AnaerobicLagoon = AnaerobicLagoon

    SlurryStorageOutdoor = SlurryStorageOutdoor

    SlurryStorageUnderfloor = SlurryStorageUnderfloor

    Composting = Composting
    BeddedPack = BeddedPack
    OpenLot = OpenLot

    DailySpread = DailySpread

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
            processor: Type["Processor"] = cls[processor_type].value
            return processor
        except KeyError:
            raise ValueError(f"Unknown processor type: {processor_type}.")
