from __future__ import annotations

from dataclasses import astuple, fields
from dataclasses import dataclass

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
    pen_id_unit: str
        Unit for pen_id.
    simulation_day: int
        Number of days into the simulation.
    simulation_day_unit: str
        Unit for simulation_day.
    liquid_manure_total_ammoniacal_nitrogen: float
        Total ammoniacal nitrogen, kg.
    liquid_manure_total_ammoniacal_nitrogen_unit: str
        Unit for liquid_manure_total_ammoniacal_nitrogen.
    liquid_manure_nitrogen: float
        Amount of nitrogen in manure, kg.
    liquid_manure_nitrogen_unit: str
        Unit for liquid_manure_nitrogen.
    liquid_manure_total_solids: float
        Total amount of solids from the manure and the bedding, kg.
    liquid_manure_total_solids_unit: str
        Unit for liquid_manure_total_solids.
    liquid_manure_total_volatile_solids: float
        Total amount of volatile solids, kg.
    liquid_manure_total_volatile_solids_unit: str
        Unit for liquid_manure_total_volatile_solids.
    liquid_manure_phosphorus: float
        Amount of phosphorus excreted in manure, kg.
    liquid_manure_phosphorus_unit: str
        Unit for liquid_manure_phosphorus.
    liquid_manure_potassium: float
        Amount of potassium in manure, kg.
    liquid_manure_potassium_unit: str
        Unit for liquid_manure_potassium.
    daily_final_manure_volume: float
        Final manure volume after treatment, m^3.
    daily_final_manure_volume_unit: str
        Unit for daily_final_manure_volume.
    liquid_manure_daily_volume: float
        Daily volume of manure, m^3.
    liquid_manure_daily_volume_unit: str
        Unit for liquid_manure_daily_volume.
    storage_methane: float
        Amount of methane produced by the manure treatment process, kg.
    storage_methane_unit: str
        Unit for storage_methane.
    storage_ammonia: float
        Amount of ammonia produced by the manure treatment process, kg.
    storage_ammonia_unit: str
        Unit for storage_ammonia.
    storage_nitrous_oxide: float
        Amount of nitrous oxide produced by the manure treatment process, kg.
    storage_nitrous_oxide_unit: str
        Unit for storage_nitrous_oxide.
    storage_nitrogen_leached: float
        Amount of nitrogen lost through leaching during the manure treatment process, kg.
    storage_nitrogen_leached_unit: str
        Unit for storage_nitrogen_leached.
    sludge_manure_total_solids: float
        Total amount of solids in the sludge manure, kg.
    sludge_manure_total_solids_unit: str
        Unit for sludge_manure_total_solids.
    sludge_manure_total_volatile_solids: float
        Total amount of volatile solids in the sludge manure, kg.
    sludge_manure_total_volatile_solids_unit: str
        Unit for sludge_manure_total_volatile_solids.
    sludge_manure_nitrogen: float
        Amount of nitrogen in the sludge manure, kg.
    sludge_manure_nitrogen_unit: str
        Unit for sludge_manure_nitrogen.
    sludge_manure_phosphorus: float
        Amount of phosphorus in the sludge manure, kg.
    sludge_manure_phosphorus_unit: str
        Unit for sludge_manure_phosphorus.
    sludge_manure_potassium: float
        Amount of potassium in the sludge manure, kg.
    sludge_manure_potassium_unit: str
        Unit for sludge_manure_potassium.
    sludge_manure_daily_volume: float
        Daily volume of sludge manure, m^3.
    sludge_manure_daily_volume_unit: str
        Unit for sludge_manure_daily_volume.
    solid_manure_total_solids: float
        Total amount of solids in the solid manure, kg.
    solid_manure_total_solids_unit: str
        Unit for solid_manure_total_solids.
    solid_manure_total_volatile_solids: float
        Total amount of volatile solids in the solid manure, kg.
    solid_manure_total_volatile_solids_unit: str
        Unit for solid_manure_total_volatile_solids.
    solid_manure_nitrogen: float
        Amount of nitrogen in the solid manure, kg.
    solid_manure_nitrogen_unit: str
        Unit for solid_manure_nitrogen.
    solid_manure_inorganic_nitrogen: float
        Amount of inorganic nitrogen in the solid manure, kg.
    solid_manure_inorganic_nitrogen_unit: str
        Unit for solid_manure_inorganic_nitrogen.
    solid_manure_organic_nitrogen: float
        Amount of organic nitrogen in the solid manure, kg.
    solid_manure_organic_nitrogen_unit: str
        Unit for solid_manure_organic_nitrogen.
    solid_manure_total_ammoniacal_nitrogen_ammonium: float
        Amount of ammonium in the inorganic nitrogen in the solid manure, kg.
    solid_manure_total_ammoniacal_nitrogen_ammonium_unit: str
        Unit for solid_manure_total_ammoniacal_nitrogen_ammonium.
    solid_manure_phosphorus: float
        Amount of phosphorus in the solid manure, kg.
    solid_manure_phosphorus_unit: str
        Unit for solid_manure_phosphorus.
    solid_manure_water_extractable_inorganic_phosphorus: float
        Amount of water-extractable inorganic phosphorus in the solid manure, kg.
    solid_manure_water_extractable_inorganic_phosphorus_unit: str
        Unit for solid_manure_water_extractable_inorganic_phosphorus.
    solid_manure_water_extractable_organic_phosphorus: float
        Amount of water-extractable organic phosphorus in the solid manure, kg.
    solid_manure_water_extractable_organic_phosphorus_unit: str
        Unit for solid_manure_water_extractable_organic_phosphorus.
    solid_manure_non_water_extractable_inorganic_phosphorus: float
        Amount of non-water-extractable inorganic phosphorus in the solid manure, kg.
    solid_manure_non_water_extractable_inorganic_phosphorus_unit: str
        Unit for solid_manure_non_water_extractable_inorganic_phosphorus.
    solid_manure_non_water_extractable_organic_phosphorus: float
        Amount of non-water-extractable organic phosphorus in the solid manure, kg.
    solid_manure_non_water_extractable_organic_phosphorus_unit: str
        Unit for solid_manure_non_water_extractable_organic_phosphorus.
    solid_manure_potassium: float
        Amount of potassium in the solid manure, kg.
    solid_manure_potassium_unit: str
        Unit for solid_manure_potassium.
    solid_manure_daily_mass: float
        Daily mass of solid manure, kg.
    solid_manure_daily_mass_unit: str
        Unit for solid_manure_daily_mass.
    biogas: float
        Amount of biogas produced, m^3.
    biogas_unit: str
        Unit for biogas.
    biogas_energy_content: float
        Energy content of biogas, MJ/m^3.
    biogas_energy_content_unit: str
        Unit for biogas_energy_content.
    methane_generation_volume: float
        Amount of methane generated, m^3.
    methane_generation_volume_unit: str
        Unit for methane_generation_volume.
    heating_input_energy: float
        Amount of energy input to the heating system, MJ.
    heating_input_energy_unit: str
        Unit for heating_input_energy.
    evaporated_water: float
        Amount of water evaporated, m^3.
    evaporated_water_unit: str
        Unit for evaporated_water.
    minimum_digester_volume: float
        Minimum digester volume, m^3.
    minimum_digester_volume_unit: str
        Unit for minimum_digester_volume.
    top_cover_volume: float
        Volume of the top cover, m^3.
    top_cover_volume_unit: str
        Unit for top_cover_volume.
    solid_manure_carbon_decomposition: float
        Carbon decomposition, kg.
    solid_manure_carbon_decomposition_unit: str
        Unit for solid_manure_carbon_decomposition.
    """

    pen_id: int = -1
    pen_id_unit: str = "unitless"

    simulation_day: int = -1
    simulation_day_unit: str = "simulation days"

    liquid_manure_total_ammoniacal_nitrogen: float = 0.0
    liquid_manure_total_ammoniacal_nitrogen_unit: str = "kg"

    liquid_manure_nitrogen: float = 0.0
    liquid_manure_nitrogen_unit: str = "kg"

    liquid_manure_total_solids: float = 0.0
    liquid_manure_total_solids_unit: str = "kg"

    liquid_manure_total_volatile_solids: float = 0.0
    liquid_manure_total_volatile_solids_unit: str = "kg"

    liquid_manure_phosphorus: float = 0.0
    liquid_manure_phosphorus_unit: str = "kg"

    liquid_manure_potassium: float = 0.0
    liquid_manure_potassium_unit: str = "kg"

    daily_final_manure_volume: float = 0.0
    daily_final_manure_volume_unit: str = "m^3"

    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: float = 0.0
    liquid_manure_daily_volume_unit: str = "m^3"

    storage_methane: float = 0.0
    storage_methane_unit: str = "kg"

    storage_ammonia: float = 0.0
    storage_ammonia_unit: str = "kg"

    storage_nitrous_oxide: float = 0.0
    storage_nitrous_oxide_unit: str = "kg"

    storage_nitrogen_leached: float = 0.0
    storage_nitrogen_leached_unit: str = "kg"

    sludge_manure_total_solids: float = 0.0
    sludge_manure_total_solids_unit: str = "kg"

    sludge_manure_total_volatile_solids: float = 0.0
    sludge_manure_total_volatile_solids_unit: str = "kg"

    sludge_manure_nitrogen: float = 0.0
    sludge_manure_nitrogen_unit: str = "kg"

    sludge_manure_phosphorus: float = 0.0
    sludge_manure_phosphorus_unit: str = "kg"

    sludge_manure_potassium: float = 0.0
    sludge_manure_potassium_unit: str = "kg"

    sludge_manure_daily_volume: float = 0.0
    sludge_manure_daily_volume_unit: str = "m^3"

    solid_manure_total_solids: float = 0.0
    solid_manure_total_solids_unit: str = "kg"

    solid_manure_total_volatile_solids: float = 0.0
    solid_manure_total_volatile_solids_unit: str = "kg"

    solid_manure_nitrogen: float = 0.0
    solid_manure_nitrogen_unit: str = "kg"

    solid_manure_inorganic_nitrogen: float = 0.0
    solid_manure_inorganic_nitrogen_unit: str = "kg"

    solid_manure_organic_nitrogen: float = 0.0
    solid_manure_organic_nitrogen_unit: str = "kg"

    solid_manure_total_ammoniacal_nitrogen: float = 0.0
    solid_manure_total_ammoniacal_nitrogen_unit: str = "kg"

    solid_manure_phosphorus: float = 0.0
    solid_manure_phosphorus_unit: str = "kg"

    solid_manure_water_extractable_inorganic_phosphorus: float = 0.0
    solid_manure_water_extractable_inorganic_phosphorus_unit: str = "kg"

    solid_manure_water_extractable_organic_phosphorus: float = 0.0
    solid_manure_water_extractable_organic_phosphorus_unit: str = "kg"

    solid_manure_non_water_extractable_inorganic_phosphorus: float = 0.0
    solid_manure_non_water_extractable_inorganic_phosphorus_unit: str = "kg"

    solid_manure_non_water_extractable_organic_phosphorus: float = 0.0
    solid_manure_non_water_extractable_organic_phosphorus_unit: str = "kg"

    solid_manure_potassium: float = 0.0
    solid_manure_potassium_unit: str = "kg"

    solid_manure_daily_mass: float = 0.0
    solid_manure_daily_mass_unit: str = "kg"

    # different unit from docstring m^3 vs m^3/day?
    biogas: float = 0.0  # biogas production per day (m3/day)
    biogas_unit: str = "m^3/day"

    biogas_energy_content: float = 0.0  # biogas energy content (MJ/m3)
    biogas_energy_content_unit: str = "MJ/m^3"

    methane_generation_volume: float = 0.0
    methane_generation_volume_unit: str = "m^3"

    heating_input_energy: float = 0.0
    heating_input_energy_unit: str = "MJ"

    evaporated_water: float = 0.0
    evaporated_water_unit: str = "m^3"

    minimum_digester_volume: float = 0.0
    minimum_digester_volume_unit: str = "m^3"

    top_cover_volume: float = 0.0
    top_cover_volume_unit: str = "m^3"

    solid_manure_carbon_decomposition: float = 0.0
    solid_manure_carbon_decomposition_unit: str = "kg"

    def __post_init__(self) -> None:
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

        summed_attributes = {
            field.name: getattr(self, field.name) + getattr(other, field.name)
            for field in fields(self)
            if not field.name.endswith("_unit")
        }

        units_vars_list = list(key for (key, value) in self.__dict__.items() if key.endswith("_unit"))

        units_attributes = {unit_key: getattr(self, unit_key) for unit_key in units_vars_list}
        summed_attributes.update(units_attributes)

        return ManureTreatmentDailyOutput(**summed_attributes)

    def clone(self) -> ManureTreatmentDailyOutput:
        """Returns a clone of this object.

        Returns:
            ManureTreatmentDailyOutput object with the same attributes as this object.

        """
        return ManureTreatmentDailyOutput(*astuple(self))
