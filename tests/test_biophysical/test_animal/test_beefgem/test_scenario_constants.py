"""Tests for the named-scenario constants and their two AnimalConfig levers.

Verifies:
- The eight named-scenario constants and their pinned values
- The calving-month classmethod pair over beef_breeding_season_start_day
- beef_conception_rate_multiplier parsing, validation and effect
- The conception probability clamp
- Regression: the shipped breeding-season default and baseline behaviour
"""

from __future__ import annotations

from typing import Any, Generator

import pytest

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.reproduction.beef_reproduction import (
    calculate_seasonal_conception_probability,
)
from RUFAS.data_validator import DataValidator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BREEDING_SEASON_DAYS: int = 63
_REFERENCE_BCS: float = 5.0
_REFERENCE_BULL_RATIO: int = 25
_ELIGIBLE_DAYS_POSTPARTUM: int = 60  # past the 45-day anestrus gate

_BASELINE_SEASONAL_RATE: float = 0.9256
_HIGH_SEASONAL_RATE: float = 0.95
_LOW_SEASONAL_RATE: float = 0.80


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


_COW_CALF_CONFIG_FIELDS: tuple[str, ...] = (
    "beef_breeding_season_start_day",
    "beef_conception_rate_multiplier",
    "beef_breeding_season_length",
    "beef_weaning_age_days",
    "beef_mature_cow_weight_kg",
    "beef_natural_service_bull_ratio",
    "beef_cow_cull_rate_annual",
    "beef_weaning_weight_kg",
    "beef_creep_feeding_enabled",
    "beef_post_weaning_destination",
    "beef_reproduction_program",
)
"""Every ClassVar _initialize_beef_cow_calf_config assigns.

No single map in animal_config.py enumerates these the way
beef_scenario_runner._SCENARIO_FIELD_TO_CONFIG enumerates the scenario
fields it writes -- the assignments are split across _merge_beef_defaults,
_assign_beef_config_fields and _parse_beef_enum_fields, so this list is
hand-maintained rather than derived. test_conception_multiplier_parsed_from_config
calls the full initializer with a config that sets only
conception_rate_multiplier, so every other field here is reset to its
declared default by that one call and must be restored, not just the two
fields these tests deliberately vary.
"""


@pytest.fixture(autouse=True)
def _restore_beef_config() -> Generator[None, None, None]:
    """Save and restore every ClassVar _initialize_beef_cow_calf_config touches.

    A call to that initializer with a partial config resets every field it
    owns to its declared default, not only the ones the calling test cares
    about -- so the fixture must cover the full set, not just the fields
    these tests deliberately vary.
    """
    saved = {name: getattr(AnimalConfig, name) for name in _COW_CALF_CONFIG_FIELDS}
    yield
    for name, value in saved.items():
        setattr(AnimalConfig, name, value)


def _make_beef_config(**overrides: object) -> dict[str, Any]:
    """Return a beef cow-calf config dict with optional overrides."""
    config: dict[str, Any] = {}
    config.update(overrides)
    return config


def _seasonal_rate(multiplier: float) -> float:
    """Seasonal pregnancy rate at the calibration reference point for a multiplier."""
    daily = calculate_seasonal_conception_probability(
        body_condition_score=_REFERENCE_BCS,
        bull_to_cow_ratio=_REFERENCE_BULL_RATIO,
        days_since_calving=_ELIGIBLE_DAYS_POSTPARTUM,
        conception_rate_multiplier=multiplier,
    )
    return 1.0 - (1.0 - daily) ** _BREEDING_SEASON_DAYS


# ---------------------------------------------------------------------------
# C-1.1 — the eight named-scenario constants
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("BEEF_SCENARIO_SPRING_CALVING_MONTH", 4),
        ("BEEF_SCENARIO_FALL_CALVING_MONTH", 10),
        ("BEEF_SCENARIO_EARLY_WEANING_AGE_DAYS", 150),
    ],
)
def test_integer_scenario_constants(name: str, expected: int) -> None:
    """Each integer scenario constant must exist with its pinned value."""
    assert getattr(AnimalModuleConstants, name) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("BEEF_SCENARIO_HIGH_CONCEPTION_MULTIPLIER", 1.15),
        ("BEEF_SCENARIO_LOW_CONCEPTION_MULTIPLIER", 0.625),
        ("BEEF_SCENARIO_AGGRESSIVE_CULL_RATE", 0.22),
    ],
)
def test_float_scenario_constants(name: str, expected: float) -> None:
    """Each float scenario constant must exist with its pinned value."""
    assert getattr(AnimalModuleConstants, name) == pytest.approx(expected)


@pytest.mark.unit
def test_calving_month_constants_are_valid_months() -> None:
    """Both calving-month constants must be inside 1-12."""
    for month in (
        AnimalModuleConstants.BEEF_SCENARIO_SPRING_CALVING_MONTH,
        AnimalModuleConstants.BEEF_SCENARIO_FALL_CALVING_MONTH,
    ):
        assert 1 <= month <= 12


# ---------------------------------------------------------------------------
# C-1.2 — the calving-month classmethod pair
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_calving_month_at_shipped_default_is_january() -> None:
    """At the shipped breeding default the derived calving month is January.

    Breeding opens on day 90 and gestation is 283 days, so calving falls on
    day 373, which wraps to 8 January. The spring-calving scenario constant is
    April, so the shipped default is not a spring-calving herd. Pinned so that
    changing BEEF_DEFAULT_BREEDING_SEASON_START_DAY fails here and says why.
    """
    AnimalConfig.beef_breeding_season_start_day = AnimalModuleConstants.BEEF_DEFAULT_BREEDING_SEASON_START_DAY
    assert AnimalConfig.get_beef_calving_month() == 1


@pytest.mark.unit
@pytest.mark.parametrize("month", list(range(1, 13)))
def test_calving_month_round_trips_losslessly(month: int) -> None:
    """month -> day -> month must return the original month for all twelve."""
    AnimalConfig.set_beef_calving_month(month)
    assert AnimalConfig.get_beef_calving_month() == month


@pytest.mark.unit
def test_setter_stores_only_the_breeding_day() -> None:
    """The setter must move beef_breeding_season_start_day and store nothing else."""
    before = AnimalConfig.beef_breeding_season_start_day
    AnimalConfig.set_beef_calving_month(AnimalModuleConstants.BEEF_SCENARIO_SPRING_CALVING_MONTH)
    assert AnimalConfig.beef_breeding_season_start_day != before
    assert AnimalConfig.get_beef_calving_month() == AnimalModuleConstants.BEEF_SCENARIO_SPRING_CALVING_MONTH


@pytest.mark.unit
def test_breeding_day_stays_inside_the_year() -> None:
    """The derived breeding day must always land in 1-365."""
    for month in range(1, 13):
        AnimalConfig.set_beef_calving_month(month)
        assert 1 <= AnimalConfig.beef_breeding_season_start_day <= 365


@pytest.mark.unit
@pytest.mark.parametrize("bad_month", [0, 13, -1, 100])
def test_setter_rejects_out_of_range_month(bad_month: int) -> None:
    """Months outside 1-12 must raise ValueError."""
    with pytest.raises(ValueError, match="calving_month"):
        AnimalConfig.set_beef_calving_month(bad_month)


@pytest.mark.unit
def test_day_to_month_to_day_snaps_to_month_start() -> None:
    """day -> month -> day snaps to the first of the month, as documented."""
    AnimalConfig.beef_breeding_season_start_day = 187  # mid-April calving
    month = AnimalConfig.get_beef_calving_month()
    AnimalConfig.set_beef_calving_month(month)
    assert AnimalConfig.get_beef_calving_month() == month


# ---------------------------------------------------------------------------
# C-1.2 — the conception rate multiplier
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_conception_multiplier_defaults_to_one() -> None:
    """The default must be 1.0 so calibrated behaviour is untouched."""
    assert AnimalConfig.beef_conception_rate_multiplier == pytest.approx(1.0)


@pytest.mark.unit
def test_conception_multiplier_parsed_from_config() -> None:
    """A configured multiplier must land on the ClassVar."""
    AnimalConfig._initialize_beef_cow_calf_config({"beef_cow_calf": _make_beef_config(conception_rate_multiplier=1.15)})
    assert AnimalConfig.beef_conception_rate_multiplier == pytest.approx(1.15)


@pytest.mark.unit
@pytest.mark.parametrize("bad_multiplier", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_conception_multiplier_raises(bad_multiplier: float) -> None:
    """Zero, negative, NaN and infinite multipliers must raise ValueError."""
    with pytest.raises(ValueError, match="conception_rate_multiplier"):
        DataValidator.validate_beef_cow_calf_config(_make_beef_config(conception_rate_multiplier=bad_multiplier))


@pytest.mark.unit
@pytest.mark.parametrize("good_multiplier", [0.1, 0.625, 1.0, 1.15, 5.0])
def test_valid_conception_multiplier_accepted(good_multiplier: float) -> None:
    """Any positive finite multiplier must validate."""
    DataValidator.validate_beef_cow_calf_config(_make_beef_config(conception_rate_multiplier=good_multiplier))


@pytest.mark.unit
def test_multiplier_scales_daily_probability() -> None:
    """The daily probability must scale linearly with the multiplier."""
    baseline = calculate_seasonal_conception_probability(
        _REFERENCE_BCS, _REFERENCE_BULL_RATIO, 60, conception_rate_multiplier=1.0
    )
    doubled = calculate_seasonal_conception_probability(
        _REFERENCE_BCS, _REFERENCE_BULL_RATIO, 60, conception_rate_multiplier=2.0
    )
    assert doubled == pytest.approx(baseline * 2.0)


@pytest.mark.regression
def test_omitted_multiplier_leaves_probability_unchanged() -> None:
    """Omitting the multiplier must reproduce the calibrated base probability exactly.

    The parameter defaults to 1.0, so every pre-existing call site is unaffected
    by the signature change.
    """
    daily = calculate_seasonal_conception_probability(_REFERENCE_BCS, _REFERENCE_BULL_RATIO, 60)
    assert daily == pytest.approx(AnimalModuleConstants.BEEF_CONCEPTION_BASE_DAILY_PROB)


@pytest.mark.unit
def test_anestrus_gate_still_returns_zero_under_any_multiplier() -> None:
    """The postpartum anestrus gate must short-circuit before the multiplier applies."""
    daily = calculate_seasonal_conception_probability(
        _REFERENCE_BCS, _REFERENCE_BULL_RATIO, days_since_calving=10, conception_rate_multiplier=10.0
    )
    assert daily == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# The derivation the scenario multipliers are built on
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_baseline_seasonal_rate_is_92_56_percent() -> None:
    """The calibrated baseline yields 92.56% across the 63-day season.

    BEEF_CONCEPTION_BASE_DAILY_PROB documents itself as calibrated to a USDA
    91.5% seasonal rate; the figure it actually produces at the reference point
    is 92.56%. Pinned so the gap stays visible and the scenario multiplier
    derivation remains reproducible.
    """
    assert _seasonal_rate(1.0) == pytest.approx(_BASELINE_SEASONAL_RATE, abs=1e-4)


@pytest.mark.unit
def test_high_conception_multiplier_yields_95_percent() -> None:
    """The high-conception multiplier must produce a 95% seasonal rate."""
    rate = _seasonal_rate(AnimalModuleConstants.BEEF_SCENARIO_HIGH_CONCEPTION_MULTIPLIER)
    assert rate == pytest.approx(_HIGH_SEASONAL_RATE, abs=1e-3)


@pytest.mark.unit
def test_low_conception_multiplier_yields_80_percent() -> None:
    """The low-conception multiplier must produce an 80% seasonal rate."""
    rate = _seasonal_rate(AnimalModuleConstants.BEEF_SCENARIO_LOW_CONCEPTION_MULTIPLIER)
    assert rate == pytest.approx(_LOW_SEASONAL_RATE, abs=1e-3)


@pytest.mark.unit
def test_conception_probability_is_clamped_to_one() -> None:
    """An extreme multiplier must not push the daily probability above 1.0.

    Unreachable under validated inputs: both adjustment factors cap at 1.0, so
    triggering the clamp needs a multiplier of 24.75. Guarded regardless.
    """
    daily = calculate_seasonal_conception_probability(
        _REFERENCE_BCS, _REFERENCE_BULL_RATIO, 60, conception_rate_multiplier=100.0
    )
    assert daily == pytest.approx(1.0)


@pytest.mark.unit
def test_conception_probability_never_negative() -> None:
    """A very small multiplier must stay at or above zero."""
    daily = calculate_seasonal_conception_probability(
        _REFERENCE_BCS, _REFERENCE_BULL_RATIO, 60, conception_rate_multiplier=1e-6
    )
    assert daily >= 0.0
