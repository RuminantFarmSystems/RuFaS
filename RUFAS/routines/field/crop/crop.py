from __future__ import annotations
from copy import copy
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.routines.feed_storage.feed_manager import FeedManager
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
from RUFAS.routines.field.field.field_data import FieldData
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
    _data : CropData
        Reference to the crop data; tracks all crop variables through the simulation.
    _growth_constraints : GrowthConstraints
        Process component controlling growth constraints, limits plant growth as a function of stressors.
    _biomass_allocation : BiomassAllocation
        Process component controlling allocation of plant biomass as a function of growth and photosynthesis.
    _water_dynamics : WaterDynamics
        Process component controlling plant water dynamics.
    _water_uptake : WaterUptake
        Process component controlling water uptake from soil.
    _nitrogen_incorporation : NitrogenIncorporation
        Process component controlling plant nitrogen incorporation, including uptake and fixation.
    _phosphorus_incorporation : PhosphorusIncorporation
        Process component controlling plant phosphorus uptake and incorporation.
    _heat_units : HeatUnits
        Process component controlling plant heat accumulation.
    _leaf_area_index : LeafAreaIndex
        Process component controlling canopy growth, including leaf area index.
    _root_development : RootDevelopment
        Process component controlling plant root development.
    _crop_management : CropManagement
        Process component controlling calculation of end-of-season production.
    _dormancy : Dormancy
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
        self._data = crop_data or CropData()  # defaults if not given

        # growth process components
        self._growth_constraints = GrowthConstraints(self._data)
        self._biomass_allocation = BiomassAllocation(self._data)
        self._water_dynamics = WaterDynamics(self._data)  # needs soil.evapotranspiration.evapotranspirate() called 1st
        self._water_uptake = WaterUptake(self._data)
        self._nitrogen_incorporation = NitrogenIncorporation(self._data)
        self._phosphorus_incorporation = PhosphorusIncorporation(self._data)
        self._heat_units = HeatUnits(self._data)  # TODO: rename module and component (e.g., "HeatAccumulation")?
        self._leaf_area_index = LeafAreaIndex(self._data)  # TODO: rename module and component (e.g., "CanopyGrowth")?
        self._root_development = RootDevelopment(self._data)
        self._crop_management = CropManagement(self._data)
        self._dormancy = Dormancy(self._data)

    def perform_daily_crop_update(
        self, current_conditions: CurrentDayConditions, field_data: FieldData, soil_data: SoilData
    ) -> None:
        """
        Updates the crop for the current day.

        Parameters
        ----------
        current_conditions : CurrentDayConditions
            Object containing the environment conditions on this day.
        field_data : FieldData
            The FieldData object that tracks field properties.
        soil_data : SoilData
            The SoilData object that tracks soil properties.
        """
        if self._data.is_mature or self._data.is_dormant:
            return

        self._heat_units.absorb_heat_units(
            current_conditions.mean_air_temperature,
            current_conditions.min_air_temperature,
            current_conditions.max_air_temperature,
        )
        self._root_development.develop_roots()
        self._nitrogen_incorporation.incorporate_nitrogen(soil_data)
        self._phosphorus_incorporation.incorporate_phosphorus(soil_data)
        self._growth_constraints.constrain_growth(
            self._data.max_transpiration,
            current_conditions.mean_air_temperature,
            field_data.simulate_water_stress,
            field_data.simulate_temp_stress,
            field_data.simulate_nitrogen_stress,
            field_data.simulate_phosphorus_stress,
        )
        self._leaf_area_index.grow_canopy()
        self._biomass_allocation.allocate_biomass(current_conditions.incoming_light)

    def cycle_water_for_crops(
        self, actual_evaporation: float, full_evapotranspirative_demand: float, soil_data: SoilData
    ) -> None:
        """
        Executes the daily water cycling for crops on a field.

        Parameters
        ----------
        actual_evaporation : float
            Evaporation on a given day (mm).
        full_evapotranspirative_demand : float
            Potential evapotranspiration on a given day (mm).
        soil_data : SoilData
            An instance of the SoilData class (unitless).
        """

        if self._data.in_growing_season:
            self._water_uptake.uptake_water(soil_data)
            self._water_dynamics.cycle_water(
                actual_evaporation,
                self._data.water_uptake,
                full_evapotranspirative_demand,
            )
        else:
            self._data.cumulative_evaporation = 0.0
            self._data.cumulative_transpiration = 0.0
            self._data.cumulative_potential_evapotranspiration = 0.0
            self._data.cumulative_water_uptake = 0.0

    def get_canopy_water_excess_capacity(self) -> float:
        """
        Returns the excess capacity of the canopy water storage.
        This is the difference between the storage capacity and the current water stored in the canopy.

        Returns
        -------
        float
            The excess capacity in the canopy (can be negative if over capacity).
        """
        return self._data.water_canopy_storage_capacity - self._data.canopy_water

    def calculate_canopy_excess_water(self, canopy_water_excess_capacity: float) -> float:
        """
        Calculates the excess water in the canopy based on the canopy storage capacity.

        Parameters
        ----------
        canopy_water_excess_capacity : float
            The excess capacity of the canopy.

        Returns
        -------
        float
            The excess water in the canopy (negative if there is excess).
        """
        return min(0.0, canopy_water_excess_capacity)

    def adjust_canopy_water_for_excess(self, excess_water_in_canopy: float) -> None:
        """
        Adjusts the canopy water based on the calculated excess.

        Parameters
        ----------
        excess_water_in_canopy : float
            The excess water in the canopy to adjust (negative value).
        """
        if excess_water_in_canopy != 0.0:
            self._data.canopy_water = self._data.water_canopy_storage_capacity

    def store_water_in_canopy(self, canopy_water_excess_capacity: float, precipitation_reaching_soil: float) -> float:
        """
        Stores water in the canopy and returns the amount of precipitation that remains to reach the soil.

        Parameters
        ----------
        canopy_water_excess_capacity : float
            The excess capacity of the canopy (mm).
        precipitation_reaching_soil : float
            Amount of precipitation available to be stored in the canopy (mm).

        Returns
        -------
        float
            The amount of precipitation left after storing in the canopy (mm).
        """
        water_taken_to_be_stored = min(precipitation_reaching_soil, max(0.0, canopy_water_excess_capacity))
        self._data.canopy_water += water_taken_to_be_stored
        return precipitation_reaching_soil - water_taken_to_be_stored

    def evaporate_from_canopy(self, evapotranspirative_demand: float) -> float:
        """
        Evaporates water from the crop's canopy based on the evapotranspirative demand.

        Parameters
        ----------
        evapotranspirative_demand : float
            The evapotranspirative demand on the field on the current day (mm).

        Returns
        -------
        float
            The amount of water evaporated from the crop's canopy (mm).
        """
        amount_evaporated = self._water_dynamics.evaporate_from_canopy(evapotranspirative_demand)
        return amount_evaporated

    def should_harvest_based_on_heat(self) -> bool:
        """Checks if any of the active plants in the field should be harvested based on their heat schedule."""
        return self._data.use_heat_scheduling and self._data.heat_fraction >= self._data.harvest_heat_fraction

    def manage_crop_harvest(
        self,
        harvest_op: HarvestOperation,
        field_name: str,
        field_size: float,
        time: Time,
        soil_data: SoilData,
        feed_manager: FeedManager,
    ) -> None:
        """Wrapper function for the Crop's CropManagement harvesting operation.

        Parameters
        ----------
        harvest_op : HarvestOperation
            The operation to be executed on this crop.
        field_name : str
            The name of the field that contains this crop.
        field_size : float
            Size of the field that contains this crop (ha)
        time : Time
            Time instance containing the current time of the simulation.
        soil_data : SoilData
            The object tracking the attributes of the soil profile.
        feed_manager : FeedManager
            Instance of the FeedManager that receives harvested crops.
        """
        self._crop_management.manage_harvest(harvest_op, field_name, field_size, time, soil_data, feed_manager)

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def species(self) -> str:
        return self._data.species

    @property
    def id(self) -> str:
        return self._data.id

    @property
    def is_alive(self) -> bool:
        return self._data.is_alive

    @property
    def max_transpiration(self) -> float:
        return self._data.max_transpiration

    @property
    def field_proportion(self) -> float:
        return self._data.field_proportion

    @property
    def above_ground_biomass(self) -> float:
        return self._data.above_ground_biomass

    @property
    def planting_day(self) -> int:
        return self._data.planting_day

    @property
    def planting_year(self) -> int:
        return self._data.planting_year

    @property
    def root_depth(self) -> float:
        return self._data.root_depth

    @property
    def biomass(self) -> float:
        return self._data.biomass

    @property
    def usable_light(self) -> float:
        return self._data.usable_light

    @property
    def biomass_growth_max(self) -> float:
        return self._data.biomass_growth_max

    @property
    def biomass_growth(self) -> float:
        return self._data.biomass_growth

    @property
    def root_biomass(self) -> float:
        return self._data.root_biomass

    @property
    def growth_factor(self) -> float:
        return self._data.growth_factor

    @property
    def water_uptake(self) -> float:
        return self._data.water_uptake

    @property
    def water_stress(self) -> float:
        return self._data.water_stress

    @property
    def temp_stress(self) -> float:
        return self._data.temp_stress

    @property
    def nitrogen_stress(self) -> float:
        return self._data.nitrogen_stress

    @property
    def phosphorus_stress(self) -> float:
        return self._data.phosphorus_stress

    @property
    def accumulated_heat_units(self) -> float:
        return self._data.accumulated_heat_units

    @property
    def heat_fraction(self) -> float:
        return self._data.heat_fraction

    @property
    def is_growing(self) -> float:
        return self._data.is_growing

    @property
    def is_dormant(self) -> float:
        return self._data.is_dormant

    @property
    def leaf_area_index(self) -> float:
        return self._data.leaf_area_index

    @property
    def canopy_height(self) -> float:
        return self._data.canopy_height

    @property
    def leaf_area_added(self) -> float:
        return self._data.leaf_area_added

    @property
    def optimal_leaf_area_change(self) -> float:
        return self._data.optimal_leaf_area_change

    @property
    def potential_nitrogen_uptake(self) -> float:
        return self._data.potential_nitrogen_uptake

    @property
    def total_phosphorus_uptake(self) -> float:
        return self._data.total_phosphorus_uptake

    @property
    def total_nitrogen_uptake(self) -> float:
        return self._data.total_nitrogen_uptake

    @property
    def optimal_nitrogen_fraction(self) -> float:
        return self._data.optimal_nitrogen_fraction

    @property
    def potential_phosphorus_uptake(self) -> float:
        return self._data.potential_phosphorus_uptake

    @property
    def actual_phosphorus_uptakes(self) -> float:
        return self._data.actual_phosphorus_uptakes

    @property
    def actual_nitrogen_uptakes(self) -> float:
        return self._data.actual_nitrogen_uptakes

    @property
    def cumulative_evaporation(self) -> float:
        return self._data.cumulative_evaporation

    @property
    def cumulative_transpiration(self) -> float:
        return self._data.cumulative_transpiration

    @property
    def cumulative_evapotranspiration(self) -> float:
        return self._data.cumulative_evapotranspiration

    @property
    def water_deficiency(self) -> float:
        return self._data.water_deficiency

    @property
    def canopy_water(self) -> float:
        return self._data.canopy_water

    @property
    def cut_biomass(self) -> float:
        return self._data.cut_biomass

    @property
    def wet_yield_collected(self) -> float:
        return self._data.wet_yield_collected

    @property
    def yield_residue(self) -> float:
        return self._data.yield_residue

    @property
    def yield_nitrogen(self) -> float:
        return self._data.yield_nitrogen

    @property
    def yield_phosphorus(self) -> float:
        return self._data.yield_phosphorus

    @property
    def residue_nitrogen(self) -> float:
        return self._data.residue_nitrogen

    @property
    def residue_phosphorus(self) -> float:
        return self._data.residue_phosphorus

    @field_proportion.setter
    def field_proportion(self, field_proportion: float) -> None:
        self._data.field_proportion = field_proportion

    def set_maximum_transpiration(self, evapotranspirative_demand: float) -> None:
        """Sets the max transpiration for a crop."""
        self._water_dynamics.set_maximum_transpiration(evapotranspirative_demand)

    def assess_dormancy(self, daylength: float, dormancy_threshold_daylength: float, rainfall: float,
                        soil_data: SoilData) -> None:
        """
        Assess and manage dormancy status based on the daylength.

        Parameters
        ----------
        daylength : float
            Length of time from sunup to sundown on the current day (hours).
        dormancy_threshold_daylength : float
            The threshold daylength below which the crop should enter dormancy.
        rainfall : float
            Amount of rain that fell on the current day (mm).
        soil_data : SoilData
            The soil data relevant for dormancy and biomass partitioning.
        """
        if daylength <= dormancy_threshold_daylength:
            self.enter_dormancy(rainfall, soil_data)
        else:
            self.exit_dormancy()

    def enter_dormancy(self, rainfall: float, soil_data) -> None:
        """
        Puts the crop into dormancy and handles biomass partitioning and residue addition.

        Parameters
        ----------
        rainfall : float
            Amount of rain that fell on the current day (mm).
        soil_data : SoilData
            The soil data relevant for dormancy and biomass partitioning.
        """
        self._dormancy.enter_dormancy(soil_data)
        self._biomass_allocation.partition_biomass()
        soil_data.carbon_cycling.residue_partition.add_residue_to_pools(rainfall)

    def exit_dormancy(self) -> None:
        """
        Brings the crop out of dormancy.
        """
        self._data.is_dormant = False

    @classmethod
    def create_crop(cls, crop_reference: str, custom_crop_specifications: dict, use_heat_scheduled_harvesting: bool,
                    time: Time) -> Crop:
        """
        Factory method to create a crop instance based on the crop reference.

        Parameters
        ----------
        crop_reference : str
            The reference for the crop to be planted.
        custom_crop_specifications : dict
            Dictionary of custom crop specifications, if any.
        use_heat_scheduled_harvesting : bool
            Whether heat-scheduled harvesting should be used.
        time : Time
            The current time in the simulation.

        Returns
        -------
        Crop
            A fully initialized Crop instance.

        Raises
        ------
        KeyError
            If the crop reference is for a custom crop that does not exist in the specifications.
        """
        supported_species = set(item.value for item in CropSpecies)
        if crop_reference in supported_species:
            crop = cls.make_supported_crop(crop_reference)
        else:
            try:
                crop_specifications = copy(custom_crop_specifications[crop_reference])
            except KeyError:
                raise KeyError(
                    f"Expected to have crop specification for '{crop_reference}', "
                    f"received specifications for '{tuple(custom_crop_specifications.keys())}' crop types."
                )
            crop = cls.make_crop_from_config_dict(crop_specifications)

        crop.initialize_crop(crop_reference, use_heat_scheduled_harvesting, time)
        return crop

    def initialize_crop(self, crop_reference: str, use_heat_scheduled_harvesting: bool, time: Time) -> None:
        """
        Initializes the crop's attributes related to planting.

        Parameters
        ----------
        crop_reference : str
            The reference for the crop to be planted.
        use_heat_scheduled_harvesting : bool
            Whether heat-scheduled harvesting should be used.
        time : Time
            The current time in the simulation.
        """
        self._data.use_heat_scheduling = use_heat_scheduled_harvesting
        self._data.id = crop_reference
        self._data.planting_year = time.current_calendar_year
        self._data.planting_day = time.current_julian_day

    def make_crop_from_config_dict(self, config: dict) -> Crop:
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
                return self.make_supported_crop(species=species, **config)
            else:
                config["species"] = "custom " + str(species)

        return self._make_custom_crop(**config)

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
