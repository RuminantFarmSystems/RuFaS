from typing import Optional

from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.rufas_time import RufasTime

"""
This module is based upon the "Root Development" section of the SWAT model (5.2.1.3)
"""


class RootDevelopment:
    """
    Manages the development of crop roots based on the "Root Development" section of the SWAT model (5.2.1.3).

    Parameters
    ----------
    crop_data : CropData, optional
        An instance of `CropData` containing specific crop parameters and states. If not provided, a default
        instance with generic crop parameters is created.

    Attributes
    ----------
    data : CropData
        Stores and provides access to crop-related data influencing root development, including parameters
        like root depth, growth rates, and environmental conditions affecting root expansion.

    """

    def __init__(self, crop_data: Optional[CropData] = None):
        self.data = crop_data or CropData()

    def develop_roots(self, time: RufasTime) -> None:
        """
        Main root development function that updates the root_fraction and root_depth attributes.

        Parameters
        ----------
        time : RufasTime
            The current time in the simulation.

        Notes
        -----
        root_depth attributes are updated differently depending upon whether the plant is perennial.

        """
        self.data.root_fraction = self._determine_root_fraction(self.data.heat_fraction)

        if self.data.is_perennial and time.current_calendar_year != self.data.planting_year:
            self.data.root_depth = self.data.max_root_depth
        else:
            self.data.root_depth = self._determine_root_depth(self.data.max_root_depth, self.data.heat_fraction)

    @staticmethod
    def _determine_root_fraction(heat_fraction: float) -> float:
        """
        Calculates root fraction as a function of plant maturity.

        Parameters
        ----------
        heat_fraction : float
            The proportion of potential heat units accumulated to date; a proxy for maturity (unitless).

        Returns
        -------
        float
            The fraction of a plant's biomass comprised of roots, typically ranging from 0.4 to 0.2 as the plant
            matures (unitless).

        References
        ----------
        SWAT 5:2.1.21

        """
        heat_fraction = max(heat_fraction, 0)  # bound to zero
        if heat_fraction >= 2:  # leads to fraction < 0
            return 0
        else:
            return 0.4 - 0.2 * heat_fraction

    @staticmethod
    def _determine_root_depth(max_depth: float, heat_fraction: float) -> float:
        """
        Calculates a plant's root depth on a given day.

        Parameters
        ----------
        max_depth : float
            Maximum possible root depth in millimeters (mm).
        heat_fraction : float
            Fraction of potential heat units accumulated, indicating the stage of plant growth (unitless).

        Returns
        -------
        float
            Root depth in millimeters for the given day (mm).

        References
        ----------
        SWAT 5:2.1.23, 24

        """
        if heat_fraction <= 0.4:
            return 2.5 * heat_fraction * max_depth
        else:
            return max_depth
