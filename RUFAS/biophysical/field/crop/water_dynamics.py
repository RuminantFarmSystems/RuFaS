from typing import Optional

from RUFAS.biophysical.field.crop.crop_data import CropData


class WaterDynamics:
    """
    Manages water dynamics related to crop growth, including water uptake, transpiration, and evaporation.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        An instance of `CropData` containing crop specifications and states relevant to water dynamics.
        If not provided, a default instance with generic parameters is used.
    cumulative_evapotranspiration : float, default 0.0
        Total water lost to evapotranspiration by the plant during the growing season (mm).

    Attributes
    ----------
    data : CropData
        Reference to the `CropData` instance used to access and modify water-related parameters and states
        for the crop.
    cumulative_evapotranspiration : float
        Total water lost to evapotranspiration by the plant during the growing season (mm).

    """

    def __init__(
        self,
        crop_data: Optional[CropData] = None,
        cumulative_evapotranspiration: float = 0.0,
    ):
        self.data = crop_data or CropData()
        self.cumulative_evapotranspiration = cumulative_evapotranspiration

    def cycle_water(
        self,
        evaporation: float,
        transpiration: float,
        potential_evapotranspiration: float,
    ) -> None:
        """
        Executes the daily cycling of water between the plants, soil, and environment.

        Parameters
        ----------
        evaporation : float
            Evaporation on a given day (mm).
        transpiration : float
            Transpiration on a given day (mm).
        potential_evapotranspiration : float
            Potential evapotranspiration on a given day (mm).

        Notes
        -----
        This method updates cumulative sums that are used to keep the water deficiency factor updated.

        """
        self.data.cumulative_evaporation += evaporation
        self.data.cumulative_transpiration += transpiration
        self.data.cumulative_potential_evapotranspiration += potential_evapotranspiration
        self.cumulative_evapotranspiration += self._determine_evapotranspiration(
            self.data.cumulative_evaporation, self.data.cumulative_transpiration
        )

        self.data.water_deficiency = self._determine_water_deficiency(
            self.data.cumulative_water_uptake,
            self.data.cumulative_potential_evapotranspiration,
        )

    def evaporate_from_canopy(self, potential_evapotranspiration: float) -> float:
        """Evaporates water from the canopy.

        Parameters
        ----------
        potential_evapotranspiration : float
            Evapotranspirative demand on the field on the current day (mm)

        Returns
        -------
        float
            Amount evaporated from canopy (mm)

        References
        ----------
        SWAT Theoretical documentation section 2:2.3.1

        Notes
        -----
        This method evaporates water from the crop's canopy until either 1) there is no more water in the canopy or 2)
        there is no more evapotranspirative demand. It then returns the amount of water that was evaporated from the
        canopy.

        """
        more_canopy_water_than_demand = self.data.canopy_water >= potential_evapotranspiration
        if more_canopy_water_than_demand:
            self.data.canopy_water -= potential_evapotranspiration
            return potential_evapotranspiration
        else:
            amount_evaporated = self.data.canopy_water
            self.data.canopy_water = 0
            return amount_evaporated

    def set_maximum_transpiration(self, potential_evapotranspiration_adjusted: float) -> None:
        """
        Sets the maximum transpiration based on the adjusted potential evapotranspiration of this day.

        Parameters
        ----------
        potential_evapotranspiration_adjusted : float
            Evapotranspirative demand remaining after evaporating water in the canopy (mm)

        References
        ----------
        SWAT Theoretical documentation section 2:2.3.2

        """
        self.data.max_transpiration = self._determine_maximum_transpiration(
            self.data.leaf_area_index, potential_evapotranspiration_adjusted
        )

    @staticmethod
    def _determine_maximum_transpiration(leaf_area_index: float, potential_evapotranspiration_adjusted: float) -> float:
        """
        Calculates the maximum transpiration for a given day.

        Parameters
        ----------
        leaf_area_index : float
            Leaf area index of the plant (unitless).
        potential_evapotranspiration_adjusted : float
            Potential evapotranspiration adjusted for evaporation of free water from the canopy (mm).

        Returns
        -------
        float
            Maximum transpiration (mm).

        References
        ----------
        SWAT 2:2.3.5, 6

        """
        if leaf_area_index <= 3:  # 2:2.3.5
            return (potential_evapotranspiration_adjusted * leaf_area_index) / 3
        else:  # 2:2.3.6
            return potential_evapotranspiration_adjusted

    @staticmethod
    def _determine_evapotranspiration(evaporation: float, transpiration: float) -> float:
        """
        Calculate evapotranspiration as the sum of evaporation and transpiration.

        Parameters
        ----------
        evaporation : float
            Evaporation (mm).
        transpiration : float
            Transpiration (mm).

        Returns
        -------
        float
            Total evapotranspiration (mm).

        """
        return evaporation + transpiration

    @staticmethod
    def _determine_water_deficiency(
        cumulative_evapotranspiration: float,
        cumulative_potential_evapotranspiration: float,
    ) -> float:
        """
        Calculate water deficiency factor.

        Parameters
        ----------
        cumulative_evapotranspiration : float
            Annual evapotranspiration (mm).
        cumulative_potential_evapotranspiration : float
            Maximum annual evapotranspiration (mm).

        Returns
        -------
        float
            Water deficiency factor (unitless).

        References
        ----------
        SWAT 5:3.3.2

        """
        if cumulative_potential_evapotranspiration != 0:
            return 100 * (cumulative_evapotranspiration / cumulative_potential_evapotranspiration)
        else:
            return 0
