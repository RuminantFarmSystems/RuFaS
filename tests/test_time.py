import pytest
from unittest.mock import patch, MagicMock

from RUFAS.config import Config
from RUFAS.time import Time


@pytest.fixture
def mock_config() -> Config:
    config = MagicMock(Config)
    setattr(config, "start_year", 1999)
    setattr(config, "years", [[None, 1]])
    setattr(config, "leap_year_length", 366)
    setattr(config, "year_length", 365)
    return config


def test_time_initialization(mock_config: Config) -> None:
    """Tests that Time instances are created correctly."""
    time = Time(mock_config)
    assert time.start_year == 1999 and time.calendar_year == 1999
    assert time.leap_year_length == 366
    assert time.year_length == 365
    assert time.day == 1
    assert time.index == 0
    assert time.year == 1
    assert time.years == [[None, 1]]


def test_to_str() -> None:
    """Tests that string representations are correctly created for Time instances."""
    pass


def test_advance() -> None:
    """Tests that Time instances are advanced correctly."""
    pass


def test_end_year() -> None:
    """Tests that Time instances correctly determine if it is the end of a year."""
    pass


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
