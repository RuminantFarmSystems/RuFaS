"""Combined lactating+pregnant benchmark and pipeline smoke tests (Task 11, PR-D).

NRC 2016 reference: a beef cow rebred during lactation enters a combined state
where BOTH lactation (NEl/MPl) AND gestation (NEy/MPy) requirements are active
concurrently — they sum, not replace each other (NRC 2016 Ch.13).

Test 1 verifies the calculator correctly sums both energy components.
Test 2 confirms the full dispatch chain (animal.daily_routines) is wired
correctly for a cow in this combined state.
"""

import datetime
from typing import Generator

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import BeefCowCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.nutrients.beef_cow_calf_requirements_calculator import (
    BeefCowCalfRequirementsCalculator,
    CowCalfRequirementsInputs,
)
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.rufas_time import RufasTime

# ── Shared benchmark inputs ──────────────────────────────────────────────────

_ANGUS_COW_MAINT_ONLY = CowCalfRequirementsInputs(
    body_weight=520.0,
    mature_body_weight=520.0,
    animal_type=AnimalType.BEEF_COW,
    breed="Angus",
    sex="female",
    body_condition_score=5.0,
    days_pregnant=None,
    days_in_milk=None,
    parity=2,
    target_adg=0.0,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)

_ANGUS_COW_LACT_ONLY = CowCalfRequirementsInputs(
    body_weight=520.0,
    mature_body_weight=520.0,
    animal_type=AnimalType.BEEF_COW,
    breed="Angus",
    sex="female",
    body_condition_score=5.0,
    days_pregnant=None,
    days_in_milk=60,
    parity=2,
    target_adg=0.0,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)

_ANGUS_COW_GEST_ONLY = CowCalfRequirementsInputs(
    body_weight=520.0,
    mature_body_weight=520.0,
    animal_type=AnimalType.BEEF_COW,
    breed="Angus",
    sex="female",
    body_condition_score=5.0,
    days_pregnant=30,
    days_in_milk=None,
    parity=2,
    target_adg=0.0,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)

_ANGUS_COW_COMBINED = CowCalfRequirementsInputs(
    body_weight=520.0,
    mature_body_weight=520.0,
    animal_type=AnimalType.BEEF_COW,
    breed="Angus",
    sex="female",
    body_condition_score=5.0,
    days_pregnant=30,
    days_in_milk=60,
    parity=2,
    target_adg=0.0,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)


# ── Autouse fixture: save/restore AnimalConfig beef class attrs ───────────────


@pytest.fixture(autouse=True)
def _restore_animal_config() -> Generator[None, None, None]:
    """Save and restore AnimalConfig beef class attributes after each test."""
    saved = {
        "beef_breeding_season_start_day": AnimalConfig.beef_breeding_season_start_day,
        "beef_breeding_season_length": AnimalConfig.beef_breeding_season_length,
        "beef_weaning_age_days": AnimalConfig.beef_weaning_age_days,
        "beef_weaning_weight_kg": AnimalConfig.beef_weaning_weight_kg,
        "beef_creep_feeding_enabled": AnimalConfig.beef_creep_feeding_enabled,
        "beef_post_weaning_destination": AnimalConfig.beef_post_weaning_destination,
        "beef_mature_cow_weight_kg": AnimalConfig.beef_mature_cow_weight_kg,
        "beef_natural_service_bull_ratio": AnimalConfig.beef_natural_service_bull_ratio,
        "beef_cow_cull_rate_annual": AnimalConfig.beef_cow_cull_rate_annual,
    }
    yield
    for attr, val in saved.items():
        setattr(AnimalConfig, attr, val)


# ── Autouse fixture: save/restore RationManager beef ration class attrs ───────


@pytest.fixture(autouse=True)
def _restore_ration_manager() -> Generator[None, None, None]:
    """Save and restore RationManager beef ration class attributes after each test."""
    saved_lp = dict(RationManager.beef_lactating_pasture_ration)
    saved_dg = dict(RationManager.beef_dry_gestating_ration)
    saved_cf = dict(RationManager.beef_creep_feed_ration)
    saved_rh = dict(RationManager.beef_replacement_heifer_ration)
    yield
    RationManager.beef_lactating_pasture_ration = saved_lp
    RationManager.beef_dry_gestating_ration = saved_dg
    RationManager.beef_creep_feed_ration = saved_cf
    RationManager.beef_replacement_heifer_ration = saved_rh


# ── Autouse fixture: save/restore MilkProduction class-level quality attrs ────


@pytest.fixture(autouse=True)
def _restore_milk_production() -> Generator[None, None, None]:
    """Save and restore MilkProduction class-level quality attributes after each test."""
    had_fat = hasattr(MilkProduction, "fat_percent")
    had_protein = hasattr(MilkProduction, "true_protein_percent")
    had_lactose = hasattr(MilkProduction, "lactose_percent")
    saved_fat = getattr(MilkProduction, "fat_percent", None)
    saved_protein = getattr(MilkProduction, "true_protein_percent", None)
    saved_lactose = getattr(MilkProduction, "lactose_percent", None)
    yield
    if had_fat:
        MilkProduction.fat_percent = saved_fat  # type: ignore[assignment]
    elif hasattr(MilkProduction, "fat_percent"):
        delattr(MilkProduction, "fat_percent")
    if had_protein:
        MilkProduction.true_protein_percent = saved_protein  # type: ignore[assignment]
    elif hasattr(MilkProduction, "true_protein_percent"):
        delattr(MilkProduction, "true_protein_percent")
    if had_lactose:
        MilkProduction.lactose_percent = saved_lactose  # type: ignore[assignment]
    elif hasattr(MilkProduction, "lactose_percent"):
        delattr(MilkProduction, "lactose_percent")


# ── Helper: build a minimal RufasTime without InputManager/OutputManager ──────


def _make_rufas_time_stub(current: datetime.datetime) -> RufasTime:
    """
    Create a RufasTime bypassing its normal __init__ (which needs InputManager).

    Parameters
    ----------
    current : datetime.datetime
        The date to use as both start_date and current_date (simulation day 0→1).

    Returns
    -------
    RufasTime
        A stub whose simulation_day and day_of_year properties are computed from
        current_date and start_date as per RufasTime's property implementations.

    """
    time: RufasTime = RufasTime.__new__(RufasTime)
    time.start_date = current
    time.end_date = current + datetime.timedelta(days=365)
    time.current_date = current + datetime.timedelta(days=1)
    return time


# ── Helper: set required AnimalConfig beef class attributes ──────────────────


def _set_beef_animal_config() -> None:
    """
    Set all AnimalConfig beef class attributes to minimal valid defaults.

    The autouse _restore_animal_config fixture will reset them after the test.
    """
    AnimalConfig.beef_breeding_season_start_day = 90
    AnimalConfig.beef_breeding_season_length = AnimalModuleConstants.BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS
    AnimalConfig.beef_weaning_age_days = AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS
    AnimalConfig.beef_weaning_weight_kg = None
    AnimalConfig.beef_post_weaning_destination = "sell"
    AnimalConfig.beef_mature_cow_weight_kg = AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG
    AnimalConfig.beef_cow_cull_rate_annual = AnimalModuleConstants.BEEF_ANNUAL_CULL_RATE


# ── Test 1: combined state calculator — both energy components active ─────────


@pytest.mark.unit
def test_combined_lactating_pregnant_sums_both_energy_components() -> None:
    """
    A BEEF_COW simultaneously lactating (DIM=60) and newly pregnant (DP=30)
    must receive BOTH lactation and gestation energy requirements — not one or the other.

    NRC 2016 Ch.13: these states overlap in the 63-day breeding season window following
    calving, and both requirements are active concurrently (they sum, not replace).
    Assertions:
    - lactation_energy > 0 AND pregnancy_energy > 0 (both active, neither zero).
    - total maintenance + growth + pregnancy + lactation > maintenance-only for same cow.
    - combined requirement is larger than either lactation-only or gestation-only separately.
    """
    result_combined = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_COMBINED)

    assert result_combined.lactation_energy > 0.0, "Lactation energy must be positive for DIM=60 cow"
    assert result_combined.pregnancy_energy > 0.0, "Gestation energy must be positive for DP=30 cow"

    result_maint = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_MAINT_ONLY)
    total_combined = (
        result_combined.maintenance_energy
        + result_combined.pregnancy_energy
        + result_combined.lactation_energy
        + result_combined.growth_energy
    )
    total_maint_only = result_maint.maintenance_energy
    assert (
        total_combined > total_maint_only
    ), f"Combined total ({total_combined:.4f}) must exceed maintenance-only ({total_maint_only:.4f})"

    result_lact_only = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT_ONLY)
    result_gest_only = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_GEST_ONLY)

    assert result_combined.lactation_energy == pytest.approx(
        result_lact_only.lactation_energy, rel=0.001
    ), "Combined-state lactation_energy must equal lactation-only at the same DIM"
    assert result_combined.pregnancy_energy == pytest.approx(
        result_gest_only.pregnancy_energy, rel=0.001
    ), "Combined-state pregnancy_energy must equal gestation-only at the same DP"

    combined_preg_lact = result_combined.pregnancy_energy + result_combined.lactation_energy
    assert (
        combined_preg_lact > result_lact_only.lactation_energy
    ), "Summed preg+lact must exceed lactation-only (gestation adds positive energy)"
    assert (
        combined_preg_lact > result_gest_only.pregnancy_energy
    ), "Summed preg+lact must exceed gestation-only (lactation adds positive energy)"


# ── Test 2: combined state dispatch through animal.daily_routines ─────────────


@pytest.mark.unit
def test_combined_state_dispatch_reaches_calculator_without_error(mocker: MockerFixture) -> None:
    """
    A BEEF_COW in combined lactating+pregnant state must not raise AttributeError
    or ValueError when animal.daily_routines(time) is called once.

    Confirms the full dispatch chain (Animal → beef cow-calf daily update →
    BeefCowCalfRequirementsCalculator) is wired correctly without requiring
    the full SimulationEngine stack.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture for patching AnimalModuleReporter.report_cow_calf_performance.

    """
    _set_beef_animal_config()
    MilkProduction.set_milk_quality(
        fat_percent=AnimalConfig.milk_fat_percent,
        true_protein_percent=AnimalConfig.true_protein_percent,
        lactose_percent=AnimalModuleConstants.MILK_LACTOSE,
    )

    mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)

    time = _make_rufas_time_stub(datetime.datetime(2024, 1, 1))

    cow_args: BeefCowCalfValuesTypedDict = {
        "id": 1,
        "breed": "AN",
        "animal_type": AnimalType.BEEF_COW.value,
        "days_born": 730,
        "birth_weight": AnimalModuleConstants.BEEF_CALF_BIRTH_WEIGHT_KG,
        "body_weight": AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG,
        "mature_body_weight": AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG,
        "sex": "FEMALE",
        "times_calved": 2,
        "is_open": False,
        "days_since_calving": 60,
    }
    animal = Animal(cow_args, time)

    animal.days_in_pregnancy = 30
    animal.calf_at_side = mocker.MagicMock()
    animal.lactation_day = 60

    result = animal.daily_routines(time)

    assert isinstance(
        result, DailyRoutinesOutput
    ), f"daily_routines must return DailyRoutinesOutput; got {type(result)}"
