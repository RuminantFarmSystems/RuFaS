import pytest
from pytest_mock.plugin import MockerFixture
from unittest.mock import MagicMock, patch
from typing import Callable

from RUFAS.config import Config
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.time import Time
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
def mock_config() -> Config:
    mock_config = MagicMock(Config)
    setattr(mock_config, "years", [[1]])
    setattr(mock_config, "w_start_year", 0)
    setattr(mock_config, "w_start_day", 1)
    setattr(mock_config, "start_year", 1)
    setattr(mock_config, "start_day", 1)
    setattr(mock_config, "end_year", 1)
    setattr(mock_config, "end_day", 5)
    setattr(mock_config, "year_length", 365)
    setattr(mock_config, "leap_year_length", 366)
    return mock_config


@pytest.fixture
def mock_weather(mocker: MockerFixture) -> Weather:
    """Fixture for Weather object."""
    mocker.patch("RUFAS.weather.Weather.__init__", return_value=None)
    mock_config = MagicMock(Config)
    mock_weather = Weather({}, mock_config)
    mock_weather._Weather__radiation = [[1.0, 2.0, 3.0]]
    mock_weather._Weather__min_daily_temperature = [[1.1, 2.1, 3.1]]
    mock_weather._Weather__mean_daily_temperature = [[1.2, 2.2, 3.2]]
    mock_weather._Weather__max_daily_temperature = [[1.3, 2.3, 3.3]]
    mock_weather._Weather__precipitation = [[1.4, 2.4, 3.4]]
    mock_weather._Weather__irrigation = [[1.5, 2.5, 3.5]]
    mock_weather._Weather__mean_annual_temperature = 15.0

    return mock_weather


@pytest.fixture
def weather_original_method_states(mock_weather: Weather) -> dict[str, Callable]:
    """Fixture to store unmocked methods of Weather."""
    return {
        "_calculate_average_annual_temperature": mock_weather._calculate_average_annual_temperature,
        "get_current_day_conditions": mock_weather.get_current_day_conditions
    }


@pytest.fixture
def mock_current_day_conditions() -> CurrentDayConditions:
    """Fixture for CurrentDayConditions object."""
    mock_current_weather = MagicMock(CurrentDayConditions)
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


@pytest.fixture
def mock_time() -> Time:
    """Fixture for Time object."""
    mock_time = MagicMock(Time)
    mock_time.year = 1
    mock_time.day = 1
    return mock_time


def test_annual_average_temperature_recording(mock_weather_input: dict,
                                              mock_config: Config) -> None:
    """Tests that the annual average temperature is recorded correctly to the OutputManager when Weather is created."""
    with patch("RUFAS.weather.Weather._calculate_average_annual_temperature") as avg, \
            patch("RUFAS.output_manager.OutputManager.add_variable") as add:
        Weather(mock_weather_input, mock_config)
        avg.assert_called_once()
        add.assert_called_once()


@pytest.mark.parametrize("avg_daily_temperatures,expected", [
    ([12.3, 20.4, 15.6, 20.5, 17.8], 17.32),
    ([-4.55, -3.22, -1.05, -0.3, 1.44, 3.99, 8.6], 0.7014285714285712)
])
def test_calculate_average_annual_temperature(avg_daily_temperatures: list[float], expected: float) -> None:
    """Tests that the annual average air temperature is correctly calculated based on average daily temperatures."""
    actual = Weather._calculate_average_annual_temperature(avg_daily_temperatures)
    assert actual == expected


@pytest.mark.parametrize("day,year,calendar_year,expected", [
    (1, 1, 1999, CurrentDayConditions(incoming_light=1.0, min_air_temperature=1.1, mean_air_temperature=1.2,
                                      max_air_temperature=1.3, annual_mean_air_temperature=15.0, precipitation=1.4,
                                      irrigation=1.5, daylength=10.0)),
    (3, 1, 2010, CurrentDayConditions(incoming_light=3.0, min_air_temperature=3.1, mean_air_temperature=3.2,
                                      max_air_temperature=3.3, annual_mean_air_temperature=15.0, precipitation=3.4,
                                      irrigation=3.5, daylength=10.0))
])
def test_get_current_day_conditions(mock_weather: Weather, day: int, year: int, calendar_year: int,
                                    expected: CurrentDayConditions) -> None:
    """Tests that CurrentDayConditions instances are correctly created by Weather."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "day", day)
    setattr(mocked_time, "year", year)
    setattr(mocked_time, "calendar_year", calendar_year)
    with patch("RUFAS.util.Utility.day_to_month_conversion", new_callable=MagicMock, return_value=3) as day, \
            patch("RUFAS.current_day_conditions.CurrentDayConditions.determine_daylength", new_callable=MagicMock,
                  return_value=10.0) as daylength:
        actual = mock_weather.get_current_day_conditions(mocked_time)

        assert actual == expected
        assert day.call_count == 1
        daylength.assert_called_once_with(3)


@pytest.mark.parametrize("day,year,calendar_year,expected", [
    (4, 1, 2000, "Attempted to get weather conditions for day: 4, year: 1."),
    (2, 8, 1979, "Attempted to get weather conditions for day: 2, year: 8.")
])
def test_get_current_day_conditions_error(mock_weather: Weather, day: int, year: int, calendar_year: int,
                                          expected: CurrentDayConditions) -> None:
    """Tests that error is raised properly when weather does not have data for specified time."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "day", day)
    setattr(mocked_time, "year", year)
    setattr(mocked_time, "calendar_year", calendar_year)
    with patch("RUFAS.util.Utility.day_to_month_conversion", new_callable=MagicMock, return_value=3), \
            patch("RUFAS.current_day_conditions.CurrentDayConditions.determine_daylength", new_callable=MagicMock,
                  return_value=10.0), \
            pytest.raises(IndexError) as e:
        mock_weather.get_current_day_conditions(mocked_time)
    assert str(e.value) == expected


def test_record_weather(mock_weather: Weather, mock_current_day_conditions: CurrentDayConditions,
                        mock_time: Time) -> None:
    """Tests that weather conditions are correctly recorded to the OutputManager."""
    with patch("RUFAS.output_manager.OutputManager.add_variable") as add_var, \
            patch.object(mock_weather, "get_current_day_conditions", return_value=mock_current_day_conditions) \
            as mock_current_day_conditions:
        mock_weather.record_weather(mock_time)
        assert mock_current_day_conditions.call_count == 1
        assert add_var.call_count == 9
