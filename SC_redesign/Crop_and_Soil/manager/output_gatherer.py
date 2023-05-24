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
            self.om.add_variable("accumulated_runoff", field.soil.data.accumulated_runoff,
                                 info_map)
            for crop in field.crops:
                info_map["prefix"] = "field" + field.field_data.name + "crop" + crop.data.name
                self.om.add_variable("root_depth", crop.data.root_depth, info_map)

    def send_annual_variables(self):
        """sends annual variables to the output manager"""
        pass
