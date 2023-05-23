from typing import Optional

from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module contains all necessary methods for executing tillage operations on a field, based on SWAT Theoretical 
documentation section 6:1.6 and  
"""


class TillageApplication:

    def __init__(self, field_data: Optional[FieldData], soil_data: Optional[SoilData], field_size: Optional[float]):
        """
        Creates a TillageApplication object based on a SoilData object.

        Parameters
        ----------
        field_data : FieldData, optional
            FieldData object that tracks attributes on the soil surface as they are updated by tillage applications.
        soil_data : SoilData, optional
            SoilData object that tracks all attributes of the soil profile as they are updated by tillage applications.
        field_size : float, optional
            Size of the field (ha)

        Notes
        -----
        If no SoilData object is provided, one is created with the default configuration based on the field size.

        """
        self.soil_data = soil_data or SoilData(field_size=field_size)

    def till_soil(self, tillage_depth: float, incorporation_fraction: float, mixing_fraction: float) -> None:
        """
        Mixes nutrients, manure/fertilizer mass, and residue from the soil profile and soil surface together in the soil
        profile.

        Parameters
        ----------
        tillage_depth : float
            The lowest depth the tilling implement reaches (mm)
        incorporation_fraction : float
            Fraction of stuff incorporated into the soil profile from the soil surface (unitless)
        mixing_fraction : float
            Fraction of stuff mixed and redistributed from each layer in the soil profile (unitless)

        References
        ----------
        SWAT Theoretical documentation section 6:1.6,

        """
        pass

    def 
