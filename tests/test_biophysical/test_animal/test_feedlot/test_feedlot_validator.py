"""Tests for feedlot configuration validation rules in DataValidator."""

import pytest
from RUFAS.data_validator import DataValidator


def _valid_config() -> dict[str, object]:
    """Return a fully valid feedlot config for use as a base in parametrized tests."""
    return {
        "entry_weight": 320.0,
        "slaughter_weight": 580.0,
        "max_days_on_feed": 220,
        "mud_condition": "none",
    }


@pytest.mark.unit
def test_validate_feedlot_config_valid_passes() -> None:
    """validate_feedlot_config must not raise for a fully valid config."""
    DataValidator.validate_feedlot_config(_valid_config())


@pytest.mark.unit
def test_validate_feedlot_config_entry_weight_zero_raises() -> None:
    """validate_feedlot_config must raise ValueError when entry_weight <= 0."""
    cfg = _valid_config()
    cfg["entry_weight"] = 0.0
    with pytest.raises(ValueError, match="entry_weight"):
        DataValidator.validate_feedlot_config(cfg)


@pytest.mark.unit
def test_validate_feedlot_config_entry_weight_negative_raises() -> None:
    """validate_feedlot_config must raise ValueError when entry_weight is negative."""
    cfg = _valid_config()
    cfg["entry_weight"] = -10.0
    with pytest.raises(ValueError, match="entry_weight"):
        DataValidator.validate_feedlot_config(cfg)


@pytest.mark.unit
def test_validate_feedlot_config_slaughter_weight_le_entry_raises() -> None:
    """validate_feedlot_config must raise ValueError when slaughter_weight <= entry_weight."""
    cfg = _valid_config()
    cfg["slaughter_weight"] = 320.0  # equal to entry_weight
    with pytest.raises(ValueError, match="slaughter_weight"):
        DataValidator.validate_feedlot_config(cfg)


@pytest.mark.unit
def test_validate_feedlot_config_slaughter_weight_less_than_entry_raises() -> None:
    """validate_feedlot_config must raise ValueError when slaughter_weight < entry_weight."""
    cfg = _valid_config()
    cfg["slaughter_weight"] = 300.0
    with pytest.raises(ValueError, match="slaughter_weight"):
        DataValidator.validate_feedlot_config(cfg)


@pytest.mark.unit
def test_validate_feedlot_config_max_days_zero_raises() -> None:
    """validate_feedlot_config must raise ValueError when max_days_on_feed <= 0."""
    cfg = _valid_config()
    cfg["max_days_on_feed"] = 0
    with pytest.raises(ValueError, match="max_days_on_feed"):
        DataValidator.validate_feedlot_config(cfg)


@pytest.mark.unit
def test_validate_feedlot_config_max_days_negative_raises() -> None:
    """validate_feedlot_config must raise ValueError when max_days_on_feed is negative."""
    cfg = _valid_config()
    cfg["max_days_on_feed"] = -1
    with pytest.raises(ValueError, match="max_days_on_feed"):
        DataValidator.validate_feedlot_config(cfg)


@pytest.mark.unit
@pytest.mark.parametrize("mud", ["none", "mild", "severe"])
def test_validate_feedlot_config_valid_mud_conditions(mud: str) -> None:
    """validate_feedlot_config must accept 'none', 'mild', and 'severe' mud conditions."""
    cfg = _valid_config()
    cfg["mud_condition"] = mud
    DataValidator.validate_feedlot_config(cfg)


@pytest.mark.unit
@pytest.mark.parametrize("bad_mud", ["heavy", "deep", "None", "NONE", ""])
def test_validate_feedlot_config_invalid_mud_raises(bad_mud: str) -> None:
    """validate_feedlot_config must raise ValueError for unrecognised mud_condition strings."""
    cfg = _valid_config()
    cfg["mud_condition"] = bad_mud
    with pytest.raises(ValueError, match="mud_condition"):
        DataValidator.validate_feedlot_config(cfg)


@pytest.mark.unit
@pytest.mark.parametrize("bad_weight", [float("nan"), float("inf"), float("-inf")])
def test_validate_feedlot_config_non_finite_entry_weight_raises(bad_weight: float) -> None:
    """validate_feedlot_config must raise ValueError when entry_weight is non-finite."""
    cfg = _valid_config()
    cfg["entry_weight"] = bad_weight
    with pytest.raises(ValueError, match="entry_weight"):
        DataValidator.validate_feedlot_config(cfg)


@pytest.mark.unit
@pytest.mark.parametrize("bad_weight", [float("nan"), float("inf"), float("-inf")])
def test_validate_feedlot_config_non_finite_slaughter_weight_raises(bad_weight: float) -> None:
    """validate_feedlot_config must raise ValueError when slaughter_weight is non-finite."""
    cfg = _valid_config()
    cfg["slaughter_weight"] = bad_weight
    with pytest.raises(ValueError, match="slaughter_weight"):
        DataValidator.validate_feedlot_config(cfg)
