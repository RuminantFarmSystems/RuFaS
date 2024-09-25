from dataclasses import dataclass


@dataclass
class AnimalGrowthProperties:
    """
    Collection of animal properties that are related to reproduction.

    Attributes
    ----------
    daily_growth: float
    conceptus_weight: float
    DBW: float
    tissue_changed: float
    """

    daily_growth: float
    conceptus_weight: float
    DBW: float
    tissue_changed: float
