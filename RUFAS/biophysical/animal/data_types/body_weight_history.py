from typing import TypedDict


class BodyWeightHistory(TypedDict):
    """
    A class to represent the history of body weight for an individual animal on a farm.

    Attributes
    ----------
    simulation_day : int
        The day of the simulation corresponding to the body weight record of the animal.
    days_born : int
        The number of days since the birth of the animal.
    body_weight : float
        The body weight of the animal on the simulation day.
    """

    simulation_day: int
    days_born: int
    body_weight: float
