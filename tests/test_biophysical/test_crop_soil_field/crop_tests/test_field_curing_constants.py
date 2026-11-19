"""Tests for RUFAS/biophysical/field/crop/field_curing_constants.py.

Covers the module importing cleanly plus the physical/numerical invariants its constants must
hold. Every constant's *value* is already exercised for real via the behavioral tests in
test_field_curing.py (e.g. test_dry_bulb_drying_rate_typical_values, test_respiration_dm_loss_matches_dafosym_eq7)
-- this file only pins invariants that a self-referential "== its own literal" test cannot.
"""

import pytest

from RUFAS.biophysical.field.crop import field_curing_constants as fcc
from RUFAS.biophysical.field.crop.field_curing import FieldCuring
from RUFAS.general_constants import GeneralConstants


@pytest.mark.smoke
def test_field_curing_constants_module_imports() -> None:
    """The module must import cleanly and expose every constant field_curing.py depends on."""
    for name in (
        "CELSIUS_TO_FAHRENHEIT_SCALE",
        "CELSIUS_TO_FAHRENHEIT_OFFSET",
        "MM_TO_INCHES_DIVISOR",
        "FIELD_CURING_RESPIRATION_MOISTURE_THRESHOLD",
        "FIELD_CURING_RNL_MAX",
        "MJ_PER_M2_DAY_TO_W_PER_M2",
        "SWATH_MOISTURE_EQUILIBRIUM_FRACTION",
    ):
        assert hasattr(fcc, name)


@pytest.mark.unit
def test_respiration_moisture_threshold_is_a_valid_wet_basis_fraction() -> None:
    """FIELD_CURING_RESPIRATION_MOISTURE_THRESHOLD (AMC, Eq.7) must be a 0-1 wet-basis fraction --
    the equation's own domain, not just an arbitrary positive number."""
    assert 0.0 < fcc.FIELD_CURING_RESPIRATION_MOISTURE_THRESHOLD < 1.0


@pytest.mark.unit
def test_rnl_max_is_a_numerical_guard_below_unity() -> None:
    """FIELD_CURING_RNL_MAX must stay strictly below 1.0 -- it exists specifically to prevent
    Eq.11's division-by-(1-RNL) singularity as RNL approaches 1."""
    assert fcc.FIELD_CURING_RNL_MAX < 1.0


@pytest.mark.unit
def test_mj_per_m2_day_to_w_per_m2_matches_seconds_per_day_identity() -> None:
    """MJ_PER_M2_DAY_TO_W_PER_M2 must equal the J/s <-> J/day unit identity, derived from
    RUFAS's own GeneralConstants.HOURS_PER_DAY rather than a second copy of the literal 86400."""
    assert fcc.MJ_PER_M2_DAY_TO_W_PER_M2 == pytest.approx(1_000_000.0 / (GeneralConstants.HOURS_PER_DAY * 3600))


@pytest.mark.unit
def test_celsius_to_fahrenheit_constants_reproduce_boiling_point() -> None:
    """CELSIUS_TO_FAHRENHEIT_SCALE and _OFFSET, used together via FieldCuring.celsius_to_fahrenheit,
    must reproduce a known reference point (water boils at 100C == 212F) -- exercises both
    constants together through the real conversion function rather than re-asserting each in
    isolation."""
    assert FieldCuring.celsius_to_fahrenheit(100.0) == pytest.approx(212.0)
