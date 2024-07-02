from datetime import datetime
import pytest
from pytest_mock.plugin import MockerFixture
from unittest.mock import MagicMock, patch
from typing import Callable

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.time import Time
from RUFAS.weather import Weather
from RUFAS.output_manager import OutputManager

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
    weather_data = {datetime(2023, 9, 24): CurrentDayConditions(
        incoming_light=1, min_air_temperature=1,
        mean_air_temperature=1, max_air_temperature=1,
        precipitation=1, irrigation=1
    ), datetime(2023, 9, 25): CurrentDayConditions(
        incoming_light=2, min_air_temperature=2,
        mean_air_temperature=2, max_air_temperature=2,
        precipitation=2, irrigation=2
    ), datetime(2023, 9, 26): CurrentDayConditions(
        incoming_light=3, min_air_temperature=3,
        mean_air_temperature=3, max_air_temperature=3,
        precipitation=3, irrigation=3
    )}
    mock_weather.weather_data = weather_data

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


def test_weather_init(mock_weather_input: dict, mock_time: Time, mocker: MockerFixture) -> None:
    """Tests that subroutines are called appropriately when Weather instance in initialized."""
    with (
        patch("RUFAS.weather.Weather.check_adequate_weather_data") as check,
        patch("RUFAS.output_manager.OutputManager.add_variable") as add,
        patch("RUFAS.weather.Weather._calculate_average_annual_temperature") as avg,
    ):
        mock_time.start_date = datetime(2023, 11, 1)
        mock_time.end_date = datetime(2023, 11, 5)
        convert = mocker.patch.object(mock_time, "convert_simulation_day_to_date",
                                      return_value=datetime(2023, 11, 3))
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
    "day,calendar_year,expected,time",
    [
        (
            1,
            1,
            CurrentDayConditions(
                incoming_light=1, min_air_temperature=1,
                mean_air_temperature=1, max_air_temperature=1,
                precipitation=1, irrigation=1, daylength=10.0
            ),
            datetime(2023, 9, 24)
        ),
        (
            3,
            1,
            CurrentDayConditions(
                incoming_light=2,
                min_air_temperature=2,
                mean_air_temperature=2,
                max_air_temperature=2,
                precipitation=2,
                irrigation=2,
                daylength=10.0,
            ),
            datetime(2023, 9, 25)
        ),
    ],
)
def test_get_current_day_conditions(
        mocker: MockerFixture,
        mock_weather: Weather,
        day: int,
        calendar_year: int,
        expected: CurrentDayConditions,
        time: datetime
) -> None:
    """Tests that CurrentDayConditions instances are correctly created by Weather."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "current_date", time)
    setattr(mocked_time, "current_calendar_year", calendar_year)
    setattr(mocked_time, "current_julian_day", day)
    daylength = mocker.patch("RUFAS.current_day_conditions.CurrentDayConditions.determine_daylength", return_value=10.0)
    latitude = mocker.patch("RUFAS.weather.Weather._get_latitude", return_value=20)

    actual = mock_weather.get_current_day_conditions(mocked_time)
    print(actual)

    assert actual == expected
    latitude.assert_called_once()
    daylength.assert_called_once_with(day, 20, calendar_year)


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
        time: datetime
) -> None:
    """Tests that error is raised properly when weather does not have data for specified time."""
    mocked_time = MagicMock(Time)
    setattr(mocked_time, "current_date", time)
    setattr(mocked_time, "current_julian_day", day)
    setattr(mocked_time, "current_calendar_year", calendar_year)
    mocker.patch("RUFAS.current_day_conditions.CurrentDayConditions.determine_daylength", return_value=10.0)

    with pytest.raises(KeyError) as e:
        mock_weather.get_current_day_conditions(mocked_time)

    assert str(e.value.args[0]) == expected


@pytest.mark.parametrize(
    "start,end,expected",
    [
        (
            -1,
            1,
            [
                CurrentDayConditions(
                    incoming_light=1,
                    min_air_temperature=1,
                    mean_air_temperature=1,
                    max_air_temperature=1,
                    precipitation=1,
                    irrigation=1,
                    daylength=15.6,
                ),
                CurrentDayConditions(
                    incoming_light=2,
                    min_air_temperature=2,
                    mean_air_temperature=2,
                    max_air_temperature=2,
                    precipitation=2,
                    irrigation=2,
                    daylength=15.6,
                ),
                CurrentDayConditions(
                    incoming_light=3,
                    min_air_temperature=3,
                    mean_air_temperature=3,
                    max_air_temperature=3,
                    precipitation=3,
                    irrigation=3,
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
    setattr(mock_time, "current_date", datetime(2023, 9, 25))
    daylength = mocker.patch.object(CurrentDayConditions, "determine_daylength", return_value=15.6)

    actual = mock_weather.get_conditions_series(mock_time, start, end)

    assert actual == expected
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
