from enum import Enum


class Breed(Enum):
    """Enum indicating the breed of the animal."""

    HO = "Holstein"
    JE = "Jersey"


class Sex(Enum):
    """Enum indicating the sex of the animal."""

    MALE = "male"
    FEMALE = "female"


class AnimalStatus(Enum):
    REMAIN = "remain"
    LIFE_STAGE_CHANGED = "life stage changed"
    NEW_CALF_BORN = "new calf born"
    DEAD = "dead"
    SOLD = "sold"
    CULLED = "culled"


class RationGroupings(Enum):
    """Enum indicating which set of feeds can be used to feed an animal."""

    CALF = "calf"
    GROWING = "growing"
    CLOSE_UP = "close up"
    LACTATING = "lactating"
