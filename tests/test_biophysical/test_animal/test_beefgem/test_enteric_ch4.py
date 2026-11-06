"""Tests for the stocker forage enteric methane equation and its reporter output.

Verifies:
- The forage intercept and slope constants
- calculate_beef_stocker_methane arithmetic and input guarding
- Where the equation sits against the NRC 2016 Ch.16 grazing range
- stocker_mean_daily_enteric_ch4_g_d emitted at stocker exit
- Regression: the Phase A feedlot routing is untouched
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_module_reporter as reporter_module
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_enums import FinishingSystem
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.units import MeasurementUnits

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_FORAGE_INTERCEPT: float = 10.04  # g CH4/d
_FORAGE_SLOPE: float = 23.7  # g CH4 per kg DMI/d

_PINNED_DMI: float = 10.0  # kg DM/d
_PINNED_CH4: float = 247.04  # g CH4/d = 10.04 + 23.7 x 10

_GRAZING_CH4_MIN_G_D: float = 87.0  # NRC 2016 Ch.16 published grazing floor
_GRAZING_CH4_MAX_G_D: float = 252.0  # NRC 2016 Ch.16 published grazing ceiling

_CH4_VARIABLE_NAME: str = "stocker_mean_daily_enteric_ch4_g_d"

_EXIT_DAYS_IN_STOCKER: int = 150
_EXIT_CUMULATIVE_DMI: float = 900.0  # kg DM over the backgrounding period
_EXIT_MEAN_DAILY_DMI: float = _EXIT_CUMULATIVE_DMI / _EXIT_DAYS_IN_STOCKER  # 6.0 kg DM/d


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_exiting_stocker(
    days_in_stocker: int = _EXIT_DAYS_IN_STOCKER,
    cumulative_dmi: float = _EXIT_CUMULATIVE_DMI,
) -> Animal:
    """Construct a minimal stocker at pen exit carrying only what the reporter reads."""
    animal: Animal = Animal.__new__(Animal)
    animal.id = 1
    animal.animal_type = AnimalType.BEEF_STOCKER_STEER
    animal.body_weight = 350.0
    animal.stocker_entry_weight = 240.0
    animal.days_in_stocker = days_in_stocker
    animal.stocker_cumulative_dmi = cumulative_dmi
    return animal


def _make_exiting_feedlot_animal() -> Animal:
    """Construct a minimal feedlot steer at pen exit, for the Phase A regression guard."""
    animal: Animal = Animal.__new__(Animal)
    animal.id = 2
    animal.animal_type = AnimalType.FEEDLOT_STEER
    animal.body_weight = 580.0
    animal.entry_weight = 320.0
    animal.days_on_feed = 150
    animal.cumulative_dmi = 1350.0
    return animal


def _emitted(spy: MagicMock, name: str) -> float:
    """Return the value the reporter passed to om.add_variable for ``name``."""
    call = next(c for c in spy.call_args_list if c.args[0] == name)
    return float(call.args[1])


# ---------------------------------------------------------------------------
# B-2.1 — the forage constants
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_forage_intercept_constant_value() -> None:
    """The forage intercept must be 10.04 g CH4/d."""
    assert AnimalModuleConstants.BEEF_CH4_STOCKER_FORAGE_INTERCEPT == pytest.approx(_FORAGE_INTERCEPT)


@pytest.mark.unit
def test_forage_slope_constant_value() -> None:
    """The forage slope must be 23.7 g CH4 per kg DMI/d."""
    assert AnimalModuleConstants.BEEF_CH4_STOCKER_FORAGE_SLOPE == pytest.approx(_FORAGE_SLOPE)


# ---------------------------------------------------------------------------
# B-2.2 — the stocker equation
# ---------------------------------------------------------------------------


@pytest.mark.nrc2016
def test_stocker_ch4_at_pinned_dmi() -> None:
    """At DMI 10 kg/d the equation must yield 247.04 g/d exactly."""
    assert EntericMethaneCalculator.calculate_beef_stocker_methane(_PINNED_DMI) == pytest.approx(_PINNED_CH4)


@pytest.mark.unit
def test_stocker_ch4_at_zero_dmi_returns_intercept() -> None:
    """At zero intake the equation returns its intercept, not zero.

    The reporter must therefore short-circuit a zero-day phase rather than
    feeding it a zero DMI; see test_reporter_zero_days_yields_zero_ch4.
    """
    result = EntericMethaneCalculator.calculate_beef_stocker_methane(0.0)
    assert result == pytest.approx(_FORAGE_INTERCEPT)


@pytest.mark.unit
def test_stocker_ch4_is_monotonic_in_dmi() -> None:
    """Stocker CH4 must increase with intake."""
    low = EntericMethaneCalculator.calculate_beef_stocker_methane(5.0)
    high = EntericMethaneCalculator.calculate_beef_stocker_methane(9.0)
    assert high > low


@pytest.mark.unit
@pytest.mark.parametrize("bad_dmi", [-1.0, float("nan"), float("inf")])
def test_stocker_ch4_rejects_invalid_dmi(bad_dmi: float) -> None:
    """Negative, NaN and infinite intake must raise ValueError."""
    with pytest.raises(ValueError, match="dmi"):
        EntericMethaneCalculator.calculate_beef_stocker_methane(bad_dmi)


@pytest.mark.nrc2016
@pytest.mark.parametrize("dmi", [6.0, 8.0, 10.0])
def test_stocker_ch4_inside_published_grazing_range(dmi: float) -> None:
    """Across realistic stocker intakes the equation stays inside 87-252 g/d.

    NRC 2016 Ch.16 reports that range for grazing beef cattle. Unlike the
    grass-fed finishing coefficients, this equation sits inside it throughout
    the practical intake range.
    """
    result = EntericMethaneCalculator.calculate_beef_stocker_methane(dmi)
    assert _GRAZING_CH4_MIN_G_D <= result <= _GRAZING_CH4_MAX_G_D


@pytest.mark.nrc2016
def test_stocker_ch4_leaves_published_range_above_ten_kg() -> None:
    """Above roughly 10.2 kg DM/d the equation exceeds the published grazing ceiling.

    Pinned so the boundary is visible in the suite. Stocker intakes at typical
    backgrounding weights sit near 6-7 kg DM/d, so this is outside the normal
    operating range rather than a defect, but it bounds where the equation
    stops agreeing with NRC 2016 Ch.16.
    """
    assert EntericMethaneCalculator.calculate_beef_stocker_methane(11.0) > _GRAZING_CH4_MAX_G_D


# ---------------------------------------------------------------------------
# B-2.3 — the reporter output
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_reporter_emits_stocker_ch4_variable(mocker: MockerFixture) -> None:
    """The stocker exit reporter must emit the mean-daily CH4 variable."""
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_stocker_performance(_make_exiting_stocker(), simulation_day=400)

    emitted_names = {c.args[0] for c in spy.call_args_list}
    assert _CH4_VARIABLE_NAME in emitted_names


@pytest.mark.unit
def test_reporter_ch4_matches_mean_daily_intake(mocker: MockerFixture) -> None:
    """The emitted value must be the equation evaluated at mean daily intake."""
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_stocker_performance(_make_exiting_stocker(), simulation_day=400)

    expected = EntericMethaneCalculator.calculate_beef_stocker_methane(_EXIT_MEAN_DAILY_DMI)
    assert _emitted(spy, _CH4_VARIABLE_NAME) == pytest.approx(expected)


@pytest.mark.unit
def test_reporter_zero_days_yields_zero_ch4(mocker: MockerFixture) -> None:
    """days_in_stocker = 0 must emit 0.0, not the equation intercept, and not raise."""
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_stocker_performance(
        _make_exiting_stocker(days_in_stocker=0, cumulative_dmi=0.0), simulation_day=400
    )

    assert _emitted(spy, _CH4_VARIABLE_NAME) == pytest.approx(0.0)


@pytest.mark.unit
def test_reporter_ch4_uses_grams_per_day_units(mocker: MockerFixture) -> None:
    """The CH4 variable must be tagged GRAMS_PER_DAY."""
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_stocker_performance(_make_exiting_stocker(), simulation_day=400)

    call = next(c for c in spy.call_args_list if c.args[0] == _CH4_VARIABLE_NAME)
    assert call.args[2]["units"] is MeasurementUnits.GRAMS_PER_DAY


@pytest.mark.regression
def test_reporter_still_emits_all_six_original_stocker_variables(mocker: MockerFixture) -> None:
    """The six pre-existing stocker exit variables must survive unchanged."""
    spy = mocker.patch.object(reporter_module.om, "add_variable")

    AnimalModuleReporter.report_stocker_performance(_make_exiting_stocker(), simulation_day=400)

    emitted_names = {c.args[0] for c in spy.call_args_list}
    assert {
        "stocker_days_in_phase",
        "stocker_total_gain_kg",
        "stocker_adg_kg_d",
        "stocker_fcr",
        "stocker_exit_weight_kg",
        "stocker_cumulative_dmi_kg",
    } <= emitted_names


# ---------------------------------------------------------------------------
# Regression — Phase A feedlot routing untouched
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_feedlot_grain_fed_routing_unchanged(mocker: MockerFixture) -> None:
    """Adding the stocker path must not disturb the Phase A grain-fed routing."""
    mocker.patch.object(AnimalConfig, "finishing_system", FinishingSystem.GRAIN_FED)
    spy = mocker.patch.object(reporter_module.om, "add_variable")
    AnimalModuleReporter.report_feedlot_performance(_make_exiting_feedlot_animal(), simulation_day=400)
    expected = EntericMethaneCalculator.calculate_beef_grain_fed_methane(1350.0 / 150)
    assert _emitted(spy, "feedlot_mean_daily_enteric_ch4_g_d") == pytest.approx(expected)


@pytest.mark.regression
def test_feedlot_grass_fed_routing_unchanged(mocker: MockerFixture) -> None:
    """The Phase A grass-fed routing must also be untouched."""
    mocker.patch.object(AnimalConfig, "finishing_system", FinishingSystem.GRASS_FED)
    spy = mocker.patch.object(reporter_module.om, "add_variable")
    AnimalModuleReporter.report_feedlot_performance(_make_exiting_feedlot_animal(), simulation_day=400)
    expected = EntericMethaneCalculator.calculate_beef_grass_fed_methane(1350.0 / 150)
    assert _emitted(spy, "feedlot_mean_daily_enteric_ch4_g_d") == pytest.approx(expected)


@pytest.mark.regression
def test_stocker_and_feedlot_equations_are_distinct() -> None:
    """The stocker forage equation must not coincide with either finishing equation."""
    dmi = 8.0
    stocker = EntericMethaneCalculator.calculate_beef_stocker_methane(dmi)
    grain = EntericMethaneCalculator.calculate_beef_grain_fed_methane(dmi)
    grass = EntericMethaneCalculator.calculate_beef_grass_fed_methane(dmi)
    assert stocker != pytest.approx(grain)
    assert stocker != pytest.approx(grass)
