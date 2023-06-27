from typing import List
import pytest

from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather


@pytest.mark.parametrize("months, expected", [
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [9, 10, 11, 13, 14, 15, 15, 15, 13, 12, 10, 9])
])
def test_determine_daylength(months: List[int], expected: List[int]):
    """Tests that correct day length were returned by the corresponding month"""
    day_length = []
    for month in months:
        day_length.append(CurrentWeather.determine_daylength(month))
    assert day_length == expected
