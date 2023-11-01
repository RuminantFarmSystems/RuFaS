import pytest
from pytest_mock.plugin import MockerFixture
from unittest.mock import MagicMock, patch
from typing import Callable

from RUFAS.config import Config
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.time import Time
from RUFAS.weather import Weather


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


@pytest.mark.parametrize("avg_daily_temperatures,expected", [
    ([12.3, 20.4, 15.6, 20.5, 17.8], 17.32),
    ([-4.55, -3.22, -1.05, -0.3, 1.44, 3.99, 8.6], 0.7014285714285712)
])
def test_calculate_average_annual_temperature(avg_daily_temperatures: list[float], expected: float) -> None:
    """Tests that the annual average air temperature is correctly calculated based on average daily temperatures."""
    actual = Weather._calculate_average_annual_temperature(avg_daily_temperatures)
    assert actual == expected


@pytest.mark.parametrize("day,year,expected", [
    (1, 1, CurrentDayConditions(incoming_light=1.0, min_air_temperature=1.1, mean_air_temperature=1.2,
                                max_air_temperature=1.3, annual_mean_air_temperature=15.0, precipitation=1.4,
                                irrigation=1.5,
                                daylength=10.0)),
    (3, 1, CurrentDayConditions(incoming_light=3.0, min_air_temperature=3.1, mean_air_temperature=3.2,
                                max_air_temperature=3.3, annual_mean_air_temperature=15.0, precipitation=3.4,
                                irrigation=3.5,
                                daylength=10.0))
])
def test_get_current_day_conditions(mock_weather: Weather, day: int, year: int, expected: CurrentDayConditions) -> None:
    """Tests that CurrentDayConditions instances are correctly created by Weather."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "day", day)
    setattr(mocked_time, "year", year)
    with patch("RUFAS.util.Utility.day_to_month_conversion", new_callable=MagicMock,
               return_value=3) as day, \
            patch("RUFAS.current_day_conditions.CurrentDayConditions.determine_daylength", new_callable=MagicMock,
                  return_value=10.0) as daylength:
        actual = mock_weather.get_current_day_conditions(mocked_time)

        assert actual == expected
        assert day.call_count == 1
        daylength.assert_called_once_with(3)


@pytest.mark.parametrize("day,year,expected", [
    (4, 1, "Attempted to get weather conditions for day: 4, year: 1."),
    (2, 8, "Attempted to get weather conditions for day: 2, year: 8.")
])
def test_get_current_day_conditions_error(mock_weather: Weather, day: int, year: int,
                                          expected: CurrentDayConditions) -> None:
    """Tests that error is raised properly when weather does not have data for specified time."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "day", day)
    setattr(mocked_time, "year", year)
    with patch("RUFAS.util.Utility.day_to_month_conversion", new_callable=MagicMock,
               return_value=3), \
            patch("RUFAS.current_day_conditions.CurrentDayConditions.determine_daylength", new_callable=MagicMock,
                  return_value=10.0), \
            pytest.raises(IndexError) as e:
        mock_weather.get_current_day_conditions(mocked_time)
    assert str(e.value) == expected
