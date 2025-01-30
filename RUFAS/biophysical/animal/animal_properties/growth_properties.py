from dataclasses import dataclass


@dataclass
class GrowthProperties:
    """
    Collection of animal properties that are related to reproduction.

    Attributes
    ----------
    daily_growth: float
        The body weight of the animal (kg).
    tissue_changed: float
        Body weight change due to tissue mobilization (kg).
    """

    daily_growth: float
    tissue_changed: float
