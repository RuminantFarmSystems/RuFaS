from __future__ import annotations
from SC_redesign.Crop_and_Soil.crop.growth_constraints import GrowthConstraints
from SC_redesign.Crop_and_Soil.crop.biomass_allocation import BiomassAllocation
from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import NitrogenIncorporation
from SC_redesign.Crop_and_Soil.crop.water_dynamics import WaterDynamics
from SC_redesign.Crop_and_Soil.crop.heat_units import HeatUnits
from SC_redesign.Crop_and_Soil.crop.leaf_area_index import LeafAreaIndex
from SC_redesign.Crop_and_Soil.crop.root_development import RootDevelopment
from SC_redesign.Crop_and_Soil.crop.yields import Yields

from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from typing import List, Optional

# TODO: Should use an ENUM class to represent the supported species??

class Crop(GrowthConstraints, BiomassAllocation,
           NitrogenIncorporation, HeatUnits, LeafAreaIndex):
    def __init__(self, crop_data: Optional[CropData] = None):
        data = crop_data or CropData() # defaults if not given


        # Initialize inherited classes
        GrowthConstraints.__init__(self)
        BiomassAllocation.__init__(self)
        self.water_dynamics = WaterDynamics(data)
        NitrogenIncorporation.__init__(self)
        HeatUnits.__init__(self)
        LeafAreaIndex.__init__(self)
        self.root_development = RootDevelopment(data)
        self.crop_yields = Yields(data)
        # TODO: Loi recommended that a composition pattern might fit better
        #  than multiple inheritance: A crop "has" a Growth constraint (system)
        #  but is not itself a growth constraint. This pattern might be worth
        #  looking into in the future. One problem I foresee is that because
        #  individual attributes occur in multiple process classes
        #  (e.g., nitrogen in GrowthConstraints and NitrogenIncorporation), a
        #  composite design would require interdependence such that these
        #  common attributes remain in-sync. - GitHub Issue #255


    def grow_crop(self, layer_nitrates: List[float], layer_depths: List[float],
                  soil_water_factor: float,
                  max_transpiration: float, air_temperature: float,
                  incoming_light: float,
                  evaporation: float, transpiration: float,
                  max_evapotranspiration: float,
                  mean_air_temperature: float, min_air_temperature: float,
                  max_air_temperature: float) -> None:
        """main function for growing the crop on a daily basis

        Args:
            layer_nitrates: nitrates present in each layer of the soil profile
                (kg/ha)
            layer_depths: the maximum depth of each soil layer
            soil_water_factor: the soil water factor

            max_transpiration: maximum amount of transpiration possible (mm),
                as determined by soil, on this day
            air_temperature: current air temperature (C)

            incoming_light: incoming light radiation energy (MJ/m)

            evaporation: total evaporation occurring (mm) as determined by soil,
                on a given day
            transpiration: total transpiration occurring (mm) as determined by
                soil, on a given day
            max_evapotranspiration: maximum amount of evapotranspiration
                possible (mm), as determined by soil on a given day.

            mean_air_temperature: average air temperature for the day (C)
            min_air_temperature: minimum air temperature for the day (C)
            max_air_temperature: maximum air temperature for the day (C)

        Details: grow_crop is a wrapper function for all the Crop growth
            process sub-routines. It should be called every day that the crop
            is alive and growing in the simulation
        """
        self.absorb_heat_units(mean_air_temperature, min_air_temperature,
                               max_air_temperature)
        self.root_development._develop_roots()
        self.incorporate_nitrogen(layer_nitrates, layer_depths,
                                  soil_water_factor)
        #
        # phosphorus_uptake.update_all()
        #
        self.constrain_growth(max_transpiration, air_temperature)
        self.grow_canopy()
        self.allocate_biomass(incoming_light)
        self.water_dynamics.cycle_water(evaporation, transpiration, max_evapotranspiration)

    @classmethod
    def plant_species(cls, species) -> Crop:
        """creates a crop instance with attributes determined by the species of
        the crop.

        Details: species attributes are read from species configuration
        files/classes
        """
        pass

    # TODO: implement cut() and kill() methods - GitHub Issue #248
    #   the old versions are pasted in the comment blocks below.
    #   these method (or a similar harvest method) will eventually need to call
    #   obtain_yields()
    def cut(self, fraction: float, mass=None) -> None:
        """remove biomass from the plant (via cutting)"""
        pass

    def kill(self) -> None:
        """kill the plant, preventing it from growing"""
        pass

    def harvest(self):
        """harvests the crop's cut yield biomass"""
        pass

    def reset_perennial(self):
        """resets some attributes for perennial crops at the start of the
        new growing season"""
        pass

    def destroy(self):  # Needed?
        """destoys the crop - Destructor class. This removes the crop instance
        from existance"""
        pass

    def _list_all_parent_var_names(self):
        """list all variables used by Crop"""
        return vars(self)  # TODO: check for duplicates or conflicts among parents

# ---- Old versions of cut() and kill()
# def kill(crop_type, field_management, time):
#     """
#     Description:
#         Kills the crop.
#         NOTE: Any day-of-yield values reset here will be reported to the
#         output handler as 0. To reset after reporting see crop.daily_reset()
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
