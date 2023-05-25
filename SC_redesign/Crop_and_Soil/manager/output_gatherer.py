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

            for layer in field.soil.data.soil_layers:
                info_map["prefix"] = "field" + field.field_data.name + " layer top depth" + layer.top_depth + \
                                     " layer bottom depth" + layer.bottom_depth
                # not sure
                self.om.add_variable("temperature", layer.temperature, info_map)
                self.om.add_variable("percolated_water", layer.percolated_water, info_map)


            for crop in field.crops:
                info_map["prefix"] = "field" + field.field_data.name + " crop" + crop.data.name
                self.om.add_variable("root_depth", crop.data.root_depth, info_map)


    def send_annual_variables(self):
        """sends annual variables to the output manager"""
        pass
