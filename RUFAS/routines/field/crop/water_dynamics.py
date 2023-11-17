from typing import Optional
from RUFAS.routines.field.crop.crop_data import CropData


# TODO: This module needs to be updated to include water uptake by plants and evapotranspiration (implemented in Field?)

class WaterDynamics:
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    def cycle_water(self, evaporation: float, transpiration: float, potential_evapotranspiration: float) -> None:
        """executes the daily cycling of water between the plants, soil, and environment

        Args:
            evaporation: evaporation on a given day in mm
            transpiration: transpiration on a given day in mm
            potential_evapotranspiration: potential evapotranspiration on a given day in mm

        """
        self.data.cumulative_evaporation += evaporation
        self.data.cumulative_transpiration += transpiration
        self.data.cumulative_potential_evapotranspiration += potential_evapotranspiration
        self.data.cumulative_evapotranspiration += \
            self._determine_evapotranspiration(self.data.cumulative_evaporation,
                                               self.data.cumulative_transpiration)
        self.data.water_deficiency = self._determine_water_deficiency(self.data.cumulative_evapotranspiration,
                                                                      self.data.cumulative_potential_evapotranspiration)
        actual_transpiration = min(self.data.water_content, self.data.max_transpiration)
        self.data.actual_transpiration = actual_transpiration
        self.data.water_content -= actual_transpiration

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
        """Sets the maximum transpiration based on the adjusted potential evapotranspiration of this day.

        Parameters
        ----------
        potential_evapotranspiration_adjusted : float
            Evapotranspirative demand remaining after evaporating water in the canopy (mm)

        References
        ----------
        SWAT Theoretical documentation section 2:2.3.2

        """
        self.data.max_transpiration = self._determine_maximum_transpiration(self.data.leaf_area_index,
                                                                            potential_evapotranspiration_adjusted)

    @staticmethod
    def _determine_maximum_transpiration(leaf_area_index, potential_evapotranspiration_adjusted: float) -> float:
        """calculates the maximum transpiration for a given day

        Args:
            leaf_area_index: leaf area index of plant, unitless
            potential_evapotranspiration_adjusted: potential evapotranspiration adjusted for evaporation of free water
                the canopy in mm

        Returns:
            maximum transpiration in mm

        SWAT Reference: 2:2.3.5, 6
        """
        if leaf_area_index <= 3:  # 2:2.3.5
            return (potential_evapotranspiration_adjusted * leaf_area_index) / 3
        else:  # 2:2.3.6
            return potential_evapotranspiration_adjusted

    @staticmethod
    def _determine_evapotranspiration(evaporation: float, transpiration: float) -> float:
        # TODO: belongs in Soil class? - GitHub Issue #303
        """
        Description: calculate the annual evapotranspiration #TODO: why is this 'annual' routine executed every day?

        Args:
            evaporation: evaporation
            transpiration: transpiration

        Returns: total evapotranspiration

        TODO: find where SWAT has this equation (if it does, if not make note of assumption)
        """
        return evaporation + transpiration

    @staticmethod
    def _determine_water_deficiency(cumulative_evapotranspiration: float,
                                    cumulative_potential_evapotranspiration: float) -> float:
        """
        Description: calculate water deficiency factor

        SWAT Reference: 5:3.3.2

        Args:
            cumulative_evapotranspiration: annual evapotranspiration
            cumulative_potential_evapotranspiration: maximum annual evapotranspiration

        Returns: water deficiency factor
        """
        if cumulative_potential_evapotranspiration != 0:
            return 100 * (cumulative_evapotranspiration / cumulative_potential_evapotranspiration)
        else:
            return 0

    # TODO: Further functions water files need to be translated (into soil methods?) - GitHub Issue #303
    #    RUFAS/routines/field/crop/transpiration.py
    #    No water uptake yet?
