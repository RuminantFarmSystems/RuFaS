from typing import List

from RUFAS.output_manager import OutputManager
from RUFAS.routines.field.field.field import Field

om = OutputManager()


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
        self.fields = fields

    def send_daily_variables(self) -> None:
        """sends daily variables to the output manager"""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_daily_variables.__name__,
        }
        for field in self.fields:
            info_map["suffix"] = "field='" + field.field_data.name + "'"
            # --------------------------adding field data
            om.add_variable(
                "current_residue",
                field.field_data.current_residue,
                dict(info_map, **{"data_origin": [("Field", "_cycle_water")], "units": "kg/ha"}),
            )
            om.add_variable(
                "transpiration", field.field_data.transpiration, dict(info_map, **{"data_origin": [("FieldData", "")],
                                                                                   "units": "mm"})
            )
            om.add_variable(
                "max_transpiration",
                field.field_data.max_transpiration,
                dict(info_map, **{"data_origin": [("FieldData", "")], "units": "mm"}),
            )
            om.add_variable(
                "max_evapotranspiration",
                field.field_data.max_evapotranspiration,
                dict(info_map, **{"data_origin": [("Field", "_cycle_water")], "units": "mm"}),
            )
            # confirm unit
            om.add_variable(
                "days_into_watering_interval",
                field.field_data.days_into_watering_interval,
                dict(info_map, **{"data_origin": [("Field", "_determine_watering_amount")], "units": "days"}),
            )

            # ----------------------------adding soil data
            om.add_variable(
                "water_evaporated",
                field.soil.data.water_evaporated,
                dict(info_map, **{"data_origin": [("Evaporation", "evaporate")], "units": "mm"}),
            )
            om.add_variable(
                "eroded_sediment",
                field.soil.data.eroded_sediment,
                dict(info_map, **{"data_origin": [("SoilErosion", "erode")], "units": "metric tons"}),
            )
            om.add_variable(
                "accumulated_runoff",
                field.soil.data.accumulated_runoff,
                dict(info_map, **{"data_origin": [("Infiltration", "infiltrate")], "units": "mm"}),
            )
            om.add_variable(
                "infiltrated_water",
                field.soil.data.infiltrated_water,
                dict(info_map, **{"data_origin": [("Infiltration", "infiltrate")], "units": "mm"}),
            )
            om.add_variable(
                "snow_content",
                field.soil.data.snow_content,
                dict(info_map, **{"data_origin": [("Snow", "update_snow"), ("Snow", "sublimate")], "units": "mm"}),
            )
            om.add_variable(
                "snow_melt",
                field.soil.data.snow_melt_amount,
                dict(info_map, **{"data_origin": [("Snow", "update_snow")], "units": "mm"}),
            )
            om.add_variable(
                "current_day_snow_temperature",
                field.soil.data.current_day_snow_temperature,
                dict(info_map, **{"data_origin": [("Snow", "update_snow")], "units": "ºC"}),
            )
            om.add_variable(
                "water_sublimated",
                field.soil.data.water_sublimated,
                dict(info_map, **{"data_origin": [("Snow", "sublimate")], "units": "mm"}),
            )
            om.add_variable(
                "cover_type", field.soil.data.cover_type, dict(info_map, **{"data_origin": [("SoilData", "")],
                                                                            "units": "unitless"})
            )
            om.add_variable(
                "full_available_phosphorus_pool",
                field.soil.data.full_available_phosphorus_pool,
                dict(info_map, **{"data_origin": [("Fertilizer", "add_fertilizer_phosphorus")], "units": "kg"}),
            )
            om.add_variable(
                "available_phosphorus_pool",
                field.soil.data.available_phosphorus_pool,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Fertilizer", "_update_before_and_at_first_rain"),
                            ("Fertilizer", "add_fertilizer_phosphorus"),
                            ("Fertilizer", "_absorb_phosphorus_from_available_pool"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "recalcitrant_phosphorus_pool",
                field.soil.data.recalcitrant_phosphorus_pool,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Fertilizer", "_update_after_first_rain"),
                            ("Fertilizer", "add_fertilizer_phosphorus"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "runoff_fertilizer_phosphorus",
                field.soil.data.runoff_fertilizer_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Fertilizer", "do_fertilizer_phosphorus_operations"),
                            ("Fertilizer", "_update_before_and_at_first_rain"),
                            ("Fertilizer", "_update_after_first_rain"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            # confirm unit
            om.add_variable(
                "days_since_application",
                field.soil.data.days_since_application,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Fertilizer", "do_fertilizer_phosphorus_operations"),
                            ("Fertilizer", "add_fertilizer_phosphorus"),
                        ],
                        "units": "days"
                    },
                ),
            )
            # confirm unit
            om.add_variable(
                "rain_events_after_fertilizer_application",
                field.soil.data.rain_events_after_fertilizer_application,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Fertilizer", "do_fertilizer_phosphorus_operations"),
                            ("Fertilizer", "add_fertilizer_phosphorus"),
                        ],
                        "units": "unitless"
                    },
                ),
            )
            om.add_variable(
                "machine_manure_dry_mass",
                field.soil.data.machine_manure_dry_mass,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "_apply_solid_machine_manure"),
                            ("ManureApplication", "_apply_liquid_machine_manure"),
                            ("Manure", "daily_manure_update"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "machine_manure_applied_mass",
                field.soil.data.machine_manure_applied_mass,
                dict(info_map, **{"data_origin": [("ManureApplication", "apply_machine_manure")], "units": "kg"}),
            )
            om.add_variable(
                "machine_manure_field_coverage",
                field.soil.data.machine_manure_field_coverage,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "_apply_solid_machine_manure"),
                            ("ManureApplication", "_apply_liquid_machine_manure"),
                            ("Manure", "daily_manure_update"),
                        ],
                        "units": "unitless"
                    },
                ),
            )
            om.add_variable(
                "machine_manure_moisture_factor",
                field.soil.data.machine_manure_moisture_factor,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "_apply_solid_machine_manure"),
                            ("ManureApplication", "_apply_liquid_machine_manure"),
                            ("Manure", "_adjust_manure_moisture_factor"),
                        ],
                        "units": "unitless"
                    },
                ),
            )
            om.add_variable(
                "machine_water_extractable_inorganic_phosphorus",
                field.soil.data.machine_water_extractable_inorganic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "_apply_solid_machine_manure"),
                            ("ManureApplication", "_apply_liquid_machine_manure"),
                            ("Manure", "daily_manure_update"),
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "machine_water_extractable_organic_phosphorus",
                field.soil.data.machine_water_extractable_organic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "_apply_solid_machine_manure"),
                            ("ManureApplication", "_apply_liquid_machine_manure"),
                            ("Manure", "daily_manure_update"),
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "machine_stable_inorganic_phosphorus",
                field.soil.data.machine_stable_inorganic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "_apply_solid_machine_manure"),
                            ("ManureApplication", "_apply_liquid_machine_manure"),
                            ("Manure", "daily_manure_update"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "machine_stable_organic_phosphorus",
                field.soil.data.machine_stable_organic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "_apply_solid_machine_manure"),
                            ("ManureApplication", "_apply_liquid_machine_manure"),
                            ("Manure", "daily_manure_update"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "machine_organic_phosphorus_runoff",
                field.soil.data.machine_organic_phosphorus_runoff,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Manure", "daily_manure_update"),
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "machine_inorganic_phosphorus_runoff",
                field.soil.data.machine_inorganic_phosphorus_runoff,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Manure", "daily_manure_update"),
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "grazing_manure_dry_mass",
                field.soil.data.grazing_manure_dry_mass,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "apply_grazing_manure"),
                            ("Manure", "daily_manure_update"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "grazing_manure_applied_mass",
                field.soil.data.grazing_manure_applied_mass,
                dict(info_map, **{"data_origin": [("ManureApplication", "apply_grazing_manure")], "units": "kg"}),
            )
            om.add_variable(
                "grazing_manure_field_coverage",
                field.soil.data.grazing_manure_field_coverage,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "apply_grazing_manure"),
                            ("Manure", "daily_manure_update"),
                        ],
                        "units": "unitless"
                    },
                ),
            )
            om.add_variable(
                "grazing_manure_moisture_factor",
                field.soil.data.grazing_manure_moisture_factor,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "apply_grazing_manure"),
                            ("Manure", "_adjust_manure_moisture_factor"),
                        ],
                        "units": "unitless"
                    },
                ),
            )
            om.add_variable(
                "grazing_water_extractable_inorganic_phosphorus",
                field.soil.data.grazing_water_extractable_inorganic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "apply_grazing_manure"),
                            ("Manure", "daily_manure_update"),
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "grazing_water_extractable_organic_phosphorus",
                field.soil.data.grazing_water_extractable_organic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "apply_grazing_manure"),
                            ("Manure", "daily_manure_update"),
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "grazing_stable_inorganic_phosphorus",
                field.soil.data.grazing_stable_inorganic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "apply_grazing_manure"),
                            ("Manure", "daily_manure_update"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "grazing_stable_organic_phosphorus",
                field.soil.data.grazing_stable_organic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("ManureApplication", "apply_grazing_manure"),
                            ("Manure", "daily_manure_update"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "grazing_organic_phosphorus_runoff",
                field.soil.data.grazing_organic_phosphorus_runoff,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Manure", "daily_manure_update"),
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "grazing_inorganic_phosphorus_runoff",
                field.soil.data.grazing_inorganic_phosphorus_runoff,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Manure", "daily_manure_update"),
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "soil_phosphorus_runoff",
                field.soil.data.soil_phosphorus_runoff,
                dict(info_map, **{"data_origin": [("SolublePhosphorus", "daily_update_routine")], "units": "kg/ha"}),
            )
            om.add_variable(
                "nitrate_runoff",
                field.soil.data.nitrate_runoff,
                dict(info_map, **{"data_origin": [("LeachingRunoffErosion", "_erode_nitrogen")], "units": "kg/ha"}),
            )
            om.add_variable(
                "ammonium_runoff",
                field.soil.data.ammonium_runoff,
                dict(info_map, **{"data_origin": [("LeachingRunoffErosion", "_erode_nitrogen")], "units": "kg/ha"}),
            )
            om.add_variable(
                "eroded_fresh_organic_nitrogen",
                field.soil.data.eroded_fresh_organic_nitrogen,
                dict(info_map, **{"data_origin": [("LeachingRunoffErosion", "_erode_nitrogen")], "units": "kg/ha"}),
            )
            om.add_variable(
                "eroded_stable_organic_nitrogen",
                field.soil.data.eroded_stable_organic_nitrogen,
                dict(info_map, **{"data_origin": [("LeachingRunoffErosion", "_erode_nitrogen")], "units": "kg/ha"}),
            )
            om.add_variable(
                "eroded_active_organic_nitrogen",
                field.soil.data.eroded_active_organic_nitrogen,
                dict(info_map, **{"data_origin": [("LeachingRunoffErosion", "_erode_nitrogen")], "units": "kg/ha"}),
            )

            om.add_variable(
                "profile_carbon_total",
                field.soil.data.profile_carbon_total,
                dict(info_map, **{"data_origin": [("SoilData", "profile_carbon_total")], "units": "kg/ha"}),
            )
            om.add_variable(
                "profile_carbon_emissions",
                field.soil.data.profile_carbon_emissions,
                dict(info_map, **{"data_origin": [("SoilData", "profile_carbon_emissions")], "units": "kg/ha"}),
            )
            om.add_variable(
                "profile_nitrates_total",
                field.soil.data.profile_nitrates_total,
                dict(info_map, **{"data_origin": [("SoilData", "profile_nitrates_total")], "units": "kg/ha"}),
            )
            om.add_variable(
                "profile_ammonium_total",
                field.soil.data.profile_ammonium_total,
                dict(info_map, **{"data_origin": [("SoilData", "profile_ammonium_total")], "units": "kg/ha"}),
            )
            om.add_variable(
                "profile_active_organic_nitrogen_total",
                field.soil.data.profile_active_organic_nitrogen_total,
                dict(info_map, **{"data_origin": [("SoilData", "profile_active_organic_nitrogen_total")],
                                  "units": "kg/ha"}),
            )
            om.add_variable(
                "profile_stable_organic_nitrogen_total",
                field.soil.data.profile_stable_organic_nitrogen_total,
                dict(info_map, **{"data_origin": [("SoilData", "profile_stable_organic_nitrogen_total")],
                                  "units": "kg/ha"}),
            )
            om.add_variable(
                "profile_fresh_organic_nitrogen_total",
                field.soil.data.profile_fresh_organic_nitrogen_total,
                dict(info_map, **{"data_origin": [("SoilData", "profile_fresh_organic_nitrogen_total")],
                                  "units": "kg/ha"}),
            )

            # Adding vadose zone layer data
            info_map["suffix"] = "field='" + field.field_data.name + "',vadose_zone_layer"
            om.add_variable(
                "active_organic_nitrogen_content",
                field.soil.data.vadose_zone_layer.active_organic_nitrogen_content,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("LayerData", "_initialize_nitrogen_pools"),
                            ("CropManagement", "_distribute_residue_nutrients"),
                            ("FertilizerApplication", "apply_fertilizer"),
                            ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                            ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                            ("HumusMineralization", "mineralize_organic_nitrogen"),
                            ("LeachingRunoffErosion", "_erode_nitrogen"),
                            ("LeachingRunoffErosion", "_leach_nitrogen"),
                            ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                            ("MineralizationDecomposition", "_correct_fresh_organic_nitrogen_pools"),
                            ("SoilData", "__post_init__"),
                        ],
                        "units": "kg/ha"
                    },
                ),
            )
            om.add_variable(
                "stable_organic_nitrogen_content",
                field.soil.data.vadose_zone_layer.stable_organic_nitrogen_content,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("LayerData", "_initialize_nitrogen_pools"),
                            ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                            ("HumusMineralization", "mineralize_organic_nitrogen"),
                            ("LeachingRunoffErosion", "_erode_nitrogen"),
                            ("SoilData", "__post_init__"),
                        ],
                        "units": "kg/ha"
                    },
                ),
            )
            om.add_variable(
                "nitrate_content",
                field.soil.data.vadose_zone_layer.nitrate_content,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("LayerData", "_initialize_nitrogen_pools"),
                            ("FertilizerApplication", "apply_fertilizer"),
                            ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                            ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                            ("Denitrification", "denitrify"),
                            ("LeachingRunoffErosion", "_erode_nitrogen"),
                            ("LeachingRunoffErosion", "_leach_nitrogen"),
                            ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                            ("NitrificationVolatilization", "do_daily_nitrification_and_volatilization"),
                        ],
                        "units": "kg/ha"
                    },
                ),
            )
            om.add_variable(
                "fresh_organic_nitrogen_content",
                field.soil.data.vadose_zone_layer.fresh_organic_nitrogen_content,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("LayerData", "_initialize_nitrogen_pools"),
                            ("CropManagement", "_transfer_residue"),
                            ("CropManagement", "_distribute_residue_nutrients"),
                            ("FertilizerApplication", "apply_fertilizer"),
                            ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                            ("LeachingRunoffErosion", "_erode_nitrogen"),
                            ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                            ("MineralizationDecomposition", "_correct_fresh_organic_nitrogen_pools"),
                        ],
                        "units": "kg/ha"
                    },
                ),
            )
            om.add_variable(
                "water_content",
                field.soil.data.vadose_zone_layer.water_content,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Evaporation", "evaporate"),
                            ("LayerData", "__post_init__"),
                            ("Percolation", "percolate"),
                            ("Percolation", "_percolate_excess_water"),
                        ],
                        "units": "mm"
                    },
                ),
            )
            om.add_variable(
                "labile_inorganic_phosphorus_content",
                field.soil.data.vadose_zone_layer.labile_inorganic_phosphorus_content,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("CropManagement", "_transfer_residue"),
                            ("CropManagement", "_distribute_residue_nutrients"),
                            ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                            ("LayerData", "__post_init__"),
                            ("LayerData", "add_to_labile_phosphorus"),
                            ("PhosphorusMineralization", "mineralize_phosphorus"),
                            ("SolublePhosphorus", "daily_update_routine"),
                        ],
                        "units": "kg/ha"
                    },
                ),
            )
            om.add_variable(
                "active_inorganic_phosphorus_content",
                field.soil.data.vadose_zone_layer.active_inorganic_phosphorus_content,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("LayerData", "__post_init__"),
                            ("LayerData", "add_to_labile_phosphorus"),
                            ("PhosphorusMineralization", "mineralize_phosphorus"),
                        ],
                        "units": "kg/ha"
                    },
                ),
            )
            om.add_variable(
                "stable_inorganic_phosphorus_content",
                field.soil.data.vadose_zone_layer.stable_inorganic_phosphorus_content,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("LayerData", "__post_init__"),
                            ("PhosphorusMineralization", "mineralize_phosphorus"),
                        ],
                        "units": "kg/ha"
                    },
                ),
            )
            om.add_variable(
                "fresh_organic_phosphorus_content",
                field.soil.data.vadose_zone_layer.fresh_organic_phosphorus_content,
                dict(info_map, **{"data_origin": [("LayerData", "")], "units": "kg/ha"}),
            )

            # ----------------------------adding layer data
            for index, layer in enumerate(field.soil.data.soil_layers):
                info_map["suffix"] = "field='" + field.field_data.name + "',layer='" + str(index) + "'"

                om.add_variable(
                    "temperature",
                    layer.temperature,
                    dict(info_map, **{"data_origin": [("SoilTemp", "daily_soil_temperature_update")], "units": "ºC"}),
                )
                om.add_variable(
                    "percolated_water",
                    layer.percolated_water,
                    dict(
                        info_map,
                        **{"data_origin": [("Percolation", "percolate"), ("Percolation", "_percolate_excess_water")],
                           "units": "mm"},
                    ),
                )
                om.add_variable(
                    "water_content",
                    layer.water_content,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("Evaporation", "evaporate"),
                                ("LayerData", "__post_init__"),
                                ("Percolation", "percolate"),
                                ("Percolation", "_percolate_excess_water"),
                            ],
                            "units": "mm"
                        },
                    ),
                )
                om.add_variable(
                    "water_factor",
                    layer.water_factor,
                    dict(info_map, **{"data_origin": [("LayerData", "water_factor")], "units": "unitless"}),
                )
                om.add_variable(
                    "evaporated_water_content",
                    layer.evaporated_water_content,
                    dict(info_map, **{"data_origin": [("Evaporation", "evaporate")], "units": "mm"}),
                )
                om.add_variable(
                    "plant_metabolic_active_carbon_usage",
                    layer.plant_metabolic_active_carbon_usage,
                    dict(info_map, **{"data_origin": [("ResiduePartition", "partition_residue")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "plant_metabolic_active_carbon_loss",
                    layer.plant_metabolic_active_carbon_loss,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "plant_metabolic_active_carbon_remaining",
                    layer.plant_metabolic_active_carbon_remaining,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "plant_structural_active_carbon_usage",
                    layer.plant_structural_active_carbon_usage,
                    dict(info_map, **{"data_origin": [("ResiduePartition", "partition_residue")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "metabolic_litter_amount",
                    layer.metabolic_litter_amount,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("ResiduePartition", "partition_residue"),
                                ("ResiduePartition", "_add_litter_to_pools"),
                                ("ResiduePartition", "_add_subsurface_residue"),
                                ("LayerData", "_initialize_carbon_pools"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "structural_litter_amount",
                    layer.structural_litter_amount,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("ResiduePartition", "partition_residue"),
                                ("ResiduePartition", "_add_litter_to_pools"),
                                ("ResiduePartition", "_add_subsurface_residue"),
                                ("LayerData", "_initialize_carbon_pools"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "plant_structural_active_carbon_remaining",
                    layer.plant_structural_active_carbon_remaining,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "plant_structural_slow_carbon_usage",
                    layer.plant_structural_slow_carbon_usage,
                    dict(info_map, **{"data_origin": [("ResiduePartition", "partition_residue")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "plant_structural_slow_carbon_loss",
                    layer.plant_structural_slow_carbon_loss,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "plant_structural_slow_carbon_remaining",
                    layer.plant_structural_slow_carbon_remaining,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_metabolic_active_carbon_usage",
                    layer.soil_metabolic_active_carbon_usage,
                    dict(info_map, **{"data_origin": [("ResiduePartition", "partition_residue")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_metabolic_active_carbon_loss",
                    layer.soil_metabolic_active_carbon_loss,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_metabolic_active_carbon_remaining",
                    layer.soil_metabolic_active_carbon_remaining,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_structural_active_carbon_usage",
                    layer.soil_structural_active_carbon_usage,
                    dict(info_map, **{"data_origin": [("ResiduePartition", "partition_residue")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_structural_active_carbon_loss",
                    layer.soil_structural_active_carbon_loss,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_structural_active_carbon_remaining",
                    layer.soil_structural_active_carbon_remaining,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_structural_slow_carbon_usage",
                    layer.soil_structural_slow_carbon_usage,
                    dict(info_map, **{"data_origin": [("ResiduePartition", "partition_residue")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_structural_slow_carbon_loss",
                    layer.soil_structural_slow_carbon_loss,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_structural_slow_carbon_remaining",
                    layer.soil_structural_slow_carbon_remaining,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "active_carbon_decomposition_amount",
                    layer.active_carbon_decomposition_amount,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "active_carbon_amount",
                    layer.active_carbon_amount,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("PoolGasPartition", "partition_pool_gas"),
                                ("LayerData", "_initialize_carbon_pools"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "slow_carbon_amount",
                    layer.slow_carbon_amount,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("PoolGasPartition", "partition_pool_gas"),
                                ("LayerData", "_initialize_carbon_pools"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "passive_carbon_amount",
                    layer.passive_carbon_amount,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("PoolGasPartition", "partition_pool_gas"),
                                ("LayerData", "_initialize_carbon_pools"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "slow_carbon_decomposition_amount",
                    layer.slow_carbon_decomposition_amount,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "passive_carbon_decomposition_amount",
                    layer.passive_carbon_decomposition_amount,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "active_carbon_to_slow_amount",
                    layer.active_carbon_to_slow_amount,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "active_carbon_to_slow_loss",
                    layer.active_carbon_to_slow_loss,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "active_carbon_to_passive_amount",
                    layer.active_carbon_to_passive_amount,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "slow_to_active_carbon_amount",
                    layer.slow_to_active_carbon_amount,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "slow_carbon_co2_lost_amount",
                    layer.slow_carbon_co2_lost_amount,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "passive_to_active_carbon_amount",
                    layer.passive_to_active_carbon_amount,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "passive_carbon_co2_lost_amount",
                    layer.passive_carbon_co2_lost_amount,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "plant_active_decompose_carbon",
                    layer.plant_active_decompose_carbon,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_active_decompose_carbon",
                    layer.soil_active_decompose_carbon,
                    dict(info_map, **{"data_origin": [("PoolGasPartition", "partition_pool_gas")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "soil_overall_carbon_fraction",
                    layer.soil_overall_carbon_fraction,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("CarbonCycling", "_soil_carbon_aggregation"),
                            ],
                            "units": "unitless"
                        },
                    ),
                )
                om.add_variable(
                    "total_soil_carbon_amount",
                    layer.total_soil_carbon_amount,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("CarbonCycling", "_soil_carbon_aggregation"),
                                ("LayerData", "_initialize_carbon_pools"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "mean_phosphorus_sorption_parameter",
                    layer.mean_phosphorus_sorption_parameter,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("LayerData", "__post_init__"),
                                ("PhosphorusMineralization", "mineralize_phosphorus"),
                            ],
                            "units": "unitless"
                        },
                    ),
                )
                om.add_variable(
                    "labile_inorganic_phosphorus_content",
                    layer.labile_inorganic_phosphorus_content,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("CropManagement", "_transfer_residue"),
                                ("CropManagement", "_distribute_residue_nutrients"),
                                ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                                ("LayerData", "__post_init__"),
                                ("LayerData", "add_to_labile_phosphorus"),
                                ("PhosphorusMineralization", "mineralize_phosphorus"),
                                ("SolublePhosphorus", "daily_update_routine"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "active_inorganic_phosphorus_content",
                    layer.active_inorganic_phosphorus_content,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("LayerData", "__post_init__"),
                                ("LayerData", "add_to_active_phosphorus"),
                                ("PhosphorusMineralization", "mineralize_phosphorus"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "stable_inorganic_phosphorus_content",
                    layer.stable_inorganic_phosphorus_content,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("LayerData", "__post_init__"),
                                ("PhosphorusMineralization", "mineralize_phosphorus"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "fresh_organic_phosphorus_content",
                    layer.fresh_organic_phosphorus_content,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("LayerData", ""),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "active_inorganic_unbalanced_counter",
                    layer.active_inorganic_unbalanced_counter,
                    dict(info_map, **{"data_origin": [("PhosphorusMineralization", "mineralize_phosphorus")],
                                      "units": "days"}),
                )
                om.add_variable(
                    "labile_inorganic_unbalanced_counter",
                    layer.labile_inorganic_unbalanced_counter,
                    dict(info_map, **{"data_origin": [("PhosphorusMineralization", "mineralize_phosphorus")],
                                      "units": "days"}),
                )
                om.add_variable(
                    "percolated_phosphorus",
                    layer.percolated_phosphorus,
                    dict(info_map, **{"data_origin": [("SolublePhosphorus", "daily_update_routine")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "nitrate_content",
                    layer.nitrate_content,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("FertilizerApplication", "apply_fertilizer"),
                                ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                                ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                                ("LayerData", "_initialize_nitrogen_pools"),
                                ("Denitrification", "denitrify"),
                                ("LeachingRunoffErosion", "_erode_nitrogen"),
                                ("LeachingRunoffErosion", "_leach_nitrogen"),
                                ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                                ("NitrificationVolatilization", "do_daily_nitrification_and_volatilization"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "ammonium_content",
                    layer.ammonium_content,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("FertilizerApplication", "apply_fertilizer"),
                                ("ManureApplication", "_apply_subsurface_fertilizer"),
                                ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                                ("LayerData", "_initialize_nitrogen_pools"),
                                ("HumusMineralization", "mineralize_organic_nitrogen"),
                                ("LeachingRunoffErosion", "_erode_nitrogen"),
                                ("LeachingRunoffErosion", "_leach_nitrogen"),
                                ("NitrificationVolatilization", "do_daily_nitrification_and_volatilization"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "active_organic_nitrogen_content",
                    layer.active_organic_nitrogen_content,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("CropManagement", "_distribute_residue_nutrients"),
                                ("FertilizerApplication", "apply_fertilizer"),
                                ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                                ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                                ("LayerData", "_initialize_nitrogen_pools"),
                                ("HumusMineralization", "mineralize_organic_nitrogen"),
                                ("LeachingRunoffErosion", "_erode_nitrogen"),
                                ("LeachingRunoffErosion", "_leach_nitrogen"),
                                ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                                ("MineralizationDecomposition", "_correct_fresh_organic_nitrogen_pools"),
                                ("SoilData", "__post_init__"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "stable_organic_nitrogen_content",
                    layer.stable_organic_nitrogen_content,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("ManureApplication", "_add_nitrogen_to_soil_layer"),
                                ("LayerData", "_initialize_nitrogen_pools"),
                                ("HumusMineralization", "mineralize_organic_nitrogen"),
                                ("LeachingRunoffErosion", "_erode_nitrogen"),
                                ("SoilData", "__post_init__"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "fresh_organic_nitrogen_content",
                    layer.fresh_organic_nitrogen_content,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("CropManagement", "_transfer_residue"),
                                ("CropManagement", "_distribute_residue_nutrients"),
                                ("FertilizerApplication", "apply_fertilizer"),
                                ("FertilizerApplication", "_apply_subsurface_fertilizer"),
                                ("LayerData", "_initialize_nitrogen_pools"),
                                ("LeachingRunoffErosion", "_erode_nitrogen"),
                                ("MineralizationDecomposition", "mineralize_and_decompose_nitrogen"),
                                ("MineralizationDecomposition", "_correct_fresh_organic_nitrogen_pools"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "nitrous_oxide_emissions",
                    layer.nitrous_oxide_emissions,
                    dict(info_map, **{"data_origin": [("Denitrification", "denitrify")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "ammonia_emissions",
                    layer.ammonia_emissions,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("NitrificationVolatilization", "do_daily_nitrification_and_volatilization")
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "percolated_nitrates",
                    layer.percolated_nitrates,
                    dict(info_map, **{"data_origin": [("LeachingRunoffErosion", "_leach_nitrogen")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "percolated_ammonium",
                    layer.percolated_ammonium,
                    dict(info_map, **{"data_origin": [("LeachingRunoffErosion", "_leach_nitrogen")], "units": "kg/ha"}),
                )
                om.add_variable(
                    "percolated_active_organic_nitrogen",
                    layer.percolated_active_organic_nitrogen,
                    dict(info_map, **{"data_origin": [("LeachingRunoffErosion", "_leach_nitrogen")], "units": "kg/ha"}),
                )

            for crop in field.crops:
                info_map["suffix"] = (
                    f"field='{field.field_data.name}',crop='{crop.data.name}',"
                    f"planted={crop.data.planting_day},{crop.data.planting_year}"
                )
                om.add_variable(
                    "root_depth",
                    crop.data.root_depth,
                    dict(info_map, **{"data_origin": [("RootDevelopment", "develop_roots")], "units": "mm"}),
                )
                om.add_variable(
                    "biomass",
                    crop.data.biomass,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("BiomassAllocation", "photosynthesize"),
                                ("CropManagement", "cut_crop"),
                                ("Dormancy", "enter_dormancy"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "usable_light",
                    crop.data.usable_light,
                    dict(info_map, **{"data_origin": [("BiomassAllocation", "photosynthesize")],
                                      "units": "MJ/m^2"}),
                )
                om.add_variable(
                    "biomass_growth_max",
                    crop.data.biomass_growth_max,
                    dict(info_map, **{"data_origin": [("BiomassAllocation", "photosynthesize")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "biomass_growth",
                    crop.data.biomass_growth,
                    dict(info_map, **{"data_origin": [("BiomassAllocation", "photosynthesize")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "growth_factor",
                    crop.data.growth_factor,
                    dict(info_map, **{"data_origin": [("constrain_growth", "constrain_growth")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "above_ground_biomass",
                    crop.data.above_ground_biomass,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("BiomassAllocation", "partition_biomass"),
                                ("CropManagement", "dry_down"),
                                ("CropManagement", "_recalculate_biomass_distribution"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "root_biomass",
                    crop.data.root_biomass,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("BiomassAllocation", "partition_biomass"),
                                ("CropManagement", "_recalculate_biomass_distribution"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "water_uptake",
                    crop.data.water_uptake,
                    dict(info_map, **{"data_origin": [("WaterUptake", "uptake_water")],
                                      "units": "mm"}),
                )
                om.add_variable(
                    "water_stress",
                    crop.data.water_stress,
                    dict(info_map, **{"data_origin": [("GrowthConstraints", "constrain_growth")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "temp_stress",
                    crop.data.temp_stress,
                    dict(info_map, **{"data_origin": [("GrowthConstraints", "constrain_growth")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "nitrogen_stress",
                    crop.data.nitrogen_stress,
                    dict(info_map, **{"data_origin": [("GrowthConstraints", "constrain_growth")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "phosphorus_stress",
                    crop.data.phosphorus_stress,
                    dict(info_map, **{"data_origin": [("GrowthConstraints", "constrain_growth")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "accumulated_heat_units",
                    crop.data.accumulated_heat_units,
                    dict(
                        info_map, **{"data_origin": [("CropManagement", "cut_crop"), ("HeatUnits", "add_heat_units")],
                                     "units": "unitless"}
                    ),
                )
                om.add_variable(
                    "heat_fraction",
                    crop.data.heat_fraction,
                    dict(info_map, **{"data_origin": [("CropData", "heat_fraction")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "is_growing",
                    crop.data.is_growing,
                    dict(info_map, **{"data_origin": [("HeatUnits", "absorb_heat_units")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "is_dormant",
                    crop.data.is_dormant,
                    dict(info_map, **{"data_origin": [("Dormancy", "enter_dormancy"), ("Field", "_assess_dormancy")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "leaf_area_index",
                    crop.data.leaf_area_index,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("CropManagement", "cut_crop"),
                                ("Dormancy", "enter_dormancy"),
                                ("LeafAreaIndex", "grow_canopy"),
                                ("LeafAreaIndex", "add_leaf_area"),
                            ],
                            "units": "unitless"
                        },
                    ),
                )
                om.add_variable(
                    "canopy_height",
                    crop.data.canopy_height,
                    dict(info_map, **{"data_origin": [("LeafAreaIndex", "grow_canopy")],
                                      "units": "m"}),
                )
                om.add_variable(
                    "leaf_area_added",
                    crop.data.leaf_area_added,
                    dict(info_map, **{"data_origin": [("LeafAreaIndex", "determine_leaf_area_added")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "optimal_leaf_area_change",
                    crop.data.optimal_leaf_area_change,
                    dict(info_map, **{"data_origin": [("LeafAreaIndex", "grow_canopy")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "potential_nitrogen_uptake",
                    crop.data.potential_nitrogen_uptake,
                    dict(info_map, **{"data_origin": [("NitrogenIncorporation", "incorporate_nitrogen")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "total_phosphorus_uptake",
                    crop.data.total_phosphorus_uptake,
                    dict(info_map, **{"data_origin": [("PhosphorusIncorporation", "tally_total_phosphorus_uptake")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "total_nitrogen_uptake",
                    crop.data.total_nitrogen_uptake,
                    dict(info_map, **{"data_origin": [("NitrogenIncorporation", "tally_total_nitrogen_uptake")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "optimal_nitrogen_fraction",
                    crop.data.optimal_nitrogen_fraction,
                    dict(info_map, **{"data_origin": [("NitrogenIncorporation", "incorporate_nitrogen")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "potential_phosphorus_uptake",
                    crop.data.potential_phosphorus_uptake,
                    dict(info_map, **{"data_origin": [("PhosphorusIncorporation", "incorporate_phosphorus")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "actual_phosphorus_uptakes",
                    crop.data.actual_phosphorus_uptakes,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("PhosphorusIncorporation", "uptake_phosphorus"),
                                ("PhosphorusIncorporation", "extend_phosphate_uptakes_to_full_profile"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "actual_nitrogen_uptakes",
                    crop.data.actual_nitrogen_uptakes,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("NitrogenIncorporation", "uptake_nitrogen"),
                                ("NitrogenIncorporation", "extend_nitrate_uptakes_to_full_profile"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "cumulative_evaporation",
                    crop.data.cumulative_evaporation,
                    dict(info_map, **{"data_origin": [("WaterDynamics", "cycle_water"), ("Field", "_cycle_water")],
                                      "units": "mm"}),
                )
                om.add_variable(
                    "cumulative_transpiration",
                    crop.data.cumulative_transpiration,
                    dict(info_map, **{"data_origin": [("WaterDynamics", "cycle_water"), ("Field", "_cycle_water")],
                                      "units": "mm"}),
                )
                om.add_variable(
                    "cumulative_evapotranspiration",
                    crop.data.cumulative_evapotranspiration,
                    dict(info_map, **{"data_origin": [("WaterDynamics", "cycle_water")],
                                      "units": "mm"}),
                )
                om.add_variable(
                    "water_deficiency",
                    crop.data.water_deficiency,
                    dict(info_map, **{"data_origin": [("WaterDynamics", "cycle_water")],
                                      "units": "unitless"}),
                )
                om.add_variable(
                    "max_transpiration",
                    crop.data.max_transpiration,
                    dict(info_map, **{"data_origin": [("WaterDynamics", "set_maximum_transpiration")],
                                      "units": "mm"}),
                )
                om.add_variable(
                    "canopy_water",
                    crop.data.canopy_water,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("WaterDynamics", "evaporate_from_canopy"),
                                ("Field", "_handle_water_in_crop_canopies"),
                            ],
                            "units": "mm"
                        },
                    ),
                )
                om.add_variable(
                    "cut_biomass",
                    crop.data.cut_biomass,
                    dict(info_map, **{"data_origin": [("CropManagement", "cut_crop")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "wet_yield_collected",
                    crop.data.wet_yield_collected,
                    dict(info_map, **{"data_origin": [("CropManagement", "cut_crop")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "dry_matter_yield_residue",
                    crop.data.yield_residue,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("CropManagement", "cut_crop"),
                                ("CropManagement", "kill"),
                                ("CropManagement", "_transfer_residue"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "yield_nitrogen",
                    crop.data.yield_nitrogen,
                    dict(info_map, **{"data_origin": [("CropManagement", "cut_crop")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "yield_phosphorus",
                    crop.data.yield_phosphorus,
                    dict(info_map, **{"data_origin": [("CropManagement", "cut_crop")],
                                      "units": "kg/ha"}),
                )
                om.add_variable(
                    "residue_nitrogen",
                    crop.data.residue_nitrogen,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("CropManagement", "cut_crop"),
                                ("CropManagement", "kill"),
                                ("CropManagement", "_transfer_residue"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "residue_phosphorus",
                    crop.data.residue_phosphorus,
                    dict(info_map, **{"data_origin": [("LeachingRunoffErosion", "_leach_nitrogen")],
                                      "units": "kg/ha"}),
                )

    def send_annual_variables(self) -> None:
        """sends annual variables to the output manager"""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.send_annual_variables.__name__,
        }
        # adding field variable
        for field in self.fields:
            # Adding field data
            info_map["suffix"] = "field='" + field.field_data.name + "'"
            om.add_variable(
                "annual_irrigation_water_use_total",
                field.field_data.annual_irrigation_water_use_total,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Field", "_determine_watering_amount"),
                            ("FieldData", "perform_annual_field_reset"),
                        ],
                        "units": "mm"
                    },
                ),
            )

            # Adding soil data
            water_content_change = field.soil.data.profile_soil_water_content - field.soil.data.initial_water_content
            om.add_variable(
                "annual_water_content_change",
                water_content_change,
                dict(info_map, **{"data_origin": [("FieldDataReporter", "send_annual_variables")],
                                  "units": "mm"}),
            )
            nitrates_content_change = field.soil.data.profile_nitrates_total - field.soil.data.initial_nitrates_total
            om.add_variable(
                "annual_nitrates_content_change",
                nitrates_content_change,
                dict(info_map, **{"data_origin": [("FieldDataReporter", "send_annual_variables")],
                                  "units": "kg/ha"}),
            )

            om.add_variable(
                "annual_soil_evaporation_total",
                field.soil.data.annual_soil_evaporation_total,
                dict(info_map, **{"data_origin": [("Evaporation", "evaporate"), ("SoilData", "do_annual_reset")],
                                  "units": "mm"}),
            )
            om.add_variable(
                "annual_eroded_sediment_total",
                field.soil.data.annual_eroded_sediment_total,
                dict(info_map, **{"data_origin": [("SoilErosion", "erode"), ("SoilData", "do_annual_reset")],
                                  "units": "metric tons"}),
            )
            om.add_variable(
                "annual_surface_runoff_total",
                field.soil.data.annual_surface_runoff_total,
                dict(info_map, **{"data_origin": [("SoilErosion", "erode"), ("SoilData", "do_annual_reset")],
                                  "units": "mm/ha"}),
            )
            om.add_variable(
                "annual_runoff_fertilizer_phosphorus",
                field.soil.data.annual_runoff_fertilizer_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Fertilizer", "_update_before_and_at_first_rain"),
                            ("Fertilizer", "_update_after_first_rain"),
                            ("SoilData", "do_annual_reset"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "annual_runoff_machine_manure_inorganic_phosphorus",
                field.soil.data.annual_runoff_machine_manure_inorganic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                            ("SoilData", "do_annual_reset"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "annual_runoff_machine_manure_organic_phosphorus",
                field.soil.data.annual_runoff_machine_manure_organic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                            ("SoilData", "do_annual_reset"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "annual_runoff_grazing_manure_inorganic_phosphorus",
                field.soil.data.annual_runoff_grazing_manure_inorganic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                            ("SoilData", "do_annual_reset"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "annual_runoff_grazing_manure_organic_phosphorus",
                field.soil.data.annual_runoff_grazing_manure_organic_phosphorus,
                dict(
                    info_map,
                    **{
                        "data_origin": [
                            ("Manure", "_leach_and_update_phosphorus_pools"),
                            ("SoilData", "do_annual_reset"),
                        ],
                        "units": "kg"
                    },
                ),
            )
            om.add_variable(
                "annual_soil_phosphorus_runoff",
                field.soil.data.annual_soil_phosphorus_runoff,
                dict(
                    info_map,
                    **{"data_origin": [("SolublePhosphorus", "daily_update_routine"), ("SoilData", "do_annual_reset")],
                       "units": "kg"},
                ),
            )
            om.add_variable(
                "annual_runoff_nitrates_total",
                field.soil.data.annual_runoff_nitrates_total,
                dict(
                    info_map,
                    **{"data_origin": [("LeachingRunoffErosion", "_erode_nitrogen"), ("SoilData", "do_annual_reset")],
                       "units": "kg"},
                ),
            )
            om.add_variable(
                "annual_runoff_ammonium_total",
                field.soil.data.annual_runoff_ammonium_total,
                dict(
                    info_map,
                    **{"data_origin": [("LeachingRunoffErosion", "_erode_nitrogen"), ("SoilData", "do_annual_reset")],
                       "units": "kg"},
                ),
            )
            om.add_variable(
                "annual_eroded_fresh_organic_nitrogen_total",
                field.soil.data.annual_eroded_fresh_organic_nitrogen_total,
                dict(
                    info_map,
                    **{"data_origin": [("LeachingRunoffErosion", "_erode_nitrogen"), ("SoilData", "do_annual_reset")],
                       "units": "kg"},
                ),
            )
            om.add_variable(
                "annual_eroded_stable_organic_nitrogen_total",
                field.soil.data.annual_eroded_stable_organic_nitrogen_total,
                dict(
                    info_map,
                    **{"data_origin": [("LeachingRunoffErosion", "_erode_nitrogen"), ("SoilData", "do_annual_reset")],
                       "units": "kg"},
                ),
            )
            om.add_variable(
                "annual_eroded_active_organic_nitrogen_total",
                field.soil.data.annual_eroded_active_organic_nitrogen_total,
                dict(
                    info_map,
                    **{"data_origin": [("LeachingRunoffErosion", "_erode_nitrogen"), ("SoilData", "do_annual_reset")],
                       "units": "kg"},
                ),
            )

            # ----------------------------adding layer data
            for index, layer in enumerate(field.soil.data.soil_layers):
                info_map["suffix"] = "field='" + field.field_data.name + "',layer='" + str(index) + "'"

                om.add_variable(
                    "annual_nitrous_oxide_emissions_total",
                    layer.annual_nitrous_oxide_emissions_total,
                    dict(
                        info_map,
                        **{"data_origin": [("Denitrification", "denitrify"), ("LayerData", "do_annual_reset")],
                           "units": "kg/ha"},
                    ),
                )
                om.add_variable(
                    "annual_ammonia_emissions_total",
                    layer.annual_ammonia_emissions_total,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("NitrificationVolatilization", "do_daily_nitrification_and_volatilization")
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "annual_decomposition_carbon_CO2_lost",
                    layer.annual_decomposition_carbon_CO2_lost,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("CarbonCycling", "_soil_carbon_aggregation"),
                                ("LayerData", "do_annual_reset"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
                om.add_variable(
                    "annual_carbon_CO2_lost",
                    layer.annual_carbon_CO2_lost,
                    dict(
                        info_map,
                        **{
                            "data_origin": [
                                ("CarbonCycling", "_soil_carbon_aggregation"),
                                ("LayerData", "do_annual_reset"),
                            ],
                            "units": "kg/ha"
                        },
                    ),
                )
