from enum import Enum


class Breed(Enum):
    """Enum indicating the breed of the animal."""

    HO = "Holstein"
    JE = "Jersey"
    # Beef breeds (NRC 2016 Table 19-1)
    AN = "Angus"
    HE = "Hereford"
    SI = "Simmental"
    CH = "Charolais"
    LM = "Limousin"
    BR = "Brahman"
    XB = "Crossbred"
    BOD = "Beef_On_Dairy"


class Sex(Enum):
    """Enum indicating the sex of the animal."""

    MALE = "male"
    FEMALE = "female"
    STEER = "steer"


class BeefPostWeaningDestination(Enum):
    """Valid destinations for a weaned beef calf."""

    SELL = "sell"
    REPLACEMENT_HEIFER = "replacement_heifer"
    DIRECT_TO_FEEDLOT = "direct_to_feedlot"
    STOCKER = "stocker"


class StockerDietSystem(Enum):
    """Valid diet systems for the stocker/backgrounding phase (NRC 2016 Ch.10)."""

    PASTURE = "pasture"
    DRYLOT_FORAGE = "drylot_forage"
    LIMIT_FEED = "limit_feed"


class FinishingSystem(Enum):
    """Production system for beef finishing cattle.

    Selects the enteric methane pathway used when reporting finishing animals.
    GRAIN_FED is the default and preserves pre-existing feedlot behaviour.
    """

    GRAIN_FED = "grain_fed"
    GRASS_FED = "grass_fed"


class AnimalStatus(Enum):
    """Enum indicating the status of the animal after performing daily routines update."""

    REMAIN = "remain"
    LIFE_STAGE_CHANGED = "life stage changed"
    DEAD = "dead"
    SOLD = "sold"
    STILLBORN = "stillborn"


class RemovalRiskParityGroup(Enum):
    """Enum indicating the parity group of the animal, used to look up parity-group-specific removal risks."""

    NONE = "none"
    ONE = "1"
    TWO = "2"
    THREE_PLUS = "3+"
