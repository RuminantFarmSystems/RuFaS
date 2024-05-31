from datetime import date
import pytest
from pytest_mock.plugin import MockerFixture
from unittest.mock import MagicMock, patch
from typing import Callable

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.time import Time
from RUFAS.weather import Weather
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility

om = OutputManager()


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
def mock_time() -> Time:
    """Fixture for Time object."""
    mock_time = MagicMock(auto_spec=Time)
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
    mock_weather._Weather__radiation = [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
    mock_weather._Weather__min_daily_temperature = [[1.1, 2.1, 3.1], [1.1, 2.1, 3.1], [1.1, 2.1, 3.1]]
    mock_weather._Weather__mean_daily_temperature = [[1.2, 2.2, 3.2], [1.2, 2.2, 3.2], [1.2, 2.2, 3.2]]
    mock_weather._Weather__max_daily_temperature = [[1.3, 2.3, 3.3], [1.3, 2.3, 3.3], [1.3, 2.3, 3.3]]
    mock_weather._Weather__precipitation = [[1.4, 2.4, 3.4], [1.4, 2.4, 3.4], [1.4, 2.4, 3.4]]
    mock_weather._Weather__irrigation = [[1.5, 2.5, 3.5], [1.5, 2.5, 3.5], [1.5, 2.5, 3.5]]
    mock_weather._Weather__mean_annual_temperature = 15.0
    mock_weather._Weather__latitude = 43.0723

    return mock_weather


@pytest.fixture
def weather_original_method_states(mock_weather: Weather) -> dict[str, Callable]:
    """Fixture to store unmocked methods of Weather."""
    return {
        "_calculate_average_annual_temperature": mock_weather._calculate_average_annual_temperature,
        "get_current_day_conditions": mock_weather.get_current_day_conditions,
        "_get_latitude": mock_weather._get_latitude(),
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


def test_weather_init(mock_weather_input: dict, mock_time: Time) -> None:
    """Tests that subroutines are called appropriately when Weather instance in initialized."""
    with (
        patch("RUFAS.weather.Weather._calculate_average_annual_temperature") as avg,
        patch("RUFAS.output_manager.OutputManager.add_variable") as add,
        patch("RUFAS.weather.Weather._get_latitude") as latitude,
    ):
        Weather(mock_weather_input, mock_time)
        avg.assert_called_once()
        add.assert_called_once()
        latitude.assert_called_once()


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
    "day,year,calendar_year,expected",
    [
        (
            1,
            1,
            1999,
            CurrentDayConditions(
                incoming_light=1.0,
                min_air_temperature=1.1,
                mean_air_temperature=1.2,
                max_air_temperature=1.3,
                annual_mean_air_temperature=15.0,
                precipitation=1.4,
                irrigation=1.5,
                daylength=10.0,
            ),
        ),
        (
            3,
            1,
            2010,
            CurrentDayConditions(
                incoming_light=3.0,
                min_air_temperature=3.1,
                mean_air_temperature=3.2,
                max_air_temperature=3.3,
                annual_mean_air_temperature=15.0,
                precipitation=3.4,
                irrigation=3.5,
                daylength=10.0,
            ),
        ),
    ],
)
def test_get_current_day_conditions(
    mocker: MockerFixture,
    mock_weather: Weather,
    day: int,
    year: int,
    calendar_year: int,
    expected: CurrentDayConditions,
) -> None:
    """Tests that CurrentDayConditions instances are correctly created by Weather."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "day", day)
    setattr(mocked_time, "year", year)
    setattr(mocked_time, "calendar_year", calendar_year)
    daylength = mocker.patch("RUFAS.current_day_conditions.CurrentDayConditions.determine_daylength", return_value=10.0)

    actual = mock_weather.get_current_day_conditions(mocked_time)

    assert actual == expected
    daylength.assert_called_once_with(day, 43.0723, calendar_year)


@pytest.mark.parametrize(
    "day,year,calendar_year,expected",
    [
        (4, 1, 2000, "Attempted to get weather conditions for day: 4, year: 1."),
        (2, 8, 1979, "Attempted to get weather conditions for day: 2, year: 8."),
    ],
)
def test_get_current_day_conditions_error(
    mocker: MockerFixture,
    mock_weather: Weather,
    day: int,
    year: int,
    calendar_year: int,
    expected: CurrentDayConditions,
) -> None:
    """Tests that error is raised properly when weather does not have data for specified time."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "day", day)
    setattr(mocked_time, "year", year)
    setattr(mocked_time, "calendar_year", calendar_year)
    mocker.patch("RUFAS.current_day_conditions.CurrentDayConditions.determine_daylength", return_value=10.0)

    with pytest.raises(IndexError) as e:
        mock_weather.get_current_day_conditions(mocked_time)

    assert str(e.value) == expected


@pytest.mark.parametrize(
    "start,end,expected",
    [
        (
            -1,
            1,
            [
                CurrentDayConditions(
                    incoming_light=1.0,
                    min_air_temperature=1.1,
                    mean_air_temperature=1.2,
                    max_air_temperature=1.3,
                    precipitation=1.4,
                    irrigation=1.5,
                    annual_mean_air_temperature=15.0,
                    daylength=15.6,
                ),
                CurrentDayConditions(
                    incoming_light=2.0,
                    min_air_temperature=2.1,
                    mean_air_temperature=2.2,
                    max_air_temperature=2.3,
                    precipitation=2.4,
                    irrigation=2.5,
                    annual_mean_air_temperature=15.0,
                    daylength=15.6,
                ),
                CurrentDayConditions(
                    incoming_light=3.0,
                    min_air_temperature=3.1,
                    mean_air_temperature=3.2,
                    max_air_temperature=3.3,
                    precipitation=3.4,
                    irrigation=3.5,
                    annual_mean_air_temperature=15.0,
                    daylength=15.6,
                ),
            ],
        )
    ],
)
def test_get_conditions_series(
    mock_weather: Weather,
    mock_time: Time,
    mocker: MockerFixture,
    start: int,
    end: int,
    expected: list[CurrentDayConditions],
) -> None:
    """Tests that series of CurrentDayConditions are created correctly."""
    setattr(mock_time, "year", 2)
    setattr(mock_time, "day", 2)
    setattr(mock_time, "simulation_day", 5)
    setattr(mock_time, "end_year_int", 2024)
    date_conversion = mocker.patch.object(Utility, "convert_ordinal_date_to_month_date", return_value=date(2023, 1, 2))
    time_series_gen = mocker.patch.object(Utility, "generate_time_series", wraps=Utility.generate_time_series)
    daylength = mocker.patch.object(CurrentDayConditions, "determine_daylength", return_value=15.6)

    actual = mock_weather.get_conditions_series(mock_time, start, end)

    assert actual == expected
    date_conversion.call_count == len(expected)
    time_series_gen.assert_called_once()
    assert daylength.call_count == len(expected)


def test_record_weather(
    mock_weather: Weather,
    mock_current_day_conditions: CurrentDayConditions,
    mock_time: Time,
) -> None:
    """Tests that weather conditions are correctly recorded to the OutputManager."""
    with (
        patch("RUFAS.output_manager.OutputManager.add_variable") as add_var,
        patch.object(
            mock_weather,
            "get_current_day_conditions",
            return_value=mock_current_day_conditions,
        ) as mock_current_day_conditions,
    ):
        mock_weather.record_weather(mock_time)
        assert mock_current_day_conditions.call_count == 1
        assert add_var.call_count == 9


@pytest.mark.parametrize(
    "field_keys,field_data,expected_latitude",
    [(["field_1", "field_2"], 34.1, 34.1), ([], None, 43.0723)],
)
def test_get_latitude(
    field_keys: list[str],
    field_data: float,
    expected_latitude: float,
    mock_weather: Weather,
) -> None:
    """Test that Weather correctly gets a latitude from Input Manager or uses the default."""
    with (
        patch(
            "RUFAS.input_manager.InputManager.get_data_keys_by_properties",
            return_value=field_keys,
        ) as keys,
        patch("RUFAS.input_manager.InputManager.get_data", return_value=field_data) as data,
        patch.object(om, "add_warning") as warning,
    ):
        actual = mock_weather._get_latitude()

        keys.assert_called_once_with("field_properties")
        if field_data:
            expected_data_address = f"{field_keys[0]}.absolute_latitude"
            data.assert_called_once_with(expected_data_address)
            warning.assert_not_called()
        else:
            data.assert_not_called()
            warning.assert_called_once()
        assert actual == expected_latitude
