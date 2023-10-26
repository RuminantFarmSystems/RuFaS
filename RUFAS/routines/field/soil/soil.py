from __future__ import annotations
from typing import Optional

from RUFAS.routines.field.soil.carbon_cycling.carbon_cycle import CarbonCycling
from RUFAS.routines.field.soil.snow import Snow
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.soil.evaporation import Evaporation
from RUFAS.routines.field.soil.infiltration import Infiltration
from RUFAS.routines.field.soil.percolation import Percolation
from RUFAS.routines.field.soil.soil_temp import SoilTemp
from RUFAS.routines.field.soil.soil_erosion import SoilErosion
from RUFAS.routines.field.soil.phosphorus_cycling.phosphorus_cycling import PhosphorusCycling
from RUFAS.routines.field.soil.nitrogen_cycling.nitrogen_cycling import NitrogenCycling


class Soil:
    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        """Creates a Soil object based on a SoilData object.

        Parameters
        ----------
        soil_data: a SoilData object containing initial attribute values as well as attributes tracked and updated
            throughout the simulation
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        Notes
        -----
        If no SoilData object is passed, default configuration is used.

        """
        self.data = soil_data or SoilData(field_size=field_size)
        """object that tracks all soil variable throughout the simulation"""

        # Process components
        self.soil_temp = SoilTemp(self.data)
        """Process component that tracks and updates the temperatures within the soil profile"""
        self.phosphorus_cycling = PhosphorusCycling(self.data)
        """Process component managing phosphorus on top of and in the soil profile"""
        self.carbon_cycling = CarbonCycling(self.data)
        """Process component that handles carbon cycling (through decomposition) in the soil."""
        # TODO: need to add phosphorus, manure, and carbon cycling main methods methods to the soil methods.
        #   It is unclear to me how best to do that.
        self.nitrogen_cycling = NitrogenCycling(self.data)
        """Process component for managing nitrogen within the soil profile."""

        # Water components
        self.evaporation = Evaporation(self.data)
        """Process component that controls evaporation from the soil"""
        self.infiltration = Infiltration(self.data)
        """Process component that controls water infiltration from the soil surface into the profile"""
        self.percolation = Percolation(self.data)
        """Process component that controls percolation of water from upper layers to lower layers"""
        self.soil_erosion = SoilErosion(self.data)
        """Process component that tracks erosion from the soil profile"""
        self.snow = Snow(self.data)
        """Process component that tracks snow"""

    def daily_soil_routine(self, solar_radiation: float, avg_temp: float, min_temp: float, max_temp: float,
                           plant_cover: float, snow_cover: float, avg_annual_air_temp: float) -> None:
        """
        Call all non-water related daily update routines.

        Parameters
        ----------
        solar_radiation : float
            Solar radiation reaching the ground on the current day (MJ per square meter per day).
        avg_temp : float
            Average temperature of the current day (degrees C).
        min_temp : float
            Minimum temperature of the current day (degrees C).
        max_temp : float
            Maximum temperature of the current day (degrees C).
        plant_cover : float
            Total above-ground plant biomass and residue on the current day (kg per hectare).
        snow_cover : float
            Water content of the snow cover on the current day (mm).
        avg_annual_air_temp : float
            Average annual air temperature (degrees C).
        """
        # TODO: if no other daily update methods are added here, this method should be removed and Field should call
        #       this method directly
        self.soil_temp.daily_soil_temperature_update(solar_radiation, avg_temp, min_temp, max_temp, plant_cover,
                                                     snow_cover, avg_annual_air_temp)

    def daily_soil_water_routine(self, rainfall: float, weighting_coefficient: float,
                                 potential_evapotranspiration: float, has_seasonal_high_water_table: bool,
                                 maximum_soil_evaporation: float, avg_air_temp: float, residue: float,
                                 minimum_cover_management_factor: float, field_size: float) -> None:
        """
        Call all water-related daily update routines.

        Parameters
        ----------
        rainfall : float
            Rainfall depth of the current day (mm).
        weighting_coefficient : float
            Weighting coefficient used to calculate the retention coefficient for daily curve number calculations,
            dependent on plant evapotranspiration (unitless).
        potential_evapotranspiration : float
            Total potential evaporation and transpiration that can occur on the current day (mm).
        has_seasonal_high_water_table : bool
            Whether the HRU has a seasonal high water table (True/False).
        maximum_soil_evaporation : float
            Maximum amount of water that can be evaporated from the soil profile on the current day (mm).
        avg_air_temp : float
            Average air temperature (degrees C).
        residue : float
            Biomass separated from plants on the ground (kg per hectare).
        minimum_cover_management_factor : float
            Minimum value for the cover and management factor for water erosion applicable to land cover/plant
            (unitless).
        field_size : float
            Size of the field (ha).

        Notes
        -----
        The daily phosphorus cycling method is called here because in large part the phosphorus dynamics of the soil
        profile depend on how much water enters and moves through the soil profile.
        """
        self.infiltration.infiltrate(rainfall, weighting_coefficient, potential_evapotranspiration)
        self.percolation.percolate(has_seasonal_high_water_table)
        self.evaporation.evaporate(maximum_soil_evaporation)
        self.soil_erosion.erode(field_size, minimum_cover_management_factor, residue, rainfall)
        self.phosphorus_cycling.cycle_phosphorus(rainfall, self.data.accumulated_runoff, field_size, avg_air_temp)
        self.nitrogen_cycling.cycle_nitrogen(field_size)
        self.carbon_cycling.cycle_carbon(rainfall, avg_air_temp, field_size)
