from math import exp, inf
from typing import Optional

from RUFAS.routines.field.soil.soil_data import SoilData


class MineralizationDecomposition:
    """
    This module is responsible for nitrogen mineralization and decomposition.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track nitrogen mineralization and decomposition, creates new one
        if one is not provided.
    field_size : float, optional
        Size of the field (ha).

    Attributes
    ----------
    data : SoilData
        The SoilData object used by this module to track nitrogen mineralization and decomposition.

    """

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def mineralize_and_decompose_nitrogen(self) -> None:
        """
        Conducts the daily mineralization and decomposition operations on the fresh organic nitrogen and residue in
        the top soil layer.

        References
        ----------
        SWAT Theoretical documentation section 3:1.2.2, specifically eqn. 3:1.2.9 (used to determine how much nitrogen
        gets transferred to the nitrate and active inorganic pools).

        """
        self._correct_fresh_organic_nitrogen_pools()

        if self.data.soil_layers[0].temperature <= 0:
            return

        carbon_nitrogen_ratio = self._calculate_residue_nutrient_ratio(
            self.data.soil_layers[0].carbon_residue_amount,
            self.data.soil_layers[0].fresh_organic_nitrogen_content,
            self.data.soil_layers[0].nitrate_content,
        )
        carbon_phosphorus_ratio = self._calculate_residue_nutrient_ratio(
            self.data.soil_layers[0].carbon_residue_amount,
            self.data.soil_layers[0].fresh_organic_phosphorus_content,
            self.data.soil_layers[0].labile_inorganic_phosphorus_content,
        )

        residue_composition_factor = self._calculate_nutrient_cycling_residue_composition_factor(
            carbon_nitrogen_ratio, carbon_phosphorus_ratio
        )

        decay_rate_constant = self._calculate_decay_rate_constant(
            self.data.soil_layers[0].residue_fresh_organic_mineralization_rate,
            residue_composition_factor,
            self.data.soil_layers[0].nutrient_cycling_temp_factor,
            self.data.soil_layers[0].nutrient_cycling_water_factor,
        )

        fresh_organic_nitrogen_removed = decay_rate_constant * self.data.soil_layers[0].fresh_organic_nitrogen_content
        fresh_organic_nitrogen_removed = min(
            self.data.soil_layers[0].fresh_organic_nitrogen_content,
            fresh_organic_nitrogen_removed,
        )

        self.data.soil_layers[0].fresh_organic_nitrogen_content -= fresh_organic_nitrogen_removed
        self.data.soil_layers[0].nitrate_content += 0.8 * fresh_organic_nitrogen_removed
        self.data.soil_layers[0].active_organic_nitrogen_content += 0.2 * fresh_organic_nitrogen_removed

    def _correct_fresh_organic_nitrogen_pools(self) -> None:
        """
        Ensures that no fresh organic nitrogen is kept in subsurface pools.

        Notes
        -----
        SWAT only simulates fresh organic nitrogen in the surface soil layer. This method ensures that RuFaS transfers
        any fresh organic nitrogen that makes it below the surface soil layer into the active organic nitrogen pool.
        This behavior is consistent with the way that sub-surface nitrogen from plant residue is handled in :class
        CropManagement:.

        """
        for layer in self.data.soil_layers[1:]:
            layer.active_organic_nitrogen_content += layer.fresh_organic_nitrogen_content
            layer.fresh_organic_nitrogen_content = 0.0

    # --- Static methods ---
    @staticmethod
    def _calculate_residue_nutrient_ratio(
        carbon_amount: float, organic_nutrient: float, inorganic_nutrient: float
    ) -> float:
        """
        Calculates the ratio carbon to the nutrient passed in the soil layer.

        Parameters
        ----------
        carbon_amount : float
            Amount of carbon in the soil layer (kg / ha).
        organic_nutrient : float
            Amount of organic nutrients in the soil layer (kg / ha).
        inorganic_nutrient : float
            Amount of inorganic nutrients in the soil layer (kg / ha).

        Returns
        -------
        float
            The residue nutrient ratio for the nutrient passed (unitless).

        References
        ----------
        SWAT Theoretical documentation, eqn. 3:1.2.5, 6

        Notes
        -----
        The equations for determining the carbon-nitrogen ratio and carbon-phosphorus ratio are identical in structure
        so they have been implemented in the same method, hence why this method takes in a generic nutrient. Also, if
        there are no nutrients in the soil, the carbon to nutrient ratio is set to be infinite.

        """
        nutrient_total = organic_nutrient + inorganic_nutrient
        if nutrient_total == 0.0:
            return inf
        return carbon_amount / nutrient_total

    @staticmethod
    def _calculate_nutrient_term_for_residue_composition_factor(nutrient_ratio: float, constant_term: float) -> float:
        """
        Calculates terms that used to determine the nutrient cycling composition factor.

        Parameters
        ----------
        nutrient_ratio : float
            The ratio of carbon to a specific nutrient (unitless).
        constant_term : float
            The constant term used in this equation (unitless).

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
    def _calculate_nutrient_cycling_residue_composition_factor(
        carbon_nitrogen_ratio: float, carbon_phosphorus_ratio: float
    ) -> float:
        """
        Calculates the residue composition factor for use in computing the decay rate constant.

        Parameters
        ----------
        carbon_nitrogen_ratio : float
            Ratio of carbon to nitrogen in this layer of the soil profile (unitless).
        carbon_phosphorus_ratio : float
            Ratio of carbon to phosphorus in this layer of the soil profile (unitless).

        Returns
        -------
        The nutrient cycling residue composition factor (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.2.8

        Notes
        -----
        The values of the constant used to determine the nitrogen and phosphorus terms are 25 and 200, respectively.

        """
        nitrogen_term = (  # noqa: F841
            MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor(
                carbon_nitrogen_ratio, 25
            )
        )
        phosphorus_term = (  # noqa: F841
            MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor(  # noqa: F841, E501
                carbon_phosphorus_ratio, 200
            )
        )
        # temporary fix to replace the process based method for the effect of the soil C, N, and P on the decomposition
        # rate factor
        return 1

    @staticmethod
    def _calculate_decay_rate_constant(
        fresh_organic_residue_mineralization_rate: float,
        residue_composition_factor: float,
        temp_factor: float,
        moisture_factor,
    ) -> float:
        """
        Calculates the decay rate constant for residue.

        Parameters
        ----------
        fresh_organic_residue_mineralization_rate : float
            Rate coefficient for mineralization of fresh organic nutrients from residue (unitless).
        residue_composition_factor : float
            Nutrient cycling residue composition factor for the current soil layer (unitless).
        temp_factor : float
            Nutrient cycling temperature factor for the current soil layer (unitless).
        moisture_factor : float
            Nutrient cycling water factor for the current soil layer (unitless).

        Returns
        -------
        The decay rate constant for residue decomposition (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.2.7

        Notes
        -----
        The definition for the rate coefficient for mineralization of the residue fresh organic nutrients can be found
        in the SWAT Input .BSN file (see "RSDCO" on page 101) and SWAT Input CROP.DAT file (see "RSDCO_PL" on page 205).

        """
        square_root_factor = (temp_factor * moisture_factor) ** 0.5
        return fresh_organic_residue_mineralization_rate * residue_composition_factor * square_root_factor
