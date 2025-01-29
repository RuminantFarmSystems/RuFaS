from typing import Optional

from RUFAS.data_structures.pen_manure_data import PenManureData


class ManureStream:
    """
    This class packages data that will be sued for transferring manure from one processor to another.

    Parameters
    ----------
    water : float
        Amount of water (kg).
    ammoniacal_nitrogen : float
        Amount of ammoniacal nitrogen (kg).
    nitrogen : float
        Amount of nitrogen (kg).
    phosphorus: float
        Amount of phosphorus (kg).
    potassium : float
        Amount of potassium (kg).
    ash : float
        Amount of ash (kg).
    non_degradable_volatile_solids : float
        Amount of non-degradable volatile solids (kg).
    degradable_volatile_solids : float
        Amount of degradable volatile solids (kg).
    total_solids : float
        Amount of total solids (kg).
    pen_manure_data : PenManureData | None
       Optional, more specific information about the manure and the pen or pens that produced it.

    Attributes
    ----------
    water : float
        Total amount of water (kg).
    ammoniacal_nitrogen : float
        Total amount of ammoniacal nitrogen (kg).
    nitrogen : float
        Total amount of nitrogen (kg).
    phosphorus: float
        Total amount of phosphorus (kg).
    potassium : float
        Total amount of potassium (kg).
    ash : float
        Total amount of ash (kg).
    non_degradable_volatile_solids : float
        Total amount of non-degradable volatile solids (kg).
    degradable_volatile_solids : float
        Total amount of degradable volatile solids (kg).
    total_solids : float
        Total amount of total solids (kg).
    pen_manure_data : PenManureData | None
       Optional, more specific information about the manure and the pen or pens that produced it.

    """

    def __init__(
        self,
        water: float,
        ammoniacal_nitrogen: float,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        ash: float,
        non_degradable_volatile_solids: float,
        degradable_volatile_solids: float,
        total_solids: float,
        pen_manure_data: Optional[PenManureData],
    ) -> None:
        self.water = water
        self.ammoniacal_nitrogen = ammoniacal_nitrogen
        self.nitrogen = nitrogen
        self.phosphorus = phosphorus
        self.potassium = potassium
        self.ash = ash
        self.non_degradable_volatile_solids = non_degradable_volatile_solids
        self.degradable_volatile_solids = degradable_volatile_solids
        self.total_solids = total_solids
        self.pen_manure_data = pen_manure_data

    def __add__(self, other: "ManureStream") -> "ManureStream":
        pass  # TODO: implement after PenManureData class implementation - issue #2192

    @property
    def total_volatile_solids(self) -> float:
        """Amount of the total volatile solids (kg)."""
        return self.non_degradable_volatile_solids + self.degradable_volatile_solids

    @property
    def mass(self) -> float:
        """Mass of the manure stream (kg)."""
        return self.water + self.total_solids

    @property
    def volume(self) -> float:
        return 0  # TODO: the methodology for determining volume has yet to be determined -- issue #2190

    def clear_pen_manure_data(self) -> None:
        """Clears the pen manure data instance."""
        self.pen_manure_data = None
