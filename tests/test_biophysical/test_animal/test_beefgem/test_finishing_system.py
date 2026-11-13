"""Tests for the beef finishing-system flag and its grass-fed enteric CH4 pathway.

Verifies:
- FinishingSystem enum members, values, and plain-Enum discipline
- AnimalConfig.finishing_system default and config parsing
- DataValidator.validate_feedlot_config rejection of unknown values
- Grass-fed linear enteric CH4 constants and equation
- Grain-fed IPCC Tier 2 enteric CH4 equation and its validation window
- Reporter routing on finishing_system, including the zero-days-on-feed guard
- Regression: the flag is inert on the existing requirements calculation
"""

from __future__ import annotations

from typing import Any, Generator
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_module_reporter as reporter_module
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_enums import FinishingSystem, Sex
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.nutrients.beef_nrc_requirements_calculator import (
    BeefNRCRequirementsCalculator,
)
from RUFAS.data_validator import DataValidator
from RUFAS.general_constants import GeneralConstants
from RUFAS.units import MeasurementUnits

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BENCHMARK_DMI: float = 8.0  # kg DM/d — grass-fed linear pin point
_EXPECTED_GRASS_FED_CH4: float = 257.85  # g CH4/d = 8.25 + 31.2 x 8.0

_GRAIN_FED_DMI: float = 9.0  # kg DM/d — IPCC Tier 2 check point
_FEEDLOT_CH4_MIN_G_D: float = 36.0  # NRC 2016 Ch.16 published feedlot floor
_FEEDLOT_CH4_MAX_G_D: float = 145.0  # NRC 2016 Ch.16 published feedlot ceiling

_GRAZING_CH4_MIN_G_D: float = 87.0  # NRC 2016 Ch.16 published grazing floor
_GRAZING_CH4_MAX_G_D: float = 252.0  # NRC 2016 Ch.16 published grazing ceiling

_CH4_VARIABLE_NAME: str = "feedlot_mean_daily_enteric_ch4_g_d"

_EXIT_DAYS_ON_FEED: int = 150
_EXIT_CUMULATIVE_DMI: float = 1350.0  # kg DM over the feeding period
_EXIT_MEAN_DAILY_DMI: float = _EXIT_CUMULATIVE_DMI / _EXIT_DAYS_ON_FEED  # 9.0 kg DM/d

_VALID_FEEDLOT_CONFIG: dict[str, Any] = {
    "entry_weight": 320.0,
    "slaughter_weight": 580.0,
    "max_days_on_feed": 220,
    "mud_condition": "none",
}


# ---------------------------------------------------------------------------
# Fixtures — restore AnimalConfig scalar ClassVar after every test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_finishing_system() -> Generator[None, None, None]:
    """Save and restore AnimalConfig.finishing_system (scalar — direct assignment)."""
    saved_finishing_system = AnimalConfig.finishing_system
    yield
    AnimalConfig.finishing_system = saved_finishing_system


def _make_feedlot_config(**overrides: object) -> dict[str, Any]:
    """Return a valid feedlot config dict with optional overrides."""
    config: dict[str, Any] = dict(_VALID_FEEDLOT_CONFIG)
    config.update(overrides)
    return config


def _make_feedlot_animal(
    days_on_feed: int = _EXIT_DAYS_ON_FEED,
    cumulative_dmi: float = _EXIT_CUMULATIVE_DMI,
) -> Animal:
    """Construct a minimal feedlot steer at pen exit via Animal.__new__.

    Parameters
    ----------
    days_on_feed : int
        Days since pen placement.
    cumulative_dmi : float
        Total dry matter consumed over the feeding period (kg DM).

    Returns
    -------
    Animal
        A BEEF feedlot steer carrying only the attributes the exit reporter reads.

    """
    animal: Animal = Animal.__new__(Animal)
    animal.id = 1
    animal.animal_type = AnimalType.FEEDLOT_STEER
    animal.body_weight = 580.0
    animal.entry_weight = 320.0
    animal.days_on_feed = days_on_feed
    animal.cumulative_dmi = cumulative_dmi
    return animal


def _emitted_ch4(spy: MagicMock) -> float:
    """Return the CH4 value the reporter passed to om.add_variable."""
    call = next(c for c in spy.call_args_list if c.args[0] == _CH4_VARIABLE_NAME)
    return float(call.args[1])


def _calculate_feedlot_requirements() -> Any:
    """Run the feedlot requirements calculation with fixed benchmark inputs."""
    return BeefNRCRequirementsCalculator.calculate_requirements(
        body_weight=400.0,
        mature_body_weight=580.0,
        animal_type=AnimalType.FEEDLOT_STEER,
        breed="Angus",
        sex=Sex.STEER,
        days_on_feed=100,
        target_adg=1.5,
        implant_adg_factor=1.0,
        housing="Open_Lot",
        mud_condition=AnimalModuleConstants.BEEF_MUD_CONDITION_NONE,
        temperature_c=20.0,
        ne_diet_concentration=1.4,
        process_based_phosphorus_requirement=0.0,
    )


# ---------------------------------------------------------------------------
# FinishingSystem enum — members, values, plain-Enum discipline
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_finishing_system_grain_fed_member_exists() -> None:
    """FinishingSystem.GRAIN_FED must exist."""
    assert hasattr(FinishingSystem, "GRAIN_FED")


@pytest.mark.unit
def test_finishing_system_grass_fed_member_exists() -> None:
    """FinishingSystem.GRASS_FED must exist."""
    assert hasattr(FinishingSystem, "GRASS_FED")


@pytest.mark.unit
def test_finishing_system_grain_fed_value() -> None:
    """GRAIN_FED value must be 'grain_fed'."""
    assert FinishingSystem.GRAIN_FED.value == "grain_fed"


@pytest.mark.unit
def test_finishing_system_grass_fed_value() -> None:
    """GRASS_FED value must be 'grass_fed'."""
    assert FinishingSystem.GRASS_FED.value == "grass_fed"


@pytest.mark.unit
def test_finishing_system_exactly_two_members() -> None:
    """FinishingSystem must have exactly two members."""
    assert len(FinishingSystem) == 2


@pytest.mark.unit
def test_finishing_system_is_plain_enum_not_str_enum() -> None:
    """FinishingSystem must be a plain Enum, never a str,Enum (house rule from PR #47)."""
    assert not issubclass(FinishingSystem, str)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("grain_fed", FinishingSystem.GRAIN_FED),
        ("grass_fed", FinishingSystem.GRASS_FED),
    ],
)
def test_finishing_system_roundtrip(raw: str, expected: FinishingSystem) -> None:
    """FinishingSystem(value) round-trips to the matching member."""
    assert FinishingSystem(raw) is expected


@pytest.mark.unit
def test_finishing_system_invalid_raises_value_error() -> None:
    """Constructing FinishingSystem from an unknown string must raise ValueError."""
    with pytest.raises(ValueError, match="is not a valid FinishingSystem"):
        FinishingSystem("silage_fed")


# ---------------------------------------------------------------------------
# AnimalConfig — default and config parsing
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_animal_config_finishing_system_defaults_to_grain_fed() -> None:
    """The default must be GRAIN_FED so existing feedlot simulations are unchanged."""
    assert AnimalConfig.finishing_system is FinishingSystem.GRAIN_FED


@pytest.mark.unit
def test_animal_config_parses_grass_fed_from_config() -> None:
    """A 'grass_fed' feedlot config value must set the ClassVar to GRASS_FED."""
    AnimalConfig._initialize_feedlot_finishing_system(_make_feedlot_config(finishing_system="grass_fed"))
    assert AnimalConfig.finishing_system is FinishingSystem.GRASS_FED


@pytest.mark.unit
def test_animal_config_absent_key_keeps_default() -> None:
    """An absent finishing_system key must leave the GRAIN_FED default in place."""
    AnimalConfig.finishing_system = FinishingSystem.GRAIN_FED
    AnimalConfig._initialize_feedlot_finishing_system(_make_feedlot_config())
    assert AnimalConfig.finishing_system is FinishingSystem.GRAIN_FED


@pytest.mark.unit
def test_animal_config_none_value_keeps_default() -> None:
    """An explicit null finishing_system must leave the GRAIN_FED default in place."""
    AnimalConfig.finishing_system = FinishingSystem.GRAIN_FED
    AnimalConfig._initialize_feedlot_finishing_system(_make_feedlot_config(finishing_system=None))
    assert AnimalConfig.finishing_system is FinishingSystem.GRAIN_FED


# ---------------------------------------------------------------------------
# DataValidator — feedlot config validation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_validator_rejects_unknown_finishing_system() -> None:
    """An unrecognised finishing_system must raise ValueError listing the valid options."""
    with pytest.raises(ValueError, match="finishing_system must be one of"):
        DataValidator.validate_feedlot_config(_make_feedlot_config(finishing_system="silage_fed"))


@pytest.mark.unit
@pytest.mark.parametrize("system", ["grain_fed", "grass_fed"])
def test_validator_accepts_valid_finishing_system(system: str) -> None:
    """Both valid finishing_system values must pass validation."""
    DataValidator.validate_feedlot_config(_make_feedlot_config(finishing_system=system))


@pytest.mark.regression
def test_validator_accepts_config_without_finishing_system() -> None:
    """A feedlot config with no finishing_system key must still validate (backward compat)."""
    DataValidator.validate_feedlot_config(_make_feedlot_config())


@pytest.mark.unit
def test_validator_accepts_none_finishing_system() -> None:
    """An explicit null finishing_system must pass validation."""
    DataValidator.validate_feedlot_config(_make_feedlot_config(finishing_system=None))


# ---------------------------------------------------------------------------
# Grass-fed enteric CH4 constants and equation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_grass_fed_intercept_constant_value() -> None:
    """BEEF_CH4_GRASS_FED_INTERCEPT must be 8.25 g CH4/d."""
    assert AnimalModuleConstants.BEEF_CH4_GRASS_FED_INTERCEPT == pytest.approx(8.25)


@pytest.mark.unit
def test_grass_fed_slope_constant_value() -> None:
    """BEEF_CH4_GRASS_FED_SLOPE must be 31.2 g CH4 per kg DMI/d."""
    assert AnimalModuleConstants.BEEF_CH4_GRASS_FED_SLOPE == pytest.approx(31.2)


@pytest.mark.nrc2016
def test_grass_fed_ch4_at_benchmark_dmi() -> None:
    """At DMI 8 kg/d the grass-fed equation must yield 257.85 g CH4/d exactly."""
    result = EntericMethaneCalculator.calculate_beef_grass_fed_methane(_BENCHMARK_DMI)
    assert result == pytest.approx(_EXPECTED_GRASS_FED_CH4)


@pytest.mark.unit
def test_grass_fed_ch4_at_zero_dmi_returns_intercept() -> None:
    """At DMI 0 the grass-fed equation must return the intercept alone."""
    result = EntericMethaneCalculator.calculate_beef_grass_fed_methane(0.0)
    assert result == pytest.approx(AnimalModuleConstants.BEEF_CH4_GRASS_FED_INTERCEPT)


@pytest.mark.nrc2016
def test_grass_fed_ch4_exceeds_published_range_at_8kg() -> None:
    """Known discrepancy: pinned coefficients exceed NRC Ch.16 range.

    The BeefGEM source coefficients give 257.85 g/d at 8 kg DM/d,
    above the 87-252 g/d NRC 2016 Ch.16 reports for grazing cattle.
    Pinned as specified for traceability. This test documents the
    discrepancy; it should be revisited if the coefficients are
    re-sourced.
    """
    result = EntericMethaneCalculator.calculate_beef_grass_fed_methane(_BENCHMARK_DMI)
    assert result > _GRAZING_CH4_MAX_G_D


@pytest.mark.nrc2016
def test_grass_fed_ch4_inside_published_range_at_typical_grazing_dmi() -> None:
    """At a typical 7 kg DM/d grazing intake the equation stays inside the NRC range.

    The discrepancy pinned above is confined to the upper intake end, not
    present across the whole range.
    """
    result = EntericMethaneCalculator.calculate_beef_grass_fed_methane(7.0)
    assert _GRAZING_CH4_MIN_G_D <= result <= _GRAZING_CH4_MAX_G_D


@pytest.mark.unit
def test_grass_fed_ch4_is_monotonic_in_dmi() -> None:
    """Grass-fed CH4 must increase with DMI."""
    low = EntericMethaneCalculator.calculate_beef_grass_fed_methane(5.0)
    high = EntericMethaneCalculator.calculate_beef_grass_fed_methane(10.0)
    assert high > low


@pytest.mark.unit
@pytest.mark.parametrize("bad_dmi", [-1.0, float("nan"), float("inf")])
def test_grass_fed_ch4_rejects_invalid_dmi(bad_dmi: float) -> None:
    """Negative, NaN, and infinite DMI must raise ValueError."""
    with pytest.raises(ValueError, match="dmi"):
        EntericMethaneCalculator.calculate_beef_grass_fed_methane(bad_dmi)


# ---------------------------------------------------------------------------
# Grain-fed enteric CH4 — IPCC Tier 2 (NRC 2016 Table 16-2)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_grain_fed_ym_fraction_constant_value() -> None:
    """BEEF_CH4_YM_FRACTION must be the IPCC Tier 2 high-grain default of 3.0%."""
    assert AnimalModuleConstants.BEEF_CH4_YM_FRACTION == pytest.approx(0.030)


@pytest.mark.unit
def test_grain_fed_gross_energy_constant_value() -> None:
    """BEEF_GROSS_ENERGY_MJ_PER_KG_DM must be the IPCC default of 18.45 MJ/kg DM."""
    assert AnimalModuleConstants.BEEF_GROSS_ENERGY_MJ_PER_KG_DM == pytest.approx(18.45)


@pytest.mark.unit
def test_grain_fed_methane_energy_constant_value() -> None:
    """The grain-fed chain converts with the shared G_CH4_TO_MJ_CH4 of 0.05565 MJ/g (55.65 MJ/kg)."""
    assert GeneralConstants.G_CH4_TO_MJ_CH4 == pytest.approx(0.05565)


@pytest.mark.nrc2016
def test_grain_fed_ch4_at_dmi_nine_matches_ipcc_tier_two() -> None:
    """At DMI 9 kg/d the IPCC Tier 2 chain must give 9 x 18.45 x 0.030 / 0.05565 g/d."""
    expected = (
        _GRAIN_FED_DMI
        * AnimalModuleConstants.BEEF_GROSS_ENERGY_MJ_PER_KG_DM
        * AnimalModuleConstants.BEEF_CH4_YM_FRACTION
    ) / GeneralConstants.G_CH4_TO_MJ_CH4
    result = EntericMethaneCalculator.calculate_beef_grain_fed_methane(_GRAIN_FED_DMI)
    assert result == pytest.approx(expected)


@pytest.mark.nrc2016
def test_grain_fed_ch4_at_dmi_nine_inside_validation_window() -> None:
    """At DMI 9 kg/d the result must fall inside the NRC 2016 Ch.16 range of 36-145 g/d."""
    result = EntericMethaneCalculator.calculate_beef_grain_fed_methane(_GRAIN_FED_DMI)
    assert _FEEDLOT_CH4_MIN_G_D <= result <= _FEEDLOT_CH4_MAX_G_D


@pytest.mark.unit
def test_grain_fed_ch4_at_zero_dmi_is_zero() -> None:
    """IPCC Tier 2 is proportional to intake, so zero DMI must give zero CH4."""
    assert EntericMethaneCalculator.calculate_beef_grain_fed_methane(0.0) == pytest.approx(0.0)


@pytest.mark.unit
def test_grain_fed_ch4_is_lower_than_grass_fed_at_same_dmi() -> None:
    """Grain finishing must emit less enteric CH4 than grass finishing at equal DMI."""
    grain = EntericMethaneCalculator.calculate_beef_grain_fed_methane(_BENCHMARK_DMI)
    grass = EntericMethaneCalculator.calculate_beef_grass_fed_methane(_BENCHMARK_DMI)
    assert grain < grass


@pytest.mark.unit
@pytest.mark.parametrize("bad_dmi", [-1.0, float("nan"), float("inf")])
def test_grain_fed_ch4_rejects_invalid_dmi(bad_dmi: float) -> None:
    """Negative, NaN, and infinite DMI must raise ValueError."""
    with pytest.raises(ValueError, match="dmi"):
        EntericMethaneCalculator.calculate_beef_grain_fed_methane(bad_dmi)


# ---------------------------------------------------------------------------
# Reporter routing — finishing_system selects the equation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_reporter_grain_fed_default_routes_to_grain_fed_equation(mocker: MockerFixture) -> None:
    """Under the GRAIN_FED default the reporter must emit the IPCC Tier 2 value."""
    AnimalConfig.finishing_system = FinishingSystem.GRAIN_FED
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_feedlot_performance(_make_feedlot_animal(), simulation_day=300)

    emitted = _emitted_ch4(spy)
    expected = EntericMethaneCalculator.calculate_beef_grain_fed_methane(_EXIT_MEAN_DAILY_DMI)
    assert emitted == pytest.approx(expected)


@pytest.mark.unit
def test_reporter_grass_fed_routes_to_grass_fed_equation(mocker: MockerFixture) -> None:
    """Under GRASS_FED the reporter must emit the linear grass-fed value."""
    AnimalConfig.finishing_system = FinishingSystem.GRASS_FED
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_feedlot_performance(_make_feedlot_animal(), simulation_day=300)

    emitted = _emitted_ch4(spy)
    expected = EntericMethaneCalculator.calculate_beef_grass_fed_methane(_EXIT_MEAN_DAILY_DMI)
    assert emitted == pytest.approx(expected)


@pytest.mark.unit
def test_reporter_grain_and_grass_fed_emit_different_values(mocker: MockerFixture) -> None:
    """The two finishing systems must not produce the same CH4 figure."""
    AnimalConfig.finishing_system = FinishingSystem.GRAIN_FED
    grain_spy = mocker.patch.object(reporter_module.om, "add_variable")
    AnimalModuleReporter.report_feedlot_performance(_make_feedlot_animal(), simulation_day=300)
    grain_ch4 = _emitted_ch4(grain_spy)

    AnimalConfig.finishing_system = FinishingSystem.GRASS_FED
    grass_spy = mocker.patch.object(reporter_module.om, "add_variable")
    AnimalModuleReporter.report_feedlot_performance(_make_feedlot_animal(), simulation_day=300)
    grass_ch4 = _emitted_ch4(grass_spy)

    assert grain_ch4 != pytest.approx(grass_ch4)


@pytest.mark.unit
def test_reporter_zero_days_on_feed_yields_zero_ch4(mocker: MockerFixture) -> None:
    """days_on_feed = 0 must give 0.0 g/d rather than raising ZeroDivisionError."""
    AnimalConfig.finishing_system = FinishingSystem.GRAIN_FED
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_feedlot_performance(
        _make_feedlot_animal(days_on_feed=0, cumulative_dmi=0.0), simulation_day=300
    )

    assert _emitted_ch4(spy) == pytest.approx(0.0)


@pytest.mark.unit
@pytest.mark.regression
def test_reporter_zero_days_on_feed_yields_zero_ch4_under_grass_fed(mocker: MockerFixture) -> None:
    """days_on_feed = 0 under GRASS_FED must give 0.0, not the equation's intercept.

    calculate_beef_grass_fed_methane has a non-zero intercept (8.25 at zero
    DMI), matching the reason the stocker reporter short-circuits a
    zero-day phase instead of evaluating the equation at zero intake. The
    feedlot reporter must apply the same short-circuit.
    """
    AnimalConfig.finishing_system = FinishingSystem.GRASS_FED
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_feedlot_performance(
        _make_feedlot_animal(days_on_feed=0, cumulative_dmi=0.0), simulation_day=300
    )

    assert _emitted_ch4(spy) == pytest.approx(0.0)


@pytest.mark.unit
def test_reporter_emits_ch4_with_grams_per_day_units(mocker: MockerFixture) -> None:
    """The CH4 variable must be tagged with GRAMS_PER_DAY units."""
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_feedlot_performance(_make_feedlot_animal(), simulation_day=300)

    call = next(c for c in spy.call_args_list if c.args[0] == _CH4_VARIABLE_NAME)
    assert call.args[2]["units"] is MeasurementUnits.GRAMS_PER_DAY


@pytest.mark.regression
def test_reporter_still_emits_all_five_original_feedlot_variables(mocker: MockerFixture) -> None:
    """The five pre-existing feedlot exit variables must all survive unchanged."""
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_feedlot_performance(_make_feedlot_animal(), simulation_day=300)

    emitted_names = {c.args[0] for c in spy.call_args_list}
    assert {
        "feedlot_days_on_feed",
        "feedlot_total_gain_kg",
        "feedlot_adg_kg_d",
        "feedlot_fcr",
        "feedlot_hot_carcass_weight_kg",
    } <= emitted_names


# ---------------------------------------------------------------------------
# Regression guard — the flag must not perturb the existing calculation
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_finishing_system_flag_does_not_change_requirements() -> None:
    """Requirements output must be identical under GRAIN_FED and GRASS_FED.

    The flag selects a reporting pathway only; it must not perturb the NRC 2016
    energy or protein calculations that predate it.
    """
    AnimalConfig.finishing_system = FinishingSystem.GRAIN_FED
    grain_fed_result = _calculate_feedlot_requirements()

    AnimalConfig.finishing_system = FinishingSystem.GRASS_FED
    grass_fed_result = _calculate_feedlot_requirements()

    assert grain_fed_result.maintenance_energy == pytest.approx(grass_fed_result.maintenance_energy)
    assert grain_fed_result.growth_energy == pytest.approx(grass_fed_result.growth_energy)
    assert grain_fed_result.metabolizable_protein == pytest.approx(grass_fed_result.metabolizable_protein)
    assert grain_fed_result.dry_matter == pytest.approx(grass_fed_result.dry_matter)
