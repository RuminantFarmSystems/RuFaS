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
        self.field_data = field_data or FieldData(field_size=field_size or 1)
        self.soil_data = soil_data or SoilData(field_size=field_data.field_size)

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

    def _till_surface_pool_into_top_layer(self, data_container: object, surface_attribute_name: str,
                                          incorporation_fraction: float, soil_attribute_name: str) -> None:
        """
        Transfers tilled stuff from soil surface into the top soil layer.

        Parameters
        ----------
        data_container : object
            Class instance containing the soil surface pool to be removed from (unitless)
        surface_attribute_name : str
            Name of the pool in the soil surface to be removed from (unitless)
        incorporation_fraction : float
            Fraction of stuff incorporated into the soil profile from the soil surface (unitless)
        soil_attribute_name : float
            Name of the pool in the top soil layer to added to (unitless)

        Notes
        -----
        Some pools on the soil surface are named differently than the pools in the soil profile which contain the same
        substance, which is why this method takes both a surface attribute name and a soil attribute name.

        """
        amount_removed_from_surface = self._remove_amount_incorporated(data_container, surface_attribute_name,
                                                                       incorporation_fraction)
        amount_in_top_layer = getattr(self.soil_data.soil_layers[0], soil_attribute_name)
        amount_in_top_layer += amount_removed_from_surface
        setattr(self.soil_data.soil_layers[0], soil_attribute_name, amount_in_top_layer)

    @staticmethod
    def _remove_amount_incorporated(data_container: object, attribute_name: str,
                                    incorporation_fraction: float) -> float:
        """
        Calculates amount of stuff incorporated from the soil surface into the soil profile.

        Parameters
        ----------
        data_container : object
            Class instance containing the soil surface pool to be removed from (unitless)
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

    @staticmethod
    def _determine_fraction_of_layer_mixed(layer_thickness: float, layer_bottom_depth: float,
                                           tillage_depth: float) -> float:
        """
        Calculates how much a soil layer is mixed when it is not tilled entirely.

        Parameters
        ----------
        layer_thickness : float
            Top depth of layer (mm)
        layer_bottom_depth : float
            Bottom depth of layer (mm)
        tillage_depth : float
            The lowest depth the tilling implement reaches (mm)

        Returns
        -------
        float
            The fraction of the soil layer affected by the tillage operation (unitless)

        Notes
        -----
        This method is necessary when determining how a soil layer is effected by a tillage operation that does not till
        the entire soil layer.

        """
        untilled_depth = layer_bottom_depth - tillage_depth
        return 1 - (untilled_depth / layer_thickness)
