from enum import Enum

from RUFAS.biophysical.manure.storage.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.biophysical.manure.storage.compost_bedded_pack_barn import CompostBeddedPackBarn
from RUFAS.biophysical.manure.storage.composting import Composting
from RUFAS.biophysical.manure.storage.open_lot import OpenLot
from RUFAS.biophysical.manure.storage.slurry_storage_outdoor import SlurryStorageOutdoor
from RUFAS.biophysical.manure.storage.slurry_storage_underfloor import SlurryStorageUnderfloor


class ManureType(Enum):
    """
    This is an Enum class that represents different types of manure.

    Attributes
    ----------
    LIQUID : str
        Represents liquid manure.
    SOLID : str
        Represents manure in solid form.
    """

    LIQUID = "liquid"
    SOLID = "solid"
