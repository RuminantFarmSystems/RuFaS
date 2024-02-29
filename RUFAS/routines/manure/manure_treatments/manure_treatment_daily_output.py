from __future__ import annotations

from dataclasses import astuple
from dataclasses import dataclass

from RUFAS.routines.manure.constants_and_units.datatype_with_unit import FloatWithUnit, IntWithUnit
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)


@dataclass
class ManureTreatmentDailyOutput(LiquidManurePortionProtocol):
    """
    Daily output of a manure treatment.

    Attribute
    ---------
    pen_id: int
        ID of the pen that this output is associated with.
    simulation_day: int
        Number of days into the simulation.
    liquid_manure_total_ammoniacal_nitrogen: float
        Total ammoniacal nitrogen, kg.
    liquid_manure_nitrogen: float
        Amount of nitrogen in manure, kg.
    liquid_manure_total_solids: float
        Total amount of solids from the manure and the bedding, kg.
    liquid_manure_total_volatile_solids: float
        Total amount of volatile solids, kg.
    liquid_manure_phosphorus: float
        Amount of phosphorus excreted in manure, kg.
    liquid_manure_potassium: float
        Amount of potassium in manure, kg.
    daily_final_manure_volume: float
        Final manure volume after treatment, m^3.
    liquid_manure_daily_volume: float
        Daily volume of manure, m^3.
    storage_methane: float
        Amount of methane produced by the manure treatment process, kg.
    storage_ammonia: float
        Amount of ammonia produced by the manure treatment process, kg.
    storage_nitrous_oxide: float
        Amount of nitrous oxide produced by the manure treatment process, kg.
    storage_nitrogen_leached: float
        Amount of nitrogen lost through leaching during the manure treatment process, kg.
    sludge_manure_total_solids: float
        Total amount of solids in the sludge manure, kg.
    sludge_manure_total_volatile_solids: float
        Total amount of volatile solids in the sludge manure, kg.
    sludge_manure_nitrogen: float
        Amount of nitrogen in the sludge manure, kg.
    sludge_manure_phosphorus: float
        Amount of phosphorus in the sludge manure, kg.
    sludge_manure_potassium: float
        Amount of potassium in the sludge manure, kg.
    sludge_manure_daily_volume: float
        Daily volume of sludge manure, m^3.
    solid_manure_total_solids: float
        Total amount of solids in the solid manure, kg.
    solid_manure_total_volatile_solids: float
        Total amount of volatile solids in the solid manure, kg.
    solid_manure_nitrogen: float
        Amount of nitrogen in the solid manure, kg.
    solid_manure_inorganic_nitrogen: float
        Amount of inorganic nitrogen in the solid manure, kg.
    solid_manure_organic_nitrogen: float
        Amount of organic nitrogen in the solid manure, kg.
    solid_manure_total_ammoniacal_nitrogen_ammonium: float
        Amount of ammonium in the inorganic nitrogen in the solid manure, kg.
    solid_manure_phosphorus: float
        Amount of phosphorus in the solid manure, kg.
    solid_manure_water_extractable_inorganic_phosphorus: float
        Amount of water-extractable inorganic phosphorus in the solid manure, kg.
    solid_manure_water_extractable_organic_phosphorus: float
        Amount of water-extractable organic phosphorus in the solid manure, kg.
    solid_manure_non_water_extractable_inorganic_phosphorus: float
        Amount of non-water-extractable inorganic phosphorus in the solid manure, kg.
    solid_manure_non_water_extractable_organic_phosphorus: float
        Amount of non-water-extractable organic phosphorus in the solid manure, kg.
    solid_manure_potassium: float
        Amount of potassium in the solid manure, kg.
    solid_manure_daily_mass: float
        Daily mass of solid manure, kg.
    biogas: float
        Amount of biogas produced, m^3.
    biogas_energy_content: float
        Energy content of biogas, MJ/m^3.
    methane_generation_volume: float
        Amount of methane generated, m^3.
    heating_input_energy: float
        Amount of energy input to the heating system, MJ.
    evaporated_water: float
        Amount of water evaporated, m^3.
    minimum_digester_volume: float
        Minimum digester volume, m^3.
    top_cover_volume: float
        Volume of the top cover, m^3.
    solid_manure_carbon_decomposition: float
        Carbon decomposition, kg.
    """

    pen_id: IntWithUnit = IntWithUnit(-1, unit="unitless")
    simulation_day: IntWithUnit = IntWithUnit(-1, unit="simulation days")
    liquid_manure_total_ammoniacal_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    liquid_manure_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    liquid_manure_total_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    liquid_manure_total_volatile_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    liquid_manure_phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    liquid_manure_potassium: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    daily_final_manure_volume: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")
    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")

    storage_methane: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    storage_ammonia: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    storage_nitrous_oxide: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    storage_nitrogen_leached: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    sludge_manure_total_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    sludge_manure_total_volatile_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    sludge_manure_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    sludge_manure_phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    sludge_manure_potassium: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    sludge_manure_daily_volume: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")

    solid_manure_total_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_total_volatile_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    solid_manure_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_inorganic_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_organic_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_total_ammoniacal_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    solid_manure_phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_water_extractable_inorganic_phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_water_extractable_organic_phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_non_water_extractable_inorganic_phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_non_water_extractable_organic_phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    solid_manure_potassium: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_daily_mass: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    # different unit from docstring m^3 vs m^3/day?
    biogas: FloatWithUnit = FloatWithUnit(0.0, unit="m^3/day")  # biogas production per day (m3/day)
    biogas_energy_content: FloatWithUnit = FloatWithUnit(0.0, unit="MJ/m^3")  # biogas energy content (MJ/m3)
    methane_generation_volume: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")
    heating_input_energy: FloatWithUnit = FloatWithUnit(0.0, unit="MJ")
    evaporated_water: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")
    minimum_digester_volume: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")
    top_cover_volume: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")

    solid_manure_carbon_decomposition: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

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

        return ManureTreatmentDailyOutput(*[attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))])

    def clone(self) -> ManureTreatmentDailyOutput:
        """Returns a clone of this object.

        Returns:
            ManureTreatmentDailyOutput object with the same attributes as this object.

        """
        return ManureTreatmentDailyOutput(*astuple(self))
