from typing import Optional

from RUFAS.data_structures.pen_manure_data import PenManureData


class ManureStream:
    """
    This class packages manure data.

    Parameters
    ----------
    water : float
        Mass of water in the manure stream (kg).
    ammoniacal_nitrogen : float
        Mass of ammoniacal nitrogen in the manure stream (kg).
    nitrogen : float
        Mass of total nitrogen in the manure stream (kg).
    phosphorus: float
        Mass of phosphorus in the manure stream (kg).
    potassium : float
        Mass of potassium in the manure stream (kg).
    ash : float
        Mass of ash in the manure stream (kg).
    non_degradable_volatile_solids : float
        Mass of non-degradable volatile solids in the manure stream (kg).
    degradable_volatile_solids : float
        Mass of degradable volatile solids in the manure stream (kg).
    total_solids : float
        Mass of total solids in the manure stream (kg).
    volume : float
        Volume of the manure stream (m^3).
    pen_manure_data : PenManureData | None
       Optional, more specific information about the manure and the pen or pens that produced it.

    Attributes
    ----------
    water : float
        Mass of water in the manure stream (kg).
    ammoniacal_nitrogen : float
        Mass of ammoniacal nitrogen in the manure stream (kg).
    nitrogen : float
        Mass of total nitrogen in the manure stream (kg).
    phosphorus: float
        Mass of phosphorus in the manure stream (kg).
    potassium : float
        Mass of potassium in the manure stream (kg).
    ash : float
        Mass of ash in the manure stream (kg).
    non_degradable_volatile_solids : float
        Mass of non-degradable volatile solids in the manure stream (kg).
    degradable_volatile_solids : float
        Mass of degradable volatile solids in the manure stream (kg).
    total_solids : float
        Mass of total solids in the manure stream (kg).
    volume : float
        Volume of the manure stream (m^3).
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
        volume: float,
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
        self.volume = volume
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

    def clear_pen_manure_data(self) -> None:
        """Clears the pen manure data instance."""
        self.pen_manure_data = None
