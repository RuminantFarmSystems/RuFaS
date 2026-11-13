"""Tests for Step 6: Stocker weaning hand-off (BEEF_CALF → BEEF_STOCKER_STEER/HEIFER).

Covers _beef_weaning_event routing to STOCKER destination, sex-based animal_type
assignment, and _initialize_stocker_animal integration via _beef_calf_life_stage_update.

HerdManager list membership update is Step 7 scope — see TODO in the STOCKER arm
of _beef_weaning_event and in test_stocker_entry_exit_path_end_to_end below.

RED before Step 6 implementation; GREEN after.
"""

from __future__ import annotations

from typing import Generator
from unittest.mock import MagicMock

import pytest

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_enums import (
    AnimalStatus,
    BeefPostWeaningDestination,
    Breed,
    Sex,
)
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_WEAN_BODY_WEIGHT: float = 185.0  # kg — representative wean weight

# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def _mock_time(simulation_day: int = 200) -> MagicMock:
    """Return a minimal time mock with simulation_day set."""
    t: MagicMock = MagicMock()
    t.simulation_day = simulation_day
    return t


def _make_weaning_calf(sex: Sex = Sex.MALE, body_weight: float = _WEAN_BODY_WEIGHT) -> Animal:
    """Construct a BEEF_CALF at weaning age via Animal.__new__.

    Parameters
    ----------
    sex : Sex
        MALE or FEMALE — determines post-weaning stocker type.
    body_weight : float
        Body weight in kg at time of weaning.

    Returns
    -------
    Animal
        Minimally constructed BEEF_CALF with days_born above weaning threshold.

    """
    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.BEEF_CALF
    animal.body_weight = body_weight
    animal.days_born = 999  # well above any configured weaning age
    animal.breed = Breed.AN
    animal.sex = sex
    animal.birth_weight = 35.0
    animal.mature_body_weight = 520.0
    animal.wean_weight = 0.0
    animal.body_condition_score_9 = 5.0
    animal.body_condition_score_5 = 3.0
    animal.dam = None
    animal.calf_at_side = None
    animal._future_cull_date = None
    animal._future_death_date = None
    animal.events = AnimalEvents()
    animal.sold_at_day = None
    animal.cull_reason = ""
    animal.om = MagicMock()
    animal.growth = MagicMock()
    animal.nutrition_supply = NutritionSupply.make_empty_nutrition_supply()
    animal.previous_nutrition_supply = None
    # feedlot tracking defaults — required on all Animal instances
    animal.days_on_feed = 0
    animal.entry_weight = 0.0
    animal.cumulative_dmi = 0.0
    animal.receiving_stress = False
    animal.step_up_phase = ""
    # stocker tracking defaults — set here so they exist before _initialize_stocker_animal
    # overwrites them; avoids AttributeError if any early guard reads them
    animal.days_in_stocker = 0
    animal.stocker_entry_weight = 0.0
    animal.stocker_cumulative_dmi = 0.0
    # dairy/cow-calf attrs required by base infrastructure methods
    animal._days_in_milk = 0
    animal._milk_production_output_days_in_milk = 0
    animal.milk_production = MagicMock()
    animal._reproduction = MagicMock()
    animal._reproduction.gestation_length = 285
    return animal


# ---------------------------------------------------------------------------
# Autouse fixture: restore AnimalConfig ClassVar state after every test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_animal_config() -> Generator[None, None, None]:
    saved_destination = AnimalConfig.beef_post_weaning_destination
    saved_genetics = AnimalConfig.simulate_genetics
    AnimalConfig.simulate_genetics = False
    yield
    AnimalConfig.beef_post_weaning_destination = saved_destination
    AnimalConfig.simulate_genetics = saved_genetics


# ---------------------------------------------------------------------------
# Group 1: STOCKER destination routing via _beef_weaning_event
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_weaning_male_sets_beef_stocker_steer_type() -> None:
    """Male calf weaned to STOCKER destination must become BEEF_STOCKER_STEER."""
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    animal._beef_weaning_event(_mock_time())
    assert animal.animal_type == AnimalType.BEEF_STOCKER_STEER


@pytest.mark.unit
def test_stocker_weaning_female_sets_beef_stocker_heifer_type() -> None:
    """Female calf weaned to STOCKER destination must become BEEF_STOCKER_HEIFER."""
    animal = _make_weaning_calf(sex=Sex.FEMALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    animal._beef_weaning_event(_mock_time())
    assert animal.animal_type == AnimalType.BEEF_STOCKER_HEIFER


@pytest.mark.unit
def test_stocker_weaning_returns_life_stage_changed_and_no_newborn() -> None:
    """STOCKER weaning must return (LIFE_STAGE_CHANGED, None)."""
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    status, newborn = animal._beef_weaning_event(_mock_time())
    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert newborn is None


@pytest.mark.unit
def test_stocker_weaning_male_sex_becomes_steer() -> None:
    """_initialize_stocker_animal must castrate males: Sex.MALE → Sex.STEER."""
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    animal._beef_weaning_event(_mock_time())
    assert animal.sex == Sex.STEER


@pytest.mark.unit
def test_stocker_weaning_female_sex_remains_female() -> None:
    """Female stocker calves retain Sex.FEMALE after _initialize_stocker_animal."""
    animal = _make_weaning_calf(sex=Sex.FEMALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    animal._beef_weaning_event(_mock_time())
    assert animal.sex == Sex.FEMALE


@pytest.mark.unit
def test_stocker_weaning_days_in_stocker_is_zero() -> None:
    """days_in_stocker must be 0 immediately after the weaning hand-off."""
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    animal._beef_weaning_event(_mock_time())
    assert animal.days_in_stocker == 0


@pytest.mark.unit
def test_stocker_weaning_entry_weight_equals_wean_body_weight() -> None:
    """stocker_entry_weight must equal the calf's body_weight at time of weaning."""
    animal = _make_weaning_calf(sex=Sex.MALE, body_weight=_WEAN_BODY_WEIGHT)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    animal._beef_weaning_event(_mock_time())
    assert animal.stocker_entry_weight == pytest.approx(_WEAN_BODY_WEIGHT)


@pytest.mark.unit
def test_stocker_weaning_mature_body_weight_from_config() -> None:
    """mature_body_weight after STOCKER hand-off must equal AnimalConfig.beef_mature_cow_weight_kg."""
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    animal._beef_weaning_event(_mock_time())
    assert animal.mature_body_weight == pytest.approx(AnimalConfig.beef_mature_cow_weight_kg)


@pytest.mark.unit
def test_stocker_weaning_calf_weaned_event_fired() -> None:
    """CALF_WEANED event must be recorded in animal.events on stocker weaning."""
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    animal._beef_weaning_event(_mock_time(simulation_day=200))
    assert animal.events.get_most_recent_date(animal_constants.CALF_WEANED) != -1


@pytest.mark.unit
def test_stocker_weaning_stocker_arrival_event_fired() -> None:
    """STOCKER_ARRIVAL event must be recorded in animal.events on stocker weaning."""
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    animal._beef_weaning_event(_mock_time(simulation_day=200))
    assert animal.events.get_most_recent_date(animal_constants.STOCKER_ARRIVAL) != -1


# ---------------------------------------------------------------------------
# Group 2: End-to-end via _beef_calf_life_stage_update
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_weaning_triggers_via_calf_life_stage_update_male() -> None:
    """_beef_calf_life_stage_update at days_born >= weaning_age routes male to BEEF_STOCKER_STEER."""
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    status, _ = animal._beef_calf_life_stage_update(_mock_time())
    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert animal.animal_type == AnimalType.BEEF_STOCKER_STEER


@pytest.mark.unit
def test_stocker_weaning_triggers_via_calf_life_stage_update_female() -> None:
    """_beef_calf_life_stage_update for a female routes to BEEF_STOCKER_HEIFER."""
    animal = _make_weaning_calf(sex=Sex.FEMALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER
    status, _ = animal._beef_calf_life_stage_update(_mock_time())
    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert animal.animal_type == AnimalType.BEEF_STOCKER_HEIFER


# ---------------------------------------------------------------------------
# Group 3: Enum-based dispatch — other destinations are unaffected
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_enum_member_exists_and_has_correct_value() -> None:
    """BeefPostWeaningDestination.STOCKER must exist as an enum member (not a raw string).

    Dispatch in _beef_weaning_event uses enum identity (`is`), not string equality.
    """
    assert BeefPostWeaningDestination.STOCKER is not None
    assert isinstance(BeefPostWeaningDestination.STOCKER, BeefPostWeaningDestination)
    assert BeefPostWeaningDestination.STOCKER.value == "stocker"


@pytest.mark.unit
def test_sell_destination_unaffected_by_stocker_arm() -> None:
    """SELL destination must still yield AnimalStatus.SOLD after the STOCKER arm is added."""
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.SELL
    status, _ = animal._beef_weaning_event(_mock_time())
    assert status == AnimalStatus.SOLD


@pytest.mark.unit
def test_direct_to_feedlot_destination_unaffected_by_stocker_arm() -> None:
    """DIRECT_TO_FEEDLOT must route male to FEEDLOT_STEER after the STOCKER arm is added."""
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.DIRECT_TO_FEEDLOT
    status, _ = animal._beef_weaning_event(_mock_time())
    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert animal.animal_type == AnimalType.FEEDLOT_STEER


# ---------------------------------------------------------------------------
# Group 4: Entry→exit path connectivity
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_entry_exit_path_end_to_end() -> None:
    """Wean into stocker then exit to feedlot via _stocker_life_stage_update.

    Confirms that the weaning entry path (Step 6) connects cleanly to the
    exit path built in Step 4.

    TODO (Step 7): assert that HerdManager list membership also updates when
    the stocker exits to feedlot — that assertion belongs in Step 7's test file.
    """
    animal = _make_weaning_calf(sex=Sex.MALE)
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.STOCKER

    # Step 1: wean calf into stocker program
    wean_status, _ = animal._beef_weaning_event(_mock_time(simulation_day=200))
    assert wean_status == AnimalStatus.LIFE_STAGE_CHANGED
    # capture into local var to avoid mypy type-narrowing the final assertion below
    stocker_type = animal.animal_type
    assert stocker_type == AnimalType.BEEF_STOCKER_STEER

    # Step 2: fast-forward body weight to stocker exit threshold
    animal.body_weight = AnimalConfig.stocker_exit_weight
    exit_status, _ = animal._stocker_life_stage_update(_mock_time(simulation_day=300))
    assert exit_status == AnimalStatus.LIFE_STAGE_CHANGED
    assert animal.animal_type == AnimalType.FEEDLOT_STEER
