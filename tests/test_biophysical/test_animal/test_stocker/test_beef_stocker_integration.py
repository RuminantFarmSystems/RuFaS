"""200-day integration test: beef stocker/backgrounding lifecycle.

Drives HerdManager._process_daily_herd_updates() directly — no SimulationEngine
field/manure/feed_storage setup required. Exercises real stocker daily growth,
weight-based exit, cohort-list separation, and reporter firing from Steps 4-7.

Scenario: 50 Angus steers + 20 Angus heifers, entry weight 240 kg, target ADG
0.80 kg/d, exit weight 350 kg, max days 210. Theoretical exit ≈ day 138
(= (350 - 240) / 0.80). All 70 animals exit within 200 days.
"""

from __future__ import annotations

import copy
import datetime
from typing import Generator

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_enums import StockerDietSystem
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_herd_updates import DailyHerdUpdates
from RUFAS.biophysical.animal.data_types.herd_statistics import HerdStatistics
from RUFAS.biophysical.animal.calf_retention_policy import CalfRetentionPolicy
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.rufas_time import RufasTime

# ── Scenario parameters ───────────────────────────────────────────────────────
_N_STEERS: int = 50
_N_HEIFERS: int = 20
_ENTRY_WEIGHT_KG: float = 240.0
_EXIT_WEIGHT_KG: float = 350.0
_MAX_DAYS: int = 210
_TARGET_ADG: float = 0.80
_SIMULATION_DAYS: int = 200
_MATURE_BW_KG: float = 520.0
_N_TOTAL: int = _N_STEERS + _N_HEIFERS

# Performance bounds from plan §9
_ADG_MIN: float = 0.65
_ADG_MAX: float = 0.95
_DAYS_MIN: int = 110
_DAYS_MAX: int = 180

# Checkpoint days for mid-run cohort-list distinctness checks.
# Days 50 and 100 precede the expected exit day (~138); 150 and 200 follow.
_CHECKPOINT_DAYS: tuple[int, ...] = (50, 100, 150, _SIMULATION_DAYS)

_STOCKER_CONFIG: dict[str, object] = {
    "num_steers": _N_STEERS,
    "num_heifers": _N_HEIFERS,
    "entry_weight_kg": _ENTRY_WEIGHT_KG,
    "breed": "AN",
}


# ── Autouse fixtures ──────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _restore_stocker_config() -> Generator[None, None, None]:
    """Save and restore AnimalConfig stocker and beef class attributes after each test."""
    saved_entry = AnimalConfig.stocker_entry_weight
    saved_exit = AnimalConfig.stocker_exit_weight
    saved_days = AnimalConfig.stocker_max_days
    saved_adg = AnimalConfig.stocker_target_adg
    saved_diet = AnimalConfig.stocker_diet_system
    saved_mature = AnimalConfig.beef_mature_cow_weight_kg
    saved_genetics = AnimalConfig.simulate_genetics
    yield
    AnimalConfig.stocker_entry_weight = saved_entry
    AnimalConfig.stocker_exit_weight = saved_exit
    AnimalConfig.stocker_max_days = saved_days
    AnimalConfig.stocker_target_adg = saved_adg
    AnimalConfig.stocker_diet_system = saved_diet
    AnimalConfig.beef_mature_cow_weight_kg = saved_mature
    AnimalConfig.simulate_genetics = saved_genetics


@pytest.fixture(autouse=True)
def _restore_ration_manager_stocker() -> Generator[None, None, None]:
    """Save and restore RationManager stocker ration ClassVars after each test."""
    saved_pasture = copy.deepcopy(RationManager.beef_stocker_pasture_ration)
    saved_drylot = copy.deepcopy(RationManager.beef_stocker_drylot_ration)
    yield
    RationManager.beef_stocker_pasture_ration = saved_pasture
    RationManager.beef_stocker_drylot_ration = saved_drylot


@pytest.fixture(autouse=True)
def _restore_herd_factory_stocker() -> Generator[None, None, None]:
    """Save and restore HerdFactory.beef_stocker_animals ClassVar after each test."""
    saved = copy.deepcopy(HerdFactory.beef_stocker_animals)
    yield
    HerdFactory.beef_stocker_animals = saved


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_rufas_time(start: datetime.datetime) -> RufasTime:
    """
    Create a RufasTime bypassing its normal __init__ (requires InputManager).

    Parameters
    ----------
    start : datetime.datetime
        Simulation start date; used for start_date, end_date, and current_date.

    Returns
    -------
    RufasTime
        A minimal RufasTime whose simulation_day property is driven by
        current_date and start_date.

    """
    time: RufasTime = RufasTime.__new__(RufasTime)
    time.start_date = start
    time.end_date = start + datetime.timedelta(days=_SIMULATION_DAYS)
    time.current_date = start
    return time


def _make_stocker_herd_manager(
    steers: list[Animal],
    heifers: list[Animal],
) -> HerdManager:
    """
    Construct a HerdManager via __new__ with all required attributes set.

    All dairy and beef cow-calf lists are empty; stocker lists are populated with
    the provided animals.

    Parameters
    ----------
    steers : list[Animal]
        Initial stocker steer Animals.
    heifers : list[Animal]
        Initial stocker heifer Animals.

    Returns
    -------
    HerdManager
        Stub instance ready for _process_daily_herd_updates calls.

    """
    hm: HerdManager = HerdManager.__new__(HerdManager)
    hm.calves = []
    hm.heiferIs = []
    hm.heiferIIs = []
    hm.heiferIIIs = []
    hm.cows = []
    hm.feedlot_animals = []
    hm.beef_cows = []
    hm.beef_replacement_heifers = []
    hm.beef_calves = []
    hm.beef_bulls = []
    hm.beef_stocker_steers = steers
    hm.beef_stocker_heifers = heifers
    hm.herd_statistics = HerdStatistics()
    hm.herd_reproduction_statistics = HerdReproductionStatistics()
    hm.daily_herd_reproduction_statistics = HerdReproductionStatistics()
    hm.calf_retention_policy = CalfRetentionPolicy()
    return hm


def _build_stocker_animals(mocker: MockerFixture) -> tuple[list[Animal], list[Animal]]:
    """
    Build stocker animals via HerdFactory._initialize_beef_stocker_herd with a mocked IM.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture for mocking InputManager.

    Returns
    -------
    tuple[list[Animal], list[Animal]]
        (steers, heifers) as two separate lists built from real Animal constructor calls.

    """
    hf: HerdFactory = HerdFactory.__new__(HerdFactory)
    mock_im = mocker.MagicMock()
    mock_im.get_data.return_value = _STOCKER_CONFIG
    hf.im = mock_im
    start_dt = datetime.datetime(2024, 1, 1)
    hf.time = _make_rufas_time(start_dt)

    all_animals = hf._initialize_beef_stocker_herd()
    steers = [a for a in all_animals if a.animal_type == AnimalType.BEEF_STOCKER_STEER]
    heifers = [a for a in all_animals if a.animal_type == AnimalType.BEEF_STOCKER_HEIFER]
    return steers, heifers


def _apply_daily_structure_updates(hm: HerdManager, daily_updates: DailyHerdUpdates) -> None:
    """
    Apply herd membership changes returned by _process_daily_herd_updates.

    Stocker exits appear in graduated_animals (LIFE_STAGE_CHANGED → feedlot type).
    Pen/feed allocation is skipped (not set up in this integration stub).

    Parameters
    ----------
    hm : HerdManager
        Herd manager stub modified in place.
    daily_updates : DailyHerdUpdates
        Updates returned by _process_daily_herd_updates.

    """
    for animal in daily_updates.graduated_animals:
        hm._remove_animal_from_current_array(animal)
        hm._add_animal_to_new_array(animal)
    for animal in daily_updates.removed_animals:
        hm._remove_animal_from_current_array(animal)


def _assert_stocker_cohorts_distinct(label: str, hm: HerdManager) -> None:
    """
    Assert that stocker steer and heifer cohort lists are distinct and non-overlapping.

    Checks list object identity, ID set disjointness, and per-animal type consistency.

    Parameters
    ----------
    label : str
        Human-readable label for assertion failure messages (e.g. "day50").
    hm : HerdManager
        Herd manager whose stocker lists are checked.

    """
    assert (
        hm.beef_stocker_steers is not hm.beef_stocker_heifers
    ), f"{label}: beef_stocker_steers and beef_stocker_heifers must be distinct list objects"
    steer_ids = {a.id for a in hm.beef_stocker_steers}
    heifer_ids = {a.id for a in hm.beef_stocker_heifers}
    assert steer_ids.isdisjoint(
        heifer_ids
    ), f"{label}: steer and heifer cohorts overlap — shared IDs: {steer_ids & heifer_ids}"
    for a in hm.beef_stocker_steers:
        assert a.animal_type is AnimalType.BEEF_STOCKER_STEER, (
            f"{label}: animal {a.id} in beef_stocker_steers has type {a.animal_type} "
            f"(expected BEEF_STOCKER_STEER — exited animals must be removed before checkpoint)"
        )
    for a in hm.beef_stocker_heifers:
        assert a.animal_type is AnimalType.BEEF_STOCKER_HEIFER, (
            f"{label}: animal {a.id} in beef_stocker_heifers has type {a.animal_type} "
            f"(expected BEEF_STOCKER_HEIFER — exited animals must be removed before checkpoint)"
        )


# ── Main integration test ─────────────────────────────────────────────────────


@pytest.mark.integration
def test_stocker_200_day_lifecycle(mocker: MockerFixture) -> None:
    """
    200-day integration test: stocker weight-based exit, cohort-list integrity, reporter accuracy.

    Drives _process_daily_herd_updates with 50 steers + 20 heifers for 200 days. Exit
    weight 350 kg at ADG 0.80 kg/d yields a theoretical exit day of 138 for all animals.
    Validates 5 requirements from plan §9: all-exit, performance bounds, cohort distinctness,
    reporter call count, and stocker attribute integrity.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture for patching AnimalModuleReporter.

    """
    AnimalConfig.stocker_entry_weight = _ENTRY_WEIGHT_KG
    AnimalConfig.stocker_exit_weight = _EXIT_WEIGHT_KG
    AnimalConfig.stocker_max_days = _MAX_DAYS
    AnimalConfig.stocker_target_adg = _TARGET_ADG
    AnimalConfig.stocker_diet_system = StockerDietSystem.PASTURE
    AnimalConfig.beef_mature_cow_weight_kg = _MATURE_BW_KG
    AnimalConfig.simulate_genetics = False

    steers, heifers = _build_stocker_animals(mocker)
    assert len(steers) == _N_STEERS, f"Expected {_N_STEERS} steers, got {len(steers)}"
    assert len(heifers) == _N_HEIFERS, f"Expected {_N_HEIFERS} heifers, got {len(heifers)}"

    hm = _make_stocker_herd_manager(steers, heifers)
    time = _make_rufas_time(datetime.datetime(2024, 1, 1))

    reporter_spy = mocker.patch.object(AnimalModuleReporter, "report_stocker_performance", return_value=None)

    total_exited: int = 0

    for _day in range(_SIMULATION_DAYS):
        time.current_date += datetime.timedelta(days=1)
        hm.herd_statistics.reset_daily_stats()

        daily_updates = hm._process_daily_herd_updates(time)
        total_exited += len(daily_updates.graduated_animals)

        _apply_daily_structure_updates(hm, daily_updates)

        sim_day = time.simulation_day
        if sim_day in _CHECKPOINT_DAYS:
            _assert_stocker_cohorts_distinct(f"day{sim_day}", hm)

    # ── Post-loop assertions ──────────────────────────────────────────────────

    # Assertion 1: all 70 animals exited within 200 days
    assert total_exited == _N_TOTAL, (
        f"Expected all {_N_TOTAL} stocker animals to exit within {_SIMULATION_DAYS} days, "
        f"but only {total_exited} exited"
    )
    assert (
        len(hm.beef_stocker_steers) == 0
    ), f"beef_stocker_steers not empty after run: {len(hm.beef_stocker_steers)} remaining"
    assert (
        len(hm.beef_stocker_heifers) == 0
    ), f"beef_stocker_heifers not empty after run: {len(hm.beef_stocker_heifers)} remaining"

    # Assertion 2: all exited animals transitioned to feedlot_animals
    assert (
        len(hm.feedlot_animals) == _N_TOTAL
    ), f"Expected {_N_TOTAL} animals in feedlot_animals after exit, got {len(hm.feedlot_animals)}"

    # Assertion 3: performance metrics within plan §9 bounds
    exited = hm.feedlot_animals
    days_values = [a.days_in_stocker for a in exited]
    mean_days: float = sum(days_values) / len(days_values)
    assert (
        _DAYS_MIN <= mean_days <= _DAYS_MAX
    ), f"Mean days in stocker {mean_days:.1f} outside expected range [{_DAYS_MIN}, {_DAYS_MAX}]"

    adg_values = [(a.body_weight - a.stocker_entry_weight) / a.days_in_stocker for a in exited if a.days_in_stocker > 0]
    mean_adg: float = sum(adg_values) / len(adg_values)
    assert (
        _ADG_MIN <= mean_adg <= _ADG_MAX
    ), f"Mean ADG {mean_adg:.3f} kg/d outside expected range [{_ADG_MIN}, {_ADG_MAX}]"

    # Assertion 4: reporter called exactly once per exiting animal
    assert reporter_spy.call_count == _N_TOTAL, (
        f"report_stocker_performance called {reporter_spy.call_count} times, "
        f"expected {_N_TOTAL} (one per exiting animal)"
    )

    # Assertion 5: stocker path taken, no cross-type attribute contamination
    for animal in exited:
        assert animal.days_in_stocker > 0, f"Animal {animal.id}: days_in_stocker == 0 — stocker path not taken"
        assert animal.stocker_entry_weight == pytest.approx(_ENTRY_WEIGHT_KG), (
            f"Animal {animal.id}: stocker_entry_weight {animal.stocker_entry_weight} " f"!= expected {_ENTRY_WEIGHT_KG}"
        )
        assert animal.days_in_milk == 0, (
            f"Animal {animal.id}: days_in_milk {animal.days_in_milk} != 0 "
            f"(dairy path must not be taken for stocker animals)"
        )
        assert animal.days_in_pregnancy == 0, (
            f"Animal {animal.id}: days_in_pregnancy {animal.days_in_pregnancy} != 0 "
            f"(reproduction path must not be taken for stocker animals)"
        )
