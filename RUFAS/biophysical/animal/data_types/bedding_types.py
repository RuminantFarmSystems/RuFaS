from enum import Enum


class BeddingType(Enum):
    """
    Enumerate the different types of bedding.

    This class provides a set of predefined constants that represent different types of bedding such as sawdust,
    straw, and sand. The default type is sand.

    Attribute
    ----------
    SAWDUST : str
        Represent the 'sawdust' type of bedding.
    CBPB_SAWDUST : str
        Represent the 'CBPB sawdust' type of bedding.
    MANURE_SOLIDS : str
        Represent the 'manure solids' type of bedding.
    STRAW : str
        Represent the 'straw' type of bedding.
    SAND : str
        Represent the 'sand' type of bedding.
    NONE : str
        Represent no bedding.

    """

    SAWDUST = "sawdust"
    CBPB_SAWDUST = "CBPB sawdust"
    MANURE_SOLIDS = "manure solids"
    STRAW = "straw"
    SAND = "sand"
    NONE = "none"
