"""730-day integration test: beef cow-calf herd lifecycle (Task 10, PR-D).

Drives HerdManager._process_daily_herd_updates() directly — no SimulationEngine
field/manure/feed_storage setup required. Exercises the real reproduction state
machine, life-stage transitions, list membership sync, and reporter calls added
across Steps 4-8.

Scope (Option B):
  - Breeding season start = day 90 of each year.
  - All 80 cows open at simulation start (days_in_pregnancy = 0).
  - First calving ~day 373, first weaning ~day 580.
  - Second breeding season active days 455-518.
  - Second calving falls outside 730-day window (documented in
    docs/beef_module/cow_calf/README.md).
"""

import datetime
from typing import Any, Generator

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_herd_updates import DailyHerdUpdates
from RUFAS.biophysical.animal.data_types.herd_statistics import HerdStatistics
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.rufas_time import RufasTime

# ── Number of exposed cows (matches config below) ─────────────────────────────
_NUM_COWS: int = 80

# ── Beef config dict passed to mock InputManager ──────────────────────────────
_BEEF_CONFIG: dict[str, object] = {
    "num_cows": _NUM_COWS,
    "num_replacement_heifers": 15,
    "num_bulls": 3,
    "mature_cow_weight_kg": 520.0,
    "breed": "AN",
    "calf_birth_weight_kg": 40.0,
}

_BEEF_TYPES = [
    AnimalType.BEEF_COW,
    AnimalType.BEEF_HEIFER_REPLACEMENT,
    AnimalType.BEEF_CALF,
    AnimalType.BEEF_BULL,
]


# ── Autouse fixture: save/restore AnimalConfig beef class attributes ──────────


@pytest.fixture(autouse=True)
def _restore_animal_config() -> Generator[None, None, None]:
    """Save and restore all AnimalConfig beef class attributes after each test."""
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


# ── Autouse fixture: save/restore RationManager beef ration class attributes ──


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


# ── Autouse fixture: save/restore MilkProduction class attributes ─────────────


@pytest.fixture(autouse=True)
def _restore_milk_production() -> Generator[None, None, None]:
    """Save and restore MilkProduction class-level quality attrs after each test."""
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


def _make_rufas_time(start: datetime.datetime) -> RufasTime:
    """
    Create a RufasTime bypassing its normal __init__ (which needs InputManager).

    Parameters
    ----------
    start : datetime.datetime
        Simulation start date; used for start_date, end_date, and current_date.

    Returns
    -------
    RufasTime
        A fully usable RufasTime whose simulation_day and day_of_year properties
        are driven by current_date and start_date.

    """
    time: RufasTime = RufasTime.__new__(RufasTime)
    time.start_date = start
    time.end_date = start + datetime.timedelta(days=730)
    time.current_date = start
    return time


# ── Helper: build HerdManager stub without calling HerdManager.__init__ ───────


def _make_herd_manager(
    beef_cows: list[Any],
    beef_replacement_heifers: list[Any],
    beef_calves: list[Any],
    beef_bulls: list[Any],
) -> HerdManager:
    """
    Construct a HerdManager via __new__ and manually assign all required attributes.

    Parameters
    ----------
    beef_cows : list
        Initial list of beef cow Animal objects.
    beef_replacement_heifers : list
        Initial list of replacement heifer Animal objects.
    beef_calves : list
        Initial beef calf list (empty at simulation start).
    beef_bulls : list
        Initial list of bull Animal objects.

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
    hm.beef_cows = beef_cows
    hm.beef_replacement_heifers = beef_replacement_heifers
    hm.beef_calves = beef_calves
    hm.beef_bulls = beef_bulls
    hm.herd_statistics = HerdStatistics()
    hm.herd_reproduction_statistics = HerdReproductionStatistics()
    return hm


# ── Helper: count CALF_WEANED events on a list of animals ────────────────────


def _count_calf_weaned_events(animal: Any) -> int:
    """
    Count CALF_WEANED events recorded on a single animal.

    Parameters
    ----------
    animal : Animal
        Any Animal instance with an ``events`` attribute.

    Returns
    -------
    int
        Total number of CALF_WEANED event strings recorded across all days.

    """
    if not hasattr(animal, "events") or animal.events is None:
        return 0
    return sum(descs.count(animal_constants.CALF_WEANED) for descs in animal.events.events.values())


# ── Helper: apply herd structure updates after each daily step ────────────────


def _apply_daily_structure_updates(hm: HerdManager, daily_updates: DailyHerdUpdates) -> None:
    """
    Apply herd membership changes returned by _process_daily_herd_updates.

    Skips pen/feed allocation (not set up in the integration stub).

    Parameters
    ----------
    hm : HerdManager
        The herd manager stub whose list attributes are modified in place.
    daily_updates : DailyHerdUpdates
        The updates object returned by _process_daily_herd_updates.

    """
    for newborn_calf in daily_updates.newborn_calves:
        hm.beef_calves.append(newborn_calf)
    for animal in daily_updates.graduated_animals:
        hm._remove_animal_from_current_array(animal)
        hm._add_animal_to_new_array(animal)
    for animal in daily_updates.removed_animals:
        hm._remove_animal_from_current_array(animal)


# ── Helper: assert animals_by_type has 4 distinct non-overlapping beef lists ──


def _assert_animals_by_type_distinct(label: str, hm: HerdManager) -> None:
    """
    Assert that animals_by_type returns 4 distinct, non-overlapping beef type lists.

    Parameters
    ----------
    label : str
        Human-readable label (e.g. "day365") for assertion failure messages.
    hm : HerdManager
        The herd manager whose animals_by_type property is exercised.

    """
    abt = hm.animals_by_type
    for bt in _BEEF_TYPES:
        assert bt in abt, f"{bt.name} missing from animals_by_type at {label}"
    assert abt[AnimalType.BEEF_COW] is not abt[AnimalType.BEEF_HEIFER_REPLACEMENT]
    assert abt[AnimalType.BEEF_COW] is not abt[AnimalType.BEEF_CALF]
    assert abt[AnimalType.BEEF_COW] is not abt[AnimalType.BEEF_BULL]
    assert abt[AnimalType.BEEF_HEIFER_REPLACEMENT] is not abt[AnimalType.BEEF_CALF]
    assert abt[AnimalType.BEEF_HEIFER_REPLACEMENT] is not abt[AnimalType.BEEF_BULL]
    assert abt[AnimalType.BEEF_CALF] is not abt[AnimalType.BEEF_BULL]
    cow_ids = {a.id for a in abt[AnimalType.BEEF_COW]}
    heifer_ids = {a.id for a in abt[AnimalType.BEEF_HEIFER_REPLACEMENT]}
    calf_ids = {a.id for a in abt[AnimalType.BEEF_CALF]}
    bull_ids = {a.id for a in abt[AnimalType.BEEF_BULL]}
    assert cow_ids.isdisjoint(heifer_ids), f"BEEF_COW/BEEF_HEIFER_REPLACEMENT overlap at {label}"
    assert cow_ids.isdisjoint(calf_ids), f"BEEF_COW/BEEF_CALF overlap at {label}"
    assert cow_ids.isdisjoint(bull_ids), f"BEEF_COW/BEEF_BULL overlap at {label}"
    assert heifer_ids.isdisjoint(calf_ids), f"BEEF_HEIFER_REPLACEMENT/BEEF_CALF overlap at {label}"
    assert heifer_ids.isdisjoint(bull_ids), f"BEEF_HEIFER_REPLACEMENT/BEEF_BULL overlap at {label}"


# ── Post-loop assertion helpers ───────────────────────────────────────────────


def _assert_calf_crop_weaned(hm: HerdManager, weaned_calf_ids: set[int]) -> None:
    """
    Assert that total calves weaned (sold + in-herd) meets the 70% threshold.

    Parameters
    ----------
    hm : HerdManager
        Herd manager stub after 730 days.
    weaned_calf_ids : set[int]
        IDs of calves that triggered a CALF_WEANED event and were removed (sold).

    """
    all_beef = [*hm.beef_cows, *hm.beef_replacement_heifers, *hm.beef_calves, *hm.beef_bulls]
    still_in_herd_weaned = sum(1 for a in all_beef if _count_calf_weaned_events(a) > 0)
    total_weaned = len(weaned_calf_ids) + still_in_herd_weaned
    min_weaned = int(0.70 * _NUM_COWS)
    assert total_weaned >= min_weaned, (
        f"Calf crop weaned {total_weaned} "
        f"(sold={len(weaned_calf_ids)}, in-herd={still_in_herd_weaned}) "
        f"< 70% threshold {min_weaned} (exposed cows={_NUM_COWS})"
    )


def _assert_gestation_invariant(hm: HerdManager) -> None:
    """
    Assert no cow's gestation exceeds the max length without a calf_at_side.

    Parameters
    ----------
    hm : HerdManager
        Herd manager stub after 730 days.

    """
    gestation_max = AnimalModuleConstants.BEEF_GESTATION_LENGTH_DAYS
    for cow in hm.beef_cows:
        overdue_and_no_calf = cow.days_in_pregnancy > gestation_max and cow.calf_at_side is None
        assert (
            not overdue_and_no_calf
        ), f"Cow {cow.id} days_in_pregnancy={cow.days_in_pregnancy} > {gestation_max} without calf_at_side"


def _assert_weaning_and_bcs(hm: HerdManager, weaned_calf_ids: set[int]) -> None:
    """
    Assert calves in herd have ≤1 weaning event, sold calves absent, BCS in range.

    Parameters
    ----------
    hm : HerdManager
        Herd manager stub after 730 days.
    weaned_calf_ids : set[int]
        IDs of calves that triggered a CALF_WEANED event and were removed (sold).

    """
    for calf in hm.beef_calves:
        count = _count_calf_weaned_events(calf)
        assert count <= 1, f"Calf {calf.id} in beef_calves has {count} CALF_WEANED events"
    current_calf_ids = {c.id for c in hm.beef_calves}
    for calf_id in weaned_calf_ids:
        assert calf_id not in current_calf_ids, f"Weaned calf {calf_id} still in beef_calves"
    for cow in hm.beef_cows:
        bcs = cow.body_condition_score_9
        assert 1.0 <= bcs <= 9.0, f"Cow {cow.id} BCS={bcs} outside [1.0, 9.0]"


def _assert_attr_access(hm: HerdManager) -> None:
    """
    Assert milk_production and feedlot attrs accessible on all beef animals without error.

    Parameters
    ----------
    hm : HerdManager
        Herd manager stub after 730 days.

    """
    all_beef = [*hm.beef_cows, *hm.beef_replacement_heifers, *hm.beef_calves, *hm.beef_bulls]
    for animal in all_beef:
        try:
            _ = animal.milk_production
        except AttributeError as exc:
            pytest.fail(f"Beef animal {animal.id} ({animal.animal_type}) AttributeError: {exc}")
        try:
            _ = animal.days_on_feed
            _ = animal.entry_weight
        except AttributeError as exc:
            pytest.fail(f"Beef animal {animal.id} AttributeError on feedlot attr: {exc}")


def _assert_heifer_open_if_underweight(hm: HerdManager) -> None:
    """
    Assert underweight heifers remain open (is_open=True) at end of simulation.

    Parameters
    ----------
    hm : HerdManager
        Herd manager stub after 730 days.

    """
    weight_threshold = (
        AnimalConfig.beef_mature_cow_weight_kg * AnimalModuleConstants.BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE
    )
    for heifer in hm.beef_replacement_heifers:
        if heifer.body_weight < weight_threshold:
            assert heifer.is_open, (
                f"Underweight heifer {heifer.id} (bw={heifer.body_weight:.1f} < "
                f"{weight_threshold:.1f}) should remain is_open=True"
            )


def _assert_deaths_keys_present(hm: HerdManager) -> None:
    """
    Assert all 4 beef AnimalType keys present in animals_deaths_by_stage.

    Parameters
    ----------
    hm : HerdManager
        Herd manager stub after 730 days.

    """
    for bt in _BEEF_TYPES:
        assert (
            bt in hm.herd_statistics.animals_deaths_by_stage
        ), f"AnimalType.{bt.name} missing from animals_deaths_by_stage"


def _assert_post_loop(hm: HerdManager, weaned_calf_ids: set[int]) -> None:
    """
    Dispatch all post-loop assertions (1-10) after the 730-day simulation.

    Parameters
    ----------
    hm : HerdManager
        The herd manager stub after 730 days.
    weaned_calf_ids : set[int]
        IDs of calves that triggered a CALF_WEANED event and were removed (sold).

    """
    _assert_calf_crop_weaned(hm, weaned_calf_ids)
    _assert_gestation_invariant(hm)
    _assert_weaning_and_bcs(hm, weaned_calf_ids)
    _assert_animals_by_type_distinct("day730-final", hm)
    _assert_attr_access(hm)
    _assert_heifer_open_if_underweight(hm)
    _assert_deaths_keys_present(hm)


# ── Main integration test ─────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.slow
def test_beef_herd_730_day_lifecycle(mocker: MockerFixture) -> None:
    """
    730-day integration test: one complete calving-weaning cycle + second breeding season.

    Option B scope (see Known gap in PLAN_beef-cowcalf-prd-validation.md):
    second calving falls outside 730-day window because initial_pregnancy_distribution
    is not yet implemented. Asserts 10 invariants defined in plan Section 10.2.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture for patching reporter calls.

    """
    MilkProduction.set_milk_quality(
        fat_percent=AnimalConfig.milk_fat_percent,
        true_protein_percent=AnimalConfig.true_protein_percent,
        lactose_percent=AnimalModuleConstants.MILK_LACTOSE,
    )

    AnimalConfig.beef_breeding_season_start_day = 90
    AnimalConfig.beef_breeding_season_length = AnimalModuleConstants.BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS
    AnimalConfig.beef_weaning_age_days = AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS
    AnimalConfig.beef_weaning_weight_kg = None
    AnimalConfig.beef_post_weaning_destination = "sell"
    AnimalConfig.beef_mature_cow_weight_kg = 520.0
    AnimalConfig.beef_cow_cull_rate_annual = AnimalModuleConstants.BEEF_ANNUAL_CULL_RATE

    hf: HerdFactory = HerdFactory.__new__(HerdFactory)
    mock_im = mocker.MagicMock()
    mock_im.get_data.return_value = _BEEF_CONFIG
    hf.im = mock_im
    start_dt = datetime.datetime(2024, 1, 1)
    hf.time = _make_rufas_time(start_dt)

    all_animals = hf._initialize_beef_cow_calf_herd()
    beef_cows = [a for a in all_animals if a.animal_type == AnimalType.BEEF_COW]
    beef_heifers = [a for a in all_animals if a.animal_type == AnimalType.BEEF_HEIFER_REPLACEMENT]
    beef_bulls = [a for a in all_animals if a.animal_type == AnimalType.BEEF_BULL]
    assert len(beef_cows) == _NUM_COWS

    hm = _make_herd_manager(beef_cows, beef_heifers, [], beef_bulls)
    time = _make_rufas_time(start_dt)

    mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)

    weaned_calf_ids: set[int] = set()

    for _day in range(730):
        time.current_date += datetime.timedelta(days=1)

        # Assertion 10 (inline): no KeyError on animals_deaths_by_stage
        for bt in _BEEF_TYPES:
            _ = hm.herd_statistics.animals_deaths_by_stage[bt]
        hm.herd_statistics.reset_daily_stats()

        daily_updates = hm._process_daily_herd_updates(time)

        # Track weanings before removal (for Assertions 1, 3, 4)
        for animal in daily_updates.removed_animals:
            if _count_calf_weaned_events(animal) > 0:
                weaned_calf_ids.add(animal.id)

        # Assertion 4 (inline): weaned calves must not remain in beef_calves
        weaned_removed_ids = {a.id for a in daily_updates.removed_animals if _count_calf_weaned_events(a) > 0}
        _apply_daily_structure_updates(hm, daily_updates)
        current_calf_ids = {c.id for c in hm.beef_calves}
        for calf_id in weaned_removed_ids:
            assert (
                calf_id not in current_calf_ids
            ), f"Day {time.simulation_day}: Weaned calf {calf_id} still in beef_calves"

        # Assertion 6 (inline): distinct non-overlapping lists at days 365 and 730
        sim_day = time.simulation_day
        if sim_day in (365, 730):
            _assert_animals_by_type_distinct(f"day{sim_day}", hm)

    _assert_post_loop(hm, weaned_calf_ids)
