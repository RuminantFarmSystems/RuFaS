from enum import Enum


class AnimalType(Enum):
    """The different types/subtypes of animals on a farm.

    Attributes
    ----------
    CALF : str
        A pre-weaned calf.
    HEIFER_I : str
        A heifer that is weaned but not yet bred.
    HEIFER_II : str
        A heifer that is either eligible for breeding (based on user-inputted Breeding Start Day for heifers),
        or in early pregnancy.
    HEIFER_III : str
        A close-up heifer (a heifer within the user-defined close-up period, i.e. Prefresh Day).
    DRY_COW : str
        A cow in the stage of their lactation cycle where milk production ceases prior to calving.
    LAC_COW : str
        A lactating cow.

    """

    CALF = "Calf"
    HEIFER_I = "HeiferI"
    HEIFER_II = "HeiferII"
    HEIFER_III = "HeiferIII"
    DRY_COW = "DryCow"
    LAC_COW = "LacCow"

    @property
    def is_heifer(self) -> bool:
        """True if the animal is a heifer, False otherwise"""
        return self in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III)

    @property
    def is_cow(self) -> bool:
        """True if the animal is a cow, False otherwise"""
        return self in (AnimalType.DRY_COW, AnimalType.LAC_COW)
