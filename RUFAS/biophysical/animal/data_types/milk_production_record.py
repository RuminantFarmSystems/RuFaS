from typing import TypedDict
from datetime import date


class MilkProductionRecord(TypedDict):
    """
    Records milk production of a single animal for a single day.

    Attributes
    ----------
    record_date : date
        Date of this milk production record.
    days_in_milk : int
        Number of days of the animal into milking.
    milk_production : float
        Amount of milk produced by the animal (kg).
    days_born : int
        Age of the animal in days.

    """
    record_date: date
    days_in_milk: int
    milk_production: float
    days_born: int
