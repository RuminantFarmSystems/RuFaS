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
        SWAT Theoretical documentation section 6:1.6, SurPhos Fortran code plow.f

        Notes
        -----
        The tillage process starts by calculating the amount of stuff removed from the

        """
        pass

    @staticmethod
    def _remove_amount_incorporated(data_container: object, attribute_name: str,
                                    incorporation_fraction: float) -> float:
        """
        Calculates amount of stuff incorporated from the soil surface into the soil profile.

        Parameters
        ----------
        data_container : object
            Class instance containing the pool to be removed from (unitless)
        attribute_name : str
            Name of the pool to be removed from (unitless)
        incorporation_fraction : float
            Fraction of stuff incorporated into the soil profile from the soil surface (unitless)

        Returns
        -------
        float
            Amount of stuff removed from soil surface and added to soil profile (units vary)

        Notes
        -----
        The units of the value returned are the same as the units of the pool being removed from.

        """
        amount_in_pool = getattr(data_container, attribute_name)
        amount_removed = amount_in_pool * incorporation_fraction
        remaining_amount_in_pool = amount_in_pool - amount_removed
        setattr(data_container, attribute_name, remaining_amount_in_pool)
        return amount_removed
