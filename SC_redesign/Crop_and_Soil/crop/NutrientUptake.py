from typing import Optional

from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""This module implement the crop's uptake of nutrients (water, N, P, etc.) from the soil"""

class NutrientUptake:
    def __int__(self, crop_data: Optional[CropData], soil_data: Optional[SoilData]):
        self.crop_data = crop_data or CropData()
        self.soil_Data = soil_data or SoilData()

    def find_deepest_accessible_layer(self):
        pass

    def access_layers(self):
        pass

    def find_uptake_potentials(self):
        pass

    def find_demands(self):
        pass

    def determine_actual_uptake(self):
        pass

    def extract(self):
        pass


class WaterUptake(NutrientUptake):
    def __init__(self, crop_data: Optional[CropData], soil_data: Optional[SoilData]):
        super().__init__(crop_data, soil_data)


class NitrogenUptake(NutrientUptake):
    def __init__(self, crop_data: Optional[CropData], soil_data: Optional[SoilData]):
        super().__init__(crop_data, soil_data)


class PhosphorusUptake(NutrientUptake):
    def __init__(self, crop_data: Optional[CropData], soil_data: Optional[SoilData]):
        super().__init__(crop_data, soil_data)
