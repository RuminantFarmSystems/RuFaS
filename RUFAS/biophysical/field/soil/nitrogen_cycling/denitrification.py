from math import atan, e, exp, pi
from typing import Optional

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData


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

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None) -> None:
        self.data = soil_data or SoilData(field_size=field_size)

    def denitrify(self, field_size: float) -> None:
        """
        Conducts the daily denitrification operations.

        Parameters
        ----------
        field_size : float
            Size of the field (ha).

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
        self.data.set_vectorized_layer_attribute("dinitrogen_emissions", [0.0] * len(self.data.soil_layers))
        for layer in self.data.soil_layers:
            nutrient_is_below_threshold = (
                layer.nutrient_cycling_water_factor < self.data.denitrification_threshold_water_content
            )
            if nutrient_is_below_threshold:
                continue

            denitrified_nitrates = self._calculate_denitrification_amount(
                layer.nitrate_content,
                self.data.denitrification_rate_coefficient,
                layer.nutrient_cycling_temp_factor,
                layer.soil_overall_carbon_fraction,
            )

            nitrate_concentration_mg_per_kg = LayerData.determine_soil_nutrient_concentration(
                layer.nitrate_content, layer.bulk_density, layer.layer_thickness, field_size
            )

            # Milligrams per kilogram is equivalent to micrograms per gram
            nitrate_denitrification_partitioning_effect = self._calculate_nitrate_effect(
                nitrate_concentration_mg_per_kg
            )
            carbon_denitrification_partitioning_effect = self._calculate_carbon_effect(layer.carbon_emissions)
            moisture_denitrification_partitioning_effect = self._calculate_moisture_effect(
                layer.water_filled_pore_space
            )
            pH_denitrification_partitioning_effect = self._calculate_pH_effect(layer.pH)
            partitioning_factor = self._calculate_partitioning_factor(
                nitrate_denitrification_partitioning_effect,
                carbon_denitrification_partitioning_effect,
                moisture_denitrification_partitioning_effect,
                pH_denitrification_partitioning_effect,
            )

            nitrous_oxide_emissions = self._calculate_nitrous_oxide_emissions(denitrified_nitrates, partitioning_factor)

            layer.nitrate_content -= denitrified_nitrates
            layer.nitrous_oxide_emissions = nitrous_oxide_emissions
            layer.dinitrogen_emissions = denitrified_nitrates - nitrous_oxide_emissions
            layer.annual_nitrous_oxide_emissions_total += nitrous_oxide_emissions

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
        exponential_term = exp(-1 * denitrification_rate_coefficient * temp_factor * organic_carbon_fraction)
        denitrification_factor = 1 - exponential_term
        bounded_denitrification_factor = max(min(1.0, denitrification_factor), 0.0)
        return nitrate_content * bounded_denitrification_factor

    def _calculate_nitrate_effect(self, nitrate_content: float) -> float:
        """
        Calculates the effect that the soil nitrate level has on the ratio of nitrous oxide to dinitrogen in denitrified
        nitrates.

        Parameters
        ----------
        nitrate_content : float
            Amount of nitrates (ug N / g soil).

        Returns
        -------
        float
            Effect of the soil nitrate level on the ratio of nitrous oxide to dinitrogen (unitless).

        Notes
        -----
        The equation here differs from what was published in Parton et al, [1]. During implementation it was discovered
        that the equation they published was producing invalid results due to a missing pair of parentheses.

        References
        ----------
        .. [1] Parton, W. J., et al. "Generalized model for N2 and N2O production from nitrification and
           denitrification." Global biogeochemical cycles 10.3 (1996): 401-412.

        """
        fractional_term = atan(pi * 0.01 * (nitrate_content - 190)) / pi

        return (1.0 - (0.5 + fractional_term)) * 25

    def _calculate_carbon_effect(self, carbon_respiration: float) -> float:
        """
        Calculates the effect that the soil carbon respiration has on the ratio of nitrous oxide to dinitrogen in
        denitrified nitrates.

        Parameters
        ----------
        carbon_respiration : float
            Carbon respiration from the soil layer (kg / ha).

        Returns
        -------
        float
            Effect of the soil carbon level on the ratio of nitrous oxide to dinitrogen (unitless).

        References
        ----------
        .. Wagena, Moges B., et al. "Development of a nitrous oxide routine for the SWAT model to assess greenhouse gas
           emissions from agroecosystems." Environmental modelling & software 89 (2017): 131-143.

        """
        carbon_respiration_grams = carbon_respiration * GeneralConstants.KG_TO_GRAMS
        numerator = 30.78 * atan(pi * 0.07 * (carbon_respiration_grams - 13))

        return 13 + numerator / pi

    def _calculate_moisture_effect(self, water_filled_pore_space: float) -> float:
        """
        Calculates the effect that the moisture level has on the ratio of nitrous oxide to dinitrogen in denitrified
        nitrates.

        Parameters
        ----------
        water_filled_pore_space : float
            Fraction of pore space that is occupied by water in the soil layer (unitless).

        Returns
        -------
        float
            Effect of the soil carbon level on the ratio of nitrous oxide to dinitrogen (unitless).

        Notes
        -----
        If the water-filled pore space is 0, then the moisture effect is 0.0.

        References
        ----------
        .. Wagena, Moges B., et al. "Development of a nitrous oxide routine for the SWAT model to assess greenhouse gas
           emissions from agroecosystems." Environmental modelling & software 89 (2017): 131-143.

        """
        if water_filled_pore_space == 0.0:
            return 0.0

        fraction = 17 / (13 ** (2.2 * water_filled_pore_space))

        return 1.4 / (13**fraction)

    def _calculate_pH_effect(self, pH: float) -> float:
        """
        Calculates the effect that the soil pH has on the ratio of nitrous oxide to dinitrogen in denitrified nitrates.

        Parameters
        ----------
        pH : float
            pH of the soil layer.

        Returns
        -------
        float
            Effect of the soil carbon level on the ratio of nitrous oxide to dinitrogen (unitless).

        References
        ----------
        .. Wagena, Moges B., et al. "Development of a nitrous oxide routine for the SWAT model to assess greenhouse gas
           emissions from agroecosystems." Environmental modelling & software 89 (2017): 131-143.

        """
        denominator: float = 1470 * e ** (-1.1 * pH)

        return 1 / denominator

    def _calculate_partitioning_factor(
        self, nitrate_effect: float, carbon_effect: float, moisture_effect: float, pH_effect: float
    ) -> float:
        """
        Calculates the factor used to determine the ratio of nitrous oxide to dinitrogen.

        Parameters
        ----------
        nitrate_effect : float
            Effect of the nitrate level (unitless).
        carbon_effect : float
            Effect of the carbon level (unitless).
        moisture_effect : float
            Effect of the moisture level (unitless).
        pH_effect : float
            Effect of the pH (unitless).

        Returns
        -------
        float
            Factor used to partition nitrified nitrates into nitrous oxide and dinitrogen.

        References
        ----------
        .. Wagena, Moges B., et al. "Development of a nitrous oxide routine for the SWAT model to assess greenhouse gas
           emissions from agroecosystems." Environmental modelling & software 89 (2017): 131-143.

        """
        partitioning_factor = min(nitrate_effect, carbon_effect) * moisture_effect * pH_effect

        return partitioning_factor

    def _calculate_nitrous_oxide_emissions(self, denitrified_nitrates: float, partitioning_factor: float) -> float:
        """
        Calculates the quantity of denitrified nitrates that are nitrous oxide.

        Parameters
        ----------
        denitrified_nitrates : float
            Amount of nitrates that have been denitrified (kg / ha).
        partitioning_factor : float
            Factor used to determine how much of the denitrified nitrates are nitrous oxide (unitless).

        Returns
        -------
        float
            Amount of nitrous oxide emissions (kg / ha).

        References
        ----------
        .. Wagena, Moges B., et al. "Development of a nitrous oxide routine for the SWAT model to assess greenhouse gas
           emissions from agroecosystems." Environmental modelling & software 89 (2017): 131-143.

        """
        nitrates = denitrified_nitrates * GeneralConstants.KG_TO_GRAMS
        n2o_grams = nitrates / (1 + partitioning_factor)
        return n2o_grams * GeneralConstants.GRAMS_TO_KG
