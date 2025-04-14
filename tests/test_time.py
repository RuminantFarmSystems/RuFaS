from datetime import date, datetime, timedelta
from typing import Any, Dict
from unittest.mock import patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.rufas_time import RufasTime


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    config = {
        "start_date": "1999:2",
        "end_date": "2000:1",
    }
    return config


def test_time_initialization() -> None:
    """Tests that RufasTime instances are created correctly."""

    time = RufasTime(datetime(year=1999, month=1, day=2), datetime(year=2000, month=1, day=1))

    assert time.start_date == datetime(year=1999, month=1, day=2)
    assert time.end_date == datetime(year=2000, month=1, day=1)

    assert time.current_date == time.start_date
    assert time.simulation_length_days == (time.end_date - time.start_date).days
    assert time.simulation_day == 0


def test_advance(mock_config: Dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that RufasTime instances are advanced correctly."""
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=mock_config)
    time = RufasTime()
    for n in range(365):
        time.advance()
        assert time.simulation_day == n + 1
        assert time.current_date == time.start_date + timedelta(days=n + 1)


def test_current_julian_day(mock_config: Dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that RufasTime instances correctly determine the julian day of the current date."""
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=mock_config)
    time = RufasTime()

    for n in range(364):
        assert time.current_julian_day == 2 + n
        time.advance()

    assert time.current_julian_day == 1


def test_current_month(mock_config: Dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that RufasTime instances correctly determine the month of the current date."""
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=mock_config)
    time = RufasTime()

    months = (
        [1] * 30
        + [2] * 28
        + [3] * 31
        + [4] * 30
        + [5] * 31
        + [6] * 30
        + [7] * 31
        + [8] * 31
        + [9] * 30
        + [10] * 31
        + [11] * 30
        + [12] * 31
        + [1]
    )

    for n in range(365):
        assert time.current_month == months[n]
        time.advance()


def test_current_simulation_year(mock_config: Dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that RufasTime instances correctly determine the simulation year of the current date."""
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=mock_config)
    time = RufasTime()

    for n in range(364):
        assert time.current_simulation_year == 1
        time.advance()

    assert time.current_simulation_year == 2


def test_current_calendar_year(mock_config: Dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that RufasTime instances correctly determine the calendar year of the current date."""
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=mock_config)
    time = RufasTime()

    for n in range(364):
        assert time.current_calendar_year == 1999
        time.advance()

    assert time.current_calendar_year == 2000


def test_year_start_day(mock_config: Dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that RufasTime instances correctly determine the first julian day of the current year."""
    mocker.patch(
        "RUFAS.input_manager.InputManager.get_data",
        return_value={
            "start_date": "1999:100",
            "end_date": "2004:10",
        },
    )
    time = RufasTime()

    year_start_days = [100] * 266 + [1] * 1471
    for start_day in year_start_days:
        assert time.year_start_day == start_day
        time.advance()


def test_year_end_day(mock_config: Dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that RufasTime instances correctly determine the last julian day of the current year."""
    mocker.patch(
        "RUFAS.input_manager.InputManager.get_data",
        return_value={
            "start_date": "1999:100",
            "end_date": "2004:10",
        },
    )
    time = RufasTime()

    year_end_days = [365] * 266 + [366] * 366 + [365] * 1095 + [10] * 10
    for end_day in year_end_days:
        assert time.year_end_day == end_day
        time.advance()


def test_record_time(mock_config: Dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that RufasTime instances correctly add current time information to the OutputManager."""
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=mock_config)
    time = RufasTime()
    with patch("RUFAS.output_manager.OutputManager.add_variable") as add_var:
        time.record_time()
        assert add_var.call_count == 4


@pytest.mark.parametrize(
    "start_date_str, simulation_day, expected_date",
    [
        # Year 2023
        ("2023:1", 1, datetime(2023, 1, 1)),
        ("2023:1", 365, datetime(2023, 12, 31)),
        # Year 2024 (Leap Year)
        ("2024:1", 1, datetime(2024, 1, 1)),
        ("2024:1", 366, datetime(2024, 12, 31)),
        ("2024:15", 17, datetime(2024, 1, 31)),
    ],
)
def test_convert_simulation_day_to_date(
    mocker: MockerFixture, start_date_str: str, simulation_day: int, expected_date: date
) -> None:
    """
    Unit test for the convert_simulation_day_to_date method of the RufasTime class.
    """

    # Arrange
    mocker.patch("RUFAS.rufas_time.RufasTime.__init__", return_value=None)
    time = RufasTime()
    time.start_date = datetime.strptime(start_date_str, "%Y:%j")

    # Act
    actual_date = time.convert_simulation_day_to_date(simulation_day)

    # Assert
    assert actual_date == expected_date


def test_str(mock_config: Dict[str, Any], mocker: MockerFixture) -> None:
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=mock_config)
    time = RufasTime()

    for n in range(364):
        assert time.__str__() == f"Year: {1}, Day: {2 + n}. Simulation Day: {n}"
        time.advance()

    assert str(time) == f"Year: {2}, Day: {1}. Simulation Day: {364}"


@pytest.mark.parametrize(
    "year,jday,expected",
    [
        (2001, 3, datetime(2001, 1, 3)),
        (2005, 350, datetime(2005, 12, 16)),
        (2020, 60, datetime(2020, 2, 29)),
    ],
)
def test_convert_year_jday_to_date(
    year: int, jday: int, expected: datetime, mocker: MockerFixture, mock_config: Dict[str, Any]
) -> None:
    """Unit test for convert_year_jday_to_date"""
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=mock_config)
    time = RufasTime()

    actual = time.convert_year_jday_to_date(year, jday)
    assert expected == actual


@pytest.mark.parametrize(
    "slice_day, simulation_length_days, expected_sim_day",
    [
        (0, 100, 1),
        (5, 100, 5),
        (-1, 100, 100),
        (-100, 100, 1),
        (100, 100, 100),
        (150, 100, 150),
    ],
)
def test_convert_slice_to_simulation_day(
    slice_day: int, simulation_length_days: int, expected_sim_day: int, mocker: MockerFixture
) -> None:
    """Test convert_slice_to_simulation_day for various slice_day inputs."""
    mocker.patch(
        "RUFAS.input_manager.InputManager.get_data", return_value={"start_date": "2023:1", "end_date": "2023:100"}
    )
    mock_time = RufasTime()

    mock_time.simulation_length_days = simulation_length_days

    result = mock_time.convert_slice_to_simulation_day(slice_day)
    assert result == expected_sim_day, f"Expected {expected_sim_day} but got {result} for slice_day={slice_day}"
