from typing import List, Optional

from RUFAS.output_manager import OutputManager
from SC_redesign.Crop_and_Soil.field.field import Field

om = OutputManager()


class OutputGatherer:
    def __init__(self, fields: List[Field]):
        self.fields = fields

    def send_daily_variables(self, filter_specs: Optional[List] = None) -> None:
        """sends daily variables to the output manager"""
        info_map = {"class": self.__class__.__name__, "function": self.send_daily_variables.__name__}
        for field in self.fields:
            info_map["prefix"] = "field:'" + field.field_data.name + "'"
            # --------------------------adding field data
            om.add_variable("current_residue", field.field_data.current_residue, info_map)
            om.add_variable("evaporation", field.field_data.evaporation, info_map)
            om.add_variable("transpiration", field.field_data.transpiration, info_map)
            om.add_variable("max_transpiration", field.field_data.max_transpiration, info_map)
            om.add_variable("max_evapotranspiration", field.field_data.max_evapotranspiration, info_map)
            om.add_variable("days_into_watering_interval", field.field_data.days_into_watering_interval, info_map)

            # ----------------------------adding soil data
            om.add_variable("water_evaporated", field.soil.data.water_evaporated,
                            info_map)
            om.add_variable("eroded_sediment", field.soil.data.eroded_sediment, info_map)
            om.add_variable("accumulated_runoff", field.soil.data.accumulated_runoff, info_map)

            om.add_variable("available_phosphorus_pool", field.soil.data.available_phosphorus_pool, info_map)
            om.add_variable("runoff_phosphorus_pool", field.soil.data.runoff_phosphorus_pool, info_map)
            om.add_variable("days_since_application", field.soil.data.days_since_application, info_map)
            om.add_variable("cover_type",
                            field.soil.data.cover_type,
                            info_map)
            om.add_variable("full_available_phosphorus_pool",
                            field.soil.data.full_available_phosphorus_pool,
                            info_map)
            om.add_variable("available_phosphorus_pool",
                            field.soil.data.available_phosphorus_pool,
                            info_map)
            om.add_variable("recalcitrant_phosphorus_pool",
                            field.soil.data.recalcitrant_phosphorus_pool,
                            info_map)
            om.add_variable("runoff_phosphorus_pool",
                            field.soil.data.runoff_phosphorus_pool,
                            info_map)
            om.add_variable("days_since_application",
                            field.soil.data.days_since_application,
                            info_map)
            om.add_variable("rain_events_after_fertilizer_application",
                            field.soil.data.rain_events_after_fertilizer_application,
                            info_map)
            om.add_variable("machine_manure_dry_mass",
                            field.soil.data.machine_manure_dry_mass,
                            info_map)
            om.add_variable("machine_manure_applied_mass",
                            field.soil.data.machine_manure_applied_mass,
                            info_map)
            om.add_variable("machine_manure_field_coverage",
                            field.soil.data.machine_manure_field_coverage,
                            info_map)
            om.add_variable("machine_manure_moisture_factor",
                            field.soil.data.machine_manure_moisture_factor,
                            info_map)
            om.add_variable("machine_water_extractable_inorganic_phosphorus",
                            field.soil.data.machine_water_extractable_inorganic_phosphorus,
                            info_map)
            om.add_variable("machine_water_extractable_organic_phosphorus",
                            field.soil.data.machine_water_extractable_organic_phosphorus,
                            info_map)
            om.add_variable("machine_stable_inorganic_phosphorus",
                            field.soil.data.machine_stable_inorganic_phosphorus,
                            info_map)
            om.add_variable("machine_stable_organic_phosphorus",
                            field.soil.data.machine_stable_organic_phosphorus,
                            info_map)
            om.add_variable("grazing_manure_dry_mass",
                            field.soil.data.grazing_manure_dry_mass,
                            info_map)
            om.add_variable("grazing_manure_applied_mass",
                            field.soil.data.grazing_manure_applied_mass,
                            info_map)
            om.add_variable("grazing_manure_field_coverage",
                            field.soil.data.grazing_manure_field_coverage,
                            info_map)
            om.add_variable("grazing_manure_moisture_factor",
                            field.soil.data.grazing_manure_moisture_factor,
                            info_map)
            om.add_variable("grazing_water_extractable_inorganic_phosphorus",
                            field.soil.data.grazing_water_extractable_inorganic_phosphorus,
                            info_map)
            om.add_variable("grazing_water_extractable_organic_phosphorus",
                            field.soil.data.grazing_water_extractable_organic_phosphorus,
                            info_map)
            om.add_variable("grazing_stable_inorganic_phosphorus",
                            field.soil.data.grazing_stable_inorganic_phosphorus,
                            info_map)
            om.add_variable("grazing_stable_organic_phosphorus",
                            field.soil.data.grazing_stable_organic_phosphorus,
                            info_map)
            # Adding vadose zone layer data
            info_map["prefix"] = "field:'" + field.field_data.name + "_vadose_layer'"
            om.add_variable("active_organic_nitrogen_content",
                            field.soil.data.vadose_zone_layer.active_organic_nitrogen_content, info_map)
            om.add_variable("stable_organic_nitrogen_content",
                            field.soil.data.vadose_zone_layer.stable_organic_nitrogen_content, info_map)
            om.add_variable("nitrate_content",
                            field.soil.data.vadose_zone_layer.nitrate_content, info_map)
            om.add_variable("fresh_organic_nitrogen_content",
                            field.soil.data.vadose_zone_layer.fresh_organic_nitrogen_content, info_map)
            om.add_variable("water_content",
                            field.soil.data.vadose_zone_layer.water_content, info_map)
            om.add_variable("labile_inorganic_phosphorus_content",
                            field.soil.data.vadose_zone_layer.labile_inorganic_phosphorus_content, info_map)
            om.add_variable("active_inorganic_phosphorus_content",
                            field.soil.data.vadose_zone_layer.active_inorganic_phosphorus_content, info_map)
            om.add_variable("stable_inorganic_phosphorus_content",
                            field.soil.data.vadose_zone_layer.stable_inorganic_phosphorus_content, info_map)
            om.add_variable("fresh_organic_phosphorus_content",
                            field.soil.data.vadose_zone_layer.fresh_organic_phosphorus_content, info_map)

            # ----------------------------adding layer data
            for index, layer in enumerate(field.soil.data.soil_layers):
                info_map["prefix"] = "field:'" + field.field_data.name + "',layer_index:'" + str(index) + "'"

                om.add_variable("temperature", layer.temperature, info_map)
                om.add_variable("percolated_water", layer.percolated_water, info_map)
                om.add_variable("plant_metabolic_active_carbon_usage", layer.plant_metabolic_active_carbon_usage,
                                info_map)
                om.add_variable("plant_metabolic_active_carbon_loss", layer.plant_metabolic_active_carbon_loss,
                                info_map)
                om.add_variable("plant_metabolic_active_carbon_remaining",
                                layer.plant_metabolic_active_carbon_remaining, info_map)
                om.add_variable("plant_structural_active_carbon_usage", layer.plant_structural_active_carbon_usage,
                                info_map)
                om.add_variable("plant_structural_active_carbon_remaining",
                                layer.plant_structural_active_carbon_remaining, info_map)
                om.add_variable("plant_structural_slow_carbon_usage", layer.plant_structural_slow_carbon_usage,
                                info_map)
                om.add_variable("plant_structural_slow_carbon_loss", layer.plant_structural_slow_carbon_loss,
                                info_map)
                om.add_variable("plant_structural_slow_carbon_remaining",
                                layer.plant_structural_slow_carbon_remaining, info_map)
                om.add_variable("soil_metabolic_active_carbon_usage", layer.soil_metabolic_active_carbon_usage,
                                info_map)
                om.add_variable("soil_metabolic_active_carbon_loss", layer.soil_metabolic_active_carbon_loss,
                                info_map)
                om.add_variable("soil_metabolic_active_carbon_remaining",
                                layer.soil_metabolic_active_carbon_remaining, info_map)
                om.add_variable("soil_structural_active_carbon_usage", layer.soil_structural_active_carbon_usage,
                                info_map)
                om.add_variable("soil_structural_active_carbon_loss", layer.soil_structural_active_carbon_loss,
                                info_map)
                om.add_variable("soil_structural_active_carbon_remaining",
                                layer.soil_structural_active_carbon_remaining, info_map)
                om.add_variable("soil_structural_slow_carbon_usage", layer.soil_structural_slow_carbon_usage,
                                info_map)
                om.add_variable("soil_structural_slow_carbon_loss", layer.soil_structural_slow_carbon_loss,
                                info_map)
                om.add_variable("soil_structural_slow_carbon_remaining",
                                layer.soil_structural_slow_carbon_remaining, info_map)
                om.add_variable("active_carbon_decomposition_amount", layer.active_carbon_decomposition_amount,
                                info_map)
                om.add_variable("active_carbon_amount", layer.active_carbon_amount, info_map)
                om.add_variable("slow_carbon_amount", layer.slow_carbon_amount, info_map)
                om.add_variable("slow_carbon_decomposition_amount", layer.slow_carbon_decomposition_amount,
                                info_map)
                om.add_variable("passive_carbon_decomposition_amount", layer.passive_carbon_decomposition_amount,
                                info_map)
                om.add_variable("active_carbon_to_slow_amount", layer.active_carbon_to_slow_amount, info_map)
                om.add_variable("active_carbon_to_slow_loss", layer.active_carbon_to_slow_loss, info_map)
                om.add_variable("active_carbon_to_passive_amount", layer.active_carbon_to_passive_amount, info_map)
                om.add_variable("slow_to_active_carbon_amount", layer.slow_to_active_carbon_amount, info_map)
                om.add_variable("slow_carbon_co2_lost_amount", layer.slow_carbon_co2_lost_amount, info_map)
                om.add_variable("passive_to_active_carbon_amount", layer.passive_to_active_carbon_amount, info_map)
                om.add_variable("passive_carbon_co2_lost_amount", layer.passive_carbon_co2_lost_amount, info_map)
                om.add_variable("plant_active_decompose_carbon", layer.plant_active_decompose_carbon, info_map)
                om.add_variable("soil_active_decompose_carbon", layer.soil_active_decompose_carbon, info_map)
                om.add_variable("soil_overall_carbon_fraction", layer.soil_overall_carbon_fraction, info_map)
                om.add_variable("total_soil_carbon_amount", layer.total_soil_carbon_amount, info_map)
                om.add_variable("mean_phosphorus_sorption_parameter", layer.mean_phosphorus_sorption_parameter,
                                info_map)
                om.add_variable("labile_inorganic_phosphorus_contentr", layer.labile_inorganic_phosphorus_content,
                                info_map)
                om.add_variable("active_inorganic_phosphorus_content", layer.active_inorganic_phosphorus_content,
                                info_map)
                om.add_variable("stable_inorganic_phosphorus_content", layer.stable_inorganic_phosphorus_content,
                                info_map)
                om.add_variable("active_inorganic_unbalanced_counter", layer.active_inorganic_unbalanced_counter,
                                info_map)
                om.add_variable("labile_inorganic_unbalanced_counter", layer.labile_inorganic_unbalanced_counter,
                                info_map)
                om.add_variable("nitrate_content", layer.nitrate_content, info_map)
                om.add_variable("ammonium_content", layer.ammonium_content, info_map)
                om.add_variable("active_organic_nitrogen_content", layer.active_organic_nitrogen_content, info_map)
                om.add_variable("stable_organic_nitrogen_content", layer.stable_organic_nitrogen_content, info_map)
                om.add_variable("fresh_organic_nitrogen_content", layer.fresh_organic_nitrogen_content, info_map)

            for crop in field.crops:
                info_map["prefix"] = "field:'" + field.field_data.name + "',crop:'" + crop.data.name + "'"
                om.add_variable("root_depth", crop.data.root_depth, info_map)
                om.add_variable("biomass", crop.data.biomass, info_map)
                om.add_variable("usable_light", crop.data.usable_light, info_map)
                om.add_variable("biomass_growth_max", crop.data.biomass_growth_max, info_map)
                om.add_variable("biomass_growth", crop.data.biomass_growth, info_map)
                om.add_variable("above_ground_biomass", crop.data.above_ground_biomass, info_map)
                om.add_variable("root_biomass", crop.data.root_biomass, info_map)
                om.add_variable("water_uptake", crop.data.water_uptake, info_map)
                om.add_variable("water_stress", crop.data.water_stress, info_map)
                om.add_variable("temp_stress", crop.data.temp_stress, info_map)
                om.add_variable("nitrogen_stress", crop.data.nitrogen_stress, info_map)
                om.add_variable("phosphorus_stress", crop.data.phosphorus_stress, info_map)
                om.add_variable("accumulated_heat_units", crop.data.accumulated_heat_units, info_map)
                om.add_variable("is_growing", crop.data.is_growing, info_map)
                om.add_variable("is_dormant", crop.data.is_dormant, info_map)
                om.add_variable("leaf_area_index", crop.data.leaf_area_index, info_map)
                om.add_variable("canopy_height", crop.data.canopy_height, info_map)
                om.add_variable("leaf_area_added", crop.data.leaf_area_added, info_map)
                om.add_variable("optimal_leaf_area_change", crop.data.optimal_leaf_area_change, info_map)
                om.add_variable("potential_nitrogen_uptake", crop.data.potential_nitrogen_uptake, info_map)
                om.add_variable("total_phosphorus_uptake", crop.data.total_phosphorus_uptake, info_map)
                om.add_variable("total_nitrogen_uptake", crop.data.total_nitrogen_uptake, info_map)
                om.add_variable("potential_phosphorus_uptake", crop.data.potential_phosphorus_uptake, info_map)
                om.add_variable("actual_phosphorus_uptakes", crop.data.actual_phosphorus_uptakes, info_map)
                om.add_variable("actual_nitrogen_uptakes", crop.data.actual_nitrogen_uptakes, info_map)
                om.add_variable("total_nitrogen_uptake", crop.data.total_nitrogen_uptake, info_map)
                om.add_variable("cumulative_evaporation", crop.data.cumulative_evaporation, info_map)
                om.add_variable("cumulative_transpiration", crop.data.cumulative_transpiration, info_map)
                om.add_variable("cumulative_evapotranspiration", crop.data.cumulative_evapotranspiration, info_map)
                om.add_variable("max_transpiration", crop.data.max_transpiration, info_map)
                om.add_variable("canopy_water", crop.data.canopy_water, info_map)
                om.add_variable("cut_biomass", crop.data.cut_biomass, info_map)
                om.add_variable("yield_collected", crop.data.yield_collected, info_map)
                om.add_variable("yield_residue", crop.data.yield_residue, info_map)
                om.add_variable("yield_nitrogen", crop.data.yield_nitrogen, info_map)
                om.add_variable("yield_phosphorus", crop.data.yield_phosphorus, info_map)
                om.add_variable("residue_nitrogen", crop.data.residue_nitrogen, info_map)
                om.add_variable("residue_phosphorus", crop.data.residue_phosphorus, info_map)

    def send_annual_variables(self, filter_specs: Optional[List] = None) -> None:
        """sends annual variables to the output manager"""
        info_map = {"class": self.__class__.__name__, "function": self.send_annual_variables.__name__}
        # adding field variable
        for field in self.fields:
            # Adding field data
            info_map["prefix"] = "field" + field.field_data.name
            self.om.add_variable("annual_irrigation_water_use_total",
                                 field.field_data.annual_irrigation_water_use_total, info_map)

            # Adding soil data
            self.om.add_variable("annual_soil_evaporation_total", field.soil.data.annual_soil_evaporation_total,
                                 info_map)
            self.om.add_variable("annual_eroded_sediment_total", field.soil.data.annual_eroded_sediment_total,
                                 info_map)
            self.om.add_variable("annual_surface_runoff_total", field.soil.data.annual_surface_runoff_total,
                                 info_map)
            self.om.add_variable("annual_runoff_fertilizer_phosphorus",
                                 field.soil.data.annual_runoff_fertilizer_phosphorus,
                                 info_map)
            self.om.add_variable("annual_runoff_machine_manure_inorganic_phosphorus",
                                 field.soil.data.annual_runoff_machine_manure_inorganic_phosphorus,
                                 info_map)
            self.om.add_variable("annual_runoff_machine_manure_organic_phosphorus",
                                 field.soil.data.annual_runoff_machine_manure_organic_phosphorus,
                                 info_map)
            self.om.add_variable("annual_runoff_grazing_manure_inorganic_phosphorus",
                                 field.soil.data.annual_runoff_grazing_manure_inorganic_phosphorus,
                                 info_map)
            self.om.add_variable("annual_runoff_grazing_manure_organic_phosphorus",
                                 field.soil.data.annual_runoff_grazing_manure_organic_phosphorus,
                                 info_map)
            self.om.add_variable("annual_soil_phosphorus_runoff",
                                 field.soil.data.annual_soil_phosphorus_runoff,
                                 info_map)
            self.om.add_variable("annual_runoff_nitrates_total",
                                 field.soil.data.annual_runoff_nitrates_total,
                                 info_map)
            self.om.add_variable("annual_runoff_ammonium_total",
                                 field.soil.data.annual_runoff_ammonium_total,
                                 info_map)
            self.om.add_variable("annual_eroded_fresh_organic_nitrogen_total",
                                 field.soil.data.annual_eroded_fresh_organic_nitrogen_total,
                                 info_map)
            self.om.add_variable("annual_eroded_stable_organic_nitrogen_total",
                                 field.soil.data.annual_eroded_stable_organic_nitrogen_total,
                                 info_map)
            self.om.add_variable("annual_eroded_active_organic_nitrogen_total",
                                 field.soil.data.annual_eroded_active_organic_nitrogen_total,
                                 info_map)

            # ----------------------------adding layer data
            for index, layer in enumerate(field.soil.data.soil_layers):
                info_map["prefix"] = "field" + field.field_data.name + " layer index " + str(index)

                self.om.add_variable("annual_denitrified_nitrogen_total", layer.annual_denitrified_nitrogen_total
                                     , info_map)
                self.om.add_variable("annual_volatilized_ammonium_total", layer.annual_volatilized_ammonium_total
                                     , info_map)
                self.om.add_variable("annual_decomposition_carbon_CO2_lost", layer.annual_decomposition_carbon_CO2_lost
                                     , info_map)
                self.om.add_variable("annual_carbon_CO2_lost", layer.annual_carbon_CO2_lost
                                     , info_map)
