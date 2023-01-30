from SC_redesign.Crop_and_Soil.soil.soil import Soil
from typing import Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData


# TODO: This module needs to be updated to include water uptake by plants and evapotranspiration (implemented in Field?)

class WaterDynamics:
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()  # initialize with defaults, if not given

    def cycle_water(self, evaporation: float, transpiration: float, max_evapotranspiration: float,
                    potential_evapotranspiration_adjusted: float) -> None:
        self.data.cumulative_evaporation = evaporation
        self.data.cumulative_transpiration = transpiration
        self.data.max_cumulative_evapotranspiration = max_evapotranspiration
        self.data.cumulative_evapotranspiration = self._determine_evapotranspiration(self.data.cumulative_evaporation,
                                                                                     self.data.cumulative_transpiration)
        self.data.water_deficiency = self._determine_water_deficiency(self.data.cumulative_evapotranspiration,
                                                                      self.data.max_cumulative_evapotranspiration)
        # @CHECKME: cumumlative evaporation, transpiration, evapotranspiration, and maximum cumulative
        # evapotranspiration are all listed as yearly totals, but maximum transpiration is a daily value.
        # Do they need to calculated in separate methods?
        self.data.max_transpiration = self._determine_maximum_transpiration(self.data.leaf_area_index,
                                                                            potential_evapotranspiration_adjusted)

    @staticmethod
    def _determine_maximum_transpiration(leaf_area_index, potential_evapotranspiration_adjusted: float) -> float:
        """calculates the maximum transpiration for a given day

        Args:
            leaf_area_index: leaf area index of plant, unitless
            potential_evapotranspiration_adjusted: potential evapotranspiration adjusted for evaporation of free water
            the canopy in mm
             - Note: this value will eventually be calculated in evapotranspiration.py - issue #313

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
        """
        return evaporation + transpiration

    @staticmethod
    def _determine_water_deficiency(evapotranspiration: float,
                                    max_evapotranspiration: float) -> float:  # pseudocode: C.9.C.1
        """
        Description: calculate water deficiency factor

        SWAT Reference: 5:3.3

        Args:
            evapotranspiration: annual evapotranspiration
            max_evapotranspiration: maximum annual evapotranspiration

        Returns: water deficiency factor
        """
        if max_evapotranspiration != 0:
            return 100 * (evapotranspiration / max_evapotranspiration)
        else:
            return 0

    # TODO: Further functions water files need to be translated (into soil methods?) - GitHub Issue #303
    #    RUFAS/routines/field/crop/transpiration.py
