from enum import Enum


class TillageImplement(Enum):
    """
    Defines the supported tillage implements for RuFaS.

    Attributes
    ----------
    SUBSOILER : str
        Subsoiler.
    MOLDBOARD_PLOW : str
        Moldboard plow.
    COULTER_CHISEL_PLOW : str
        Coulter-chisel plow.
    DISK_HARROW : str
        Disk harrow.
    CULTIVATOR : str
        Cultivator.
    SEEDBED_CONDITIONER : str
        Seedbed conditioner.
    """

    SUBSOILER = "subsoiler"
    MOLDBOARD_PLOW = "moldboard-plow"
    COULTER_CHISEL_PLOW = "coulter-chisel-plow"
    DISK_HARROW = "disk-harrow"
    CULTIVATOR = "cultivator"
    SEEDBED_CONDITIONER = "seedbed-conditioner"

    def __str__(self):
        return self.value
