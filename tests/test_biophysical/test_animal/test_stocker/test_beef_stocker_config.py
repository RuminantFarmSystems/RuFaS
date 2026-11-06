"""Tests for stocker/backgrounding AnimalConfig parameters — Step 2.

Verifies that AnimalConfig holds the five new stocker ClassVars with
correct defaults, that _initialize_beef_stocker_config() reads them from
an input dict, and that stocker_diet_system validation rejects invalid
strings (including 'limit_feed') at config load time via ValueError.

Also verifies that BeefPostWeaningDestination.STOCKER is now accepted
(no longer raises NotImplementedError) now that the stocker module exists.
"""

from collections.abc import Generator
from typing import Any

import pytest

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import BeefPostWeaningDestination, StockerDietSystem

# ---------------------------------------------------------------------------
# Autouse fixture: restore stocker ClassVars after every test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_stocker_config_state() -> Generator[None, None, None]:
    """Save and restore AnimalConfig stocker ClassVars around each test.

    Yields
    ------
    None
        Yields control to the test body; restores state on teardown.
    """
    saved_entry_weight = AnimalConfig.stocker_entry_weight
    saved_exit_weight = AnimalConfig.stocker_exit_weight
    saved_max_days = AnimalConfig.stocker_max_days
    saved_target_adg = AnimalConfig.stocker_target_adg
    saved_diet_system = AnimalConfig.stocker_diet_system
    saved_post_weaning_dest = AnimalConfig.beef_post_weaning_destination
    yield
    AnimalConfig.stocker_entry_weight = saved_entry_weight
    AnimalConfig.stocker_exit_weight = saved_exit_weight
    AnimalConfig.stocker_max_days = saved_max_days
    AnimalConfig.stocker_target_adg = saved_target_adg
    AnimalConfig.stocker_diet_system = saved_diet_system
    AnimalConfig.beef_post_weaning_destination = saved_post_weaning_dest


# ---------------------------------------------------------------------------
# Default ClassVar values
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_entry_weight_default() -> None:
    """stocker_entry_weight default must equal STOCKER_MIN_ENTRY_WEIGHT_KG."""
    assert AnimalConfig.stocker_entry_weight == pytest.approx(AnimalModuleConstants.STOCKER_MIN_ENTRY_WEIGHT_KG)


@pytest.mark.unit
def test_stocker_exit_weight_default() -> None:
    """stocker_exit_weight default must equal STOCKER_TARGET_EXIT_WEIGHT_KG."""
    assert AnimalConfig.stocker_exit_weight == pytest.approx(AnimalModuleConstants.STOCKER_TARGET_EXIT_WEIGHT_KG)


@pytest.mark.unit
def test_stocker_max_days_default() -> None:
    """stocker_max_days default must equal STOCKER_MAX_DAYS."""
    assert AnimalConfig.stocker_max_days == AnimalModuleConstants.STOCKER_MAX_DAYS


@pytest.mark.unit
def test_stocker_target_adg_default() -> None:
    """stocker_target_adg default must equal STOCKER_TARGET_ADG_KG_D."""
    assert AnimalConfig.stocker_target_adg == pytest.approx(AnimalModuleConstants.STOCKER_TARGET_ADG_KG_D)


@pytest.mark.unit
def test_stocker_diet_system_default_is_pasture() -> None:
    """stocker_diet_system default must be StockerDietSystem.PASTURE."""
    assert AnimalConfig.stocker_diet_system is StockerDietSystem.PASTURE


# ---------------------------------------------------------------------------
# Type correctness of ClassVars
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_entry_weight_is_float() -> None:
    """stocker_entry_weight must be float."""
    assert isinstance(AnimalConfig.stocker_entry_weight, float)


@pytest.mark.unit
def test_stocker_exit_weight_is_float() -> None:
    """stocker_exit_weight must be float."""
    assert isinstance(AnimalConfig.stocker_exit_weight, float)


@pytest.mark.unit
def test_stocker_max_days_is_int() -> None:
    """stocker_max_days must be int."""
    assert isinstance(AnimalConfig.stocker_max_days, int)


@pytest.mark.unit
def test_stocker_target_adg_is_float() -> None:
    """stocker_target_adg must be float."""
    assert isinstance(AnimalConfig.stocker_target_adg, float)


@pytest.mark.unit
def test_stocker_diet_system_is_stocker_diet_system() -> None:
    """stocker_diet_system must be a StockerDietSystem instance."""
    assert isinstance(AnimalConfig.stocker_diet_system, StockerDietSystem)


# ---------------------------------------------------------------------------
# _initialize_beef_stocker_config: reads values from a config dict
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_initialize_stocker_reads_entry_weight() -> None:
    """_initialize_beef_stocker_config stores stocker_entry_weight from dict."""
    AnimalConfig._initialize_beef_stocker_config({"entry_weight": 200.0})
    assert AnimalConfig.stocker_entry_weight == pytest.approx(200.0)


@pytest.mark.unit
def test_initialize_stocker_reads_exit_weight() -> None:
    """_initialize_beef_stocker_config stores stocker_exit_weight from dict."""
    AnimalConfig._initialize_beef_stocker_config({"exit_weight": 380.0})
    assert AnimalConfig.stocker_exit_weight == pytest.approx(380.0)


@pytest.mark.unit
def test_initialize_stocker_reads_max_days() -> None:
    """_initialize_beef_stocker_config stores stocker_max_days from dict."""
    AnimalConfig._initialize_beef_stocker_config({"max_days": 180})
    assert AnimalConfig.stocker_max_days == 180


@pytest.mark.unit
def test_initialize_stocker_reads_target_adg() -> None:
    """_initialize_beef_stocker_config stores stocker_target_adg from dict."""
    AnimalConfig._initialize_beef_stocker_config({"target_adg": 0.90})
    assert AnimalConfig.stocker_target_adg == pytest.approx(0.90)


@pytest.mark.unit
def test_initialize_stocker_reads_diet_system_pasture() -> None:
    """_initialize_beef_stocker_config stores StockerDietSystem.PASTURE from 'pasture' string."""
    AnimalConfig._initialize_beef_stocker_config({"stocker_diet_system": "pasture"})
    assert AnimalConfig.stocker_diet_system is StockerDietSystem.PASTURE


@pytest.mark.unit
def test_initialize_stocker_reads_diet_system_drylot_forage() -> None:
    """_initialize_beef_stocker_config stores DRYLOT_FORAGE from 'drylot_forage' string."""
    AnimalConfig._initialize_beef_stocker_config({"stocker_diet_system": "drylot_forage"})
    assert AnimalConfig.stocker_diet_system is StockerDietSystem.DRYLOT_FORAGE


@pytest.mark.unit
def test_initialize_stocker_missing_section_uses_defaults() -> None:
    """Empty stocker config dict must leave all ClassVars at their defaults."""
    AnimalConfig._initialize_beef_stocker_config({})
    assert AnimalConfig.stocker_entry_weight == pytest.approx(AnimalModuleConstants.STOCKER_MIN_ENTRY_WEIGHT_KG)
    assert AnimalConfig.stocker_exit_weight == pytest.approx(AnimalModuleConstants.STOCKER_TARGET_EXIT_WEIGHT_KG)
    assert AnimalConfig.stocker_max_days == AnimalModuleConstants.STOCKER_MAX_DAYS
    assert AnimalConfig.stocker_target_adg == pytest.approx(AnimalModuleConstants.STOCKER_TARGET_ADG_KG_D)
    assert AnimalConfig.stocker_diet_system is StockerDietSystem.PASTURE


# ---------------------------------------------------------------------------
# stocker_diet_system validation — ValueError on invalid strings
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_initialize_stocker_limit_feed_is_accepted() -> None:
    """'limit_feed' is now a supported stocker_diet_system."""
    AnimalConfig._initialize_beef_stocker_config({"stocker_diet_system": "limit_feed"})
    assert AnimalConfig.stocker_diet_system is StockerDietSystem.LIMIT_FEED


@pytest.mark.unit
def test_initialize_stocker_unknown_diet_raises_value_error() -> None:
    """Any unrecognised stocker_diet_system string must raise ValueError."""
    with pytest.raises(ValueError, match="stocker_diet_system"):
        AnimalConfig._initialize_beef_stocker_config({"stocker_diet_system": "grass_only"})


@pytest.mark.unit
@pytest.mark.parametrize("valid_str", ["pasture", "drylot_forage"])
def test_initialize_stocker_valid_diet_systems_accepted(valid_str: str) -> None:
    """'pasture' and 'drylot_forage' must be accepted without raising."""
    AnimalConfig._initialize_beef_stocker_config({"stocker_diet_system": valid_str})
    assert AnimalConfig.stocker_diet_system.value == valid_str


# ---------------------------------------------------------------------------
# BeefPostWeaningDestination.STOCKER — no longer raises NotImplementedError
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_post_weaning_destination_accepted() -> None:
    """BeefPostWeaningDestination.STOCKER must now be accepted without NotImplementedError.

    The native stocker module (Segment 3) is now implemented; the placeholder
    guard in _parse_beef_enum_fields must be removed.
    """
    AnimalConfig._parse_beef_enum_fields({"post_weaning_destination": BeefPostWeaningDestination.STOCKER.value})
    assert AnimalConfig.beef_post_weaning_destination is BeefPostWeaningDestination.STOCKER


@pytest.mark.unit
def test_stocker_post_weaning_destination_does_not_raise_not_implemented() -> None:
    """Calling _parse_beef_enum_fields with 'stocker' must NOT raise NotImplementedError."""
    try:
        AnimalConfig._parse_beef_enum_fields({"post_weaning_destination": BeefPostWeaningDestination.STOCKER.value})
    except NotImplementedError:
        pytest.fail("NotImplementedError raised for STOCKER — guard must have been removed in Step 2")


def _make_stocker_config(**kwargs: Any) -> dict[str, Any]:
    """Build a minimal stocker config dict with the given overrides."""
    base: dict[str, Any] = {
        "entry_weight": AnimalModuleConstants.STOCKER_MIN_ENTRY_WEIGHT_KG,
        "exit_weight": AnimalModuleConstants.STOCKER_TARGET_EXIT_WEIGHT_KG,
        "max_days": AnimalModuleConstants.STOCKER_MAX_DAYS,
        "target_adg": AnimalModuleConstants.STOCKER_TARGET_ADG_KG_D,
    }
    base.update(kwargs)
    return base
