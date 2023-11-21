import math
from unittest.mock import patch

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


@pytest.mark.parametrize("day_number, geographic_latitude, month, polar_location, northern_hemisphere, expected", [
    (15, 43.073, 1, False, True, 9),  # Madison example, no polar day or night possible
    (365, 68, 12, True, True, 0),  # Winter in polar circle (example take from Barrow, Alaska)
    (180, 68, 8, True, True, 24),  # Summer in polar circle
    (365, -68, 12, True, False, 24),  # Winter in polar circle (south hemisphere)
    (180, -68, 8, True, False, 0),  # Sumer in polar circle (south hemisphere)
])
def test_determine_daylength(day_number: int, geographic_latitude: float, month: int, polar_location: bool,
                             northern_hemisphere: bool, expected: float) -> None:
    """Tests that correct day length were returned by the corresponding month"""
    with patch('RUFAS.current_day_conditions.CurrentDayConditions.calculate_solar_declination_radians',
               wraps=CurrentDayConditions.calculate_solar_declination_radians) as mocked_radian_calculation:
        if polar_location:
            if month >= 6 or month <= 9:
                if northern_hemisphere:
                    assert CurrentDayConditions.determine_daylength(
                        day_number, geographic_latitude, month) == expected
                else:
                    assert CurrentDayConditions.determine_daylength(
                        day_number, geographic_latitude, month) == expected
            elif month == 12 or month <= 3:
                if northern_hemisphere:
                    assert CurrentDayConditions.determine_daylength(
                        day_number, geographic_latitude, month) == expected
                else:
                    assert CurrentDayConditions.determine_daylength(
                        day_number, geographic_latitude, month) == expected
            assert mocked_radian_calculation.call_count == 1
        else:
            assert expected == pytest.approx(CurrentDayConditions.determine_daylength(
                day_number, geographic_latitude, month), 0.1)
            assert mocked_radian_calculation.call_count == 1


@pytest.mark.parametrize("day_number", [
    2,
    82,
    365
])
def test_calculate_solar_declination_radians(day_number: int) -> None:
    """Tests the calculation of solar declination radians is as expected"""
    observed = CurrentDayConditions.calculate_solar_declination_radians(day_number)
    sin_param = (2 * math.pi) / 365 * (day_number - 82)
    asin_param = 0.4 * math.sin(sin_param)
    expected = math.asin(asin_param)
    assert observed == expected
