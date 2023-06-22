from unittest import mock
from unittest.mock import MagicMock
import pytest
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from RUFAS.classes import Weather


@pytest.mark.parametrize("radiation, T_min, T_avg, T_max, T_avg_annual, rainfall, latitude, year, day, month", [
    (1, 2, 3, 4, 5, 6, 7, 2018, 9, 10)
])
def test_check_current_weather(radiation: float, T_min: float, T_avg: float, T_max: float, T_avg_annual: float,
                               rainfall: float, latitude: float, year: int, day: int, month: int) -> None:
    """Tests that a weather object was successfully translated into a current weather object"""

    mocked_weather = MagicMock(Weather)
    setattr(mocked_weather, "radiation", radiation)
    setattr(mocked_weather, "T_min", T_min)
    setattr(mocked_weather, "T_avg", T_avg)
    setattr(mocked_weather, "T_max", T_max)
    setattr(mocked_weather, "T_avg_annual", T_avg_annual)
    setattr(mocked_weather, "rainfall", rainfall)
    CurrentWeather.check_current_weather(weather=mocked_weather, latitude=latitude, year=year,
                                         month=month, day=day)

    assert CurrentWeather.rainfall == rainfall
    assert CurrentWeather.incoming_light == radiation
    assert CurrentWeather.min_air_temperature == T_min
    assert CurrentWeather.mean_air_temperature == T_avg
    assert CurrentWeather.max_air_temperature == T_max
    assert CurrentWeather.annual_mean_air_temperature == T_avg_annual
