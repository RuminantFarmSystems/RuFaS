from enum import Enum


class IntakeOption(Enum):
    """
    Enumeration that represents the valid dry matter intake control options for a ration.

    Attributes
    ----------
    PREDICT_DMI : str
        Dry matter intake is predicted with the NASEM (2021) or NRC (2001) methodology (default behavior).
    SET_DMI : str
        Dry matter intake is equal to (fixed at) the user-provided intake value (kg DMI/animal/day).
    SET_DMI_PER_X : str
        Dry matter intake is equal to the user-provided intake value multiplied by the pen's current average milk
         production (lactating cows) or average daily gain (growing heifers) in the simulation (kg DMI/kg MY, or kg
          DMI/kg ADG).

    """

    PREDICT_DMI = "predict_DMI"
    SET_DMI = "set_DMI"
    SET_DMI_PER_X = "set_DMI_per_X"
