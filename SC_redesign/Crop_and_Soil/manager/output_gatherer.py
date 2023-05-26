from typing import List, Optional

from RUFAS.output_manager import OutputManager
from SC_redesign.Crop_and_Soil.field.field import Field


class OutputGatherer:
    def __init__(self, fields: List[Field]):
        self.fields = fields
        self.om = OutputManager()

    def send_daily_variables(self, filter_specs: Optional[List] = None) -> None:
        """sends daily variables to the output manager"""
        info_map = {"class": self.__class__.__name__, "function": self.send_daily_variables.__name__}
        for field in self.fields:
            info_map["prefix"] = "field" + field.field_data.name
            # --------------------------adding field data
            self.om.add_variable("current_residue", field.field_data.current_residue, info_map)
            self.om.add_variable("evaporation", field.field_data.evaporation, info_map)
            self.om.add_variable("transpiration", field.field_data.transpiration, info_map)
            # max_transpiration needs to be added?
            self.om.add_variable("max_transpiration", field.field_data.max_transpiration, info_map)
            self.om.add_variable("max_evapotranspiration", field.field_data.max_evapotranspiration, info_map)
            self.om.add_variable("days_into_watering_interval", field.field_data.days_into_watering_interval, info_map)

            # ----------------------------adding soil data
            self.om.add_variable("potential_evapotranspiration", field.soil.data.potential_evapotranspiration,
                                 info_map)
            self.om.add_variable("potential_evapotranspiration_adjusted",
                                 field.soil.data.potential_evapotranspiration_adjusted,
                                 info_map)
            self.om.add_variable("transpiration", field.soil.data.transpiration, info_map)
            self.om.add_variable("soil_evaporation_adjusted", field.soil.data.soil_evaporation_adjusted, info_map)
            self.om.add_variable("maximum_soil_evaporation", field.soil.data.maximum_soil_evaporation, info_map)
            self.om.add_variable("eroded_sediment", field.soil.data.eroded_sediment, info_map)
            self.om.add_variable("accumulated_runoff", field.soil.data.accumulated_runoff, info_map)
            # not sure
            self.om.add_variable("surface_runoff_volume", field.soil.data.surface_runoff_volume, info_map)
            self.om.add_variable("available_phosphorus_pool", field.soil.data.available_phosphorus_pool, info_map)
            self.om.add_variable("runoff_phosphorus_pool", field.soil.data.runoff_phosphorus_pool, info_map)
            self.om.add_variable("days_since_application", field.soil.data.days_since_application, info_map)
            # not sure
            self.om.add_variable("rain_events_after_fertilizer_application",
                                 field.soil.data.rain_events_after_fertilizer_application,
                                 info_map)

            # ----------------------------adding layer data
            for layer in field.soil.data.soil_layers:
                info_map["prefix"] = "field" + field.field_data.name + " layer top depth " + str(layer.top_depth) + \
                                     " layer bottom depth " + str(layer.bottom_depth)
                # not sure
                # self.om.add_variable("temperature", layer.temperature, info_map)
                self.om.add_variable("percolated_water", layer.percolated_water, info_map)
                # not sure
                self.om.add_variable("plant_metabolic_active_carbon_usage", layer.plant_metabolic_active_carbon_usage
                                     , info_map)
                self.om.add_variable("plant_metabolic_active_carbon_loss", layer.plant_metabolic_active_carbon_loss
                                     , info_map)
                self.om.add_variable("plant_metabolic_active_carbon_remaining"
                                     , layer.plant_metabolic_active_carbon_remaining, info_map)
                self.om.add_variable("plant_structural_active_carbon_usage", layer.plant_structural_active_carbon_usage
                                     , info_map)
                self.om.add_variable("plant_structural_active_carbon_remaining"
                                     , layer.plant_structural_active_carbon_remaining, info_map)
                self.om.add_variable("plant_structural_slow_carbon_usage", layer.plant_structural_slow_carbon_usage
                                     , info_map)
                self.om.add_variable("plant_structural_slow_carbon_loss", layer.plant_structural_slow_carbon_loss
                                     , info_map)
                self.om.add_variable("plant_structural_slow_carbon_remaining"
                                     , layer.plant_structural_slow_carbon_remaining, info_map)
                self.om.add_variable("soil_metabolic_active_carbon_usage", layer.soil_metabolic_active_carbon_usage
                                     , info_map)
                self.om.add_variable("soil_metabolic_active_carbon_loss", layer.soil_metabolic_active_carbon_loss
                                     , info_map)
                self.om.add_variable("soil_metabolic_active_carbon_remaining"
                                     , layer.soil_metabolic_active_carbon_remaining, info_map)
                self.om.add_variable("soil_structural_active_carbon_usage", layer.soil_structural_active_carbon_usage
                                     , info_map)
                self.om.add_variable("soil_structural_active_carbon_loss", layer.soil_structural_active_carbon_loss
                                     , info_map)
                self.om.add_variable("soil_structural_active_carbon_remaining"
                                     , layer.soil_structural_active_carbon_remaining, info_map)
                self.om.add_variable("soil_structural_slow_carbon_usage", layer.soil_structural_slow_carbon_usage
                                     , info_map)
                self.om.add_variable("soil_structural_slow_carbon_loss", layer.soil_structural_slow_carbon_loss
                                     , info_map)
                self.om.add_variable("soil_structural_slow_carbon_remaining"
                                     , layer.soil_structural_slow_carbon_remaining, info_map)
                self.om.add_variable("active_carbon_decomposition_amount", layer.active_carbon_decomposition_amount
                                     , info_map)
                self.om.add_variable("active_carbon_amount", layer.active_carbon_amount
                                     , info_map)
                self.om.add_variable("slow_carbon_amount", layer.slow_carbon_amount
                                     , info_map)
                self.om.add_variable("slow_carbon_decomposition_amount", layer.slow_carbon_decomposition_amount
                                     , info_map)
                self.om.add_variable("passive_carbon_decomposition_amount", layer.passive_carbon_decomposition_amount
                                     , info_map)
                self.om.add_variable("active_carbon_to_slow_amount", layer.active_carbon_to_slow_amount
                                     , info_map)
                self.om.add_variable("active_carbon_to_slow_loss", layer.active_carbon_to_slow_loss
                                     , info_map)
                self.om.add_variable("active_carbon_to_passive_amount", layer.active_carbon_to_passive_amount
                                     , info_map)
                self.om.add_variable("slow_to_active_carbon_amount", layer.slow_to_active_carbon_amount
                                     , info_map)
                self.om.add_variable("slow_carbon_co2_lost_amount", layer.slow_carbon_co2_lost_amount
                                     , info_map)
                self.om.add_variable("passive_to_active_carbon_amount", layer.passive_to_active_carbon_amount
                                     , info_map)
                self.om.add_variable("passive_carbon_co2_lost_amount", layer.passive_carbon_co2_lost_amount
                                     , info_map)
                self.om.add_variable("plant_active_decompose_carbon", layer.plant_active_decompose_carbon
                                     , info_map)
                self.om.add_variable("soil_active_decompose_carbon", layer.soil_active_decompose_carbon
                                     , info_map)
                self.om.add_variable("active_inorganic_unbalanced_counter", layer.active_inorganic_unbalanced_counter
                                     , info_map)
                self.om.add_variable("labile_inorganic_unbalanced_counter", layer.labile_inorganic_unbalanced_counter
                                     , info_map)
                self.om.add_variable("previous_phosphorus_balance", layer.previous_phosphorus_balance
                                     , info_map)
                self.om.add_variable("nitrate_content", layer.nitrate_content
                                     , info_map)
                self.om.add_variable("ammonium_content", layer.ammonium_content
                                     , info_map)
                self.om.add_variable("active_organic_nitrogen_content", layer.active_organic_nitrogen_content
                                     , info_map)
                self.om.add_variable("stable_organic_nitrogen_content", layer.stable_organic_nitrogen_content
                                     , info_map)
                self.om.add_variable("fresh_organic_nitrogen_content", layer.fresh_organic_nitrogen_content
                                     , info_map)
                self.om.add_variable("ammonium_content", layer.ammonium_content
                                     , info_map)
                self.om.add_variable("ammonium_content", layer.ammonium_content
                                     , info_map)







            for crop in field.crops:
                info_map["prefix"] = "field" + field.field_data.name + " crop" + crop.data.name
                self.om.add_variable("root_depth", crop.data.root_depth, info_map)


    def send_annual_variables(self):
        """sends annual variables to the output manager"""
        pass
