from __future__ import annotations

from dataclasses import astuple
from dataclasses import dataclass

from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)


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
        liquid_manure_daily_volume: Daily volume of manure, m^3.
        storage_methane: Amount of methane produced the manure treatment process, kg.
        storage_ammonia: Amount of ammonia produced the manure treatment process, kg.
        storage_nitrous_oxide: Amount of nitrous oxide produced the manure treatment process, kg.
        sludge_manure_total_solids: Total amount of solids in the sludge manure, kg.
        sludge_manure_total_volatile_solids: Total amount of volatile solids in the sludge manure, kg.
        sludge_manure_nitrogen: Amount of nitrogen in the sludge manure, kg.
        sludge_manure_phosphorus: Amount of phosphorus in the sludge manure, kg.
        sludge_manure_potassium: Amount of potassium in the sludge manure, kg.
        sludge_manure_daily_volume: Daily volume of sludge manure, m^3.
        solid_manure_total_solids: Total amount of solids in the solid manure, kg.
        solid_manure_total_volatile_solids: Total amount of volatile solids in the solid manure, kg.
        solid_manure_nitrogen: Amount of nitrogen in the solid manure, kg.
        solid_manure_inorganic_nitrogen: Amount of inorganic nitrogen in the solid manure, kg.
        solid_manure_organic_nitrogen: Amount of organic nitrogen in the solid manure, kg.
        solid_manure_inorganic_nitrogen_ammonium: Amount of ammonium in the inorganic nitrogen in the solid manure, kg.
        solid_manure_phosphorus: Amount of phosphorus in the solid manure, kg.
        solid_manure_water_extractable_inorganic_phosphorus: Amount of water extractable inorganic phosphorus
            in the solid manure, kg.
        solid_manure_water_extractable_organic_phosphorus: Amount of water extractable organic phosphorus
            in the solid manure, kg.
        solid_manure_non_water_extractable_inorganic_phosphorus: Amount of non-water extractable inorganic phosphorus
            in the solid manure, kg.
        solid_manure_non_water_extractable_organic_phosphorus: Amount of non-water extractable organic phosphorus
            in the solid manure, kg.
        solid_manure_potassium: Amount of potassium in the solid manure, kg.
        solid_manure_daily_mass: Daily mass of solid manure, kg.
        biogas: Amount of biogas produced, m^3.
        biogas_energy_content: Energy content of biogas, MJ/m^3.
        methane_generation_volume: Amount of methane generated, m^3.
        heating_input_energy: Amount of energy input to the heating system, MJ.
        evaporated_water: Amount of water evaporated, m^3.
        minimum_digester_volume: Minimum digester volume, m^3.
        top_cover_volume: Volume of the top cover, m^3.
        solid_manure_carbon_decomposition: Carbon decomposition, kg.
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
    liquid_manure_daily_volume: float = (
        0.0  # To satisfy the LiquidManurePortionProtocol
    )

    storage_methane: float = 0.0
    storage_ammonia: float = 0.0
    storage_nitrous_oxide: float = 0.0

    sludge_manure_total_solids: float = 0.0
    sludge_manure_total_volatile_solids: float = 0.0
    sludge_manure_nitrogen: float = 0.0
    sludge_manure_phosphorus: float = 0.0
    sludge_manure_potassium: float = 0.0
    sludge_manure_daily_volume: float = 0.0

    solid_manure_total_solids: float = 0.0
    solid_manure_total_volatile_solids: float = 0.0

    solid_manure_nitrogen: float = 0.0
    solid_manure_inorganic_nitrogen: float = 0.0
    solid_manure_organic_nitrogen: float = 0.0
    solid_manure_inorganic_nitrogen_ammonium: float = 0.0

    solid_manure_phosphorus: float = 0.0
    solid_manure_water_extractable_inorganic_phosphorus: float = 0.0
    solid_manure_water_extractable_organic_phosphorus: float = 0.0
    solid_manure_non_water_extractable_inorganic_phosphorus: float = 0.0
    solid_manure_non_water_extractable_organic_phosphorus: float = 0.0

    solid_manure_potassium: float = 0.0
    solid_manure_daily_mass: float = 0.0

    biogas: float = 0.0  # biogas production per day (m3/day)
    biogas_energy_content: float = 0.0  # biogas energy content (MJ/m3)
    methane_generation_volume: float = 0.0
    heating_input_energy: float = 0.0
    evaporated_water: float = 0.0
    minimum_digester_volume: float = 0.0
    top_cover_volume: float = 0.0

    solid_manure_carbon_decomposition: float = 0.0

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
            raise TypeError("Other must be of type ManureTreatmentDailyOutput.")

        return ManureTreatmentDailyOutput(
            *[attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))]
        )

    def clone(self) -> ManureTreatmentDailyOutput:
        """Returns a clone of this object.

        Returns:
            ManureTreatmentDailyOutput object with the same attributes as this object.

        """
        return ManureTreatmentDailyOutput(*astuple(self))
