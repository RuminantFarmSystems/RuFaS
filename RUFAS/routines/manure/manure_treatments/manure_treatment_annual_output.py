from __future__ import annotations

from dataclasses import astuple
from dataclasses import dataclass

from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)


@dataclass
class ManureTreatmentAnnualOutput(LiquidManurePortionProtocol):
    """Annual output of a manure treatment.

    Attributes:
        pen_id: ID of the pen that this output is associated with.
        simulation_calendar_year: The calendar year of simulation.
        solid_manure_nitrogen: Amount of nitrogen in the solid manure, kg.
        solid_manure_inorganic_nitrogen: Amount of inorganic nitrogen in the solid manure, kg.
        solid_manure_organic_nitrogen: Amount of organic nitrogen in the solid manure, kg.
        solid_manure_inorganic_nitrogen_ammonium: Amount of ammonium in the inorganic nitrogen in the solid manure, kg.
    """

    pen_id: int = -1
    simulation_calendar_year: int = -1

    solid_manure_nitrogen: float = 0.0
    solid_manure_inorganic_nitrogen: float = 0.0
    solid_manure_organic_nitrogen: float = 0.0
    solid_manure_inorganic_nitrogen_ammonium: float = 0.0

    def __add__(self, other: ManureTreatmentAnnualOutput) -> ManureTreatmentAnnualOutput:
        """Adds corresponding attributes between this output and another.

        Args:
            other: ManureTreatmentAnnualOutput object to add.

        Returns:
            ManureTreatmentAnnualOutput with corresponding attributes summed.

        """
        if not isinstance(other, ManureTreatmentAnnualOutput):
            raise TypeError("Other must be of type ManureTreatmentAnnualOutput.")

        return ManureTreatmentAnnualOutput(
            *[attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))]
        )

    def clone(self) -> ManureTreatmentAnnualOutput:
        """Returns a clone of this object.

        Returns:
            ManureTreatmentAnnualOutput object with the same attributes as this object.

        """
        return ManureTreatmentAnnualOutput(*astuple(self))
