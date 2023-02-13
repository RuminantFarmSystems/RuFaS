from __future__ import annotations
from itertools import groupby
from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.evapotranspiration import Evapotranspiration
from SC_redesign.Crop_and_Soil.soil.infiltration import Infiltration
from SC_redesign.Crop_and_Soil.soil.percolation import Percolation
from SC_redesign.Crop_and_Soil.soil.soil_temp import SoilTemp


class Soil:
    def __init__(self, soil_data: Optional[SoilData] = None):
        data = soil_data or SoilData()
        self.evapotranspiration = Evapotranspiration(data)
        self.infiltration = Infiltration(data)
        self.percolation = Percolation(data)
        self.soil_temp = SoilTemp(data)

    @classmethod
    def make_from_config(cls, soil_config) -> Soil:
        """"""
        Warning("create from config file not yet implement, returning default Soil()")
        return Soil()
