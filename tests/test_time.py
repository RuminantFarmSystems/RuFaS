import pytest
from unittest.mock import patch, MagicMock

from RUFAS.config import Config
from RUFAS.time import Time


@pytest.fixture
def mock_config() -> Config:
    config = MagicMock(Config)
    setattr(config, "start_year", 1999)
    setattr(config, "years", [[1]])
    setattr(config, "leap_year_length", 366)
    setattr(config, "year_length", 365)
    return config


def test_record_time(mock_config: Config) -> None:
    time = Time(mock_config)
    with patch("RUFAS.output_manager.OutputManager.add_variable") as add_var:
        time.record_time()
        assert add_var.call_count == 3
