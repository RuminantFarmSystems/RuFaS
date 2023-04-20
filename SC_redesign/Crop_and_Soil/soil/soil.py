from __future__ import annotations
from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.evapotranspiration import Evapotranspiration
from SC_redesign.Crop_and_Soil.soil.infiltration import Infiltration
from SC_redesign.Crop_and_Soil.soil.percolation import Percolation
from SC_redesign.Crop_and_Soil.soil.soil_temp import SoilTemp
from SC_redesign.Crop_and_Soil.soil.soil_erosion import SoilErosion
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.fertilizer import Fertilizer


class Soil:
    def __init__(self, soil_data: Optional[SoilData] = None):
        """creates a Soil object based on a SoilData object

        Args:
            soil_data: a SoilData object containing initial attribute values as well as attributes tracked and updated
                throughout the simulation

        Details:
            If no SoilData object is passed, default configuration is used.

        """
        self.data = soil_data or SoilData()
        """object that tracks all soil variable throughout the simulation"""

        # Process components
        self.evapotranspiration = Evapotranspiration(self.data)
        """Process component that controls evapotranspiration from the soil"""
        self.infiltration = Infiltration(self.data)
        """Process component that controls water infiltration from the soil surface into the profile"""
        self.percolation = Percolation(self.data)
        """Process component that controls percolation of water from upper layers to lower layers"""
        self.soil_temp = SoilTemp(self.data)
        """Process component that tracks and updates the temperatures within the soil profile"""
        self.soil_erosion = SoilErosion(self.data)
        """Process component that track erosion from the soil profile"""
        self.fertilizer_phosphorus = Fertilizer(self.data)
        """Process component that tracks fertilizer added to the soil via """

    @classmethod
    def make_from_config(cls, soil_config) -> Soil:
        """Creates a soil profile with attributes specified in the soil_config passed"""
        Warning("create from config file not yet implement, returning default Soil()")
        return Soil()

    def daily_soil_routine(self, solar_radiation: float, avg_temp: float, min_temp: float, max_temp: float,
                           plant_cover: float, snow_cover: float, avg_annual_air_temp: float) -> None:
        """this method calls all now-water related daily update routines

        Args:
            solar_radiation: solar radiation reaching the ground on the current day (MJ per square meter per day)
            avg_temp: average temperature of the current day (degrees C)
            min_temp: minimum temperature of the current day (degrees C)
            max_temp: maximum temperature of the current day (degrees C)
            plant_cover: total above-ground plant biomass and residue on the current day (kg per hectare)
            snow_cover: water content of the snow cover on the current day (mm)
            avg_annual_air_temp: average annual air temperature (degrees C)
        """
        # TODO: if no other daily update methods are added here, this method should be removed and Field should call
        #       this method directly
        self.soil_temp.daily_soil_temperature_update(solar_radiation, avg_temp, min_temp, max_temp, plant_cover,
                                                     snow_cover, avg_annual_air_temp)

    def daily_soil_water_routine(self, rainfall: float, weighting_coefficient: float,
                                 has_seasonal_high_water_table: bool, solar_radiation: float,
                                 max_air_temp: float, min_air_temp: float,
                                 avg_air_temp: float, above_ground_biomass: float, residue: float,
                                 snow_water_content: float, initial_canopy_free_water: float,
                                 minimum_cover_management_factor: float, field_size: float) -> None:
        """this method calls all water related daily update routines

        Args:
            rainfall: rainfall depth of current day (mm)
            weighting_coefficient: weighting coefficient used to calculate retention coefficient for daily curve number
                calculations dependent on plant evapotranspiration (unitless)
            has_seasonal_high_water_table: if the HRU has a seasonal high water table (true/false)
            solar_radiation: incoming solar, in MJ per square meter per day
            max_air_temp: maximum air temperature (degrees C)
            min_air_temp: minimum air temperature (degrees C)
            avg_air_temp: average air temperature (degrees C)
            above_ground_biomass: mass of plant above ground (kg per hectare)
            residue: biomass separated from plant on the ground (kg per hectare)
            snow_water_content: amount of water from snow (mm)
            initial_canopy_free_water: initial amount of free water held in canopy on a given day (mm)
            minimum_cover_management_factor: minimum value for cover and management factor for water erosion applicable
                to land cover/plant (unitless)
            field_size: size of the field (ha)
        """
        self.infiltration.infiltrate(rainfall, weighting_coefficient)
        self.percolation.percolate(has_seasonal_high_water_table)
        self.evapotranspiration.evapotranspirate(solar_radiation, max_air_temp, min_air_temp, avg_air_temp,
                                                 above_ground_biomass, residue, snow_water_content,
                                                 initial_canopy_free_water)
        self.soil_erosion.erode(field_size, minimum_cover_management_factor, residue)
        self.fertilizer_phosphorus.do_fertilizer_phosphorus_operations(rainfall,
                                                                       self.data.accumulated_runoff * field_size,
                                                                       field_size)
