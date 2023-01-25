from __future__ import annotations

from dataclasses import astuple
from dataclasses import dataclass

from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol


@dataclass
class ManureTreatmentDailyOutput(LiquidManurePortionProtocol):
    """Daily output of a manure treatment.

    Attributes:
        pen_id: ID of the pen that this output is associated with.
        simulation_day: Number of days into the simulation.
        liquid_manure_total_ammoniacal_nitrogen: Total ammoniacal nitrogen, kg.
        liquid_manure_nitrogen: Amount of nitrogen in manure, kg.
        liquid_manure_total_solids: Total amount of solids from the manure and the bedding, kg.
        liquid_manure_total_volatile_solids: Total amount of volatile solids, kg.
        liquid_manure_phosphorus: Amount of phosphorus excreted in manure, kg.
        liquid_manure_potassium: Amount of potassium in manure, kg.
        daily_final_manure_volume: Final manure volume after treatment, m^3.

        # TODO: Document remaining attributes.

    """
    pen_id: int = -1
    simulation_day: int = -1
    liquid_manure_total_ammoniacal_nitrogen: float = 0.0
    liquid_manure_nitrogen: float = 0.0
    liquid_manure_total_solids: float = 0.0
    liquid_manure_total_volatile_solids: float = 0.0
    liquid_manure_phosphorus: float = 0.0
    liquid_manure_potassium: float = 0.0
    daily_final_manure_volume: float = 0.0
    liquid_manure_daily_volume: float = 0.0  # To satisfy the LiquidManurePortionProtocol

    storage_methane: float = 0.0
    storage_ammonia: float = 0.0

    sludge_manure_total_solids: float = 0.0
    sludge_manure_total_volatile_solids: float = 0.0
    sludge_manure_nitrogen: float = 0.0
    sludge_manure_phosphorus: float = 0.0
    sludge_manure_potassium: float = 0.0
    sludge_manure_daily_volume: float = 0.0

    biogas: float = 0.0  # biogas production per day (m3/day)
    biogas_energy_content: float = 0.0  # biogas energy content (MJ/m3)
    methane_generation_volume: float = 0.0
    heating_input_energy: float = 0.0
    evaporated_water: float = 0.0
    minimum_digester_volume: float = 0.0
    top_cover_volume: float = 0.0

    def __post_init__(self):
        """Ensures that the daily volume is set to the final manure volume."""
        self.liquid_manure_daily_volume = self.daily_final_manure_volume

    def set_daily_final_manure_volume(self, daily_final_manure_volume: float) -> None:
        """Sets the daily final manure volume and ensures that the daily volume is set to the final manure volume.

        Args:
            daily_final_manure_volume: Daily final manure volume, m^3.

        """
        self.daily_final_manure_volume = daily_final_manure_volume
        self.liquid_manure_daily_volume = daily_final_manure_volume

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

    def clone(self) -> ManureTreatmentDailyOutput:
        """Returns a clone of this object.

        Returns:
            ManureTreatmentDailyOutput object with the same attributes as this object.

        """
        return ManureTreatmentDailyOutput(*astuple(self))
