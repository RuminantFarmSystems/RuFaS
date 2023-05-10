from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.leaching_runoff_erosion import LeachingRunoffErosion
from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.nitrification_volatilization import NitrificationVolatilization
from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.denitrification import Denitrification
from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.mineralization_decomp import MineralizationDecomposition
from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.humus_mineralization import HumusMineralization

"""
This module contains the composite class for nitrogen cycling, which contains and manages all the necessary elements for
managing nitrogen in the soil profile.
"""


class NitrogenCycling:

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        """Initializes the SoilData object that this module will work with, or creates one if none is provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track nitrogen cycling, creates new one if one is not provided.
        field_size : float, optional
            Size of the field (ha)

        Notes
        -----
        Field size is used to initialize a SoilData object for this module to work with, if a pre-configured SoilData
        object is not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

        self.leaching_runoff_erode = LeachingRunoffErosion(self.data)
        """Process component for tracking nitrogen movement between soil layers and loss to runoff and erosion."""
        self.nitrification_volatilization = NitrificationVolatilization(self.data)
        """Process component for managing ammonium within the soil profile."""
        self.denitrification = Denitrification(self.data)
        """Process component for managing the denitrification of nitrate within the soil profile."""
        self.mineralization_decomposition = MineralizationDecomposition(self.data)
        """Process component for managing the mineralization and decomposition of fresh nitrogen and residue in the soil
            profile."""
        self.humus_mineralization = HumusMineralization(self.data)
        """Process component for managing the active and stable organic nitrogen pools."""

    def cycle_nitrogen(self, field_size: float) -> None:
        """Executes the daily update operations on all process components.

        Parameters
        ----------
        field_size : float
            Size of the field (ha)

        """
        self.leaching_runoff_erode.leach_runoff_and_erode_nitrogen(field_size)
        self.nitrification_volatilization.do_daily_nitrification_and_volatilization()
        self.denitrification.denitrify()
        self.humus_mineralization.mineralize_organic_nitrogen()
