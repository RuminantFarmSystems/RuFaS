"""Tests for beef weaned calf hand-off — Step 8 (PR-C)."""

from collections.abc import Generator
from datetime import date
from unittest.mock import MagicMock

import pytest

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, BeefPostWeaningDestination, Sex
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.herd_manager import HerdManager

# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _restore_animal_config_state() -> Generator[None, None, None]:
    """Save and restore AnimalConfig beef weaning attributes around each test.

    Prevents test state from leaking into subsequent tests.

    Yields
    ------
    None
        Yields control to the test body; restores state on teardown.
    """
    saved_destination = AnimalConfig.beef_post_weaning_destination
    saved_weaning_age = AnimalConfig.beef_weaning_age_days
    saved_weaning_weight = AnimalConfig.beef_weaning_weight_kg
    saved_mature_cow_weight = AnimalConfig.beef_mature_cow_weight_kg
    yield
    AnimalConfig.beef_post_weaning_destination = saved_destination
    AnimalConfig.beef_weaning_age_days = saved_weaning_age
    AnimalConfig.beef_weaning_weight_kg = saved_weaning_weight
    AnimalConfig.beef_mature_cow_weight_kg = saved_mature_cow_weight


# ── helpers ───────────────────────────────────────────────────────────────────


def _mock_time(simulation_day: int = 207) -> MagicMock:
    """Build a minimal mock RufasTime for weaning tests.

    Parameters
    ----------
    simulation_day : int
        The simulation day counter.

    Returns
    -------
    MagicMock
        A mock with simulation_day, day_of_year, and current_date attributes.
    """
    t: MagicMock = MagicMock()
    t.simulation_day = simulation_day
    t.day_of_year = 207
    t.current_date = date(2025, 7, 26)
    return t


def _make_beef_calf(
    sex: Sex = Sex.FEMALE,
    days_born: int = 210,
    body_weight: float = 200.0,
) -> Animal:
    """Construct a minimal BEEF_CALF via Animal.__new__ with all weaning attrs pre-set.

    Parameters
    ----------
    sex : Sex
        Sex of the calf.
    days_born : int
        Age in simulation days (triggers weaning when >= beef_weaning_age_days).
    body_weight : float
        Body weight in kg.

    Returns
    -------
    Animal
        A minimally constructed BEEF_CALF instance.
    """
    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.BEEF_CALF
    animal.body_weight = body_weight
    animal.days_born = days_born
    animal.sex = sex
    animal.birth_weight = 35.0
    animal.mature_body_weight = 520.0
    animal.wean_weight = 0.0
    animal.dam = None
    animal.calf_at_side = None
    animal.events = AnimalEvents()
    animal.sold_at_day = None
    animal.om = MagicMock()
    # feedlot tracking defaults (required for all Animal instances)
    animal.days_on_feed = 0
    animal.entry_weight = 0.0
    animal.cumulative_dmi = 0.0
    animal.receiving_stress = False
    animal.step_up_phase = ""
    return animal


def _make_minimal_herd_manager() -> HerdManager:
    """Construct a minimal HerdManager via __new__ with only list attrs set.

    Returns
    -------
    HerdManager
        A minimally constructed HerdManager instance with all animal lists initialised.
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
    return hm


# ── Task 8.2 tests: _beef_weaning_event in animal.py ─────────────────────────


@pytest.mark.unit
def test_weaning_replacement_heifer_changes_type_and_clears_dam() -> None:
    """Weaned female calf with replacement_heifer destination must change to BEEF_HEIFER_REPLACEMENT.

    Verifies Task 8.2: _beef_weaning_event sets BEEF_HEIFER_REPLACEMENT, clears dam.calf_at_side,
    and returns LIFE_STAGE_CHANGED.
    """
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.REPLACEMENT_HEIFER
    AnimalConfig.beef_weaning_age_days = 207
    AnimalConfig.beef_weaning_weight_kg = None
    AnimalConfig.beef_mature_cow_weight_kg = AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG

    calf = _make_beef_calf(sex=Sex.FEMALE, days_born=210)

    dam: Animal = Animal.__new__(Animal)
    dam.animal_type = AnimalType.BEEF_COW
    dam.calf_at_side = calf
    calf.dam = dam

    time = _mock_time(simulation_day=210)
    status, newborn = calf._beef_calf_life_stage_update(time)

    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert newborn is None
    assert calf.animal_type == AnimalType.BEEF_HEIFER_REPLACEMENT
    assert dam.calf_at_side is None


@pytest.mark.unit
def test_weaning_direct_to_feedlot_changes_type_to_steer_or_heifer() -> None:
    """Male calf with direct_to_feedlot destination must become FEEDLOT_STEER.

    Verifies Task 8.2: _beef_weaning_event correctly assigns FEEDLOT_STEER for a male calf.
    """
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.DIRECT_TO_FEEDLOT
    AnimalConfig.beef_weaning_age_days = 207
    AnimalConfig.beef_weaning_weight_kg = None
    AnimalConfig.beef_mature_cow_weight_kg = AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG

    calf = _make_beef_calf(sex=Sex.MALE, days_born=210)

    time = _mock_time(simulation_day=210)
    status, newborn = calf._beef_calf_life_stage_update(time)

    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert newborn is None
    assert calf.animal_type == AnimalType.FEEDLOT_STEER


@pytest.mark.unit
def test_weaning_sell_sets_sold_at_day() -> None:
    """Calf with 'sell' destination must set sold_at_day and return SOLD.

    Verifies Task 8.2: _beef_weaning_event sets sold_at_day == simulation_day.
    """
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.SELL
    AnimalConfig.beef_weaning_age_days = 207
    AnimalConfig.beef_weaning_weight_kg = None
    AnimalConfig.beef_mature_cow_weight_kg = AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG

    calf = _make_beef_calf(sex=Sex.FEMALE, days_born=210)
    simulation_day = 210
    time = _mock_time(simulation_day=simulation_day)

    status, newborn = calf._beef_calf_life_stage_update(time)

    assert status == AnimalStatus.SOLD
    assert newborn is None
    assert calf.sold_at_day == simulation_day


@pytest.mark.unit
def test_weaning_unknown_destination_raises_value_error() -> None:
    """Unknown post-weaning destination must raise ValueError.

    Verifies Task 8.2: _beef_weaning_event raises ValueError for invalid destination strings.
    """
    AnimalConfig.beef_post_weaning_destination = "not_valid"  # type: ignore[assignment]
    AnimalConfig.beef_weaning_age_days = 207
    AnimalConfig.beef_weaning_weight_kg = None
    AnimalConfig.beef_mature_cow_weight_kg = AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG

    calf = _make_beef_calf(sex=Sex.FEMALE, days_born=210)
    time = _mock_time(simulation_day=210)

    with pytest.raises(ValueError, match="Unknown beef_post_weaning_destination"):
        calf._beef_calf_life_stage_update(time)


# ── Task 8.1 tests: HerdManager list-sync methods ────────────────────────────


@pytest.mark.unit
def test_weaning_animal_type_change_syncs_herd_manager_lists() -> None:
    """_remove_animal_from_current_array + _add_animal_to_new_array must sync BEEF_CALF → BEEF_HEIFER_REPLACEMENT.

    Verifies after weaning a BEEF_CALF becomes BEEF_HEIFER_REPLACEMENT;
    the HerdManager lists must be updated accordingly.
    """
    hm = _make_minimal_herd_manager()
    calf = _make_beef_calf(sex=Sex.FEMALE, days_born=210)
    hm.beef_calves = [calf]

    hm._remove_animal_from_current_array(calf)
    assert calf not in hm.beef_calves

    calf.animal_type = AnimalType.BEEF_HEIFER_REPLACEMENT
    hm._add_animal_to_new_array(calf)
    assert calf in hm.beef_replacement_heifers


@pytest.mark.unit
def test_heifer_replacement_promotion_to_cow_syncs_lists() -> None:
    """_remove_animal_from_current_array + _add_animal_to_new_array must sync BEEF_HEIFER_REPLACEMENT → BEEF_COW.

    Verifies Task 8.1: a replacement heifer promoted to cow is moved from
    beef_replacement_heifers to beef_cows correctly.
    """
    hm = _make_minimal_herd_manager()
    heifer = _make_beef_calf(sex=Sex.FEMALE, days_born=800)
    heifer.animal_type = AnimalType.BEEF_HEIFER_REPLACEMENT
    hm.beef_replacement_heifers = [heifer]

    hm._remove_animal_from_current_array(heifer)
    assert heifer not in hm.beef_replacement_heifers

    heifer.animal_type = AnimalType.BEEF_COW
    hm._add_animal_to_new_array(heifer)
    assert heifer in hm.beef_cows


# ── FIX 1 + FIX 6 regression tests (PR #35 round 2) ─────────────────────────


@pytest.mark.unit
def test_weaning_replacement_heifer_male_calf_sells() -> None:
    """Male calf with REPLACEMENT_HEIFER destination sells at weaning instead of raising ValueError.

    Verifies FIX 1: male calves cannot become replacement heifers; they route to
    SOLD so the simulation continues rather than crashing.
    """
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.REPLACEMENT_HEIFER
    AnimalConfig.beef_weaning_age_days = 207
    AnimalConfig.beef_weaning_weight_kg = None
    AnimalConfig.beef_mature_cow_weight_kg = AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG

    calf = _make_beef_calf(sex=Sex.MALE, days_born=210)
    time = _mock_time(simulation_day=210)

    status, newborn = calf._beef_calf_life_stage_update(time)

    assert status == AnimalStatus.SOLD
    assert newborn is None
    assert calf.sold_at_day == 210


@pytest.mark.unit
def test_weaning_sets_wean_weight() -> None:
    """_beef_weaning_event captures wean_weight == body_weight at the moment of weaning.

    Verifies FIX 6: wean_weight is assigned before the destination branch so the
    reporter can read it regardless of the post-weaning path taken.
    """
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.SELL
    AnimalConfig.beef_weaning_age_days = 207
    AnimalConfig.beef_weaning_weight_kg = None
    AnimalConfig.beef_mature_cow_weight_kg = AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG

    calf = _make_beef_calf(sex=Sex.FEMALE, days_born=210, body_weight=185.5)
    time = _mock_time(simulation_day=210)

    calf._beef_calf_life_stage_update(time)

    assert calf.wean_weight == 185.5
