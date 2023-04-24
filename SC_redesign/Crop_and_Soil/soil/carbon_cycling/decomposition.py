import math
from typing import Optional
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


# TODO: the equations for this model, referenced in the soil psuedocode, are derived from the excel file
#   located on basecamp: https://3.basecamp.com/3486446/buckets/5296287/vaults/2740532358
#   but the meaning (and validity) of the terms is extremely unclear from either source. The
#   documentation cannot be adequately completed without a better understanding of these methods.
class Decomposition:
    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track the decomposition of carbong in the soil profile, creates
            new one if one is not provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

    def decompose(self, temp_average: float) -> None:
        """
        Determines decomposition effect for each layers and temperature effect

        Args:
            temp_average: Average temperature (Celsius)

        Returns: None

        """
        self.data.decomposition_temperature_effect = self._calc_temp_factor(temp_average)

        for layer in self.data.soil_layers:
            layer.decomposition_moisture_effect = self._calc_moisture_factor(layer.water_factor)

    @staticmethod
    def _calc_temp_factor(temp_average, x_inflection: float = 15.4, y_inflection: float = 11.75,
                          point_distance: float = 29.7, inflection_slope=0.03,
                          normalizer=20.80546) -> float:
        """
        Description: calculates the Temperature factor for carbon decomposition
            "pseudocode_soil" S.6.A.1
            defaults drawn from defac: course soil
        Args:
            temp_average: Average temperature (celsius)

        Returns: temperature effect (unitless)
        """
        # S.6.A.4
        return (y_inflection + (point_distance / math.pi) * math.atan(math.pi * inflection_slope * (
                temp_average - x_inflection))) / normalizer

    @staticmethod
    def _calc_moisture_factor(water_factor, a_term: float = 0.55, b_term: float = 1.7,
                              c_term: float = -0.007, first_exponent=6.648115,
                              second_exponent=3.22) -> float:
        """
        Description: calculates the moisture factor for carbon decomposition for the layer
            "pseudocode_soil" S.6.A.2
            defaults drawn from defac: course soil
        Args:
            water_factor: relative water saturation (%)
        Returns: moisture effect (unitless)
        """
        # S.6.A.5
        base_1 = (water_factor - b_term) / (a_term - b_term)
        base_2 = (water_factor - c_term) / (a_term - c_term)

        return (base_1 ** first_exponent) * (base_2 ** second_exponent)
