from typing import TypedDict


class MilkProductionRecord(TypedDict):
    """
    Records milk production of a single animal for a single day.

    Attributes
    ----------
    simulation_day : int
        Simulation day that milk production was recorded on.
    days_in_milk : int
        Number of days of the animal into milking.
    milk_production : float
        Amount of milk produced by the animal (kg).
    days_born : int
        Age of the animal (days).

    """

    simulation_day: int
    days_in_milk: int
    milk_production: float
    days_born: int
