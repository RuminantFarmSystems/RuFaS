from __future__ import annotations
from itertools import groupby
from typing import Optional

from SC_redesign.Crop_and_Soil.soil.evapotranspiration import Evapotranspiration
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData


class Soil:
    def __init__(self, soil_data: Optional[SoilData] = None):
        data = soil_data or SoilData()
        self.evapotranspiration = Evapotranspiration(data)

        # whole-profile attributes
        self.evaporation = 20  # arbitrary
        self.transpiration = 30  # arbitrary
        self.evapotranspiration_max = 100  # arbitrary
        self.available_water = 80  # arbitrary
        self.water_capacity = 100  # arbitrary

        self.evapotranspiration = None
        self.water_factor = None

        self.data.soil_layers = [LayerData(top_depth=0, bottom_depth=5, nitrate=0.5),
                                 LayerData(top_depth=5, bottom_depth=8, nitrate=1),
                                 LayerData(top_depth=8, bottom_depth=20, nitrate=5)]


    @classmethod
    def make_from_config(cls, soil_config) -> Soil:
        """"""
        Warning("create from config file not yet implement, returning default Soil()")
        return Soil()

    def check_layer_lengths_match(self):
        """check that soil layer attributes are all the same length"""
        layer_attribute_list = [self.depths, self.nitrates]  # TODO: update as new varibales are added
        g = groupby([len(item) for item in layer_attribute_list])
        return next(g, True) and not next(g, False)

    def update_soil_water_factor(self):
        """updates the soil water factor from available water and the maximum water at field capacity on a given day"""
        self.water_factor = calc_soil_water_factor(self.available_water, self.water_capacity)

    def update_evapotranspiration(self):
        """updates the daily evapotranspiration"""
        self.evapotranspiration = self.evaporation + self.transpiration


# ---- helper functions ---- TODO: should be moved to soil process classes
def calc_soil_water_factor(available_water: float, water_capacity: float) -> float:  # pseudocode: C.5.D.5
    """
    Description: calculates soil water factor

    Args:
        available_water: the water available in the soil profile (mm)
        water_capacity: the water accessible at field capacity (mm)

    Returns: soil water factor
    """
    return available_water / 0.85 * water_capacity
