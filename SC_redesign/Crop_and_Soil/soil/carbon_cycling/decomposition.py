import math
from typing import Optional, List

from SC_redesign.Crop_and_Soil.soil import soil_data
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

# TODO: the equations for this model, referenced in the soil psuedocode, are derived from the excel file
#   located on basecamp: https://3.basecamp.com/3486446/buckets/5296287/vaults/2740532358
#   but the meaning (and validity) of the terms is extremely unclear from either source. The 
#   documentation cannot be adequately completed without a better understanding of these methods.
class Decomposition:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

    def decompose(self, temp_average: float) -> None:
        """
        Description: Updates and tracks all the related attributes in SoilData class

        Args:
            temp_average: Average temperature to pass in the _calc_temp_factor(temp_average) function

        Returns: None

        """
        self.data.decomposition_temperature_effect = self._calc_temp_factor(temp_average)

        self.data.decomposition_moisture_effect = self._calc_moisture_factor(self.data.soil_layers)

    @staticmethod
    def _calc_temp_factor(temp_average: float) -> float:
        """
        Description: calculates the Temperature factor for carbon decomposition
            "pseudocode_soil" S.6.A.1
            defaults drawn from defac: course soil
        Args:
            temp_average: Average temperature

        Returns: Unitless temperature effect
        """
        decomposition_inflection_x = 15.400
        decomposition_inflection_y = 11.750
        max_min_distance = 29.700
        inflection_slope = 0.03
        normalizer = 20.80546

        # S.6.A.4
        return max(0.0,
                   (decomposition_inflection_y + (max_min_distance / math.pi) * math.atan(math.pi * inflection_slope * (
                           temp_average - decomposition_inflection_x))) / normalizer)

    @staticmethod
    def _calc_moisture_factor(soil_layers: List[LayerData]) -> float:
        """
        Description: calculates the moisture factor for carbon decomposition
            "pseudocode_soil" S.6.A.2
            defaults drawn from defac: course soil
        Args:
            soil_layers: Layer data
        Returns: unitless moisture effect
        """
        dimensionless_empirical_factor_a = 0.55
        dimensionless_empirical_factor_b = 1.7
        dimensionless_empirical_factor_c = -0.007
        dimensionless_empirical_factor_e1 = 6.648115
        dimensionless_empirical_factor_e2 = 3.22

        for layer in soil_layers:
            # S.6.A.5
            base_1 = (layer.water_factor - dimensionless_empirical_factor_b) / (dimensionless_empirical_factor_a -
                                                                                dimensionless_empirical_factor_b)
            base_2 = (layer.water_factor - dimensionless_empirical_factor_c) / (dimensionless_empirical_factor_a -
                                                                                dimensionless_empirical_factor_c)
            hold = (base_1 ** dimensionless_empirical_factor_e1) * (base_2 ** dimensionless_empirical_factor_e2)

        return hold
