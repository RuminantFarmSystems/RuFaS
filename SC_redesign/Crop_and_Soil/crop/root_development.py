from typing import Optional
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData

"""
This module is based upon the "Root Development" section of the SWAT model (5.2.1.3)
"""

class RootDevelopment:
    def __init__(self, crop_data: Optional[CropData] = None):
        # data reference
        self.data = crop_data or CropData()  # defaults if not given

    def develop_roots(self) -> None:
        """main root development function

        Details: updates the root_fraction and root_depth attributes.
            The latter is updated differently depending upon whether the plant
            is perennial.
        """
        # update root fraction
        self.data.root_fraction = \
            self._determine_root_fraction(self.data.heat_fraction)

        # update root depth
        if self.data.is_perennial:
            self.data.root_depth = self._determine_root_depth(self.data.max_root_depth, self.data.heat_fraction)
        else:
            self.data.root_depth = self.data.max_root_depth  # TODO: assumption by SWAT - valid perhaps after 1st year?

    @staticmethod
    def _determine_root_fraction(heat_fraction: float) -> float:
        """calculates root fraction, as a function of plant maturity

        Args:
            heat_fraction: the proportion of potential heat units accumulated
                to date; a proxy for maturity

        SWAT Reference: 5:2.1.21

        Returns: the fraction of a plant's biomass comprised of roots [0.4-0.2]
        """
        heat_fraction = max(heat_fraction, 0)  # bound to zero
        if heat_fraction >= 2:  # leads to fraction < 0
            return 0
        else:
            return 0.4 - 0.2 * heat_fraction

    @staticmethod
    def _determine_root_depth(max_depth: float, heat_fraction: float) -> float:
        """calculates a plant's root depth on a given day

        Args:
            max_depth: maximum possible root depth (mm)
            heat_fraction: fraction of potential heat units

        SWAT Reference: 5:2.1.23, 24

        Returns: root depth (mm)
        """
        if heat_fraction <= 0.4:
            return 2.5 * heat_fraction * max_depth
        else:
            return max_depth
