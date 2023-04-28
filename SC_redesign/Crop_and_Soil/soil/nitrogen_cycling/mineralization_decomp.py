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
        return carbon_amount / (organic_nutrient + inorganic_nutrient)

    # @staticmethod
    # def _calculate_nutrient_cycling_residue_composition_factor(carbon_nitrogen_ratio, carbon_phosphorus_ratio) -> float:
    #     """Calculates the residue composition factor for use in computing the decay rate constant.
    #
    #     Parameters
    #     ----------
    #     carbon_nitrogen_ratio : float
    #
    #     carbon_phosphorus_ratio
    #
    #     Returns
    #     -------
    #
    #     """