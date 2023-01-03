from SC_redesign.Crop_and_Soil.crop.growth_constraints import GrowthConstraints
from SC_redesign.Crop_and_Soil.crop.biomass_allocation import BiomassAllocation
from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import NitrogenIncorporation
from SC_redesign.Crop_and_Soil.crop.water_dynamics import WaterDynamics
from SC_redesign.Crop_and_Soil.crop.heat_units import HeatUnits
from SC_redesign.Crop_and_Soil.crop.leaf_area_index import LeafAreaIndex
from SC_redesign.Crop_and_Soil.crop.root_development import RootDevelopment
from SC_redesign.Crop_and_Soil.crop.yields import Yields

from __future__ import annotations

from typing import List

# TODO: Should use an ENUM class to represent the supported species??

class Crop(GrowthConstraints, BiomassAllocation, WaterDynamics, NitrogenIncorporation, HeatUnits, LeafAreaIndex,
           RootDevelopment, Yields):
    def __init__(self):
        GrowthConstraints.__init__(self)
        BiomassAllocation.__init__(self)
        WaterDynamics.__init__(self)
        NitrogenIncorporation.__init__(self)
        HeatUnits.__init__(self)
        LeafAreaIndex.__init__(self)
        RootDevelopment.__init__(self)
        Yields.__init__(self)


    def grow_crop(self, layer_nitrates: List[float], layer_depths: List[float], soil_water_factor: float,
                  max_transpiration: float, air_temperature: float,
                  incoming_light: float,
                  evaporation: float, transpiration: float, max_evapotranspiration: float,
                  mean_air_temperature: float, min_air_temperature: float, max_air_temperature: float) -> None:
        """main function for growing the crop on a daily basis

        Args:
            layer_nitrates: nitrates present in each layer of the soil profile (kg/ha)
            layer_depths: the maximum depth of each soil layer
            soil_water_factor: the soil water factor

            max_transpiration: maximum amount of transpiration possible (mm), as determined by soil, on this day
            air_temperature: current air temperature (C)

            incoming_light: incoming light radiation energy (MJ/m)

            evaporation: total evaporation occurring (mm) as determined by soil, on a given day
            transpiration: total transpiration occurring (mm) as determined by soil, on a given day
            max_evapotranspiration: maximum amount of evapotranspiration possible (mm), as determined by soil
                on a given day.

            mean_air_temperature:
            min_air_temperature:
            max_air_temperature:

        Details: grow_crop is a wrapper function for all the Crop growth process sub-routines. It should be called
        every day that the crop is alive and growing in the simulation
        """
        self.absorb_heat_units(mean_air_temperature, min_air_temperature, max_air_temperature)
        self.develop_roots()
        self.incorporate_nitrogen(layer_nitrates, layer_depths, soil_water_factor)
        #
        # phosphorus_uptake.update_all()
        #
        self.constrain_growth(max_transpiration, air_temperature)
        self.grow_canopy()
        self.allocate_biomass(incoming_light)
        self.cycle_water(evaporation, transpiration, max_evapotranspiration)

    @classmethod
    def plant_species(cls, species) -> Crop:
        return cls(species)

    def cut(self):
        """cuts the crop and return the cut biomass"""
        pass

    def harvest(self):
        """harvests the crop's yield"""
        pass

    def reset_perennial(self):
        """resets some attributes for perennial crops at the start of the new growing season"""
        pass

    def kill(self):
        """kills the crop - Destructor class. This prevents the crop from growing after harvest
        (i.e., for annual crops)"""
        pass

    def _list_all_parent_var_names(self):
        """list all variables used by Crop"""
        return vars(self)  # TODO: check for duplicates or conflicts among parents

    # TODO: implement cut() and kill() methods - GitHub Issue #248
    #   the old versions are pasted in the comment blocks below.
    #   these method (or a similar harvest method) will eventually need to call obtain_yields()
    def cut(self, fraction: float, mass=None) -> None:
        """remove biomass from the plant (via cutting)"""
        pass

    def kill(self) -> None:
        """kill the plant, preventing it from growing"""
        pass

# ---- Old versions of cut() and kill()
# def kill(crop_type, field_management, time):
#     """
#     Description:
#         Kills the crop.
#         NOTE: Any day-of-yield values reset here will be reported to the output
#         handler as 0. To reset after reporting see crop.daily_reset()
#         "pseudocode_crop" C.10.H.4
#
#     Args:
#         crop_type: an instance of a crop class
#         field_management: an instance of the FieldManagement class
#         time: an instance of the Time class as specified in classes.py
#     """
#     crop_type.accumulated_HU = 0
#     crop_type.prev_accumulated_HU = 0
#
#     crop_type.fr_PHU = 0
#     crop_type.prev_fr_PHU = 0
#
#     crop_type.LAI_actual = 0
#     crop_type.fr_LAI_max = 0
#
#     crop_type.biomass_actual = 0
#     crop_type.prev_biomass_actual = 0
#     crop_type.bio_AG = 0
#
#     crop_type.z_root = 0
#     crop_type.fr_root = 0
#
#     crop_type.bio_P = 0
#     crop_type.bio_N = 0
#
#     crop_type.ET_annual = 0
#
#     crop_type.planted = False
#     crop_type.growing = False
#     crop_type.killed = True
#
#     # FM.2.2
#     till_management = field_management.managed_applications['tillage']
#     if (time.calendar_year, -1) in till_management.applications:
#         till_management.schedule_application(time)
#
#
# def cut(crop_type, bio_frac):
#     """
#     Description:
#         Cuts the crop without killing it
#         "pseudocode_crop" C.10.H.2/3
#
#     Args:
#         crop_type: an instance of a crop class
#         bio_frac: fraction of biomass removed during the cut
#     """
#
#     crop_type.accumulated_HU = crop_type.accumulated_HU * (1 - bio_frac)
#     crop_type.fr_PHU = crop_type.accumulated_HU / crop_type.PHU
#
#     crop_type.LAI_actual = crop_type.LAI_actual * (1 - bio_frac)
#     crop_type.fr_LAI_max = 0
#
#     crop_type.biomass_actual -= crop_type.yield_actual
#
#     crop_type.bio_P = crop_type.bio_P * (1 - bio_frac)
#     crop_type.bio_N = crop_type.bio_N * (1 - bio_frac)
#
#     crop_type.ET_annual = 0
