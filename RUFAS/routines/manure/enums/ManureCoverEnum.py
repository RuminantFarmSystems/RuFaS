from enum import Enum


class ManureCoverEnum(Enum):
    """
    Indicates the presence or absence of a cover in the manure treatment or storage system.
    When used in the case of a Slurry Storage system (underfloor or outdoors) the cover
    refers to the presence of a natural crust.

    Attributes:
    ----------
    COVER: str
        The enum member that indicates the presence of an impermeable, human-made cover
        in the manure treatment or storage system.
    CRUST: str
        The enum member that indicates the presence of a naturally-formed crust in the manure
        treatment or storage system.
    NO_COVER: str
        The enum member that indicates the absence of a cover or crust in the manure treatment or storage system.
    NOT_APPLICABLE: "N/A"
        The enum member that indicates a cover is not applicable to the manure treatment or storage system.
    """

    COVER = "cover"
    CRUST = "crust"
    NO_COVER = "no cover"
    NOT_APPLICABLE = "N/A"
