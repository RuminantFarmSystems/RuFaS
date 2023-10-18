import pytest
from unittest.mock import patch, MagicMock

from RUFAS.config import Config
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


def test_annual_average_temperature_recording(mock_weather_input: dict,
                                              mock_config: Config) -> None:
    """Tests that the annual average temperature is recorded correctly to the OutputManager when Weather is created."""
    with patch("RUFAS.weather.Weather._calculate_average_annual_temperature") as avg, \
            patch("RUFAS.output_manager.OutputManager.add_variable") as add:
        Weather(mock_weather_input, mock_config)
        avg.assert_called_once()
        add.assert_called_once()


def test_record_weather(mock_weather_input: dict, mock_config: Config) -> None:
    """Tests that weather conditions are correctly recorded to the OutputManager."""
    weather = Weather(mock_weather_input, mock_config)
    with patch("RUFAS.output_manager.OutputManager.add_variable") as add_var:
        weather.record_weather(1, 1)
        assert add_var.call_count == 6


@pytest.mark.parametrize("avg_daily_temperatures,expected", [
    ([12.3, 20.4, 15.6, 20.5, 17.8], 17.32),
    ([-4.55, -3.22, -1.05, -0.3, 1.44, 3.99, 8.6], 0.7014285714285712)
])
def test_calculate_average_annual_temperature(avg_daily_temperatures: list[float], expected: float) -> None:
    """Tests that the annual average air temperature is correctly calculated based on average daily temperatures."""
    actual = Weather._calculate_average_annual_temperature(avg_daily_temperatures)
    assert actual == expected
