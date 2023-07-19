from __future__ import annotations
from SC_redesign.Crop_and_Soil.crop.growth_constraints import GrowthConstraints
from SC_redesign.Crop_and_Soil.crop.biomass_allocation import BiomassAllocation
from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import NitrogenIncorporation
from SC_redesign.Crop_and_Soil.crop.phosphorus_incorporation import PhosphorusIncorporation
from SC_redesign.Crop_and_Soil.crop.water_uptake import WaterUptake
from SC_redesign.Crop_and_Soil.crop.water_dynamics import WaterDynamics
from SC_redesign.Crop_and_Soil.crop.heat_units import HeatUnits
from SC_redesign.Crop_and_Soil.crop.leaf_area_index import LeafAreaIndex
from SC_redesign.Crop_and_Soil.crop.root_development import RootDevelopment
from SC_redesign.Crop_and_Soil.crop.crop_management import CropManagement
from SC_redesign.Crop_and_Soil.crop.dormancy import Dormancy

from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


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
        self.water_dynamics = WaterDynamics(self.data)  # needs soil.evapotranspiration.evapotranspirate() called 1st
        """Process component controlling plant water dynamics"""
        self.water_uptake = WaterUptake(self.data)
        """Process component controlling water uptake from soil"""
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

    def grow_crop(self, soil_data: SoilData, incoming_light: float,
                  mean_air_temperature: float, min_air_temperature: float,
                  max_air_temperature: float) -> None:
        """main function for growing the crop on a daily basis

        Args:
            soil_data: the SoilData object that tracks soil properties.

            incoming_light: incoming light radiation energy (MJ/m)

            mean_air_temperature: average air temperature for the day (C)
            min_air_temperature: minimum air temperature for the day (C)
            max_air_temperature: maximum air temperature for the day (C)

        Details: grow_crop is a wrapper function for all the Crop growth
            process sub-routines. It should be called every day that the crop
            is alive and growing in the simulation
        """
        # don't perform growth if the plant can't grow
        if self.data.in_growing_season:
            self.heat_units.absorb_heat_units(mean_air_temperature, min_air_temperature, max_air_temperature)
            self.root_development.develop_roots()
            self.nitrogen_incorporation.incorporate_nitrogen(soil_data)
            self.phosphorus_incorporation.incorporate_phosphorus(soil_data)
            self.growth_constraints.constrain_growth(self.data.max_transpiration, mean_air_temperature)
            self.leaf_area_index.grow_canopy()
            self.biomass_allocation.allocate_biomass(incoming_light)
