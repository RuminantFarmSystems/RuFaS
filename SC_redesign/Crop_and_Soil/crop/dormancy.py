from typing import Optional

from SC_redesign.Crop_and_Soil.crop.crop_data import CropData


"""
This module is based on the "Dormancy" module of SWAT (5:1.2)
"""


class Dormancy:
    def __int__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData


    @staticmethod
    def _find_threshold_daylength(minimum_daylength: float, dormancy_threshold: float) -> float:
        """calculates the threshold daylength for dormancy

        Args:
            minimum_daylength: the minimum daylength for the watershed during the year (hours)
            dormancy_threshold: the dormancy threshold for this field (hours)

        SWAT Reference: 5:1.2.1

        Returns: threshold daylength for dormancy (hours)
        """
        return minimum_daylength + dormancy_threshold

    @staticmethod
    def _find_dormancy_threshold(abs_latitude: float) -> float:
        """calculates the dormancy threshold based on the absolute latitude

        Args:
            abs_latitude: the absolute latitude value (degrees above or below the equator)

        SWAT Reference: 5:1.2.2 - 5:1.2.4

        Returns: the dormancy threshold for this latitude
        """
        # Near poles
        if abs_latitude > 40:
            return 1.0

        # Near equator
        if abs_latitude < 20:
            return 0.0

        # Middle
        if 20 <= abs_latitude <= 40:
            return (abs_latitude - 20.0) / 20.0