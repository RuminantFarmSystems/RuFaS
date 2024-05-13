import math

import pytest
from pytest_mock import MockerFixture

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.util import Utility


@pytest.mark.parametrize(
    "snow_fall, rainfall, actual",
    [
        (
            0,
            1,
            CurrentDayConditions(
                incoming_light=1,
                min_air_temperature=1,
                mean_air_temperature=1,
                max_air_temperature=1,
                annual_mean_air_temperature=1,
                precipitation=1,
                irrigation=1,
                daylength=8.5,
            ),
        ),
        (
            0,
            2,
            CurrentDayConditions(
                incoming_light=1,
                min_air_temperature=1,
                mean_air_temperature=0,
                max_air_temperature=1,
                annual_mean_air_temperature=1,
                precipitation=2,
                irrigation=1,
                daylength=8.5,
            ),
        ),
        (
            3,
            0,
            CurrentDayConditions(
                incoming_light=1,
                min_air_temperature=1,
                mean_air_temperature=-1,
                max_air_temperature=1,
                annual_mean_air_temperature=1,
                precipitation=3,
                irrigation=1,
                daylength=8.5,
            ),
        ),
    ],
)
def test_current_weather_snowfall(snow_fall: int, rainfall: int, actual: CurrentDayConditions) -> None:
    """Tests that precipitation falls either as snow or rain correctly."""
    assert actual.snowfall == snow_fall
    assert actual.rainfall == rainfall


@pytest.mark.parametrize(
    "day_number, geographic_latitude, polar_location, expected, year",
    [
        (15, 43.073, False, 9, 2023),  # Madison example, no polar day or night possible
        (365, 68, True, 0, 2023),  # Winter in polar circle (example take from Barrow, Alaska)
        (180, 68, True, 24, 2023),  # Summer in polar circle
        (365, -68, True, 24, 2023),  # Winter in polar circle (south hemisphere)
        (180, -68, True, 0, 2023),  # Sumer in polar circle (south hemisphere)
    ],
)
def test_determine_daylength(
    mocker: MockerFixture,
    day_number: int,
    geographic_latitude: float,
    polar_location: bool,
    expected: float,
    year: int,
) -> None:
    """Tests that correct day length were returned by the corresponding month"""
    mocked_radian_calculation = mocker.patch(
        "RUFAS.current_day_conditions.CurrentDayConditions.calculate_solar_declination_radians",
        wraps=CurrentDayConditions.calculate_solar_declination_radians,
    )

    mock_date_conversion = mocker.patch(
        "RUFAS.util.Utility.convert_ordinal_date_to_month_date", wraps=Utility.convert_ordinal_date_to_month_date
    )

    actual = CurrentDayConditions.determine_daylength(day_number, geographic_latitude, year)

    tolerance = 0.1 if not polar_location else 0.0
    assert expected == pytest.approx(actual, tolerance)
    assert mocked_radian_calculation.call_count == 1
    if polar_location:
        assert mock_date_conversion.call_count == 1
    else:
        assert mock_date_conversion.call_count == 0


@pytest.mark.parametrize("day_number", [2, 82, 365])
def test_calculate_solar_declination_radians(day_number: int) -> None:
    """Tests the calculation of solar declination radians is as expected"""
    observed = CurrentDayConditions.calculate_solar_declination_radians(day_number)
    sin_param = (2 * math.pi) / 365 * (day_number - 82)
    asin_param = 0.4 * math.sin(sin_param)
    expected = math.asin(asin_param)
    assert observed == expected
