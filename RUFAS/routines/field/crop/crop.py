from __future__ import annotations
from RUFAS.routines.field.crop.growth_constraints import GrowthConstraints
from RUFAS.routines.field.crop.biomass_allocation import BiomassAllocation
from RUFAS.routines.field.crop.nitrogen_incorporation import NitrogenIncorporation
from RUFAS.routines.field.crop.phosphorus_incorporation import PhosphorusIncorporation
from RUFAS.routines.field.crop.water_uptake import WaterUptake
from RUFAS.routines.field.crop.water_dynamics import WaterDynamics
from RUFAS.routines.field.crop.heat_units import HeatUnits
from RUFAS.routines.field.crop.leaf_area_index import LeafAreaIndex
from RUFAS.routines.field.crop.root_development import RootDevelopment
from RUFAS.routines.field.crop.crop_management import CropManagement
from RUFAS.routines.field.crop.dormancy import Dormancy
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.soil.soil_data import SoilData
from typing import Optional


class Crop:
    """
    A class representing a crop, encapsulating various processes and components
    related to crop growth and development throughout a simulation.

    This class integrates multiple subcomponents that manage different aspects of
    the crop's lifecycle, including growth constraints, biomass allocation, water
    dynamics, nutrient incorporation, heat accumulation, and more.

    Parameters
    ----------
    crop_data : Optional[CropData], optional
        A CropData object containing the attributes tracked throughout the simulation.
        If not provided, default specifications are used.

    Attributes
    ----------
    data : CropData
        Reference to the crop data; tracks all crop variables through the simulation.
    growth_constraints : GrowthConstraints
        Process component controlling growth constraints, limits plant growth as a function of stressors.
    biomass_allocation : BiomassAllocation
        Process component controlling allocation of plant biomass as a function of growth and photosynthesis.
    water_dynamics : WaterDynamics
        Process component controlling plant water dynamics.
    water_uptake : WaterUptake
        Process component controlling water uptake from soil.
    nitrogen_incorporation : NitrogenIncorporation
        Process component controlling plant nitrogen incorporation, including uptake and fixation.
    phosphorus_incorporation : PhosphorusIncorporation
        Process component controlling plant phosphorus uptake and incorporation.
    heat_units : HeatUnits
        Process component controlling plant heat accumulation.
    leaf_area_index : LeafAreaIndex
        Process component controlling canopy growth, including leaf area index.
    root_development : RootDevelopment
        Process component controlling plant root development.
    crop_management : CropManagement
        Process component controlling calculation of end-of-season production.
    dormancy : Dormancy
        Process component performing dormancy operations.

    Notes
    -----
    The `Crop` class is designed to be a central part of a crop growth simulation,
    integrating data and methods from various subcomponents to simulate the entire
    lifecycle of a crop.

    """

    def __init__(self, crop_data: Optional[CropData] = None):
        """
        Initialize a Crop object with the specified or default crop data.

        Parameters
        ----------
        crop_data : Optional[CropData]
            The crop data to be used for simulation. If not provided,
            default specifications are used.
        """
        # Common data object that is updated throughout routines
        self.data = crop_data or CropData()  # defaults if not given

        # growth process components
        self.growth_constraints = GrowthConstraints(self.data)
        self.biomass_allocation = BiomassAllocation(self.data)
        self.water_dynamics = WaterDynamics(self.data)  # needs soil.evapotranspiration.evapotranspirate() called 1st
        self.water_uptake = WaterUptake(self.data)
        self.nitrogen_incorporation = NitrogenIncorporation(self.data)
        self.phosphorus_incorporation = PhosphorusIncorporation(self.data)
        self.heat_units = HeatUnits(self.data)  # TODO: rename module and component (e.g., "HeatAccumulation")?
        self.leaf_area_index = LeafAreaIndex(self.data)  # TODO: rename module and component (e.g., "CanopyGrowth")?
        self.root_development = RootDevelopment(self.data)
        self.crop_management = CropManagement(self.data)
        self.dormancy = Dormancy(self.data)

    def grow_crop(self, soil_data: SoilData, incoming_light: float,
                  mean_air_temperature: float, min_air_temperature: float,
                  max_air_temperature: float) -> None:
        """
        Main function for growing the crop on a daily basis.

        This function acts as a wrapper for all the Crop growth process sub-routines.
        It should be called every day that the crop is alive and growing in the simulation.

        Parameters
        ----------
        soil_data : SoilData
            The SoilData object that tracks soil properties.
        incoming_light : float
            Incoming light radiation energy (MJ/m).
        mean_air_temperature : float
            Average air temperature for the day (°C).
        min_air_temperature : float
            Minimum air temperature for the day (°C).
        max_air_temperature : float
            Maximum air temperature for the day (°C).
        """
        if self.data.in_growing_season:
            self.heat_units.absorb_heat_units(mean_air_temperature, min_air_temperature, max_air_temperature)
            self.root_development.develop_roots()
            self.nitrogen_incorporation.incorporate_nitrogen(soil_data)
            self.phosphorus_incorporation.incorporate_phosphorus(soil_data)
            self.growth_constraints.constrain_growth(self.data.max_transpiration, mean_air_temperature)
            self.leaf_area_index.grow_canopy()
            self.biomass_allocation.allocate_biomass(incoming_light)
