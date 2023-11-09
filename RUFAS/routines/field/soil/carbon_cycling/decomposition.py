import math
from typing import Optional
from RUFAS.routines.field.soil.soil_data import SoilData


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
            The SoilData object used by this module to track the decomposition of carbon in the soil profile, creates
            new one if one is not provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

    def decompose(self) -> None:
        """
        Determines decomposition effect for each layer and temperature effect.

        Returns
        -------
        None
        """
        for layer in self.data.soil_layers:
            layer.decomposition_moisture_effect = self._calc_moisture_factor(layer.water_factor)
            layer.decomposition_temperature_effect = self._calc_temp_factor(layer.temperature)

    @staticmethod
    def _calc_temp_factor(layer_temp, x_inflection: float = 15.4, y_inflection: float = 11.75,
                          point_distance: float = 29.7, inflection_slope=0.03,
                          normalizer=20.80546) -> float:
        """
        Calculate the temperature factor for each layer.

        This function implements the "pseudocode_soil" S.6.A.1 and uses defaults drawn from defac: course soil.

        Parameters
        ----------
        layer_temp : float
            Temperature of the layer (Celsius).

        Returns
        -------
        float
            Temperature effect (unitless).

        Notes
        -----
        This temperature factor is lower-bounded at 0.0 because if negative, it may result in a negative amount
        of decomposition, which in this context would be considered a bug.
        """
        # S.6.A.4
        temp_factor = (y_inflection + (point_distance / math.pi) * math.atan(math.pi * inflection_slope * (
                layer_temp - x_inflection))) / normalizer
        return max(0.0, temp_factor)

    @staticmethod
    def _calc_moisture_factor(water_factor, a_term: float = 0.55, b_term: float = 1.7,
                              c_term: float = -0.007, first_exponent=6.648115,
                              second_exponent=3.22) -> float:
        """
        Calculate the moisture factor for carbon decomposition for the layer.

        This function implements the "pseudocode_soil" S.6.A.2 and uses defaults drawn from defac: course soil.

        Parameters
        ----------
        water_factor : float
            Relative water saturation (%).

        Returns
        -------
        float
            Moisture effect (unitless).

        Notes
        -----
        If negative bases are raised to exponents, they sometimes result in complex numbers instead of negative
        floats. This behavior can cause the program to crash. To avoid this, a sign correction factor is computed,
        allowing the absolute value of the bases to be used.

        The moisture effect is lower-bounded at 0 because if negative, it will lead to a negative decomposition factor,
        which is not meaningful.
        """
        # S.6.A.5
        base_1 = (water_factor - b_term) / (a_term - b_term)
        base_2 = (water_factor - c_term) / (a_term - c_term)

        sign_correction_factor = 1.0
        if (base_1 < 0.0 < base_2) or (base_1 > 0.0 > base_2):
            sign_correction_factor = -1.0

        first_term = abs(base_1) ** first_exponent
        second_term = abs(base_2) ** second_exponent

        return max(0.0, first_term * second_term * sign_correction_factor)
