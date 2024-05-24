from typing import Optional
from math import exp

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.field.soil.soil_data import SoilData


class Denitrification:
    """
    A class to handle the denitrification process of nitrogen in the nitrates pool, as outlined in SWAT section 3:1.4.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track the denitrification of nitrates in the soil profile.
        If not provided, a new SoilData object will be created.
    field_size : float, optional
        The size of the field in hectares (ha). This is used to initialize a SoilData object if one is not provided.

    Attributes
    ----------
    data : SoilData
        The SoilData object used for tracking denitrification.

    Notes
    -----
    The field size is used to initialize a SoilData object for this module to work with, if a pre-configured
    SoilData object is not provided.

    """

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def denitrify(self) -> None:
        """
        Conducts the daily denitrification operations.

        References
        ----------
        SWAT Theoretical documentation section 3:1.4, eqn. 3:1.4.1, 2

        Notes
        -----
        The SWAT Theoretical documentation defines denitrification as "the bacterial reduction of nitrate, NO3-, to N2
        or N2O gases" (page 194). This method conducts denitrification by calculating the amount of nitrate that is
        denitrified, then removing that amount from the nitrate pool and adding it to denitrification emissions tracker.

        """
        self.data.set_vectorized_layer_attribute("nitrous_oxide_emissions", [0.0] * len(self.data.soil_layers))
        for layer in self.data.soil_layers:
            nutrient_is_below_threshold = (
                layer.nutrient_cycling_water_factor < layer.denitrification_threshold_water_content
            )
            if nutrient_is_below_threshold:
                continue

            nitrified_nitrates = self._calculate_denitrification_amount(
                layer.nitrate_content,
                layer.denitrification_rate_coefficient,
                layer.nutrient_cycling_temp_factor,
                layer.soil_overall_carbon_fraction,
            )
            layer.nitrate_content -= nitrified_nitrates
            layer.nitrous_oxide_emissions = nitrified_nitrates
            layer.annual_nitrous_oxide_emissions_total += nitrified_nitrates

    @staticmethod
    def _calculate_denitrification_amount(
        nitrate_content: float,
        denitrification_rate_coefficient: float,
        temp_factor: float,
        organic_carbon_fraction: float,
    ) -> float:
        """
        Calculates the amount of nitrate lost to denitrification.

        Parameters
        ----------
        nitrate_content : float
            The nitrate content of this soil layer (kg / ha).
        denitrification_rate_coefficient : float
            Rate coefficient that regulates denitrification in this layer of soil (unitless).
        temp_factor : float
            The nutrient cycling temperature factor of this soil layer (unitless).
        organic_carbon_fraction : float
            The fraction of this soil layer that is made up of organic carbon, in the range [0, 1.0] (unitless).

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
        the range [0.0, 1.0]. 0 is the minimum because a negative denitrification factor would indicate nitrous gases
        turning back into nitrate, which is not an operation that is handled by this module. 1 is the maximum because it
        is physically impossible to remove more nitrate than there is in the soil.

        """
        print(organic_carbon_fraction)
        exponential_term = exp(
            -1
            * denitrification_rate_coefficient
            * temp_factor
            * organic_carbon_fraction
            * GeneralConstants.FRACTION_TO_PERCENTAGE
        )
        denitrification_factor = 1 - exponential_term
        bounded_denitrification_factor = max(min(1.0, denitrification_factor), 0.0)
        return nitrate_content * bounded_denitrification_factor
