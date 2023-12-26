import pytest
from unittest.mock import patch, MagicMock

from RUFAS.config import Config
from RUFAS.time import Time


@pytest.fixture
def mock_config() -> Config:
    config = MagicMock(Config)
    setattr(config, "start_year", 1999)
    setattr(config, "years", [[None, 2]])
    setattr(config, "leap_year_length", 366)
    setattr(config, "year_length", 365)
    return config


def test_time_initialization(mock_config: Config) -> None:
    """Tests that Time instances are created correctly."""
    time = Time(mock_config)
    assert time.start_year == 1999 and time.calendar_year == 1999
    assert time.leap_year_length == 366
    assert time.year_length == 365
    assert time.day == 2
    assert time.index == 0
    assert time.year == 1
    assert time.years == [[None, 2]]


def test_to_str(mock_config: Config) -> None:
    """Tests that string representations are correctly created for Time instances."""
    time = Time(mock_config)
    assert time.to_str() == "Year: 1 Day: 2"


def test_advance(mock_config: Config) -> None:
    """Tests that Time instances are advanced correctly."""
    time = Time(mock_config)
    time.advance()
    assert time.index == 1
    assert time.day == 3

    # second round of advance, move to a new year
    time.advance()
    assert time.day == 1
    assert time.year == 2
    assert time.calendar_year == 2000


def test_end_year(mock_config: Config) -> None:
    """Tests that Time instances correctly determine if it is the end of a year."""
    time = Time(mock_config)
    assert not time.end_year()
    time.advance()
    assert time.end_year()


def test_end_simulation() -> None:
    """Tests that Time instances correctly determine if the simulation has ended."""
    pass


def test_record_time(mock_config: Config) -> None:
    """Tests that Time instances correctly add current time information to the OutputManager."""
    time = Time(mock_config)
    with patch("RUFAS.output_manager.OutputManager.add_variable") as add_var:
        time.record_time()
        assert add_var.call_count == 3


def test_is_last_day_of_simulation() -> None:
    """Tests that Time instances correctly determine if current day is last day of a simulation."""
    pass
