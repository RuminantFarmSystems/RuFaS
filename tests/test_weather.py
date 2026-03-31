import math
from datetime import datetime
from typing import Callable
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from pytest_mock.plugin import MockerFixture

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather


@pytest.fixture
def mock_weather_input() -> dict:
    weather_data = {
        "year": [1],
        "jday": [1, 2, 3, 4, 5],
        "precip": [0.0] * 5,
        "high": [0.0] * 5,
        "low": [0.0] * 5,
        "avg": [0.0] * 5,
        "Hday": [0.0] * 5,
        "irrigation": [0.0] * 5,
    }
    return weather_data


@pytest.fixture
def mock_time() -> RufasTime:
    """Fixture for RufasTime object."""
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.calendar_year = 2023
    mock_time.year = 1
    mock_time.day = 1
    mock_time.start_year_int = 2022
    mock_time.end_year_int = 2023
    return mock_time


@pytest.fixture
def mock_weather(mocker: MockerFixture) -> Weather:
    """Fixture for Weather object."""
    mocker.patch("RUFAS.weather.Weather.__init__", return_value=None)
    mock_weather = Weather({}, mock_time)
    mock_weather.om = OutputManager()
    mock_weather.means = [10.0, 20.0, 30.0]
    mock_weather.cos = [0.5, 0.6, 0.7]
    mock_weather.sin = [0.1, 0.2, 0.3]
    weather_data = {
        datetime(2023, 9, 24): CurrentDayConditions(
            incoming_light=1,
            min_air_temperature=1,
            mean_air_temperature=1,
            max_air_temperature=1,
            precipitation=1,
            irrigation=1,
        ),
        datetime(2023, 9, 25): CurrentDayConditions(
            incoming_light=2,
            min_air_temperature=2,
            mean_air_temperature=2,
            max_air_temperature=2,
            precipitation=2,
            irrigation=2,
        ),
        datetime(2023, 9, 26): CurrentDayConditions(
            incoming_light=3,
            min_air_temperature=3,
            mean_air_temperature=3,
            max_air_temperature=3,
            precipitation=3,
            irrigation=3,
        ),
    }
    mock_weather.weather_data = weather_data
    mock_weather.mean_annual_temperature = 77

    return mock_weather


@pytest.fixture
def weather_original_method_states(mock_weather: Weather) -> dict[str, Callable]:
    """Fixture to store unmocked methods of Weather."""
    return {
        "_calculate_average_annual_temperature": mock_weather._calculate_average_annual_temperature,
        "get_current_day_conditions": mock_weather.get_current_day_conditions,
    }


@pytest.fixture
def mock_current_day_conditions() -> CurrentDayConditions:
    """Fixture for CurrentDayConditions object."""
    mock_current_weather = MagicMock(CurrentDayConditions)
    mock_current_weather.incoming_light = 12.0
    mock_current_weather.precipitation = 5.0
    mock_current_weather.rainfall = 5.0
    mock_current_weather.snowfall = 0.0
    mock_current_weather.min_air_temperature = 15.0
    mock_current_weather.mean_air_temperature = 17.0
    mock_current_weather.max_air_temperature = 19.0
    mock_current_weather.annual_mean_air_temperature = 14.5
    mock_current_weather.daylength = 15.0
    mock_current_weather.irrigation = 0.0
    return mock_current_weather


def test_weather_init(mock_weather_input: dict, mock_time: RufasTime, mocker: MockerFixture) -> None:
    """Tests that subroutines are called appropriately when Weather instance in initialized."""
    with (
        patch("RUFAS.weather.Weather.check_adequate_weather_data") as check,
        patch("RUFAS.output_manager.OutputManager.add_variable") as add,
        patch("RUFAS.weather.Weather._calculate_average_annual_temperature") as avg,
    ):
        mock_time.start_date = datetime(2023, 11, 1)
        mock_time.end_date = datetime(2023, 11, 5)
        convert = mocker.patch.object(RufasTime, "convert_year_jday_to_date", return_value=datetime(2023, 11, 3))
        Weather(mock_weather_input, mock_time)
        check.assert_called_once()
        add.assert_called_once()
        avg.assert_called_once()
        assert convert.call_count == 1


@pytest.mark.parametrize(
    "avg_daily_temperatures,expected",
    [
        ([12.3, 20.4, 15.6, 20.5, 17.8], 17.32),
        ([-4.55, -3.22, -1.05, -0.3, 1.44, 3.99, 8.6], 0.7014285714285712),
    ],
)
def test_calculate_average_annual_temperature(avg_daily_temperatures: list[float], expected: float) -> None:
    """Tests that the annual average air temperature is correctly calculated based on average daily temperatures."""
    actual = Weather._calculate_average_annual_temperature(avg_daily_temperatures)
    assert actual == expected


@pytest.mark.parametrize(
    "day,calendar_year,latitude,expected,time",
    [
        (
            1,
            1,
            43.0,
            CurrentDayConditions(
                incoming_light=1,
                min_air_temperature=1,
                mean_air_temperature=1,
                max_air_temperature=1,
                precipitation=1,
                irrigation=1,
                daylength=10.0,
                annual_mean_air_temperature=77,
            ),
            datetime(2023, 9, 24),
        ),
        (
            3,
            1,
            None,
            CurrentDayConditions(
                incoming_light=2,
                min_air_temperature=2,
                mean_air_temperature=2,
                max_air_temperature=2,
                precipitation=2,
                irrigation=2,
                daylength=None,
                annual_mean_air_temperature=77,
            ),
            datetime(2023, 9, 25),
        ),
    ],
)
def test_get_current_day_conditions(
    mocker: MockerFixture,
    mock_weather: Weather,
    day: int,
    calendar_year: int,
    latitude: float | None,
    expected: CurrentDayConditions,
    time: datetime,
) -> None:
    """Tests that CurrentDayConditions instances are correctly created by Weather."""
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "current_date", time)
    setattr(mocked_time, "current_calendar_year", calendar_year)
    setattr(mocked_time, "current_julian_day", day)
    daylength = mocker.patch("RUFAS.current_day_conditions.CurrentDayConditions.determine_daylength", return_value=10.0)

    actual = mock_weather.get_current_day_conditions(mocked_time, latitude)

    assert actual == expected
    if latitude:
        daylength.assert_called_once_with(day, latitude, calendar_year)
    else:
        daylength.assert_not_called


@pytest.mark.parametrize(
    "day,calendar_year,expected,time",
    [
        (1, 2069, "Attempted to get weather conditions for day: 1, year: 2069.", datetime(2069, 1, 1)),
        (1, 1950, "Attempted to get weather conditions for day: 1, year: 1950.", datetime(1950, 1, 1)),
    ],
)
def test_get_current_day_conditions_error(
    mocker: MockerFixture,
    mock_weather: Weather,
    day: int,
    calendar_year: int,
    expected: CurrentDayConditions,
    time: datetime,
) -> None:
    """Tests that error is raised properly when weather does not have data for specified time."""
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "current_date", time)
    setattr(mocked_time, "current_julian_day", day)
    setattr(mocked_time, "current_calendar_year", calendar_year)
    mocker.patch("RUFAS.current_day_conditions.CurrentDayConditions.determine_daylength", return_value=10.0)

    with pytest.raises(KeyError) as e:
        mock_weather.get_current_day_conditions(mocked_time)

    assert str(e.value.args[0]) == expected


@pytest.mark.parametrize(
    "start,end,latitude,expected",
    [
        (
            -1,
            1,
            43.0,
            [
                CurrentDayConditions(
                    incoming_light=1,
                    min_air_temperature=1,
                    mean_air_temperature=1,
                    max_air_temperature=1,
                    precipitation=1,
                    irrigation=1,
                    daylength=15.6,
                    annual_mean_air_temperature=77,
                ),
                CurrentDayConditions(
                    incoming_light=2,
                    min_air_temperature=2,
                    mean_air_temperature=2,
                    max_air_temperature=2,
                    precipitation=2,
                    irrigation=2,
                    daylength=15.6,
                    annual_mean_air_temperature=77,
                ),
                CurrentDayConditions(
                    incoming_light=3,
                    min_air_temperature=3,
                    mean_air_temperature=3,
                    max_air_temperature=3,
                    precipitation=3,
                    irrigation=3,
                    daylength=15.6,
                    annual_mean_air_temperature=77,
                ),
            ],
        ),
        (
            -1,
            1,
            None,
            [
                CurrentDayConditions(
                    incoming_light=1,
                    min_air_temperature=1,
                    mean_air_temperature=1,
                    max_air_temperature=1,
                    precipitation=1,
                    irrigation=1,
                    daylength=None,
                    annual_mean_air_temperature=77,
                ),
                CurrentDayConditions(
                    incoming_light=2,
                    min_air_temperature=2,
                    mean_air_temperature=2,
                    max_air_temperature=2,
                    precipitation=2,
                    irrigation=2,
                    daylength=None,
                    annual_mean_air_temperature=77,
                ),
                CurrentDayConditions(
                    incoming_light=3,
                    min_air_temperature=3,
                    mean_air_temperature=3,
                    max_air_temperature=3,
                    precipitation=3,
                    irrigation=3,
                    daylength=None,
                    annual_mean_air_temperature=77,
                ),
            ],
        ),
    ],
)
def test_get_conditions_series(
    mock_weather: Weather,
    mock_time: RufasTime,
    mocker: MockerFixture,
    start: int,
    end: int,
    latitude: float | None,
    expected: list[CurrentDayConditions],
) -> None:
    """Tests that series of CurrentDayConditions are created correctly."""
    setattr(mock_time, "current_date", datetime(2023, 9, 25))
    daylength = mocker.patch.object(CurrentDayConditions, "determine_daylength", return_value=15.6)

    actual = mock_weather.get_conditions_series(mock_time, start, end, latitude)

    assert actual == expected
    assert daylength.call_count == (len(expected) if latitude else 0)


def test_record_weather(
    mock_weather: Weather,
    mock_current_day_conditions: CurrentDayConditions,
    mock_time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Tests that weather conditions are correctly recorded to the OutputManager."""

    add_var = mocker.patch("RUFAS.output_manager.OutputManager.add_variable")
    mock_current_day_conditions = mocker.patch.object(
        mock_weather, "get_current_day_conditions", return_value=mock_current_day_conditions
    )

    mock_weather.record_weather(mock_time)
    assert mock_current_day_conditions.call_count == 1
    assert add_var.call_count == 8


@pytest.mark.parametrize("weather_file", [{"year": [2023], "jday": [267, 268, 269, 270, 271]}])
def test_check_adequate_weather_data(weather_file: dict, mock_weather: Weather) -> None:
    """Checks that check_adequate_weather_data works correctly"""
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "current_date", datetime(2023, 9, 24))
    setattr(mocked_time, "start_date", datetime(2023, 9, 24))
    setattr(mocked_time, "end_date", datetime(2023, 9, 26))

    mock_weather.check_adequate_weather_data(weather_file, mocked_time)


@pytest.mark.parametrize("weather_file", [{"year": [2023], "jday": [267]}])
def test_check_adequate_weather_data_error(weather_file: dict, mocker: MockerFixture) -> None:
    """Checks that check_adequate_weather_data works correctly when there's insufficient weather data"""
    patch_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "current_date", datetime(2023, 9, 24))
    setattr(mocked_time, "start_date", datetime(2023, 9, 24))
    setattr(mocked_time, "end_date", datetime(2023, 9, 26))

    try:
        Weather.check_adequate_weather_data(weather_file, mocked_time)
        patch_add_error.assert_called_once()
    except ValueError as e:
        assert e.args[0] == "Not enough weather data provided to support the duration of simulation period"


@pytest.mark.parametrize(
    "lstsq_result, expected_intercept, expected_amplitude, expected_phase_shift",
    [
        (
            (np.array([10.0, 0.0, 20.0]), None, None, None),
            20.0,
            10.0,
            365.0,
        ),
        (
            (np.array([0.0, 10.0, 15.0]), None, None, None),
            15.0,
            10.0,
            -273.75,
        ),
        (
            (np.array([3.0, 4.0, 5.0]), None, None, None),
            5.0,
            5.0,
            ((math.atan2(4.0, 3.0) / (2 * math.pi) * 365) - 365),
        ),
        (
            (np.array([-3.0, 4.0, 10.0]), None, None, None),
            10.0,
            5.0,
            ((math.atan2(4.0, -3.0) / (2 * math.pi) * 365) - 365),
        ),
    ],
)
def test_set_LINEST_temperature_factors(
    mock_weather: Weather,
    mocker: MockerFixture,
    lstsq_result: tuple,
    expected_intercept: float,
    expected_amplitude: float,
    expected_phase_shift: float,
) -> None:
    """
    Tests that LINEST factors (amplitude, intercept, phase shift) are correctly
    calculated and set as attributes based on regression coefficients.
    """
    mocker.patch("numpy.linalg.lstsq", return_value=lstsq_result)

    mock_weather.means = [0.0] * 3
    mock_weather.cos = [0.0] * 3
    mock_weather.sin = [0.0] * 3

    mock_weather.set_linest_temperature_factors()

    assert mock_weather.intercept_mean_temp == expected_intercept
    assert mock_weather.amplitude == expected_amplitude
    assert mock_weather.phase_shift == pytest.approx(expected_phase_shift, abs=1e-4)
