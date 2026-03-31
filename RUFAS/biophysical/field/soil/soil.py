from __future__ import annotations

from typing import Optional

from RUFAS.biophysical.field.soil.carbon_cycling.carbon_cycle import CarbonCycling
from RUFAS.biophysical.field.soil.evaporation import Evaporation
from RUFAS.biophysical.field.soil.infiltration import Infiltration
from RUFAS.biophysical.field.soil.nitrogen_cycling.nitrogen_cycling import NitrogenCycling
from RUFAS.biophysical.field.soil.percolation import Percolation
from RUFAS.biophysical.field.soil.phosphorus_cycling.phosphorus_cycling import PhosphorusCycling
from RUFAS.biophysical.field.soil.snow import Snow
from RUFAS.biophysical.field.soil.soil_data import SoilData
from RUFAS.biophysical.field.soil.soil_erosion import SoilErosion
from RUFAS.biophysical.field.soil.soil_temp import SoilTemp


class Soil:
    """
    A class to manage and simulate various soil processes based on a given SoilData object.

    Parameters
    ----------
    soil_data : SoilData, optional
        A SoilData object containing initial attribute values as well as attributes tracked and updated throughout the
        simulation.
    field_size : float, optional
        The size of the field in hectares (ha), used to initialize a SoilData object if a pre-configured SoilData object
        is not provided.

    Attributes
    ----------
    data : SoilData
        An object that tracks all soil variables throughout the simulation.
    soil_temp : SoilTemp
        Process component that tracks and updates the temperatures within the soil profile.
    phosphorus_cycling : PhosphorusCycling
        Process component managing phosphorus on top of and in the soil profile.
    carbon_cycling : CarbonCycling
        Process component that handles carbon cycling through decomposition in the soil.
    nitrogen_cycling : NitrogenCycling
        Process component for managing nitrogen within the soil profile.
    evaporation : Evaporation
        Process component that controls evaporation from the soil.
    infiltration : Infiltration
        Process component that controls water infiltration from the soil surface into the profile.
    percolation : Percolation
        Process component that controls percolation of water from upper layers to lower layers.
    soil_erosion : SoilErosion
        Process component that tracks erosion from the soil profile.
    snow : Snow
        Process component that tracks snow.

    """

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

        self.soil_temp = SoilTemp(self.data)
        self.phosphorus_cycling = PhosphorusCycling(self.data)
        self.carbon_cycling = CarbonCycling(self.data)
        self.nitrogen_cycling = NitrogenCycling(self.data)

        self.evaporation = Evaporation(self.data)
        self.infiltration = Infiltration(self.data)
        self.percolation = Percolation(self.data)
        self.soil_erosion = SoilErosion(self.data)
        self.snow = Snow(self.data)

    def daily_soil_routine(
        self,
        solar_radiation: float,
        avg_temp: float,
        min_temp: float,
        max_temp: float,
        plant_cover: float,
        snow_cover: float,
        avg_annual_air_temp: float,
    ) -> None:
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
        self.soil_temp.daily_soil_temperature_update(
            solar_radiation,
            avg_temp,
            min_temp,
            max_temp,
            plant_cover,
            snow_cover,
            avg_annual_air_temp,
        )

    def daily_soil_water_routine(
        self,
        rainfall: float,
        weighting_coefficient: float,
        potential_evapotranspiration: float,
        has_seasonal_high_water_table: bool,
        maximum_soil_evaporation: float,
        avg_air_temp: float,
        residue: float,
        minimum_cover_management_factor: float,
        field_size: float,
    ) -> None:
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
        self.percolation.percolate(has_seasonal_high_water_table)
        self.infiltration.infiltrate(rainfall, weighting_coefficient, potential_evapotranspiration)
        self.percolation.percolate_infiltrated_water()
        self.evaporation.evaporate(maximum_soil_evaporation)
        self.soil_erosion.erode(field_size, minimum_cover_management_factor, residue, rainfall)
        self.phosphorus_cycling.cycle_phosphorus(rainfall, self.data.accumulated_runoff, field_size, avg_air_temp)
        self.nitrogen_cycling.cycle_nitrogen(field_size)
        self.carbon_cycling.cycle_carbon(rainfall, avg_air_temp, field_size)
