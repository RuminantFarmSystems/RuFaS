from typing import List
from unittest.mock import MagicMock
import pytest

from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from RUFAS.classes import Weather


@pytest.mark.parametrize("radiation, T_min, T_avg, T_max, T_avg_annual, irrigation, rainfall, latitude, year, day, "
                         "month", [
                             (1, 2, 3, 4, 5, 6, 7, 10.5, 2018, 9, 10)
                         ])
def test_check_current_weather(radiation: float, T_min: float, T_avg: float, T_max: float, T_avg_annual: float,
                               irrigation: float, rainfall: float, latitude: float, year: int, day: int, month: int,
                               mocker) -> None:
    """Tests that a weather object was successfully translated into a current weather object"""

    mocked_weather = MagicMock(Weather)
    setattr(mocked_weather, "radiation", radiation)
    setattr(mocked_weather, "T_min", T_min)
    setattr(mocked_weather, "T_avg", T_avg)
    setattr(mocked_weather, "T_max", T_max)
    setattr(mocked_weather, "T_avg_annual", T_avg_annual)
    setattr(mocked_weather, "rainfall", rainfall)
    setattr(mocked_weather, "irrigation", irrigation)
    CurrentWeather._determine_daylength = MagicMock(return_value=12)
    CurrentWeather.check_current_weather(weather=mocked_weather, month=month)

    assert CurrentWeather.rainfall == rainfall
    assert CurrentWeather.incoming_light == radiation
    assert CurrentWeather.min_air_temperature == T_min
    assert CurrentWeather.mean_air_temperature == T_avg
    assert CurrentWeather.max_air_temperature == T_max
    assert CurrentWeather.annual_mean_air_temperature == T_avg_annual
    assert CurrentWeather._determine_daylength.call_count == 1
    assert CurrentWeather.daylength == 12
    assert CurrentWeather.irrigation == irrigation


@pytest.mark.parametrize("months, expected", [
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [9, 10, 11, 13, 14, 15, 15, 15, 13, 12, 10, 9])
])
def test_determine_daylength(months: List[int], expected: List[int]):
    """Tests that correct day length were returned by the corresponding month"""
    day_length = []
    for month in months:
        day_length.append(CurrentWeather._determine_daylength(month))
    assert day_length == expected
