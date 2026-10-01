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
    """Enum indicating the status of the animal after performing daily routines update."""

    REMAIN = "remain"
    LIFE_STAGE_CHANGED = "life stage changed"
    DEAD = "dead"
    SOLD = "sold"
    STILLBORN = "stillborn"


class CowParity(Enum):
    """Enum indicating the parity group of the animal, used to look up parity-group-specific removal risks."""

    NONE = "none"
    ONE = "1"
    TWO = "2"
    THREE_PLUS = "3+"
