from typing import List
import pytest

from RUFAS.current_day_conditions import CurrentDayConditions


@pytest.mark.parametrize("snow_fall, rainfall, actual", [
    (0, 1, CurrentDayConditions(incoming_light=1, min_air_temperature=1, mean_air_temperature=1, max_air_temperature=1,
                                annual_mean_air_temperature=1, precipitation=1, irrigation=1, daylength=8.5)),
    (0, 2, CurrentDayConditions(incoming_light=1, min_air_temperature=1, mean_air_temperature=0, max_air_temperature=1,
                                annual_mean_air_temperature=1, precipitation=2, irrigation=1, daylength=8.5)),
    (3, 0, CurrentDayConditions(incoming_light=1, min_air_temperature=1, mean_air_temperature=-1, max_air_temperature=1,
                                annual_mean_air_temperature=1, precipitation=3, irrigation=1, daylength=8.5))
])
def test_current_weather_snowfall(snow_fall: int, rainfall: int, actual: CurrentDayConditions) -> None:
    """Tests that precipitation falls either as snow or rain correctly."""
    assert actual.snowfall == snow_fall
    assert actual.rainfall == rainfall


@pytest.mark.parametrize("months, expected", [
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [9, 10, 11, 13, 14, 15, 15, 15, 13, 12, 10, 9])
])
def test_determine_daylength(months: List[int], expected: List[int]):
    """Tests that correct day length were returned by the corresponding month"""
    day_length = []
    for month in months:
        day_length.append(CurrentDayConditions.determine_daylength(month))
    assert day_length == expected
