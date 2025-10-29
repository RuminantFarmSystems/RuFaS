from typing import Optional

from RUFAS.biophysical.field.soil.phosphorus_cycling.fertilizer import Fertilizer
from RUFAS.biophysical.field.soil.phosphorus_cycling.manure import Manure
from RUFAS.biophysical.field.soil.phosphorus_cycling.phosphorus_mineralization import PhosphorusMineralization
from RUFAS.biophysical.field.soil.phosphorus_cycling.soluble_phosphorus import SolublePhosphorus
from RUFAS.biophysical.field.soil.soil_data import SoilData


class PhosphorusCycling:
    """
    This module contains the composite class for phosphorus cycling, which contains and manages all the necessary
    aspects for managing phosphorus in and on top of a soil profile.

    Parameters
    ----------
    soil_data : SoilData, optional
        An instance of SoilData to be used for tracking phosphorus cycling. If not provided, a new instance
        will be created with the given field size.
    field_size : float, optional
        The size of the field (ha).

    Attributes
    ----------
    data : SoilData
        The SoilData object that contains data and functionality related to soil and phosphorus properties.
    manure : Manure
        Process component that manages manure on the field.
    fertilizer : Fertilizer
        Process component that manages fertilizer on the field.
    mineralization : PhosphorusMineralization
        Process component that controls the mineralization of phosphorus within the soil profile.
    soluble_phosphorus : SolublePhosphorus
        Process component that controls the movement of phosphorus between layers of soil.

    """

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

        self.manure = Manure(self.data)
        self.fertilizer = Fertilizer(self.data)
        self.mineralization = PhosphorusMineralization(self.data)
        self.soluble_phosphorus = SolublePhosphorus(self.data)

    def cycle_phosphorus(
        self,
        rainfall: float,
        runoff: float,
        field_size: float,
        mean_air_temperature: float,
    ) -> None:
        """This method calls all daily routines that manage phosphorus on the soil surface and in the soil profile.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm).
        runoff : float
            The amount of runoff from rainfall on the current day (mm).
        field_size : float
            The size of the field (ha).
        mean_air_temperature : float
            Mean air temperature on the current day (°C).

        """
        self.manure.daily_manure_update(rainfall, runoff, field_size, mean_air_temperature)
        self.fertilizer.do_fertilizer_phosphorus_operations(rainfall, runoff, field_size)
        self.mineralization.mineralize_phosphorus(field_size)
        self.soluble_phosphorus.daily_update_routine(runoff, field_size)
