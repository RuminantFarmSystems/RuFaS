from typing import List

from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.crop.crop import Crop
from RUFAS.biophysical.field.field.field import Field
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.units import MeasurementUnits
from RUFAS.rufas_time import RufasTime


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

    def send_daily_variables(self, time: RufasTime) -> None:
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

    def send_crop_daily_variables(self, crop: Crop, field_name: str | None, time: RufasTime) -> None:
        """Sends crop related daily variables to the output manager."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_crop_daily_variables.__name__,
            "suffix": f"field='{field_name}',crop='{crop.data.name}',"
            f"planted={crop.data.planting_day},{crop.data.planting_year}",
            "simulation_day": time.simulation_day,
        }
        self.om.add_variable(
            "root_depth",
            crop.data.root_depth,
            dict(
                info_map,
                **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("RootDevelopment", "develop_roots")]},
            ),
        )
        self.om.add_variable(
            "biomass",
            crop.data.biomass,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("BiomassAllocation", "photosynthesize"),
                        ("CropManagement", "cut_crop"),
                        ("Dormancy", "enter_dormant"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "usable_light",
            crop.biomass_allocation.usable_light,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MEGAJOULES_PER_SQUARE_METER,
                    "data_origin": [("BiomassAllocation", "photosynthesize")],
                },
            ),
        )
        self.om.add_variable(
            "biomass_growth_max",
            crop.data.biomass_growth_max,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("BiomassAllocation", "photosynthesize")],
                },
            ),
        )
        self.om.add_variable(
            "biomass_growth",
            crop.biomass_allocation.biomass_growth,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("BiomassAllocation", "photosynthesize")],
                },
            ),
        )
        self.om.add_variable(
            "growth_factor",
            crop.data.growth_factor,
            dict(
                info_map,
                **{"units": MeasurementUnits.UNITLESS, "data_origin": [("GrowthConstraints", "constrain_growth")]},
            ),
        )
        self.om.add_variable(
            "above_ground_biomass",
            crop.data.above_ground_biomass,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("BiomassAllocation", "partition_biomass"),
                        ("CropManagement", "_recalculate_biomass_distribution"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "root_biomass",
            crop.data.root_biomass,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("BiomassAllocation", "partition_biomass"),
                        ("CropManagement", "_recalculate_biomass_distribution"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "water_uptake",
            crop.data.water_uptake,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("WaterUptake", "uptake")]}),
        )
        self.om.add_variable(
            "crop_nitrogen",
            crop.data.nitrogen,
            dict(
                info_map,
                **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE, "data_origin": [("Nitrogen_uptake", "uptake")]},
            ),
        )
        self.om.add_variable(
            "optimal_crop_nitrogen",
            crop.data.optimal_nitrogen,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE, "data_origin": [("CropData", "")]}),
        )
        self.om.add_variable(
            "water_stress",
            crop.growth_constraints.water_stress,
            dict(
                info_map,
                **{"units": MeasurementUnits.UNITLESS, "data_origin": [("GrowthConstraints", "constrain_growth")]},
            ),
        )
        self.om.add_variable(
            "temp_stress",
            crop.growth_constraints.temp_stress,
            dict(
                info_map,
                **{"units": MeasurementUnits.UNITLESS, "data_origin": [("GrowthConstraints", "constrain_growth")]},
            ),
        )
        self.om.add_variable(
            "nitrogen_stress",
            crop.growth_constraints.nitrogen_stress,
            dict(
                info_map,
                **{"units": MeasurementUnits.UNITLESS, "data_origin": [("GrowthConstraints", "constrain_growth")]},
            ),
        )
        self.om.add_variable(
            "phosphorus_stress",
            crop.growth_constraints.phosphorus_stress,
            dict(
                info_map,
                **{"units": MeasurementUnits.UNITLESS, "data_origin": [("GrowthConstraints", "constrain_growth")]},
            ),
        )
        self.om.add_variable(
            "accumulated_heat_units",
            crop.data.accumulated_heat_units,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [("CropManagement", "cut_crop"), ("HeatUnits", "add_heat_units")],
                },
            ),
        )
        self.om.add_variable(
            "heat_fraction",
            crop.data.heat_fraction,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [("CropData", "heat_fraction")],
                },
            ),
        )
        self.om.add_variable(
            "is_growing",
            crop.data.is_growing,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS, "data_origin": [("HeatUnits", "absorb_heat_units")]}),
        )
        self.om.add_variable(
            "is_dormant",
            crop.data.is_dormant,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [("Crop", "exit_dormancy"), ("Dormancy", "enter_dormancy")],
                },
            ),
        )
        self.om.add_variable(
            "leaf_area_index",
            crop.data.leaf_area_index,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [
                        ("CropManagement", "cut_crop"),
                        ("LeafAreaIndex", "grow_canopy"),
                        ("LeafAreaIndex", "add_leaf_area"),
                        ("Dormancy", "enter_dormancy"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "canopy_height",
            crop.leaf_area_index.canopy_height,
            dict(info_map, **{"units": MeasurementUnits.METERS, "data_origin": [("LeafAreaIndex", "grow_canopy")]}),
        )
        self.om.add_variable(
            "leaf_area_added",
            crop.leaf_area_index.leaf_area_added,
            dict(
                info_map,
                **{"units": MeasurementUnits.UNITLESS, "data_origin": [("LeafAreaIndex", "determine_leaf_area_added")]},
            ),
        )
        self.om.add_variable(
            "optimal_leaf_area_change",
            crop.leaf_area_index.optimal_leaf_area_change,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS, "data_origin": [("LeafAreaIndex", "grow_canopy")]}),
        )
        self.om.add_variable(
            "potential_nitrogen_uptake",
            crop.nitrogen_uptake.potential_nutrient_uptake,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("NonWaterUptake", "uptake_main_process")],
                },
            ),
        )
        self.om.add_variable(
            "total_nitrogen_uptake",
            crop.nitrogen_uptake.total_nutrient_uptake,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("NonWaterUptake", "uptake_nutrient")],
                },
            ),
        )
        self.om.add_variable(
            "actual_nitrogen_uptakes",
            crop.nitrogen_uptake.actual_nutrient_uptakes,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("NonWaterUptake", "uptake_nutrient")],
                },
            ),
        )
        self.om.add_variable(
            "optimal_nitrogen_fraction",
            crop.data.optimal_nitrogen_fraction,
            dict(
                info_map,
                **{"units": MeasurementUnits.FRACTION, "data_origin": [("NonWaterUptake", "uptake_main_process")]},
            ),
        )
        self.om.add_variable(
            "potential_phosphorus_uptake",
            crop.phosphorus_incorporation.potential_nutrient_uptake,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("NonWaterUptake", "uptake_main_process")],
                },
            ),
        )
        self.om.add_variable(
            "total_phosphorus_uptake",
            crop.phosphorus_incorporation.total_nutrient_uptake,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("NonWaterUptake", "uptake_nutrient")],
                },
            ),
        )
        self.om.add_variable(
            "actual_phosphorus_uptakes",
            crop.phosphorus_incorporation.actual_nutrient_uptakes,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("NonWaterUptake", "uptake_nutrient")],
                },
            ),
        )
        self.om.add_variable(
            "cumulative_evaporation",
            crop.data.cumulative_evaporation,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [("Crop", "cycle_water_for_crop"), ("WaterDynamics", "cycle_water")],
                },
            ),
        )
        self.om.add_variable(
            "cumulative_transpiration",
            crop.data.cumulative_transpiration,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [("Crop", "cycle_water_for_crop"), ("WaterDynamics", "cycle_water")],
                },
            ),
        )
        self.om.add_variable(
            "cumulative_evapotranspiration",
            crop.water_dynamics.cumulative_evapotranspiration,
            dict(
                info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("WaterDynamics", "cycle_water")]}
            ),
        )
        self.om.add_variable(
            "water_deficiency",
            crop.data.water_deficiency,
            dict(
                info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("WaterDynamics", "cycle_water")]}
            ),
        )
        self.om.add_variable(
            "max_transpiration",
            crop.data.max_transpiration,
            dict(
                info_map,
                **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("WaterDynamics", "set_max_transpiration")]},
            ),
        )
        self.om.add_variable(
            "canopy_water",
            crop.data.canopy_water,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [("Crop", "handle_water_in_canopy"), ("WaterDynamics", "evaporate_from_canopy")],
                },
            ),
        )
        self.om.add_variable(
            "cut_biomass",
            crop.crop_management.cut_biomass,
            dict(
                info_map,
                **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE, "data_origin": [("CropManagement", "cut_crop")]},
            ),
        )
        self.om.add_variable(
            "wet_yield_collected",
            crop.crop_management.wet_yield_collected,
            dict(
                info_map,
                **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE, "data_origin": [("CropManagement", "cut_crop")]},
            ),
        )
        self.om.add_variable(
            "dry_matter_yield_residue",
            crop.crop_management.yield_residue,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CropManagement", "kill"),
                        ("CropManagement", "cut_crop"),
                        ("CropManagement", "_transfer_residue"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "yield_nitrogen",
            crop.crop_management.yield_nitrogen,
            dict(
                info_map,
                **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE, "data_origin": [("CropManagement", "cut_crop")]},
            ),
        )
        self.om.add_variable(
            "yield_phosphorus",
            crop.crop_management.yield_phosphorus,
            dict(
                info_map,
                **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE, "data_origin": [("CropManagement", "cut_crop")]},
            ),
        )
        self.om.add_variable(
            "residue_nitrogen",
            crop.crop_management.residue_nitrogen,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CropManagement", "kill"),
                        ("CropManagement", "cut_crop"),
                        ("CropManagement", "_transfer_residue"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "residue_phosphorus",
            crop.crop_management.residue_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CropManagement", "kill"),
                        ("CropManagement", "cut_crop"),
                        ("CropManagement", "_transfer_residue"),
                    ],
                },
            ),
        )

    def send_soil_layer_daily_variables(
        self, layer: LayerData, index: int, field_name: str | None, time: RufasTime
    ) -> None:
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
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.DEGREES_CELSIUS,
                    "data_origin": [("SoilTemp", "daily_soil_temperature_update")],
                },
            ),
        )
        self.om.add_variable(
            "percolated_water",
            layer.percolated_water,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [("Percolation", "percolate"), ("Percolation", "percolate_infiltrated_water")],
                },
            ),
        )
        self.om.add_variable(
            "water_content",
            layer.water_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [
                        ("LayerData", "__post_init__"),
                        ("Evaporation", "evaporate"),
                        ("Percolation", "percolate"),
                        ("Percolation", "percolate_infiltrated_water"),
                        ("WaterUptake", "extract_water_from_soil"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "water_factor",
            layer.water_factor,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [("LayerData", "water_factor")],
                },
            ),
        )
        self.om.add_variable(
            "evaporated_water_content",
            layer.evaporated_water_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [("Evaporation", "evaporate")],
                },
            ),
        )
        self.om.add_variable(
            "plant_metabolic_active_carbon_usage",
            layer.plant_metabolic_active_carbon_usage,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("ResiduePartition", "partition_residue")],
                },
            ),
        )
        self.om.add_variable(
            "plant_metabolic_active_carbon_loss",
            layer.plant_metabolic_active_carbon_loss,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "plant_metabolic_active_carbon_remaining",
            layer.plant_metabolic_active_carbon_remaining,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "plant_structural_active_carbon_usage",
            layer.plant_structural_active_carbon_usage,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("ResiduePartition", "partition_residue")],
                },
            ),
        )
        self.om.add_variable(
            "metabolic_litter_amount",
            layer.metabolic_litter_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("ResiduePartition", "partition_residue"),
                        ("ResiduePartition", "_add_litter_to_pools"),
                        ("LayerData", "_initialize_carbon_pools"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "structural_litter_amount",
            layer.structural_litter_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("ResiduePartition", "partition_residue"),
                        ("ResiduePartition", "_add_litter_to_pools"),
                        ("LayerData", "_initialize_carbon_pools"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "plant_structural_active_carbon_remaining",
            layer.plant_structural_active_carbon_remaining,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "plant_structural_slow_carbon_usage",
            layer.plant_structural_slow_carbon_usage,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("ResiduePartition", "partition_residue")],
                },
            ),
        )
        self.om.add_variable(
            "plant_structural_slow_carbon_loss",
            layer.plant_structural_slow_carbon_loss,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "plant_structural_slow_carbon_remaining",
            layer.plant_structural_slow_carbon_remaining,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "soil_metabolic_active_carbon_usage",
            layer.soil_metabolic_active_carbon_usage,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("ResiduePartition", "partition_residue")],
                },
            ),
        )
        self.om.add_variable(
            "soil_metabolic_active_carbon_loss",
            layer.soil_metabolic_active_carbon_loss,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "soil_metabolic_active_carbon_remaining",
            layer.soil_metabolic_active_carbon_remaining,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "soil_structural_active_carbon_usage",
            layer.soil_structural_active_carbon_usage,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("ResiduePartition", "partition_residue")],
                },
            ),
        )
        self.om.add_variable(
            "soil_structural_active_carbon_loss",
            layer.soil_structural_active_carbon_loss,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "soil_structural_active_carbon_remaining",
            layer.soil_structural_active_carbon_remaining,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "soil_structural_slow_carbon_usage",
            layer.soil_structural_slow_carbon_usage,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("ResiduePartition", "partition_residue")],
                },
            ),
        )
        self.om.add_variable(
            "soil_structural_slow_carbon_loss",
            layer.soil_structural_slow_carbon_loss,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "soil_structural_slow_carbon_remaining",
            layer.soil_structural_slow_carbon_remaining,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "active_carbon_decomposition_amount",
            layer.active_carbon_decomposition_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "active_carbon_amount",
            layer.active_carbon_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("PoolGasPartition", "partition_pool_gas"),
                        ("LayerData", "_initialize_carbon_pools"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "slow_carbon_amount",
            layer.slow_carbon_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("PoolGasPartition", "partition_pool_gas"),
                        ("LayerData", "_initialize_carbon_pools"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "passive_carbon_amount",
            layer.passive_carbon_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("PoolGasPartition", "partition_pool_gas"),
                        ("LayerData", "_initialize_carbon_pools"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "slow_carbon_decomposition_amount",
            layer.slow_carbon_decomposition_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "passive_carbon_decomposition_amount",
            layer.passive_carbon_decomposition_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "active_carbon_to_slow_amount",
            layer.active_carbon_to_slow_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "active_carbon_to_slow_loss",
            layer.active_carbon_to_slow_loss,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "active_carbon_to_passive_amount",
            layer.active_carbon_to_passive_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "slow_to_active_carbon_amount",
            layer.slow_to_active_carbon_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "slow_carbon_co2_lost_amount",
            layer.slow_carbon_co2_lost_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "passive_to_active_carbon_amount",
            layer.passive_to_active_carbon_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "passive_carbon_co2_lost_amount",
            layer.passive_carbon_co2_lost_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "plant_active_decompose_carbon",
            layer.plant_active_decompose_carbon,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "soil_active_decompose_carbon",
            layer.soil_active_decompose_carbon,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("PoolGasPartition", "partition_pool_gas")],
                },
            ),
        )
        self.om.add_variable(
            "soil_overall_carbon_fraction",
            layer.soil_overall_carbon_fraction,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.FRACTION,
                    "data_origin": [("CarbonCycling", "_soil_carbon_aggregation")],
                },
            ),
        )
        self.om.add_variable(
            "total_soil_carbon_amount",
            layer.total_soil_carbon_amount,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CarbonCycling", "_soil_carbon_aggregation"),
                        ("LayerData", "_initialize_carbon_pools"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "mean_phosphorus_sorption_parameter",
            layer.mean_phosphorus_sorption_parameter,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [
                        ("LayerData", "___post_init__"),
                        ("PhosphorusMineralization", "mineralize_phosphorus"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "labile_inorganic_phosphorus_content",
            layer.labile_inorganic_phosphorus_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CropManagement", "_add_yield_residue_to_layer"),
                        ("CropManagement", "_transfer_residue"),
                        ("LayerData", "__post_init__"),
                        ("LayerData", "add_to_labile_phosphorus"),
                        ("PhosphorusMineralization", "mineralize_phosphorus"),
                        ("SolublePhosphorus", "daily_update_routine"),
                        ("TillageApplication", "_mix_soil_layers"),
                        ("NonWaterUptake", "uptake_main_process"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "active_inorganic_phosphorus_content",
            layer.active_inorganic_phosphorus_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("LayerData", "__post_init__"),
                        ("LayerData", "add_to_active_phosphorus"),
                        ("PhosphorusMineralization", "mineralize_phosphorus"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "stable_inorganic_phosphorus_content",
            layer.stable_inorganic_phosphorus_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("LayerData", "__post_init__"),
                        ("PhosphorusMineralization", "mineralize_phosphorus"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "fresh_organic_phosphorus_content",
            layer.fresh_organic_phosphorus_content,
            dict(
                info_map,
                **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE, "data_origin": [("LayerData", "")]},
            ),
        )
        self.om.add_variable(
            "active_inorganic_unbalanced_counter",
            layer.active_inorganic_unbalanced_counter,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.DAYS,
                    "data_origin": [("PhosphorusMineralization", "mineralize_phosphorus")],
                },
            ),
        )
        self.om.add_variable(
            "labile_inorganic_unbalanced_counter",
            layer.labile_inorganic_unbalanced_counter,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.DAYS,
                    "data_origin": [("PhosphorusMineralization", "mineralize_phosphorus")],
                },
            ),
        )
        self.om.add_variable(
            "percolated_phosphorus",
            layer.percolated_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("SolublePhosphorus", "daily_update_routine")],
                },
            ),
        )
        self.om.add_variable(
            "nitrate_content",
            layer.nitrate_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                        ("LayerData", "_initialize_nitrogen_pools"),
                        ("Denitrification", "denitrify"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                        ("LeachingRunoffErosion", "_leach_nitrogen"),
                        ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                        ("NitrificationVolatilization", "do_daily_nitrification_and_volatilization"),
                        ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                        ("FertilizerApplication", "apply_fertilizer"),
                        ("TillageApplication", "_mix_soil_layers"),
                        ("NonWaterUptake", "uptake_main_process"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "ammonium_content",
            layer.ammonium_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                        ("LayerData", "_initialize_nitrogen_pools"),
                        ("HumusMineralization", "mineralize_organic_nitrogen"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                        ("LeachingRunoffErosion", "_leach_nitrogen"),
                        ("NitrificationVolatilization", "do_daily_nitrification_and_volatilization"),
                        ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                        ("FertilizerApplication", "apply_fertilizer"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "active_organic_nitrogen_content",
            layer.active_organic_nitrogen_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CropManagement", "_add_yield_residue_to_layer"),
                        ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                        ("LayerData", "_initialize_nitrogen_pools"),
                        ("SoilData", "__post_init__"),
                        ("HumusMineralization", "mineralize_organic_nitrogen"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                        ("LeachingRunoffErosion", "_leach_nitrogen"),
                        ("MineralizationDecomposition", "_correct_fresh_organic_nitrogen_pools"),
                        ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "stable_organic_nitrogen_content",
            layer.stable_organic_nitrogen_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                        ("LayerData", "_initialize_nitrogen_pools"),
                        ("SoilData", "__post_init__"),
                        ("HumusMineralization", "mineralize_organic_nitrogen"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "fresh_organic_nitrogen_content",
            layer.fresh_organic_nitrogen_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CropManagement", "_add_yield_residue_to_layer"),
                        ("CropManagement", "_transfer_residue"),
                        ("LayerData", "_initialize_nitrogen_pools"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                        ("MineralizationDecomposition", "_correct_fresh_organic_nitrogen_pools"),
                        ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "nitrous_oxide_emissions",
            layer.nitrous_oxide_emissions,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": ["Denitrification", "denitrify"],
                },
            ),
        )
        self.om.add_variable(
            "dinitrogen_emissions",
            layer.dinitrogen_emissions,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": ["Denitrification", "denitrify"],
                },
            ),
        )
        self.om.add_variable(
            "ammonia_emissions",
            layer.ammonia_emissions,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": ["NitrificationVolatilization", "do_daily_nitrification_and_volatilization"],
                },
            ),
        )
        self.om.add_variable(
            "percolated_nitrates",
            layer.percolated_nitrates,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": ["LeachingRunoffErosion", "_leach_nitrogen"],
                },
            ),
        )
        self.om.add_variable(
            "percolated_ammonium",
            layer.percolated_ammonium,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": ["LeachingRunoffErosion", "_leach_nitrogen"],
                },
            ),
        )
        self.om.add_variable(
            "percolated_active_organic_nitrogen",
            layer.percolated_active_organic_nitrogen,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": ["LeachingRunoffErosion", "_leach_nitrogen"],
                },
            ),
        )

    def send_vadose_zone_layer_daily_variables(self, field: Field, time: RufasTime) -> None:
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
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CropManagement", "_add_yield_residue_to_layer"),
                        ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                        ("LayerData", "_initialize_nitrogen_pools"),
                        ("SoilData", "__post_init__"),
                        ("HumusMineralization", "mineralize_organic_nitrogen"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                        ("LeachingRunoffErosion", "_leach_nitrogen"),
                        ("MineralizationDecomposition", "_correct_fresh_organic_nitrogen_pools"),
                        ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "stable_organic_nitrogen_content",
            field.soil.data.vadose_zone_layer.stable_organic_nitrogen_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                        ("LayerData", "_initialize_nitrogen_pools"),
                        ("SoilData", "__post_init__"),
                        ("HumusMineralization", "mineralize_organic_nitrogen"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "nitrate_content",
            field.soil.data.vadose_zone_layer.nitrate_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                        ("LayerData", "_initialize_nitrogen_pools"),
                        ("Denitrification", "denitrify"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                        ("LeachingRunoffErosion", "_leach_nitrogen"),
                        ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                        ("NitrificationVolatilization", "do_daily_nitrification_and_volatilization"),
                        ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                        ("FertilizerApplication", "apply_fertilizer"),
                        ("TillageApplication", "_mix_soil_layers"),
                        ("NonWaterUptake", "uptake_main_process"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "fresh_organic_nitrogen_content",
            field.soil.data.vadose_zone_layer.fresh_organic_nitrogen_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CropManagement", "_add_yield_residue_to_layer"),
                        ("CropManagement", "_transfer_residue"),
                        ("LayerData", "_initialize_nitrogen_pools"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                        ("MineralizationDecomposition", "_correct_fresh_organic_nitrogen_pools"),
                        ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "water_content",
            field.soil.data.vadose_zone_layer.water_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [
                        ("LayerData", "__post_init__"),
                        ("Evaporation", "evaporate"),
                        ("Percolation", "percolate"),
                        ("Percolation", "percolate_infiltrated_water"),
                        ("WaterUptake", "extract_water_from_soil"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "labile_inorganic_phosphorus_content",
            field.soil.data.vadose_zone_layer.labile_inorganic_phosphorus_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CropManagement", "_add_yield_residue_to_layer"),
                        ("CropManagement", "_transfer_residue"),
                        ("LayerData", "__post_init__"),
                        ("LayerData", "add_to_labile_phosphorus"),
                        ("PhosphorusMineralization", "mineralize_phosphorus"),
                        ("SolublePhosphorus", "daily_update_routine"),
                        ("TillageApplication", "_mix_soil_layers"),
                        ("NonWaterUptake", "uptake_main_process"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "active_inorganic_phosphorus_content",
            field.soil.data.vadose_zone_layer.active_inorganic_phosphorus_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("LayerData", "__post_init__"),
                        ("LayerData", "add_to_active_phosphorus"),
                        ("PhosphorusMineralization", "mineralize_phosphorus"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "stable_inorganic_phosphorus_content",
            field.soil.data.vadose_zone_layer.stable_inorganic_phosphorus_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("LayerData", "__post_init__"),
                        ("PhosphorusMineralization", "mineralize_phosphorus"),
                        ("TillageApplication", "_mix_soil_layers"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "fresh_organic_phosphorus_content",
            field.soil.data.vadose_zone_layer.fresh_organic_phosphorus_content,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE, "data_origin": [("LayerData", "")]}),
        )
        self.om.add_variable(
            "plant_residue",
            field.soil.data.vadose_zone_layer.plant_residue,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("CropManagement", "_add_yield_residue_to_layer"),
                        ("ResiduePartition", "_add_litter_to_pools"),
                    ],
                },
            ),
        )

    def send_soil_daily_variables(self, field: Field, time: RufasTime) -> None:
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
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("Evaporation", "evaporate")]}),
        )
        self.om.add_variable(
            "eroded_sediment",
            field.soil.data.eroded_sediment,
            dict(info_map, **{"units": MeasurementUnits.METRIC_TONS, "data_origin": [("SoilErosion", "erode")]}),
        )
        self.om.add_variable(
            "accumulated_runoff",
            field.soil.data.accumulated_runoff,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("Infiltration", "infiltrate")]}),
        )
        self.om.add_variable(
            "infiltrated_water",
            field.soil.data.infiltrated_water,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("Infiltration", "infiltrate")]}),
        )
        self.om.add_variable(
            "snow_content",
            field.soil.data.snow_content,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [("Snow", "update_snow"), ("Snow", "sublimate")],
                },
            ),
        )
        self.om.add_variable(
            "snow_melt",
            field.soil.data.snow_melt_amount,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("Snow", "update_snow")]}),
        )
        self.om.add_variable(
            "current_day_snow_temperature",
            field.soil.data.current_day_snow_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS, "data_origin": [("Snow", "update_snow")]}),
        )
        self.om.add_variable(
            "water_sublimated",
            field.soil.data.water_sublimated,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("Snow", "sublimate")]}),
        )
        self.om.add_variable(
            "cover_type",
            field.soil.data.cover_type,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS, "data_origin": [("SoilData", "")]}),
        )
        self.om.add_variable(
            "full_available_phosphorus_pool",
            field.soil.data.full_available_phosphorus_pool,
            dict(
                info_map,
                **{"units": MeasurementUnits.KILOGRAMS, "data_origin": [("Fertilizer", "add_fertilizer_phosphorus")]},
            ),
        )
        self.om.add_variable(
            "available_phosphorus_pool",
            field.soil.data.available_phosphorus_pool,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("Fertilizer", "_update_before_and_at_first_rain"),
                        ("Fertilizer", "add_fertilizer_phosphorus"),
                        ("Fertilizer", "_absorb_phosphorus_from_available_pool"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "recalcitrant_phosphorus_pool",
            field.soil.data.recalcitrant_phosphorus_pool,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("Fertilizer", "_update_after_first_rain"),
                        ("Fertilizer", "add_fertilizer_phosphorus"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "runoff_fertilizer_phosphorus",
            field.soil.data.runoff_fertilizer_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("Fertilizer", "_update_after_first_rain"),
                        ("Fertilizer", "_update_before_and_at_first_rain"),
                        ("Fertilizer", "do_fertilizer_phosphorus_operations"),
                    ],
                },
            ),
        )
        # confirm unit
        self.om.add_variable(
            "days_since_application",
            field.soil.data.days_since_application,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.DAYS,
                    "data_origin": [
                        ("Fertilizer", "do_fertilizer_phosphorus_operations"),
                        ("Fertilizer", "add_fertilizer_phosphorus"),
                    ],
                },
            ),
        )
        # confirm unit
        self.om.add_variable(
            "rain_events_after_fertilizer_application",
            field.soil.data.rain_events_after_fertilizer_application,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [
                        ("Fertilizer", "do_fertilizer_phosphorus_operations"),
                        ("Fertilizer", "add_fertilizer_phosphorus"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "machine_manure_dry_mass",
            field.soil.data.machine_manure.manure_dry_mass,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_machine_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "machine_manure_applied_mass",
            field.soil.data.machine_manure.manure_applied_mass,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_machine_manure"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "machine_manure_field_coverage",
            field.soil.data.machine_manure.manure_field_coverage,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [
                        ("ManureApplication", "apply_machine_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "machine_manure_moisture_factor",
            field.soil.data.machine_manure.manure_moisture_factor,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [
                        ("ManureApplication", "apply_machine_manure"),
                        ("ManurePool", "adjust_manure_moisture_factor"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "machine_water_extractable_inorganic_phosphorus",
            field.soil.data.machine_manure.water_extractable_inorganic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_machine_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("ManurePool", "leach_phosphorus_pools"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "machine_water_extractable_organic_phosphorus",
            field.soil.data.machine_manure.water_extractable_organic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_machine_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("ManurePool", "leach_phosphorus_pools"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "machine_stable_inorganic_phosphorus",
            field.soil.data.machine_manure.stable_inorganic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_machine_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "machine_stable_organic_phosphorus",
            field.soil.data.machine_manure.stable_organic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_machine_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "machine_organic_phosphorus_runoff",
            field.soil.data.machine_manure.organic_phosphorus_runoff,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManurePool", "runoff_reset"),
                        ("ManurePool", "leach_phosphorus_pools"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "machine_inorganic_phosphorus_runoff",
            field.soil.data.machine_manure.inorganic_phosphorus_runoff,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManurePool", "runoff_reset"),
                        ("ManurePool", "leach_phosphorus_pools"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "grazing_manure_dry_mass",
            field.soil.data.grazing_manure.manure_dry_mass,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_grazing_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "grazing_manure_applied_mass",
            field.soil.data.grazing_manure.manure_applied_mass,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_grazing_manure"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "grazing_manure_field_coverage",
            field.soil.data.grazing_manure.manure_field_coverage,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [
                        ("ManureApplication", "apply_grazing_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "grazing_manure_moisture_factor",
            field.soil.data.grazing_manure.manure_moisture_factor,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.UNITLESS,
                    "data_origin": [
                        ("ManureApplication", "apply_grazing_manure"),
                        ("ManurePool", "adjust_manure_moisture_factor"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "grazing_water_extractable_inorganic_phosphorus",
            field.soil.data.grazing_manure.water_extractable_inorganic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_grazing_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("ManurePool", "leach_phosphorus_pools"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "grazing_water_extractable_organic_phosphorus",
            field.soil.data.grazing_manure.water_extractable_organic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_grazing_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("ManurePool", "leach_phosphorus_pools"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "grazing_stable_inorganic_phosphorus",
            field.soil.data.grazing_manure.stable_inorganic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_grazing_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "grazing_stable_organic_phosphorus",
            field.soil.data.grazing_manure.stable_organic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManureApplication", "apply_grazing_manure"),
                        ("ManurePool", "daily_manure_update"),
                        ("TillageApplication", "_remove_amount_incorporated"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "grazing_organic_phosphorus_runoff",
            field.soil.data.grazing_manure.organic_phosphorus_runoff,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManurePool", "runoff_reset"),
                        ("ManurePool", "leach_phosphorus_pools"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "grazing_inorganic_phosphorus_runoff",
            field.soil.data.grazing_manure.inorganic_phosphorus_runoff,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManurePool", "runoff_reset"),
                        ("ManurePool", "leach_phosphorus_pools"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "soil_phosphorus_runoff",
            field.soil.data.soil_phosphorus_runoff,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("SolublePhosphorus", "daily_update_routine")],
                },
            ),
        )
        self.om.add_variable(
            "nitrate_runoff",
            field.soil.data.nitrate_runoff,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("LeachingRunoffErosion", "_erode_nitrogen")],
                },
            ),
        )
        self.om.add_variable(
            "ammonium_runoff",
            field.soil.data.ammonium_runoff,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("LeachingRunoffErosion", "_erode_nitrogen")],
                },
            ),
        )
        self.om.add_variable(
            "eroded_fresh_organic_nitrogen",
            field.soil.data.eroded_fresh_organic_nitrogen,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("LeachingRunoffErosion", "_erode_nitrogen")],
                },
            ),
        )
        self.om.add_variable(
            "eroded_stable_organic_nitrogen",
            field.soil.data.eroded_stable_organic_nitrogen,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("LeachingRunoffErosion", "_erode_nitrogen")],
                },
            ),
        )
        self.om.add_variable(
            "eroded_active_organic_nitrogen",
            field.soil.data.eroded_active_organic_nitrogen,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("LeachingRunoffErosion", "_erode_nitrogen")],
                },
            ),
        )

        self.om.add_variable(
            "profile_carbon_total",
            field.soil.data.profile_carbon_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("SoilData", "profile_carbon_total")],
                },
            ),
        )
        self.om.add_variable(
            "profile_carbon_emissions",
            field.soil.data.profile_carbon_emissions,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("SoilData", "profile_carbon_emissions")],
                },
            ),
        )
        self.om.add_variable(
            "profile_nitrates_total",
            field.soil.data.profile_nitrates_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("SoilData", "profile_nitrates_total")],
                },
            ),
        )
        self.om.add_variable(
            "profile_ammonium_total",
            field.soil.data.profile_ammonium_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("SoilData", "profile_ammonium_total")],
                },
            ),
        )
        self.om.add_variable(
            "profile_active_organic_nitrogen_total",
            field.soil.data.profile_active_organic_nitrogen_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("SoilData", "profile_active_organic_nitrogen_total")],
                },
            ),
        )
        self.om.add_variable(
            "profile_stable_organic_nitrogen_total",
            field.soil.data.profile_stable_organic_nitrogen_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("SoilData", "profile_stable_organic_nitrogen_total")],
                },
            ),
        )
        self.om.add_variable(
            "profile_fresh_organic_nitrogen_total",
            field.soil.data.profile_fresh_organic_nitrogen_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("SoilData", "profile_fresh_organic_nitrogen_total")],
                },
            ),
        )

    def send_field_daily_variables(self, field: Field, time: RufasTime) -> None:
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
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_HECTARE, "data_origin": [("FieldData", "")]}),
        )
        self.om.add_variable(
            "transpiration",
            field.field_data.transpiration,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("FieldData", "")]}),
        )
        self.om.add_variable(
            "max_transpiration",
            field.field_data.max_transpiration,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("FieldData", "")]}),
        )
        self.om.add_variable(
            "max_evapotranspiration",
            field.field_data.max_evapotranspiration,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS, "data_origin": [("Field", "_cycle_water")]}),
        )
        # confirm unit
        self.om.add_variable(
            "days_into_watering_interval",
            field.field_data.days_into_watering_interval,
            dict(
                info_map, **{"units": MeasurementUnits.DAYS, "data_origin": [("Field", "_determine_watering_amount")]}
            ),
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
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("LayerData", "do_annual_reset"), ("Denitrification", "denitrify")],
                },
            ),
        )
        self.om.add_variable(
            "annual_ammonia_emissions_total",
            layer.annual_ammonia_emissions_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("NitrificationVolatilization", "do_daily_nitrification_and_volatilization")],
                },
            ),
        )
        self.om.add_variable(
            "annual_decomposition_carbon_CO2_lost",
            layer.annual_decomposition_carbon_CO2_lost,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("LayerData", "do_annual_reset"), ("CarbonCycling", "_soil_carbon_aggregation")],
                },
            ),
        )
        self.om.add_variable(
            "annual_carbon_CO2_lost",
            layer.annual_carbon_CO2_lost,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("LayerData", "do_annual_reset"), ("CarbonCycling", "_soil_carbon_aggregation")],
                },
            ),
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
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [
                        ("FieldData", "perform_annual_field_reset"),
                        ("Field", "_determine_watering_amount"),
                    ],
                },
            ),
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
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [("FieldDataReporter", "send_soil_annual_variables")],
                },
            ),
        )

        nitrates_content_change = field.soil.data.profile_nitrates_total - field.soil.data.initial_nitrates_total
        self.om.add_variable(
            "annual_nitrates_content_change",
            nitrates_content_change,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [("FieldDataReporter", "send_soil_annual_variables")],
                },
            ),
        )

        self.om.add_variable(
            "annual_soil_evaporation_total",
            field.soil.data.annual_soil_evaporation_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS,
                    "data_origin": [("Evaporation", "evaporate"), ("SoilData", "do_annual_reset")],
                },
            ),
        )
        self.om.add_variable(
            "annual_eroded_sediment_total",
            field.soil.data.annual_eroded_sediment_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.METRIC_TONS,
                    "data_origin": [("SoilData", "do_annual_reset"), ("SoilErosion", "erode")],
                },
            ),
        )
        self.om.add_variable(
            "annual_surface_runoff_total",
            field.soil.data.annual_surface_runoff_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.MILLIMETERS_PER_HECTARE,
                    "data_origin": [("SoilData", "do_annual_reset"), ("SoilErosion", "erode")],
                },
            ),
        )
        self.om.add_variable(
            "annual_runoff_fertilizer_phosphorus",
            field.soil.data.annual_runoff_fertilizer_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("SoilData", "do_annual_reset"),
                        ("Fertilizer", "_update_after_first_rain"),
                        ("Fertilizer", "_update_before_and_at_first_rain"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_runoff_machine_manure_inorganic_phosphorus",
            field.soil.data.machine_manure.annual_runoff_manure_inorganic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManurePool", "leach_phosphorus_pools"),
                        ("SoilData", "do_annual_reset"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_machine_decomposed_manure",
            field.soil.data.machine_manure.annual_decomposed_manure,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManurePool", "daily_manure_update"),
                        ("SoilData", "do_annual_reset"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_runoff_machine_manure_organic_phosphorus",
            field.soil.data.machine_manure.annual_runoff_manure_organic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManurePool", "leach_phosphorus_pools"),
                        ("SoilData", "do_annual_reset"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_runoff_grazing_manure_inorganic_phosphorus",
            field.soil.data.grazing_manure.annual_runoff_manure_inorganic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManurePool", "leach_phosphorus_pools"),
                        ("SoilData", "do_annual_reset"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_runoff_grazing_manure_organic_phosphorus",
            field.soil.data.grazing_manure.annual_runoff_manure_organic_phosphorus,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManurePool", "leach_phosphorus_pools"),
                        ("SoilData", "do_annual_reset"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_grazing_decomposed_manure",
            field.soil.data.grazing_manure.annual_decomposed_manure,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("ManurePool", "daily_manure_update"),
                        ("SoilData", "do_annual_reset"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_soil_phosphorus_runoff",
            field.soil.data.annual_soil_phosphorus_runoff,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                    "data_origin": [
                        ("SolublePhosphorus", "daily_update_routine"),
                        ("SoilData", "do_annual_reset"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_runoff_nitrates_total",
            field.soil.data.annual_runoff_nitrates_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("SoilData", "do_annual_reset"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_runoff_ammonium_total",
            field.soil.data.annual_runoff_ammonium_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("SoilData", "do_annual_reset"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_eroded_fresh_organic_nitrogen_total",
            field.soil.data.annual_eroded_fresh_organic_nitrogen_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("SoilData", "do_annual_reset"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_eroded_stable_organic_nitrogen_total",
            field.soil.data.annual_eroded_stable_organic_nitrogen_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("SoilData", "do_annual_reset"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                    ],
                },
            ),
        )
        self.om.add_variable(
            "annual_eroded_active_organic_nitrogen_total",
            field.soil.data.annual_eroded_active_organic_nitrogen_total,
            dict(
                info_map,
                **{
                    "units": MeasurementUnits.KILOGRAMS,
                    "data_origin": [
                        ("SoilData", "do_annual_reset"),
                        ("LeachingRunoffErosion", "_erode_nitrogen"),
                    ],
                },
            ),
        )
