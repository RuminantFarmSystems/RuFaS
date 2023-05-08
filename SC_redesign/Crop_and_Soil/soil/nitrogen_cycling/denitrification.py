from typing import Optional
from math import exp

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module handles the denitrification of nitrogen in the nitrates pool, based on SWAT section 3:1.4.
"""


class Denitrification:

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track the denitrification of nitrates in the soil profile,
            creates new one if one is not provided.
        field_size : float, optional
            Size of the field (ha)

        Notes
        -----
        The field size is used to initialize a SoilData object for this module to work with, if a pre-configured
        SoilData object is not provided.

        """
        self.data = soil_data or SoilData(field_size=field_size)

    def do_denitrification(self) -> None:
        """Conducts the daily denitrification operations.

        References
        ----------
        SWAT Theoretical documentation section 3:1.4, eqn. 3:1.4.1, 2

        """
        for layer in self.data.soil_layers:
            if layer.nutrient_cycling_water_factor < layer.denitrification_threshold_water_content:
                continue

            # TODO: check that soil_overall_carbon_fraction is being used correctly in this context - issue #475
            nitrified_nitrates = self._calculate_nitrification_amount(layer.nitrate_content,
                                                                      layer.denitrification_rate_coefficient,
                                                                      layer.nutrient_cycling_temp_factor,
                                                                      layer.soil_overall_carbon_fraction * 100)
            layer.nitrate_content -= nitrified_nitrates
            layer.annual_denitrified_nitrogen_total += nitrified_nitrates

    # --- Static methods ---
    @staticmethod
    def _calculate_nitrification_amount(nitrate_content: float, denitrification_rate_coefficient: float,
                                        temp_factor: float, percent_organic_carbon_content: float) -> float:
        """This method calculates the amount of nitrate lost to denitrification.

        Parameters
        ----------
        nitrate_content : float
            The nitrate content of this soil layer (kg / ha)
        denitrification_rate_coefficient : float
            Rate coefficient that regulates denitrification in this layer of soil (unitless)
        temp_factor : float
            The nutrient cycling temperature factor of this soil layer (unitless)
        percent_organic_carbon_content : float
            The percent of this soil layer that is made up of organic carbon, in the range [0, 100] (unitless)

        Returns
        -------
        float
            The amount of nitrate that is denitrified in this soil layer (kg / ha)

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.4.1

        Notes
        -----
        This calculates the fraction of nitrates lost to nitrification as nitrification factor, and bounds it to be in
        the range [0.0, 1.0].

        """
        exponential_term = exp(-1 * denitrification_rate_coefficient * temp_factor * percent_organic_carbon_content)
        nitrification_factor = max(min(1.0, (1 - exponential_term)), 0.0)
        return nitrate_content * nitrification_factor
