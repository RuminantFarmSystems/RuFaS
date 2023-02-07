from __future__ import annotations
from typing import Optional

from SC_redesign.Crop_and_Soil.soil.evapotranspiration import Evapotranspiration
from SC_redesign.Crop_and_Soil.soil.infiltration import Infiltration
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData


class Soil:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()
        self.evapotranspiration = Evapotranspiration(self.data)
        self.infiltration = Infiltration(self.data)

        # TODO: Find a way to set defaults for soil layers in SoilData
        self.data.soil_layers = [LayerData(top_depth=0, bottom_depth=5, nitrate=0.5),
                                 LayerData(top_depth=5, bottom_depth=8, nitrate=1),
                                 LayerData(top_depth=8, bottom_depth=20, nitrate=5)]

    @classmethod
    def make_from_config(cls, soil_config) -> Soil:
        """"""
        Warning("create from config file not yet implement, returning default Soil()")
        return Soil()
