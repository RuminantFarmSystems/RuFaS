from __future__ import annotations

from typing import Optional

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.biophysical.field.crop.biomass_allocation import BiomassAllocation
from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.crop_data_factory import CropDataFactory
from RUFAS.biophysical.field.crop.crop_management import CropManagement
from RUFAS.biophysical.field.crop.dormancy import Dormancy
from RUFAS.biophysical.field.crop.growth_constraints import GrowthConstraints
from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation
from RUFAS.biophysical.field.crop.heat_units import HeatUnits
from RUFAS.biophysical.field.crop.leaf_area_index import LeafAreaIndex
from RUFAS.biophysical.field.crop.nitrogen_uptake import NitrogenUptake
from RUFAS.biophysical.field.crop.phosphorus_uptake import PhosphorusUptake
from RUFAS.biophysical.field.crop.root_development import RootDevelopment
from RUFAS.biophysical.field.crop.water_dynamics import WaterDynamics
from RUFAS.biophysical.field.crop.water_uptake import WaterUptake
from RUFAS.biophysical.field.field.field_data import FieldData
from RUFAS.biophysical.field.soil.soil import Soil
from RUFAS.biophysical.field.soil.soil_data import SoilData
from RUFAS.rufas_time import RufasTime


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
    _nitrogen_uptake : NitrogenUptake
        Process component controlling plant nitrogen incorporation, including uptake and fixation.
    _phosphorus_uptake : PhosphorusUptake
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
        self._data = crop_data or CropData()
        self._growth_constraints = GrowthConstraints(self._data)
        self._biomass_allocation = BiomassAllocation(self._data)
        self._water_dynamics = WaterDynamics(self._data)
        self._water_uptake = WaterUptake(self._data)
        self._nitrogen_uptake = NitrogenUptake(self._data)
        self._phosphorus_uptake = PhosphorusUptake(self._data)
        self._heat_units = HeatUnits(self._data)
        self._leaf_area_index = LeafAreaIndex(self._data)
        self._root_development = RootDevelopment(self._data)
        self._crop_management = CropManagement(self._data)
        self._dormancy = Dormancy(self._data)

    @property
    def data(self) -> CropData:
        """Provides access to the CropData object."""
        return self._data

    @property
    def growth_constraints(self) -> GrowthConstraints:
        """Provides access to the GrowthConstraints object."""
        return self._growth_constraints

    @property
    def biomass_allocation(self) -> BiomassAllocation:
        """Provides access to the BiomassAllocation object."""
        return self._biomass_allocation

    @property
    def nitrogen_uptake(self) -> NitrogenUptake:
        """Provides access to the NitrogenUptake object."""
        return self._nitrogen_uptake

    @property
    def leaf_area_index(self) -> LeafAreaIndex:
        """Provides access to the LeafAreaIndex object."""
        return self._leaf_area_index

    @property
    def water_dynamics(self) -> WaterDynamics:
        """Provides access to the WaterDynamics object."""
        return self._water_dynamics

    @property
    def crop_management(self) -> CropManagement:
        """Provides access to the CropManagement object."""
        return self._crop_management

    @property
    def phosphorus_incorporation(self) -> PhosphorusUptake:
        """Provides access to the PhosphorusUptake object."""
        return self._phosphorus_uptake

    def perform_daily_crop_update(
        self, current_conditions: CurrentDayConditions, field_data: FieldData, soil_data: SoilData, time: RufasTime
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
        self._root_development.develop_roots(time)
        self._nitrogen_uptake.uptake(soil_data)
        self._phosphorus_uptake.uptake(soil_data)
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

    def cycle_water_for_crop(
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
            self._water_uptake.uptake(soil_data)
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

    def handle_water_in_canopy(self, available_precipitation: float) -> float:
        """
        Handles the water addition to the crop's canopy and calculates excess water.

        Parameters
        ----------
        available_precipitation : float
            Amount of water available to reach the soil after considering other crops (mm).

        Returns
        -------
        tuple
            Amount of precipitation that reaches the soil after this crop (mm).
        """
        canopy_water_excess_capacity = self._data.water_canopy_storage_capacity - self._data.canopy_water

        water_taken_to_be_stored = max(0.0, canopy_water_excess_capacity)
        water_taken_to_be_stored = min(available_precipitation, water_taken_to_be_stored)
        self._data.canopy_water += water_taken_to_be_stored

        precipitation_reaching_soil = available_precipitation - water_taken_to_be_stored

        return precipitation_reaching_soil

    def evaporate_from_canopy(self, evapotranspirative_demand: float) -> float:
        """Wrapper for the canopy evaporation routine."""
        amount_evaporated = self._water_dynamics.evaporate_from_canopy(evapotranspirative_demand)
        return amount_evaporated

    def should_harvest_based_on_heat(self) -> bool:
        """Checks if any of the active plants in the field should be harvested based on their heat schedule."""
        return self._data.use_heat_scheduling and self._data.heat_fraction >= self._data.harvest_heat_fraction

    def manage_crop_harvest(
        self,
        harvest_operation: HarvestOperation,
        field_name: str,
        field_size: float,
        time: RufasTime,
        soil_data: SoilData,
    ) -> HarvestedCrop:
        """Wrapper function for the Crop's CropManagement harvesting operation.

        Parameters
        ----------
        harvest_operation : HarvestOperation
            The operation to be executed on this crop.
        field_name : str
            The name of the field that contains this crop.
        field_size : float
            Size of the field that contains this crop (ha)
        time : RufasTime
            RufasTime instance containing the current time of the simulation.
        soil_data : SoilData
            The object tracking the attributes of the soil profile.

        Returns
        -------
        HarvestedCrop
            A harvested crop data structure.

        """
        return self._crop_management.manage_harvest(harvest_operation, field_name, field_size, time, soil_data)

    def set_maximum_transpiration(self, evapotranspirative_demand: float) -> None:
        """Wrapper method for setting the max transpiration for a crop."""
        self._water_dynamics.set_maximum_transpiration(evapotranspirative_demand)

    def assess_dormancy(
        self, daylength: float, dormancy_threshold_daylength: float, rainfall: float, soil_data: SoilData, soil: Soil
    ) -> None:
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
        soil : Soil
            The soil profile.
        """
        if daylength <= dormancy_threshold_daylength:
            self.enter_dormancy(rainfall, soil_data, soil)
        else:
            self.exit_dormancy()

    def enter_dormancy(self, rainfall: float, soil_data: SoilData, soil: Soil) -> None:
        """
        Puts the crop into dormancy and handles biomass partitioning and residue addition.

        Parameters
        ----------
        rainfall : float
            Amount of rain that fell on the current day (mm).
        soil_data : SoilData
            The soil data relevant for dormancy and biomass partitioning.
        soil : Soil
            The soil profile.
        """
        self._dormancy.enter_dormancy(soil_data)
        self._biomass_allocation.partition_biomass()
        soil.carbon_cycling.residue_partition.add_residue_to_pools(rainfall)

    def exit_dormancy(self) -> None:
        """
        Brings the crop out of dormancy.
        """
        self._data.is_dormant = False

    @classmethod
    def create_crop(
        cls,
        crop_reference: str,
        use_heat_scheduled_harvesting: bool,
        time: RufasTime,
    ) -> Crop:
        """
        Factory method to create a crop instance based on the crop reference.

        Parameters
        ----------
        crop_reference : str
            The reference for the crop to be planted.
        use_heat_scheduled_harvesting : bool
            Whether heat-scheduled harvesting should be used.
        time : RufasTime
            The current time in the simulation.

        Returns
        -------
        Crop
            A fully initialized Crop instance.

        Notes
        -----
        This method starts by trying to determine if the crop is of a supported species, if so it passes
        it to the supported crop creation method. If not, it passes it to the custom crop creation method.

        """
        crop_data = CropDataFactory.create_crop_data(crop_reference)
        crop = Crop(crop_data=crop_data)

        crop.set_crop_planting_attributes(crop_reference, use_heat_scheduled_harvesting, time)
        return crop

    def set_crop_planting_attributes(
        self, crop_reference: str, use_heat_scheduled_harvesting: bool, time: RufasTime
    ) -> None:
        """
        Initializes the crop's attributes related to planting.

        Parameters
        ----------
        crop_reference : str
            The reference for the crop to be planted.
        use_heat_scheduled_harvesting : bool
            Whether heat-scheduled harvesting should be used.
        time : RufasTime
            The current time in the simulation.
        """
        self._data.use_heat_scheduling = use_heat_scheduled_harvesting
        self._data.id = crop_reference
        self._data.planting_year = time.current_calendar_year
        self._data.planting_day = time.current_julian_day

    def update_crop_max_root_depth(self, bottom_layer_depth: float) -> None:
        """
        Restricts the crops maximum rooting depth to the depth of the bottom of the soil profile in cases where the
        user-provided maximum rooting depth is greater than the bottom of the soil profile

        Parameters
        ----------

        """
        self.data.max_root_depth = min(bottom_layer_depth, self.data.max_root_depth)
