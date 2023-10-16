from typing import List
import pytest
from unittest.mock import MagicMock

from RUFAS.classes.current_weather import CurrentWeather
from RUFAS.classes.time import Time


@pytest.mark.parametrize("snow_fall, rainfall, actual", [
    (0, 1, CurrentWeather(incoming_light=1, min_air_temperature=1, mean_air_temperature=1, max_air_temperature=1,
                          annual_mean_air_temperature=1, precipitation=1, irrigation=1, daylength=8.5)),
    (0, 2, CurrentWeather(incoming_light=1, min_air_temperature=1, mean_air_temperature=0, max_air_temperature=1,
                          annual_mean_air_temperature=1, precipitation=2, irrigation=1, daylength=8.5)),
    (3, 0, CurrentWeather(incoming_light=1, min_air_temperature=1, mean_air_temperature=-1, max_air_temperature=1,
                          annual_mean_air_temperature=1, precipitation=3, irrigation=1, daylength=8.5))
])
def test_current_weather_snowfall(snow_fall: int, rainfall: int, actual: CurrentWeather) -> None:
    """Tests that precipitation falls either as snow or rain correctly."""
    assert actual.snow_fall == snow_fall
    assert actual.rainfall == rainfall


@pytest.mark.parametrize("months, expected", [
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [9, 10, 11, 13, 14, 15, 15, 15, 13, 12, 10, 9])
])
def test_determine_daylength(months: List[int], expected: List[int]):
    """Tests that correct day length were returned by the corresponding month"""
    day_length = []
    for month in months:
        day_length.append(CurrentWeather.determine_daylength(month))
    assert day_length == expected


@pytest.mark.parametrize("year, day, expected_month", [
    (2000, 366, 12),  # leap year
    (2001, 365, 12),  # normal year
    (2000, 60, 2),
    (2001, 60, 3)
])
def test_date_conversion_month(year: int, day: int, expected_month: int):
    """Tests that number of days were converted into months correctly"""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "calendar_year", year)
    setattr(mocked_time, "day", day)
    assert CurrentWeather.date_conversion_month(mocked_time) == expected_month
