from typing import Optional

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
