from enum import Enum


class ManureCoverEnum(Enum):
    """
    Indicates the presence or absence of a cover in the manure treatment or storage system.
    When used in the case of a Slurry Storage system (underfloor or outdoors) the cover
    refers to the presence of a natural crust.

    Attributes:
    ----------
    COVER: str
        The enum member that indicates the presence of a cover in the manure treatment or storage system.
    NO_COVER: str
        The enum member that indicates the absence of a cover in the manure treatment or storage system.
    """

    COVER = 'cover'
    NO_COVER = 'no cover'
    NOT_APPLICABLE = 'N/A'
