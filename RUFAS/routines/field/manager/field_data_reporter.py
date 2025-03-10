from typing import List

from RUFAS.output_manager import OutputManager
from RUFAS.routines.field.crop.crop import Crop
from RUFAS.routines.field.field.field import Field
from RUFAS.routines.field.soil.layer_data import LayerData
from RUFAS.units import MeasurementUnits
from RUFAS.time import Time


class FieldDataReporter:
    """
    This class is responsible for reporting daily and annual variables for the whole field.

    Parameters
    ----------
    fields : List[Field]
        A list of Field instances.

    Attributes
    ----------
    fields : List[Field]
        A list of Field instances.

    """

    def __init__(self, fields: List[Field]):
        self.om = OutputManager()
        self.fields = fields

    def send_daily_variables(self, time: Time) -> None:
        """Sends daily variables of soil and crop module to the output manager"""
        for field in self.fields:
            self.send_field_daily_variables(field, time)

            self.send_soil_daily_variables(field, time)

            self.send_vadose_zone_layer_daily_variables(field, time)

            for index, layer in enumerate(field.soil.data.soil_layers):
                self.send_soil_layer_daily_variables(layer, index, field.field_data.name, time)
            for crop in field.crops:
                self.send_crop_daily_variables(crop, field.field_data.name, time)

    def send_annual_variables(self) -> None:
        """Sends annual variables of soil and crop to the output manager."""
        for field in self.fields:
            self.send_field_annual_variables(field)

            self.send_soil_annual_variables(field)

            for index, layer in enumerate(field.soil.data.soil_layers):
                self.send_soil_layer_annual_variables(layer, field.field_data.name, index)

    def send_crop_daily_variables(self, crop: Crop, field_name: str | None, time: Time) -> None:
        """Sends crop related daily variables to the output manager."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_crop_daily_variables.__name__,
            "suffix": f"field='{field_name}',crop='{crop.data.name}',"
            f"planted={crop.data.planting_day},{crop.data.planting_year}",
            "simulation_day": time.simulation_day,
        }
        self.om.add_variable(
            "root_depth", crop.data.root_depth, dict(info_map, **{"units": MeasurementUnits.MILLIMETERS})
        )
        self.om.add_variable(
            "biomass",
            crop.data.biomass,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "usable_light",
            crop.biomass_allocation.usable_light,
            dict(info_map, **{"units": MeasurementUnits.MEGAJOULES_PER_SQUARE_METER}),
        )
        self.om.add_variable(
            "biomass_growth_max",
            crop.data.biomass_growth_max,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "biomass_growth",
            crop.biomass_allocation.biomass_growth,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "growth_factor",
            crop.data.growth_factor,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "above_ground_biomass",
            crop.data.above_ground_biomass,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "root_biomass",
            crop.data.root_biomass,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "water_uptake",
            crop.data.water_uptake,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "water_stress", crop.growth_constraints.water_stress, dict(info_map, **{"units": MeasurementUnits.UNITLESS})
        )
        self.om.add_variable(
            "temp_stress", crop.growth_constraints.temp_stress, dict(info_map, **{"units": MeasurementUnits.UNITLESS})
        )
        self.om.add_variable(
            "nitrogen_stress",
            crop.growth_constraints.nitrogen_stress,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "phosphorus_stress",
            crop.growth_constraints.phosphorus_stress,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "accumulated_heat_units",
            crop.data.accumulated_heat_units,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "heat_fraction",
            crop.data.heat_fraction,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable("is_growing", crop.data.is_growing, dict(info_map, **{"units": MeasurementUnits.UNITLESS}))
        self.om.add_variable("is_dormant", crop.data.is_dormant, dict(info_map, **{"units": MeasurementUnits.UNITLESS}))
        self.om.add_variable(
            "leaf_area_index",
            crop.data.leaf_area_index,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "canopy_height", crop.leaf_area_index.canopy_height, dict(info_map, **{"units": MeasurementUnits.METERS})
        )
        self.om.add_variable(
            "leaf_area_added",
            crop.leaf_area_index.leaf_area_added,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "optimal_leaf_area_change",
            crop.leaf_area_index.optimal_leaf_area_change,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "potential_nitrogen_uptake",
            crop.nitrogen_uptake.potential_nutrient_uptake,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "total_nitrogen_uptake",
            crop.nitrogen_uptake.total_nutrient_uptake,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "actual_nitrogen_uptakes",
            crop.nitrogen_uptake.actual_nutrient_uptakes,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "optimal_nitrogen_fraction",
            crop.data.optimal_nitrogen_fraction,
            dict(info_map, **{"units": MeasurementUnits.FRACTION}),
        )
        self.om.add_variable(
            "potential_phosphorus_uptake",
            crop.phosphorus_incorporation.potential_nutrient_uptake,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "total_phosphorus_uptake",
            crop.phosphorus_incorporation.total_nutrient_uptake,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "actual_phosphorus_uptakes",
            crop.phosphorus_incorporation.actual_nutrient_uptakes,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "cumulative_evaporation",
            crop.data.cumulative_evaporation,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "cumulative_transpiration",
            crop.data.cumulative_transpiration,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "cumulative_evapotranspiration",
            crop.water_dynamics.cumulative_evapotranspiration,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "water_deficiency",
            crop.data.water_deficiency,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "max_transpiration",
            crop.data.max_transpiration,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "canopy_water",
            crop.data.canopy_water,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "cut_biomass",
            crop.crop_management.cut_biomass,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "wet_yield_collected",
            crop.crop_management.wet_yield_collected,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "dry_matter_yield_residue",
            crop.crop_management.yield_residue,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "yield_nitrogen",
            crop.crop_management.yield_nitrogen,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "yield_phosphorus",
            crop.crop_management.yield_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "residue_nitrogen",
            crop.crop_management.residue_nitrogen,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "residue_phosphorus",
            crop.crop_management.residue_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )

    def send_soil_layer_daily_variables(self, layer: LayerData, index: int, field_name: str | None, time: Time) -> None:
        """Sends soil layer related daily variables to the output manager."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_soil_layer_daily_variables.__name__,
            "suffix": "field='" + field_name + "',layer='" + str(index) + "'",
            "simulation_day": time.simulation_day,
        }
        self.om.add_variable(
            "temperature",
            layer.temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )
        self.om.add_variable(
            "percolated_water",
            layer.percolated_water,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "water_content",
            layer.water_content,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable("water_factor", layer.water_factor, dict(info_map, **{"units": MeasurementUnits.UNITLESS}))
        self.om.add_variable(
            "evaporated_water_content",
            layer.evaporated_water_content,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "plant_metabolic_active_carbon_usage",
            layer.plant_metabolic_active_carbon_usage,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "plant_metabolic_active_carbon_loss",
            layer.plant_metabolic_active_carbon_loss,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "plant_metabolic_active_carbon_remaining",
            layer.plant_metabolic_active_carbon_remaining,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "plant_structural_active_carbon_usage",
            layer.plant_structural_active_carbon_usage,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "metabolic_litter_amount",
            layer.metabolic_litter_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "structural_litter_amount",
            layer.structural_litter_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "plant_structural_active_carbon_remaining",
            layer.plant_structural_active_carbon_remaining,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "plant_structural_slow_carbon_usage",
            layer.plant_structural_slow_carbon_usage,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "plant_structural_slow_carbon_loss",
            layer.plant_structural_slow_carbon_loss,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "plant_structural_slow_carbon_remaining",
            layer.plant_structural_slow_carbon_remaining,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_metabolic_active_carbon_usage",
            layer.soil_metabolic_active_carbon_usage,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_metabolic_active_carbon_loss",
            layer.soil_metabolic_active_carbon_loss,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_metabolic_active_carbon_remaining",
            layer.soil_metabolic_active_carbon_remaining,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_structural_active_carbon_usage",
            layer.soil_structural_active_carbon_usage,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_structural_active_carbon_loss",
            layer.soil_structural_active_carbon_loss,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_structural_active_carbon_remaining",
            layer.soil_structural_active_carbon_remaining,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_structural_slow_carbon_usage",
            layer.soil_structural_slow_carbon_usage,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_structural_slow_carbon_loss",
            layer.soil_structural_slow_carbon_loss,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_structural_slow_carbon_remaining",
            layer.soil_structural_slow_carbon_remaining,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "active_carbon_decomposition_amount",
            layer.active_carbon_decomposition_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "active_carbon_amount",
            layer.active_carbon_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "slow_carbon_amount",
            layer.slow_carbon_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "passive_carbon_amount",
            layer.passive_carbon_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "slow_carbon_decomposition_amount",
            layer.slow_carbon_decomposition_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "passive_carbon_decomposition_amount",
            layer.passive_carbon_decomposition_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "active_carbon_to_slow_amount",
            layer.active_carbon_to_slow_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "active_carbon_to_slow_loss",
            layer.active_carbon_to_slow_loss,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "active_carbon_to_passive_amount",
            layer.active_carbon_to_passive_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "slow_to_active_carbon_amount",
            layer.slow_to_active_carbon_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "slow_carbon_co2_lost_amount",
            layer.slow_carbon_co2_lost_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "passive_to_active_carbon_amount",
            layer.passive_to_active_carbon_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "passive_carbon_co2_lost_amount",
            layer.passive_carbon_co2_lost_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "plant_active_decompose_carbon",
            layer.plant_active_decompose_carbon,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_active_decompose_carbon",
            layer.soil_active_decompose_carbon,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "soil_overall_carbon_fraction",
            layer.soil_overall_carbon_fraction,
            dict(info_map, **{"units": MeasurementUnits.FRACTION}),
        )
        self.om.add_variable(
            "total_soil_carbon_amount",
            layer.total_soil_carbon_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "carbon_emissions",
            layer.total_soil_carbon_amount,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "mean_phosphorus_sorption_parameter",
            layer.mean_phosphorus_sorption_parameter,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "labile_inorganic_phosphorus_content",
            layer.labile_inorganic_phosphorus_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "active_inorganic_phosphorus_content",
            layer.active_inorganic_phosphorus_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "stable_inorganic_phosphorus_content",
            layer.stable_inorganic_phosphorus_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "fresh_organic_phosphorus_content",
            layer.fresh_organic_phosphorus_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "active_inorganic_unbalanced_counter",
            layer.active_inorganic_unbalanced_counter,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        self.om.add_variable(
            "labile_inorganic_unbalanced_counter",
            layer.labile_inorganic_unbalanced_counter,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        self.om.add_variable(
            "percolated_phosphorus",
            layer.percolated_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "nitrate_content",
            layer.nitrate_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "ammonium_content",
            layer.ammonium_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "active_organic_nitrogen_content",
            layer.active_organic_nitrogen_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "stable_organic_nitrogen_content",
            layer.stable_organic_nitrogen_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "fresh_organic_nitrogen_content",
            layer.fresh_organic_nitrogen_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "nitrous_oxide_emissions",
            layer.nitrous_oxide_emissions,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "dinitrogen_emissions",
            layer.dinitrogen_emissions,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "ammonia_emissions",
            layer.ammonia_emissions,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "percolated_nitrates",
            layer.percolated_nitrates,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "percolated_ammonium",
            layer.percolated_ammonium,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "percolated_active_organic_nitrogen",
            layer.percolated_active_organic_nitrogen,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )

    def send_vadose_zone_layer_daily_variables(self, field: Field, time: Time) -> None:
        """Sends vadose zone layer related daily variables to output manager."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_vadose_zone_layer_daily_variables.__name__,
            "suffix": "field='" + field.field_data.name + "',vadose_zone_layer",
            "simulation_day": time.simulation_day,
        }
        self.om.add_variable(
            "active_organic_nitrogen_content",
            field.soil.data.vadose_zone_layer.active_organic_nitrogen_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "stable_organic_nitrogen_content",
            field.soil.data.vadose_zone_layer.stable_organic_nitrogen_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "nitrate_content",
            field.soil.data.vadose_zone_layer.nitrate_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "fresh_organic_nitrogen_content",
            field.soil.data.vadose_zone_layer.fresh_organic_nitrogen_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "water_content",
            field.soil.data.vadose_zone_layer.water_content,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "labile_inorganic_phosphorus_content",
            field.soil.data.vadose_zone_layer.labile_inorganic_phosphorus_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "active_inorganic_phosphorus_content",
            field.soil.data.vadose_zone_layer.active_inorganic_phosphorus_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "stable_inorganic_phosphorus_content",
            field.soil.data.vadose_zone_layer.stable_inorganic_phosphorus_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "fresh_organic_phosphorus_content",
            field.soil.data.vadose_zone_layer.fresh_organic_phosphorus_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "plant_residue",
            field.soil.data.vadose_zone_layer.plant_residue,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )

    def send_soil_daily_variables(self, field: Field, time: Time) -> None:
        """Sends soil related daily variables."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_soil_daily_variables.__name__,
            "suffix": "field='" + field.field_data.name + "'",
            "simulation_day": time.simulation_day,
        }

        self.om.add_variable(
            "water_evaporated",
            field.soil.data.water_evaporated,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "eroded_sediment",
            field.soil.data.eroded_sediment,
            dict(info_map, **{"units": MeasurementUnits.METRIC_TONS}),
        )
        self.om.add_variable(
            "accumulated_runoff",
            field.soil.data.accumulated_runoff,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "infiltrated_water",
            field.soil.data.infiltrated_water,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "snow_content",
            field.soil.data.snow_content,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "snow_melt",
            field.soil.data.snow_melt_amount,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "current_day_snow_temperature",
            field.soil.data.current_day_snow_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )
        self.om.add_variable(
            "water_sublimated",
            field.soil.data.water_sublimated,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "cover_type", field.soil.data.cover_type, dict(info_map, **{"units": MeasurementUnits.UNITLESS})
        )
        self.om.add_variable(
            "full_available_phosphorus_pool",
            field.soil.data.full_available_phosphorus_pool,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "available_phosphorus_pool",
            field.soil.data.available_phosphorus_pool,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "recalcitrant_phosphorus_pool",
            field.soil.data.recalcitrant_phosphorus_pool,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "runoff_fertilizer_phosphorus",
            field.soil.data.runoff_fertilizer_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        # confirm unit
        self.om.add_variable(
            "days_since_application",
            field.soil.data.days_since_application,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        # confirm unit
        self.om.add_variable(
            "rain_events_after_fertilizer_application",
            field.soil.data.rain_events_after_fertilizer_application,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "machine_manure_dry_mass",
            field.soil.data.machine_manure.manure_dry_mass,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "machine_manure_applied_mass",
            field.soil.data.machine_manure.manure_applied_mass,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "machine_manure_field_coverage",
            field.soil.data.machine_manure.manure_field_coverage,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "machine_manure_moisture_factor",
            field.soil.data.machine_manure.manure_moisture_factor,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "machine_water_extractable_inorganic_phosphorus",
            field.soil.data.machine_manure.water_extractable_inorganic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "machine_water_extractable_organic_phosphorus",
            field.soil.data.machine_manure.water_extractable_organic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "machine_stable_inorganic_phosphorus",
            field.soil.data.machine_manure.stable_inorganic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "machine_stable_organic_phosphorus",
            field.soil.data.machine_manure.stable_organic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "machine_organic_phosphorus_runoff",
            field.soil.data.machine_manure.organic_phosphorus_runoff,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "machine_inorganic_phosphorus_runoff",
            field.soil.data.machine_manure.inorganic_phosphorus_runoff,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "grazing_manure_dry_mass",
            field.soil.data.grazing_manure.manure_dry_mass,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "grazing_manure_applied_mass",
            field.soil.data.grazing_manure.manure_applied_mass,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "grazing_manure_field_coverage",
            field.soil.data.grazing_manure.manure_field_coverage,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "grazing_manure_moisture_factor",
            field.soil.data.grazing_manure.manure_moisture_factor,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        self.om.add_variable(
            "grazing_water_extractable_inorganic_phosphorus",
            field.soil.data.grazing_manure.water_extractable_inorganic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "grazing_water_extractable_organic_phosphorus",
            field.soil.data.grazing_manure.water_extractable_organic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "grazing_stable_inorganic_phosphorus",
            field.soil.data.grazing_manure.stable_inorganic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "grazing_stable_organic_phosphorus",
            field.soil.data.grazing_manure.stable_organic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "grazing_organic_phosphorus_runoff",
            field.soil.data.grazing_manure.organic_phosphorus_runoff,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "grazing_inorganic_phosphorus_runoff",
            field.soil.data.grazing_manure.inorganic_phosphorus_runoff,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "soil_phosphorus_runoff",
            field.soil.data.soil_phosphorus_runoff,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "nitrate_runoff",
            field.soil.data.nitrate_runoff,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "ammonium_runoff",
            field.soil.data.ammonium_runoff,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "eroded_fresh_organic_nitrogen",
            field.soil.data.eroded_fresh_organic_nitrogen,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "eroded_stable_organic_nitrogen",
            field.soil.data.eroded_stable_organic_nitrogen,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "eroded_active_organic_nitrogen",
            field.soil.data.eroded_active_organic_nitrogen,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )

        self.om.add_variable(
            "profile_carbon_total",
            field.soil.data.profile_carbon_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "profile_carbon_emissions",
            field.soil.data.profile_carbon_emissions,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "profile_nitrates_total",
            field.soil.data.profile_nitrates_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "profile_ammonium_total",
            field.soil.data.profile_ammonium_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "profile_active_organic_nitrogen_total",
            field.soil.data.profile_active_organic_nitrogen_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "profile_stable_organic_nitrogen_total",
            field.soil.data.profile_stable_organic_nitrogen_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "profile_fresh_organic_nitrogen_total",
            field.soil.data.profile_fresh_organic_nitrogen_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )

    def send_field_daily_variables(self, field: Field, time: Time) -> None:
        """Sends field related daily variables to the output manager."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_field_daily_variables.__name__,
            "suffix": "field='" + field.field_data.name + "'",
            "simulation_day": time.simulation_day,
        }

        self.om.add_variable(
            "current_residue",
            field.field_data.current_residue,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "transpiration",
            field.field_data.transpiration,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "max_transpiration",
            field.field_data.max_transpiration,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "max_evapotranspiration",
            field.field_data.max_evapotranspiration,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        # confirm unit
        self.om.add_variable(
            "days_into_watering_interval",
            field.field_data.days_into_watering_interval,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )

    def send_soil_layer_annual_variables(self, layer: LayerData, field_name: str | None, index: int) -> None:
        """Sends layer related annual variables to the output manager."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_soil_layer_annual_variables.__name__,
            "suffix": "field='" + field_name + "',layer='" + str(index) + "'",
        }

        self.om.add_variable(
            "annual_nitrous_oxide_emissions_total",
            layer.annual_nitrous_oxide_emissions_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "annual_ammonia_emissions_total",
            layer.annual_ammonia_emissions_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "annual_decomposition_carbon_CO2_lost",
            layer.annual_decomposition_carbon_CO2_lost,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "annual_carbon_CO2_lost",
            layer.annual_carbon_CO2_lost,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )

    def send_field_annual_variables(self, field: Field) -> None:
        """Sends field related annual variables to the output manager."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_field_annual_variables.__name__,
            "suffix": "field='" + field.field_data.name + "'",
        }
        self.om.add_variable(
            "annual_irrigation_water_use_total",
            field.field_data.annual_irrigation_water_use_total,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )

    def send_soil_annual_variables(self, field: Field) -> None:
        """Sends soil related annual variables to the output manager."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_soil_annual_variables.__name__,
            "suffix": "field='" + field.field_data.name + "'",
        }
        water_content_change = field.soil.data.profile_soil_water_content - field.soil.data.initial_water_content
        self.om.add_variable(
            "annual_water_content_change",
            water_content_change,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )

        nitrates_content_change = field.soil.data.profile_nitrates_total - field.soil.data.initial_nitrates_total
        self.om.add_variable(
            "annual_nitrates_content_change",
            nitrates_content_change,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )

        self.om.add_variable(
            "annual_soil_evaporation_total",
            field.soil.data.annual_soil_evaporation_total,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        self.om.add_variable(
            "annual_eroded_sediment_total",
            field.soil.data.annual_eroded_sediment_total,
            dict(info_map, **{"units": MeasurementUnits.METRIC_TONS}),
        )
        self.om.add_variable(
            "annual_surface_runoff_total",
            field.soil.data.annual_surface_runoff_total,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS_PER_HECTARE}),
        )
        self.om.add_variable(
            "annual_runoff_fertilizer_phosphorus",
            field.soil.data.annual_runoff_fertilizer_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_runoff_machine_manure_inorganic_phosphorus",
            field.soil.data.machine_manure.annual_runoff_manure_inorganic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_machine_decomposed_manure",
            field.soil.data.machine_manure.annual_decomposed_manure,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_runoff_machine_manure_organic_phosphorus",
            field.soil.data.machine_manure.annual_runoff_manure_organic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_runoff_grazing_manure_inorganic_phosphorus",
            field.soil.data.grazing_manure.annual_runoff_manure_inorganic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_runoff_grazing_manure_organic_phosphorus",
            field.soil.data.grazing_manure.annual_runoff_manure_organic_phosphorus,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_grazing_decomposed_manure",
            field.soil.data.grazing_manure.annual_decomposed_manure,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_soil_phosphorus_runoff",
            field.soil.data.annual_soil_phosphorus_runoff,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE}),
        )
        self.om.add_variable(
            "annual_runoff_nitrates_total",
            field.soil.data.annual_runoff_nitrates_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_runoff_ammonium_total",
            field.soil.data.annual_runoff_ammonium_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_eroded_fresh_organic_nitrogen_total",
            field.soil.data.annual_eroded_fresh_organic_nitrogen_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_eroded_stable_organic_nitrogen_total",
            field.soil.data.annual_eroded_stable_organic_nitrogen_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        self.om.add_variable(
            "annual_eroded_active_organic_nitrogen_total",
            field.soil.data.annual_eroded_active_organic_nitrogen_total,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
