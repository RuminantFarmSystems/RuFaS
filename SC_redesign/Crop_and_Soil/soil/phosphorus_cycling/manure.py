from typing import Optional
from math import exp, sqrt

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module adds and tracks manure phosphorus dynamics based on the SurPhos model.
"""


class Manure:

    def __init__(self, soil_data: Optional[SoilData] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track manure phosphorus activity, creates new one if one is not
            provided.

        """
        self.data = soil_data or SoilData()

    # --- Static Methods ---
    @staticmethod
    def _determine_temperature_factor(avg_air_temperature: float) -> float:
        """Calculates the temperature factor for the current day

        Parameters
        ----------
        avg_air_temperature : float
            The average air temperature of the current day (degrees celsius).

        Returns
        -------
        float
            The temperature factor on the current day (unitless)

        References
        ----------
        SurPhos [2], pseudocode_soil [S.5.D.I.1]

        """
        calculated_temperature_factor = ((2 * (32 ** 2) * (avg_air_temperature ** 2)) - (avg_air_temperature ** 4)) / \
                                        (32 ** 4)
        return min(1.0, max(0.0, calculated_temperature_factor))

    @staticmethod
    def determine_dry_matter_decomposition_rate(temperature_factor: float) -> float:
        """Calculates the rate of manure dry matter decomposition on the current day.

        Parameters
        ----------
        temperature_factor : float
            The temperature factor on the current day (unitless)

        Returns
        -------
        float
            The rate of manure dry matter decomposition on the current day (unitless)

        References
        ----------
        SurPhos [1], pseudocode_soil [S.5.D.III.4]

        """
        return 0.003 * (temperature_factor ** 0.5)

    @staticmethod
    def determine_dry_manure_matter_assimilation(moisture_factor: float, temperature_factor: float,
                                                 manure_cover_area: float, is_dung: bool) -> float:
        """Calculates the mass of dry manure matter applied by machine assimilated into the soil that day

        Parameters
        ----------
        moisture_factor : float
            Manure moisture factor, in range [0.0, 1.0] (unitless)
        temperature_factor : float
            The temperature factor on the current day (unitless)
        manure_cover_area : float
            Area of the field covered by manure (ha)
        is_dung : bool
            Was the manure being assimilated applied via animal (true / false)

        Returns
        -------
        float
            The amount of manure dry matter that is assimilated into the soil by macroinvertebrates (bioturbation) on
            the current day (kg)

        References
        ----------
        SurPhos [3, 7], pseudocode_soil [S.5.D.III.4] (Note the equation in the pseudocode is wrong)

        """
        if is_dung:
            exponential_term = exp(3.5 * sqrt(moisture_factor))
            temperature_term = temperature_factor ** 0.1
        else:
            exponential_term = exp(2.5 * moisture_factor)
            temperature_term = temperature_factor
        return (30 * exponential_term) * temperature_term * manure_cover_area
