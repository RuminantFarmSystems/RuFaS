"""Tests for stocker/backgrounding constants in AnimalModuleConstants.

Step 2 of the stocker module. Every constant is pinned to its NRC 2016
source value so equation-coefficient regressions surface immediately.
"""

import pytest

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants

# ---------------------------------------------------------------------------
# Exact values — pinned to NRC 2016 Ch.10-12 source
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    ("attr", "expected"),
    [
        ("STOCKER_MIN_ENTRY_WEIGHT_KG", 180.0),  # NRC 2016 minimum weaning weight for stocker placement
        ("STOCKER_TARGET_EXIT_WEIGHT_KG", 350.0),  # NRC 2016 feedlot entry 300-400 kg; 350 kg midpoint
        ("STOCKER_TARGET_ADG_KG_D", 0.80),  # NRC 2016 Ch.10 mid-range of 0.35-1.15 kg/d on forage
    ],
)
def test_stocker_float_constants(attr: str, expected: float) -> None:
    """Float stocker constants must exist with exact NRC 2016 source values."""
    assert hasattr(AnimalModuleConstants, attr), f"Missing constant: {attr}"
    assert getattr(AnimalModuleConstants, attr) == pytest.approx(expected)


@pytest.mark.unit
def test_stocker_max_days_value() -> None:
    """STOCKER_MAX_DAYS must be 210 (maximum backgrounding days before forced exit)."""
    assert hasattr(AnimalModuleConstants, "STOCKER_MAX_DAYS")
    assert AnimalModuleConstants.STOCKER_MAX_DAYS == 210


# ---------------------------------------------------------------------------
# Type correctness
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_max_days_is_int() -> None:
    """STOCKER_MAX_DAYS must be int, not float."""
    assert isinstance(AnimalModuleConstants.STOCKER_MAX_DAYS, int)


@pytest.mark.unit
@pytest.mark.parametrize(
    "attr",
    ["STOCKER_MIN_ENTRY_WEIGHT_KG", "STOCKER_TARGET_EXIT_WEIGHT_KG", "STOCKER_TARGET_ADG_KG_D"],
)
def test_stocker_weight_adg_constants_are_float(attr: str) -> None:
    """Weight and ADG constants must be float."""
    assert isinstance(getattr(AnimalModuleConstants, attr), float)


# ---------------------------------------------------------------------------
# Positive-value guards
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "attr",
    [
        "STOCKER_MIN_ENTRY_WEIGHT_KG",
        "STOCKER_TARGET_EXIT_WEIGHT_KG",
        "STOCKER_TARGET_ADG_KG_D",
        "STOCKER_MAX_DAYS",
    ],
)
def test_stocker_constants_positive(attr: str) -> None:
    """All stocker constants must be strictly positive."""
    value = getattr(AnimalModuleConstants, attr)
    assert value > 0, f"{attr}={value} must be > 0"


# ---------------------------------------------------------------------------
# Biological ordering and range checks
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_entry_weight_below_exit_weight() -> None:
    """Entry weight must be strictly less than target exit weight."""
    assert AnimalModuleConstants.STOCKER_MIN_ENTRY_WEIGHT_KG < AnimalModuleConstants.STOCKER_TARGET_EXIT_WEIGHT_KG


@pytest.mark.unit
def test_stocker_adg_within_nrc_forage_range() -> None:
    """STOCKER_TARGET_ADG_KG_D must lie within the NRC 2016 Ch.10 forage range (0.35-1.15 kg/d)."""
    adg = AnimalModuleConstants.STOCKER_TARGET_ADG_KG_D
    assert 0.35 <= adg <= 1.15, f"ADG {adg} outside NRC 2016 Ch.10 forage range [0.35, 1.15]"


@pytest.mark.unit
def test_stocker_max_days_reasonable() -> None:
    """STOCKER_MAX_DAYS must be between 90 and 365 (< 1 year; > typical minimum of 3 months)."""
    assert 90 <= AnimalModuleConstants.STOCKER_MAX_DAYS <= 365


@pytest.mark.unit
def test_stocker_entry_weight_above_typical_weaning_floor() -> None:
    """STOCKER_MIN_ENTRY_WEIGHT_KG must be at least 150 kg (above lightweight calf threshold)."""
    assert AnimalModuleConstants.STOCKER_MIN_ENTRY_WEIGHT_KG >= 150.0


# ---------------------------------------------------------------------------
# Scope guard — no BeefGEM constants leaked in
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_no_stocker_dmi_ratio_constant() -> None:
    """STOCKER_DMI_RATIO must NOT exist — it belongs to BeefGEM Phase B, not native module."""
    assert not hasattr(AnimalModuleConstants, "STOCKER_DMI_RATIO")


@pytest.mark.unit
def test_no_stocker_brody_k_constant() -> None:
    """STOCKER_BRODY_K must NOT exist — compensatory gain belongs to BeefGEM Phase D."""
    assert not hasattr(AnimalModuleConstants, "STOCKER_BRODY_K")
