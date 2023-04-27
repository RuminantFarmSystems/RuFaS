from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL

"""
This module handles the mineralization operations for the active and stable organic nitrogen pools, based on SWAT
section 3:1.2.1.
"""


class HumusMineralization:

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track phosphorus cycling, creates new one if one is not provided.
        field_size : float, optional
            Size of the field (ha)

        Notes
        -----
        Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is not
        provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

    def mineralize_organic_nitrogen(self) -> None:
        """Iterates through each layer in the soil profile, transfers nitrogen between active and stable organic
        nitrogen pools, and between the active organic and nitrate pools.

        """
        for layer in self.data.soil_layers:
            active_to_stable_mineralized_nitrogen = self._determine_intra_organic_mineralization(
                layer.active_organic_nitrogen_content, layer.stable_organic_nitrogen_content)
            layer.active_organic_nitrogen_content -= active_to_stable_mineralized_nitrogen
            layer.stable_organic_nitrogen_content += active_to_stable_mineralized_nitrogen

            active_to_nitrate_mineralized_nitrogen = self._determine_organic_to_nitrate_mineralization(
                layer.active_organic_nitrogen_content, layer.nutrient_cycling_temp_factor,
                layer.nutrient_cycling_water_factor, layer.humus_mineralization_rate_factor)
            layer.active_organic_nitrogen_content -= active_to_nitrate_mineralized_nitrogen
            layer.nitrate_content += active_to_nitrate_mineralized_nitrogen

    # --- Static methods ---
    @staticmethod
    def _determine_intra_organic_mineralization(active_organic_nitrogen: float,
                                                stable_organic_nitrogen: float) -> float:
        """Calculates the amount of nitrogen transferred between different organic pools.

        Parameters
        ----------
        active_organic_nitrogen : float
            Active organic nitrogen content of this soil layer (kg / ha)
        stable_organic_nitrogen : float
            Stable organic nitrogen content of this soil layer (kg / ha)

        Returns
        -------
        float
            The amount of nitrogen to transfer from the active to stable pool (kg / ha)

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.2.3

        Notes
        -----
        When the amount determined to be transferred is negative, it indicates that nitrogen is being transferred from
        the stable pool to the active pool.

        """
        rate_constant = 10 ** -5
        amount_transferred = rate_constant * active_organic_nitrogen * \
            ((1 / FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL) - 1) - stable_organic_nitrogen

        if amount_transferred > 0:
            amount_transferred = min(active_organic_nitrogen, amount_transferred)
        elif amount_transferred < 0:
            amount_transferred = -1 * min(stable_organic_nitrogen, -1 * amount_transferred)

        return amount_transferred

    @staticmethod
    def _determine_organic_to_nitrate_mineralization(active_organic_nitrogen: float, temperature_factor: float,
                                                     water_factor: float,
                                                     humus_active_organic_mineralization_coefficient: float) -> float:
        """Calculates phosphorus mineralized from the active inorganic pool that goes to the nitrate pool.

        Parameters
        ----------
        active_organic_nitrogen : float
            Active organic nitrogen content of this soil layer (kg / ha)
        temperature_factor : float
            The nutrient cycling temperature factor of this soil layer (unitless)
        water_factor : float
            The nutrient cycling water factor of this soil layer (unitless)
        humus_active_organic_mineralization_coefficient : float
            The rate coefficient for mineralization of the humus active organic nutrients (unitless)

        Returns
        -------
        float
            The amount of phosphorus mineralized from the active inorganic pool to be transferred to the nitrogen pool
            (kg / ha)

        References
        ----------
        SWAT Theoretical documentation eqn. 3:1.2.4

        """
        return humus_active_organic_mineralization_coefficient * ((temperature_factor * water_factor) ** 0.5) * \
            active_organic_nitrogen
