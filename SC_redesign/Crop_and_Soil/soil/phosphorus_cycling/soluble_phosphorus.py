from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module tracks the movement of phosphorus in the soil profile based on equations from APLE.
"""


class SolublePhosphorus:

    def __init__(self, soil_data: Optional[SoilData] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track manure phosphorus activity, creates new one if one is not
            provided.

        """
        self.data = soil_data or SoilData()

    # --- Static methods ---
    @staticmethod
    def _determine_isotherm_slope(percent_clay_content: float) -> float:
        """Calculates the slope of the linear phosphorus sorption isotherm.

        Parameters
        ----------
        percent_clay_content : float
            Percent clay content of a soil layer, expressed in the range [0, 100] (unitless)

        Returns
        -------
        float
            The slope of the phosphorus sorption isotherm (unitless)

        References
        ----------
        APLE Theoretical Documentation eqn. [15]

        """
        return 173.51 * (percent_clay_content / 100) + 8.48

    @staticmethod
    def _determine_isotherm_intercept(isotherm_slope: float) -> float:
        """Calculates the intercept of the linear phosphorus sorption isotherm.

        Parameters
        ----------
        isotherm_slope : float
            The slope of the phosphorus sorption isotherm (unitless)

        Returns
        -------
        float
            The intercept of the phosphorus sorption isotherm (unitless)

        References
        ----------
        APLE Theoretical Documentation eqn. [15]

        """
        return 4.726 * isotherm_slope - 8.97
