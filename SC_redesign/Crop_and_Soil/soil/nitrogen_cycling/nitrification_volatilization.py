from typing import Optional
from math import exp

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module handles the nitrification and volatilization operations for the ammonium pool, based on SWAT section 3:1.3.
"""


class NitrificationVolatilization:

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track the nitrification and volatilization of ammonium, creates
            new one if one is not provided.
        field_size : float, optional
            Size of the field (ha)

        Notes
        -----
        The field size is used to initialize a SoilData object for this module to work with, if a pre-configured
        SoilData object is not provided.

        """
        self.data = soil_data or SoilData(field_size=field_size)

    # --- Static methods ---
    @staticmethod
    def _calculate_nitrification_volatilization_temp_factor(temperature: float) -> float:
        """Calculates the nitrification/volatilization temperature factor.

        Parameters
        ----------
        temperature : float
            Current temperature of the soil layer (degrees C)

        Returns
        -------
        float
            The nitrification/volatilization temperature factor of the current layer of soil (unitless)

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.1

        """
        return 0.41 * ((temperature - 5) / 10)

    @staticmethod
    def _calculate_nitrification_soil_water_factor(water_content: float, wilting_point: float,
                                                   field_capacity: float) -> float:
        """Calculates the soil water factor for nitrification.

        Parameters
        ----------
        water_content : float
            Water present in this soil layer (mm)
        wilting_point : float
            Amount of water in this soil layer when at wilting point (mm)
        field_capacity : float
            Amount of water in this soil layer when at field capacity (mm)

        Returns
        -------
        float
            The nitrification soil water factor (unitless)

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.2, 3

        """
        if water_content >= 0.25 * field_capacity - 0.75 * wilting_point:
            return 1.0
        upper_term = water_content - wilting_point
        bottom_term = 0.25 * (field_capacity - wilting_point)
        return upper_term / bottom_term

    @staticmethod
    def _calculate_volatilization_depth_factor(depth: float) -> float:
        """Calculates the depth factor for use in determining volatilization.

        Parameters
        ----------
        depth : float
            The depth of the center of this soil layer (mm)

        Returns
        -------
        float
            The volatilization depth factor (mm)

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.3.4

        """
        exponential_term = exp(4.706 - 0.0305 * depth)
        return 1 - (depth / (depth + exponential_term))
