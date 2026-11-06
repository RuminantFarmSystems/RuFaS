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
    FEEDLOT_STEER : str
        A castrated male beef animal on a feedlot finishing programme.
    FEEDLOT_HEIFER : str
        A female beef animal on a feedlot finishing programme that has not calved.
    BEEF_CALF : str
        A pre-weaned calf born in the cow-calf breeding herd.
    BEEF_HEIFER_REPLACEMENT : str
        A beef heifer retained for herd replacement, from weaning until first calving.
    BEEF_COW : str
        A mature beef cow in the breeding herd (gestating, lactating, or both).
    BEEF_BULL : str
        A bull in the natural-service breeding herd.
    BEEF_STOCKER_STEER : str
        A castrated male beef animal in the stocker/backgrounding phase.
    BEEF_STOCKER_HEIFER : str
        A female beef animal in the stocker/backgrounding phase.

    """

    CALF = "Calf"
    HEIFER_I = "HeiferI"
    HEIFER_II = "HeiferII"
    HEIFER_III = "HeiferIII"
    DRY_COW = "DryCow"
    LAC_COW = "LacCow"
    FEEDLOT_STEER = "FeedlotSteer"
    FEEDLOT_HEIFER = "FeedlotHeifer"
    BEEF_CALF = "BeefCalf"
    BEEF_HEIFER_REPLACEMENT = "BeefHeiferReplacement"
    BEEF_COW = "BeefCow"
    BEEF_BULL = "BeefBull"
    BEEF_STOCKER_STEER = "BeefStockerSteer"
    BEEF_STOCKER_HEIFER = "BeefStockerHeifer"

    @property
    def is_heifer(self) -> bool:
        """True if the animal is a dairy heifer, False otherwise."""
        return self in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III)

    @property
    def is_cow(self) -> bool:
        """True if the animal is a dairy cow, False otherwise."""
        return self in (AnimalType.DRY_COW, AnimalType.LAC_COW)

    @property
    def is_feedlot(self) -> bool:
        """True if the animal is a feedlot beef animal, False otherwise."""
        return self in (AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER)

    @property
    def is_beef_cow_calf(self) -> bool:
        """True if the animal belongs to the cow-calf breeding herd system, False otherwise."""
        return self in (
            AnimalType.BEEF_CALF,
            AnimalType.BEEF_HEIFER_REPLACEMENT,
            AnimalType.BEEF_COW,
            AnimalType.BEEF_BULL,
        )

    @property
    def is_beef_stocker(self) -> bool:
        """True if the animal is in the stocker/backgrounding phase."""
        return self in (AnimalType.BEEF_STOCKER_STEER, AnimalType.BEEF_STOCKER_HEIFER)
