from __future__ import annotations
from RUFAS.routines.field.crop.crop_enum import CropSpecies
from RUFAS.routines.field.crop.growth_constraints import GrowthConstraints
from RUFAS.routines.field.crop.biomass_allocation import BiomassAllocation
from RUFAS.routines.field.crop.harvest_operations import HarvestOperation
from RUFAS.routines.field.crop.nitrogen_incorporation import NitrogenIncorporation
from RUFAS.routines.field.crop.phosphorus_incorporation import PhosphorusIncorporation
from RUFAS.routines.field.crop.species_data_factory import CropSpeciesDataFactory
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

from RUFAS.time import Time


class Crop:
    """
    A class representing a crop, encapsulating various processes and components
    related to crop growth and development throughout a simulation.

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
    This class integrates multiple subcomponents that manage different aspects of the crop's lifecycle,
    including growth constraints, biomass allocation, water dynamics, nutrient incorporation, heat accumulation,
    and more. It is designed to be a central part of a crop growth simulation, integrating data and methods from
    various subcomponents to simulate the entire lifecycle of a crop.

    """

    def __init__(self, crop_data: Optional[CropData] = None):
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

    def grow_crop(
        self,
        soil_data: SoilData,
        incoming_light: float,
        mean_air_temperature: float,
        min_air_temperature: float,
        max_air_temperature: float,
        simulate_water_stress: bool,
        simulate_temp_stress: bool,
        simulate_nitrogen_stress: bool,
        simulate_phosphorus_stress: bool,
    ) -> None:
        """
        Main function for growing the crop on a daily basis.

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
        simulate_water_stress : bool
            Whether water stress should affect crop growth.
        simulate_temp_stress : bool
            Whether temperature stress should affect crop growth.
        simulate_nitrogen_stress : bool
            Whether nitrogen stress should affect crop growth.
        simulate_phosphorus_stress : bool
            Whether phosphorus stress should affect crop growth.

        Notes
        -----
        This function acts as a wrapper for all the Crop growth process sub-routines.
        It should be called every day that the crop is alive and growing in the simulation.

        """
        if self.data.in_growing_season:
            self.heat_units.absorb_heat_units(mean_air_temperature, min_air_temperature, max_air_temperature)
            self.root_development.develop_roots()
            self.nitrogen_incorporation.incorporate_nitrogen(soil_data)
            self.phosphorus_incorporation.incorporate_phosphorus(soil_data)
            self.growth_constraints.constrain_growth(
                self.data.max_transpiration,
                mean_air_temperature,
                simulate_water_stress,
                simulate_temp_stress,
                simulate_nitrogen_stress,
                simulate_phosphorus_stress,
            )
            self.leaf_area_index.grow_canopy()
            self.biomass_allocation.allocate_biomass(incoming_light)

    def should_harvest_based_on_heat(self) -> bool:
        return self.data.use_heat_scheduling and self.data.heat_fraction >= self.data.harvest_heat_fraction

    def manage_harvest_based_on_heat(self, field_name: str, field_size: float, time: Time, soil_data, feed_manager,
                                     rainfall: float) -> None:
        self.crop_management.manage_harvest(
            HarvestOperation.HARVEST_ONLY,
            field_name,
            field_size,
            time,
            soil_data,
            feed_manager,
        )
        self.soil.carbon_cycling.residue_partition.add_residue_to_pools(rainfall)
    
    @staticmethod
    def make_crop_from_config_dict(config: dict) -> Crop:
        """
        Initialize a new crop from a configuration dictionary.

        Parameters
        ----------
        config : dict
            A dictionary containing specifications for the crop to be initialized.

        Details
        -------
        If the "species" key is present in the dictionary, that value is checked against the supported
        crop species. If it is supported, that supported crop is initialized. Otherwise, a custom crop is
        created (with 'custom' prepended to the species name, if given).

        Returns
        -------
        Crop
            A Crop object initialized with the desired attribute values.
        """
        if "species" in config.keys():
            accepted_species = set(item.value for item in CropSpecies)
            species = config.pop("species")

            if species in accepted_species:
                return Crop.make_supported_crop(species=species, **config)
            else:
                config["species"] = "custom " + str(species)

        return Crop._make_custom_crop(**config)

    @staticmethod
    def make_supported_crop(species: str, **specs) -> Crop:
        """
        Create a crop instance with attributes determined by the species of the crop.

        Parameters
        ----------
        species : str
            One of the supported species.
        **specs : optional
            An optional set of keyword arguments passed to CropSpeciesDataFactory to customize the crop species.

        Details
        -------
        Species attributes are read from species configuration files/classes. This method of creating a crop
        does not allow for customizing crop values. It is limited to creating the default crops supported by the
        CropSpecies Enum.

        Returns
        -------
        Crop
            A Crop object initialized with the desired attribute values.
        """
        crop_species = CropSpecies(species)
        crop_data = CropSpeciesDataFactory.create_species_data(crop_species, **specs)
        return Crop(crop_data)

    @staticmethod
    def _make_custom_crop(**specs) -> Crop:
        """creates a crop instance with customized attributes.

        Args:
            **specs: an optional set of arguments, passed to CropSpeciesDataFactory that customize the
              crop species

        Details, this can be used to create a new ('unsupported') crop species/type
        """
        crop_data = CropData(**specs)
        return Crop(crop_data)
