from typing import Optional

from SC_redesign.Crop_and_Soil.crop.crop_data import CropData, PlantCategory

"""
This module is based on the "Dormancy" module of SWAT (5:1.2)
"""


class Dormancy:
    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData

    def enter_dormancy(self) -> None:
        """Performs the actual transition from active to dormant in a crop.

        Details:
            When method is called, the crop's status is set to dormant, biomass is removed from plant and converted
            to residue, and the leaf area index is reset (if the current leaf area index is greater than the minimum
            leaf area index during dormancy for this crop).
        """
        if self.data.plant_category == PlantCategory.WARM_ANNUAL or PlantCategory.WARM_ANNUAL_LEGUME:
            # These types of plants do not go into dormancy
            return

        if self.data.is_dormant:
            # Crop is already dormant, so it should not re-lose biomass or have its leaf area index reset again
            return

        self.data.is_dormant = True
        if self.data.plant_category == PlantCategory.TREE or self.data.is_perennial:
            # Cool annuals and cool annual legumes do not lose any biomass or get their leaf area index reset

            # Some fraction of biomass falls off the plant and becomes residue
            self.data.yield_residue += (self.data.biomass * self.data.dormancy_loss_fraction)
            self.data.biomass *= (1 - self.data.dormancy_loss_fraction)
            # Leaf area index gets set to minimum leaf area index, if it is less than the current leaf area index
            self.data.leaf_area_index = min(self.data.leaf_area_index, self.data.minimum_lai_during_dormancy)

    @staticmethod
    def find_threshold_daylength(minimum_daylength: float, dormancy_threshold: float) -> float:
        """calculates the threshold daylength for dormancy

        Args:
            minimum_daylength: the minimum daylength for the watershed during the year (hours)
            dormancy_threshold: the dormancy threshold for this field (hours)

        SWAT Reference: 5:1.2.1

        Returns: threshold daylength for dormancy (hours)
        """
        return minimum_daylength + dormancy_threshold

    @staticmethod
    def find_dormancy_threshold(abs_latitude: float) -> float:
        """calculates the dormancy threshold based on the absolute latitude

        Args:
            abs_latitude: the absolute latitude value (degrees above or below the equator)

        SWAT Reference: 5:1.2.2 - 5:1.2.4

        Returns: the dormancy threshold for this latitude
        """
        is_near_pole = abs_latitude > 40
        if is_near_pole:
            return 1.0

        is_near_equator = abs_latitude < 20
        if is_near_equator:
            return 0.0

        is_middle = 20 <= abs_latitude <= 40
        if is_middle:
            return (abs_latitude - 20.0) / 20.0
