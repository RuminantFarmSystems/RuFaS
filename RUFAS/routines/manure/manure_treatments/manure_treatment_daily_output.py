from __future__ import annotations

from dataclasses import astuple
from dataclasses import dataclass


@dataclass
class ManureTreatmentDailyOutput:
    """Daily output of a manure treatment.

    Attributes:
        pen_id: ID of the pen that this output is associated with.
        simulation_day: Number of days into the simulation.
        TAN: Total ammonia nitrogen concentration, g/L.
        N: Amount of nitrogen in manure, kg.
        TS: Total amount of solids from the manure and the bedding, kg.
        VS_total: Total amount of volatile solids, kg.
        P: Amount of phosphorus excreted in manure, kg.
        K: Amount of potassium in manure, kg.
        final_manure_volume: Final manure volume after treatment, m^3.

    """
    pen_id: int = -1
    simulation_day: int = -1
    TAN: float = 0.0
    N: float = 0.0
    TS: float = 0.0
    VS_total: float = 0.0
    P: float = 0.0
    K: float = 0.0
    final_manure_volume: float = 0.0

    CH4: float = 0.0
    NH3: float = 0.0

    # Extra variable for development purposes
    # Will be removed when done
    sludge_TS: float = 0.0
    sludge_VS: float = 0.0
    sludge_N: float = 0.0
    sludge_P: float = 0.0
    sludge_K: float = 0.0
    accumulated_sludge_TS: float = 0.0
    accumulated_minimum_treatment_volume: float = 0.0

    def __add__(self, other: ManureTreatmentDailyOutput) -> ManureTreatmentDailyOutput:
        """Adds corresponding attributes between this output and another.

        Args:
            other: ManureTreatmentDailyOutput object to add.

        Returns:
            ManureTreatmentDailyOutput with corresponding attributes summed.

        """
        if not isinstance(other, ManureTreatmentDailyOutput):
            raise TypeError('Other must be of type ManureTreatmentDailyOutput.')

        return ManureTreatmentDailyOutput(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])


@dataclass
class AnaerobicDigestionOutput:
    biogas: float = 0.0  # biogas production per day (m3/day)
    biogas_energy_content: float = 0.0  # biogas energy content (MJ/m3)
    methane_generation_volume: float = 0.0
    input_energy_heating: float = 0.0
    evaporated_water: float = 0.0
    minimum_digester_volume: float = 0.0
    top_cover_volume: float = 0.0


@dataclass
class SludgeOutput:
    """Description: This class is for tracking sludge accumulated properties.
    """
    TS: float = 0.0
    VS: float = 0.0
    N: float = 0.0
    P: float = 0.0
    K: float = 0.0

    def __add__(self, other: SludgeOutput) -> SludgeOutput:
        """Adds corresponding attributes between this output and another.

        Args:
            other: SludgeOutput object to add.

        Returns:
            SludgeOutput with corresponding attributes summed.

        """
        if not isinstance(other, SludgeOutput):
            raise TypeError('Other must be of type SludgeOutput.')

        return SludgeOutput(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])
