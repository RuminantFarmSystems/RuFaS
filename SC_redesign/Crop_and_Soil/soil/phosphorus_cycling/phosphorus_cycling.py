from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.manure import Manure
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.fertilizer import Fertilizer
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.phosphorus_mineralization import PhosphorusMineralization
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.soluble_phosphorus import SolublePhosphorus

"""
This module contains the composite class for phosphorus cycling, which contains and manages all the necessary all 
necessary aspects for managing phosphorus in and on top of a soil profile.
"""


class PhosphorusCycling:

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track phosphorus cycling, creates new one if one is not provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

        self.manure = Manure(self.data)
        """Process component that manages manure on the field."""
        self.fertilizer = Fertilizer(self.data)
        """Process component that manages fertilizer on the field."""
        self.mineralization = PhosphorusMineralization(self.data)
        """Process component that controls the mineralization of phosphorus within the soil profile."""
        self.soluble_phosphorus = SolublePhosphorus(self.data)
        """Process component that controls the movement of phosphorus between layers of soil."""

    def cycle_phosphorus(self, rainfall: float, runoff: float, field_size: float, mean_air_temperature: float) -> None:
        """This method calls all daily routines that manage phosphorus on the soil surface and in the soil profile.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm)
        runoff : float
            The amount of runoff from rainfall on the current day (mm)
        field_size : float
            The size of the field (ha)
        mean_air_temperature : float
            Mean air temperature on the current day (degrees C)

        """
        self.manure.daily_manure_update(rainfall, runoff, field_size, mean_air_temperature)
        self.fertilizer.do_fertilizer_phosphorus_operations(rainfall, runoff, field_size)
        self.mineralization.mineralize_phosphorus(field_size)
        self.soluble_phosphorus.daily_update_routine(runoff, field_size)
