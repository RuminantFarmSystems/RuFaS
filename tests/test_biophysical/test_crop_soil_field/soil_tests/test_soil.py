from unittest.mock import MagicMock

import pytest

from RUFAS.biophysical.field.soil.soil import Soil


@pytest.mark.parametrize(
    "solar_radiation,avg_temp,min_temp,max_temp,plant_cover,snow_cover,avg_annual_air_temp",
    [(20, 18, 16, 25, 36, 77, 24), (20.1, 18.36, 16.48, 25.31, 36.66, 77.34, 24.99)],
)
def test_daily_soil_routine(
    solar_radiation: float,
    avg_temp: float,
    min_temp: float,
    max_temp: float,
    plant_cover: float,
    snow_cover: float,
    avg_annual_air_temp: float,
) -> None:
    """Tests that method calls are correct in daily soil routine method"""
    soil = Soil(field_size=50)
    soil.soil_temp.daily_soil_temperature_update = MagicMock()
    soil.daily_soil_routine(
        solar_radiation,
        avg_temp,
        min_temp,
        max_temp,
        plant_cover,
        snow_cover,
        avg_annual_air_temp,
    )
    assert soil.soil_temp.daily_soil_temperature_update.call_count == 1
    soil.soil_temp.daily_soil_temperature_update.assert_called_once_with(
        solar_radiation,
        avg_temp,
        min_temp,
        max_temp,
        plant_cover,
        snow_cover,
        avg_annual_air_temp,
    )


@pytest.mark.parametrize(
    "rainfall,weighting_coefficient,potential_evapotranspiration,has_seasonal_high_water_table,"
    "maximum_soil_evaporation,avg_air_temp,residue,minimum_cover_management_factor,field_size",
    [
        (20, 56, 23, True, 26, 374, 23, 10, 23),
        (20, 56, 23, False, 26, 374, 23, 10, 23),
        (20.35, 56.56, 23.39, True, 26.98, 374.34, 23.33, 10.64, 23.924),
        (20.35, 56.56, 23.39, False, 26.98, 374.34, 23.33, 10.64, 23.924),
    ],
)
def test_daily_soil_water_routine(
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
    soil = Soil(field_size=50)
    soil.infiltration.infiltrate = MagicMock()
    soil.percolation.percolate = MagicMock()
    soil.percolation.percolate_infiltrated_water = MagicMock()
    soil.evaporation.evaporate = MagicMock()
    soil.soil_erosion.erode = MagicMock()
    soil.phosphorus_cycling.cycle_phosphorus = MagicMock()
    soil.nitrogen_cycling.cycle_nitrogen = MagicMock()
    soil.carbon_cycling.cycle_carbon = MagicMock()
    soil.daily_soil_water_routine(
        rainfall,
        weighting_coefficient,
        potential_evapotranspiration,
        has_seasonal_high_water_table,
        maximum_soil_evaporation,
        avg_air_temp,
        residue,
        minimum_cover_management_factor,
        field_size,
    )

    soil.infiltration.infiltrate.assert_called_once_with(rainfall, weighting_coefficient, potential_evapotranspiration)
    soil.percolation.percolate.assert_called_once_with(has_seasonal_high_water_table)
    soil.percolation.percolate_infiltrated_water.assert_called_once()
    soil.evaporation.evaporate.assert_called_once_with(maximum_soil_evaporation)
    soil.soil_erosion.erode.assert_called_once_with(field_size, minimum_cover_management_factor, residue, rainfall)
    soil.phosphorus_cycling.cycle_phosphorus.assert_called_once_with(
        rainfall, soil.data.accumulated_runoff, field_size, avg_air_temp
    )
    soil.nitrogen_cycling.cycle_nitrogen.assert_called_once_with(field_size)
    soil.carbon_cycling.cycle_carbon.assert_called_once_with(rainfall, avg_air_temp, field_size)
