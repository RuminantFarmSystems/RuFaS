from __future__ import annotations
from SC_redesign.Crop_and_Soil.crop.growth_constraints import GrowthConstraints
from SC_redesign.Crop_and_Soil.crop.biomass_allocation import BiomassAllocation
from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import NitrogenIncorporation
from SC_redesign.Crop_and_Soil.crop.phosphorus_incorporation import PhosphorusIncorporation
from SC_redesign.Crop_and_Soil.crop.water_dynamics import WaterDynamics
from SC_redesign.Crop_and_Soil.crop.heat_units import HeatUnits
from SC_redesign.Crop_and_Soil.crop.leaf_area_index import LeafAreaIndex
from SC_redesign.Crop_and_Soil.crop.root_development import RootDevelopment
from SC_redesign.Crop_and_Soil.crop.crop_management import CropManagement
from SC_redesign.Crop_and_Soil.crop.dormancy import Dormancy

from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from typing import List, Optional


class Crop:
    def __init__(self, crop_data: Optional[CropData] = None):
        """Creates a crop object, from a crop data specification object.

        Args:
            crop_data: a CropData object containing the attributes tracked throughout the simulation

        Details:
            If crop_data is not given, the default specifications are used.
        """
        # Common data object that is updated throughout routines
        self.data = crop_data or CropData()  # defaults if not given
        """reference to the crop data; tracks all crop variables through the simulation"""

        # growth process components
        self.growth_constraints = GrowthConstraints(self.data)
        """Process component controlling growth constraints, limits plant growth as a function of stressors"""
        self.biomass_allocation = BiomassAllocation(self.data)
        """Process component controlling allocation of plant biomass as a function of growth and photosynthesis"""
        self.water_dynamics = WaterDynamics(self.data)
        """Process component controlling plant water dynamics"""
        self.nitrogen_incorporation = NitrogenIncorporation(self.data)
        """Process component controlling plant nitrogen incorporation, including uptake and fixation"""
        self.phosphorus_incorporation = PhosphorusIncorporation(self.data)
        """Process component controlling plant phosphorus uptake and incorporation"""
        self.heat_units = HeatUnits(self.data)  # TODO: rename module and component (e.g., "HeatAccumulation")?
        """Process component controlling plant heat accumulation"""
        self.leaf_area_index = LeafAreaIndex(self.data)  # TODO: rename module and component (e.g., "CanopyGrowth")?
        """Process component controlling canopy growth, including leaf area index"""
        self.root_development = RootDevelopment(self.data)
        """Process component controlling plant root development"""
        self.crop_management = CropManagement(self.data)
        """Process component controlling calculation of end-of-season production"""
        self.dormancy = Dormancy(self.data)
        """Process component performing dormancy operations"""

    def grow_crop(self, layer_nitrates: List[float], layer_depths: List[float],
                  layer_phosphates: List[float],
                  soil_water_factor: float,
                  max_transpiration: float,
                  incoming_light: float,
                  evaporation: float, transpiration: float,
                  max_evapotranspiration: float,
                  mean_air_temperature: float, min_air_temperature: float,
                  max_air_temperature: float, adjusted_potential_evapotranspiration: float) -> None:
        """main function for growing the crop on a daily basis

        Args:
            adjusted_potential_evapotranspiration: potential evapotranspiration adjusted for evaporation of free water in canopy in mm
            layer_nitrates: nitrates present in each layer of the soil profile (kg/ha)
            layer_depths: the maximum depth of each soil layer
            layer_phosphates: phosphates present in each layer of the soil profile (kg/ha)
            soil_water_factor: the soil water factor

            max_transpiration: maximum amount of transpiration possible (mm), as determined by soil, on this day

            incoming_light: incoming light radiation energy (MJ/m)

            evaporation: total evaporation occurring (mm) as determined by soil, on a given day
            transpiration: total transpiration occurring (mm) as determined by soil, on a given day
            max_evapotranspiration: maximum amount of evapotranspiration possible (mm), as determined by soil on
            a given day.

            mean_air_temperature: average air temperature for the day (C)
            min_air_temperature: minimum air temperature for the day (C)
            max_air_temperature: maximum air temperature for the day (C)

        Details: grow_crop is a wrapper function for all the Crop growth
            process sub-routines. It should be called every day that the crop
            is alive and growing in the simulation
        """

        # don't perform growth if the plant can't grow
        cannot_grow = not self.data.is_alive or not self.data.is_growing or self.data.is_dormant
        if cannot_grow:
            return

        # grow otherwise
        self.heat_units.absorb_heat_units(mean_air_temperature, min_air_temperature, max_air_temperature)
        self.root_development.develop_roots()
        self.nitrogen_incorporation.incorporate_nitrogen(layer_nitrates, layer_depths, soil_water_factor)
        self.phosphorus_incorporation.incorporate_phosphorus(layer_phosphates, layer_depths)
        self.growth_constraints.constrain_growth(max_transpiration, mean_air_temperature)
        self.leaf_area_index.grow_canopy()
        self.biomass_allocation.allocate_biomass(incoming_light)

    # ---- Crop Management Methods
    @classmethod
    def plant_species(cls, species) -> Crop:
        """creates a crop instance with attributes determined by the species of the crop.

        Details: species attributes are read from species configuration files/classes
        """
        pass

    def reset_perennial(self):
        """resets some attributes for perennial crops at the start of the new growing season"""
        pass

    def destroy(self):  # Needed?
        """destroys the crop - Destructor class. This removes the crop instance from existence"""
        pass

    def assess_dormancy(self):  # TODO: implement dormancy method - handled in CropData
        self.dormancy.go_into_dormancy()



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
