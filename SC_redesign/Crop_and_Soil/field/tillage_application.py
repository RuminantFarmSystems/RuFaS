from typing import Optional

from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module contains all necessary methods for executing tillage operations on a field, based on SWAT Theoretical
documentation section 6:1.6 and the SurPhos plow.f file.

Notes
-----
This module was written to be as flexible as possible, because every attribute on the soil surface and in the soil
profile gets incorporated and/or mixed with the same logic. That is why the term "stuff" is used in the docstrings to
describe the pools/attributes that are effected by tillage.
"""


class TillageApplication:

    def __init__(self, field_data: Optional[FieldData] = None, soil_data: Optional[SoilData] = None,
                 field_size: Optional[float] = None):
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
        self.soil_data = soil_data or SoilData(field_size=self.field_data.field_size)

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
        The tillage process starts by removing stuff from the soil surface and putting it into the top soil layer, then
        mixing everything in together from the different soil layers. The method also checks that tillage does not go
        deeper than the bottom of the soil profile.

        """
        # TODO : increase functionality and features - issue #538
        vadose_zone_tilled = tillage_depth > self.soil_data.soil_layers[-1].bottom_depth
        if vadose_zone_tilled:
            tillage_depth = self.soil_data.soil_layers[-1].bottom_depth

        total_phosphorus_incorporated = 0
        phosphorus_pools_to_draw_from = ["available_phosphorus_pool",
                                         "recalcitrant_phosphorus_pool",
                                         "machine_water_extractable_inorganic_phosphorus",
                                         "machine_water_extractable_organic_phosphorus",
                                         "machine_stable_inorganic_phosphorus",
                                         "machine_stable_organic_phosphorus",
                                         "grazing_water_extractable_inorganic_phosphorus",
                                         "grazing_water_extractable_organic_phosphorus",
                                         "grazing_stable_inorganic_phosphorus",
                                         "grazing_stable_organic_phosphorus"]
        for pool in phosphorus_pools_to_draw_from:
            total_phosphorus_incorporated += self._remove_amount_incorporated(self.soil_data, pool,
                                                                              incorporation_fraction)
        self.soil_data.soil_layers[0].add_to_labile_phosphorus(total_phosphorus_incorporated,
                                                               self.field_data.field_size)

        self._remove_amount_incorporated(self.soil_data, "machine_manure_dry_mass", incorporation_fraction)
        self._remove_amount_incorporated(self.soil_data, "machine_manure_field_coverage", incorporation_fraction)
        self._remove_amount_incorporated(self.soil_data, "grazing_manure_dry_mass", incorporation_fraction)
        self._remove_amount_incorporated(self.soil_data, "grazing_manure_field_coverage", incorporation_fraction)

        pools_to_till_in_soil = ["labile_inorganic_phosphorus_content",
                                 "active_inorganic_phosphorus_content",
                                 "stable_inorganic_phosphorus_content",
                                 "nitrate_content",
                                 "ammonium_content",
                                 "active_organic_nitrogen_content",
                                 "stable_organic_nitrogen_content",
                                 "fresh_organic_nitrogen_content"]
        for pool in pools_to_till_in_soil:
            self._mix_soil_layers(pool, tillage_depth, mixing_fraction)

    def _mix_soil_layers(self, pool_name: str, tillage_depth: float, mixing_fraction: float) -> None:
        """
        Redistributes stuff from the specified pool through the soil profile.

        Parameters
        ----------
        pool_name : str
            Name of the soil attribute that should be mixed within the soil profile (unitless)
        tillage_depth : float
            The lowest depth the tilling implement reaches (mm)
        mixing_fraction : float
            Fraction of stuff mixed and redistributed from each layer in the soil profile (unitless)

        References
        ----------
        SWAT Theoretical documentation, example on page 361.

        Notes
        -----
        This method executes the actual mixing between the soil layers. Each layer in the soil profile can be either
        fully tilled, partially tilled, or not tilled at all. The method starts by determining how much total stuff will
        be mixed in the profile based on the mixing fraction and how much stuff is in the pool of each layer. Then it
        redistributes mixed stuff back into the tilled layers of the profile. The amount of stuff mixed back in to a
        layer is determined by the ratio between the depth of tillage in the layer and the total overall tillage depth.

        """
        redistribution_fractions = []
        total_to_mix_from_pools = 0
        for layer in self.soil_data.soil_layers:
            layer_not_tilled = layer.top_depth >= tillage_depth
            layer_partially_tilled = layer.bottom_depth > tillage_depth
            if layer_not_tilled:
                break
            elif layer_partially_tilled:
                tilled_depth = tillage_depth - layer.top_depth
                layer_redistribution_fraction = tilled_depth / tillage_depth
                fraction_of_layer_mixed = tilled_depth / layer.layer_thickness
            else:
                layer_redistribution_fraction = layer.layer_thickness / tillage_depth
                fraction_of_layer_mixed = 1.0
            redistribution_fractions.append(layer_redistribution_fraction)

            current_pool_amount = getattr(layer, pool_name)
            amount_to_remove = current_pool_amount * mixing_fraction * fraction_of_layer_mixed
            unmixed_amount_in_pool = current_pool_amount - amount_to_remove
            setattr(layer, pool_name, unmixed_amount_in_pool)
            total_to_mix_from_pools += amount_to_remove

        number_of_tilled_layers = len(redistribution_fractions)
        for layer_index in range(number_of_tilled_layers):
            layer = self.soil_data.soil_layers[layer_index]
            layer_fraction = redistribution_fractions[layer_index]

            amount_to_add = total_to_mix_from_pools * layer_fraction

            amount_in_pool = getattr(layer, pool_name)
            new_pool_amount = amount_in_pool + amount_to_add
            setattr(layer, pool_name, new_pool_amount)

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
            Amount of stuff removed from soil surface and added to the top soil layer (units vary)

        References
        ----------
        SurPhos fortran code, plow.f lines 20 - 32.

        Notes
        -----
        This method both calculates the amount that is removed from the soil surface and actually removes it from the
        soil surface, returning that removed amount. The units of the value returned are the same as the units of the
        pool being removed from.

        """
        amount_in_pool = getattr(data_container, attribute_name)
        amount_removed = amount_in_pool * incorporation_fraction
        remaining_amount_in_pool = amount_in_pool - amount_removed
        setattr(data_container, attribute_name, remaining_amount_in_pool)
        return amount_removed
