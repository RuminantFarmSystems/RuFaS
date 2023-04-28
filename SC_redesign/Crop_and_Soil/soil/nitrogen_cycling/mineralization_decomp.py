from typing import Optional
from math import exp

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


class MineralizationDecomposition:

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track nitrogen mineralization and decomposition, creates new one
            if one is not provided.
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
    def _calculate_residue_nutrient_ratio(carbon_amount: float, organic_nutrient: float,
                                          inorganic_nutrient: float) -> float:
        """Calculates the ratio carbon to the nutrient passed in the soil layer.

        Parameters
        ----------
        carbon_amount : float
            Amount of carbon in the soil layer (kg / ha)
        organic_nutrient : float
            Amount of organic nutrients in the soil layer (kg / ha)
        inorganic_nutrient : float
            Amount of inorganic nutrients in the soil layer (kg / ha)

        Returns
        -------
        float
            The residue nutrient ratio for the nutrient passed (unitless)

        References
        ----------
        SWAT Theoretical documentation, eqn. 3:1.2.5, 6

        Notes
        -----
        The equations for determining the carbon-nitrogen ratio and carbon-phosphorus ratio are identical in structure
        so they have been implemented in the same method, hence why this method takes in a generic nutrient.

        TODO: In SWAT, this method takes the amount of residue in the soil (instead of carbon) and multiplies it by 0.58
            to get the amount of carbon in the soil. This method should be refactored to do that when we get a tracker
            for residue in LayerData.

        """
        nutrient_total = organic_nutrient + inorganic_nutrient
        if nutrient_total == 0:
            nutrient_total = 0.000_001
        return carbon_amount / nutrient_total

    @staticmethod
    def _calculate_nutrient_term_for_residue_composition_factor(nutrient_ratio: float, constant_term: float) -> float:
        """Calculates terms that used to determine the nutrient cycling composition factor.

        Parameters
        ----------
        nutrient_ratio : float
            The ratio of carbon to a specific nutrient (unitless)
        constant_term : float
            The constant term used in this equation (unitless)

        Returns
        -------
        float
            One of the terms used in the equation to calculate the nutrient cycling residue composition factor.

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.2.8

        Notes
        -----
        This is a helper method for the method that actually calculates the nutrient cycling residue composition factor.
        It is used for both the nitrogen and phosphorus terms, hence why it takes a generic "nutrient_ratio" and
        different constants.

        When calculating the nitrogen term, the constant is 25. For phosphorus, it is 200.

        """
        inner_term = -0.693 * ((nutrient_ratio - constant_term) / constant_term)
        return exp(inner_term)

    @staticmethod
    def _calculate_nutrient_cycling_residue_composition_factor(carbon_nitrogen_ratio, carbon_phosphorus_ratio) -> float:
        """Calculates the residue composition factor for use in computing the decay rate constant.

        Parameters
        ----------
        carbon_nitrogen_ratio : float
            Ratio of carbon to nitrogen in this layer of the soil profile (unitless)
        carbon_phosphorus_ratio : float
            Ratio of carbon to phosphorus in this layer of the soil profile (unitless)

        Returns
        -------
        The nutrient cycling residue composition factor (unitless)

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.2.8

        Notes
        -----
        The values of the constant used to determine the nitrogen and phosphorus terms are 25 and 200, respectively.

        """
        nitrogen_term = MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor(
            carbon_nitrogen_ratio, 25)
        phosphorus_term = MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor(
            carbon_phosphorus_ratio, 200)
        return min(nitrogen_term, phosphorus_term, 1.0)

    @staticmethod
    def _calculate_decay_rate_constant(fresh_organic_residue_mineralization_rate: float, composition_factor: float,
                                       temp_factor: float, water_factor) -> float:
        """Calculates the decay rate constant for residue.

        Parameters
        ----------
        fresh_organic_residue_mineralization_rate : float
            Rate coefficient for mineralization of fresh organic nutrients (unitless)
        composition_factor : float
            Nutrient cycling residue composition factor for the current soil layer (unitless)
        temp_factor : float
            Nutrient cycling temperature factor for the current soil layer (unitless)
        water_factor : float
            Nutrient cycling water factor for the current soil layer (unitless)

        Returns
        -------
        The decay rate constant for residue decomposition (unitless)

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.2.7

        Notes
        -----
        The definition for the rate coefficient for mineralization of the residue fresh organic nutrients can be found
        in the SWAT Input .BSN file (see "RSDCO" on page 101) and SWAT Input CROP.DAT file (see "RSDCO_PL" on page 205)

        """
        root_term = (temp_factor * water_factor) ** 0.5
        return fresh_organic_residue_mineralization_rate * composition_factor * root_term
