import math
from typing import Optional

from RUFAS.biophysical.field.soil.soil_data import SoilData


class Decomposition:
    """
    This class is responsible for calculating the factors related carbon decomposition rate.

    Parameters
    ----------
    soil_data : SoilData, optional
        An instance of SoilData containing soil properties and carbon pool information. A new instance is created if not
        provided.
    field_size : float, optional, default None
        The size of the field in hectares (ha). This is used to initialize a SoilData object if one is not provided.

    Attributes
    ----------
    data : SoilData
        The SoilData instance being used by this module. Contains information about the soil's properties, carbon pools,
        and other relevant data for simulating decomposition.

    References
    ----------
    Excel file in Basecamp, located at "Ruminant Farm Systems Model (RuFaS) › Docs & Files › Scientific Documentation ›
    Soil and Crop Module › Literature › Carbon Models › DAYCENT"

    Notes
    -----
    The equations for this model, referenced in the soil psuedocode, are derived from an
    `excel file <https://3.basecamp.com/3486446/buckets/5296287/vaults/2740532358>`_ on Basecamp, but the meaning (and
    validity) of terms is extremely unclear from both sources. The documentation cannot be adequately completed without
    a better understanding of these methods.

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def decompose(self) -> None:
        """
        Determines decomposition effect for each layer and temperature effect.

        """
        for layer in self.data.soil_layers:
            layer.decomposition_moisture_effect = self._calc_moisture_factor(layer.water_factor)
            layer.decomposition_temperature_effect = self._calc_temp_factor(layer.temperature)

    @staticmethod
    def _calc_temp_factor(
        layer_temp,
        x_inflection: float = 15.4,
        y_inflection: float = 11.75,
        point_distance: float = 29.7,
        inflection_slope=0.03,
        normalizer=20.80546,
    ) -> float:
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
        temp_factor = (
            y_inflection
            + (point_distance / math.pi) * math.atan(math.pi * inflection_slope * (layer_temp - x_inflection))
        ) / normalizer
        return max(0.0, temp_factor)

    @staticmethod
    def _calc_moisture_factor(
        water_factor,
        a_term: float = 0.55,
        b_term: float = 1.7,
        c_term: float = -0.007,
        first_exponent=6.648115,
        second_exponent=3.22,
    ) -> float:
        """
        Calculate the moisture factor for carbon decomposition for the layer.

        This function implements the "pseudocode_soil" S.6.A.2 and uses defaults drawn from defac: course soil.

        Parameters
        ----------
        water_factor : float
            Relative water saturation (%).
        a_term : float, default 0.55
            Coarse in defac row 3, column N
        b_term : float, default 1.7
            Coarse in defac row 4, column N
        c_term : float, default -0.007
            Coarse in defac row 5, column
        first_exponent : float, default 6.648115
            First exponent in defac spreadsheet
        second_exponent : float, default 3.22
            Second exponent in defac spreadsheet

        Returns
        -------
        float
            Moisture factor (unitless).

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
