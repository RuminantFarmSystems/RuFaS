"""Tests for beef cow-calf lifecycle (Step 4) — PR-B.

New-behaviour tests (L1–L19, L4b, L14b, B3) must FAIL (RED) before Step 4
is implemented and PASS (GREEN) after. Regression tests (L7, L16) must PASS
both before and after.
"""

import types
from collections.abc import Generator
from datetime import date
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, BeefPostWeaningDestination, Breed, Sex
from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics

# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_animal_config_state() -> Generator[None, None, None]:
    """Snapshot and restore AnimalConfig class state after each test."""
    original_attrs = {
        name: value
        for name, value in AnimalConfig.__dict__.items()
        if not name.startswith("__") and not isinstance(value, (types.FunctionType, classmethod, staticmethod))
    }
    original_names = set(original_attrs.keys())
    yield
    for name in list(AnimalConfig.__dict__.keys()):
        if name.startswith("__"):
            continue
        if isinstance(AnimalConfig.__dict__[name], (types.FunctionType, classmethod, staticmethod)):
            continue
        if name not in original_names:
            delattr(AnimalConfig, name)
    for name, value in original_attrs.items():
        setattr(AnimalConfig, name, value)


# ── helpers ──────────────────────────────────────────────────────────────────


def _mock_time(
    simulation_day: int = 100,
    day_of_year: int = 120,
    current_date: date = date(2025, 4, 30),
) -> MagicMock:
    """Build a minimal mock RufasTime for lifecycle tests.

    Parameters
    ----------
    simulation_day : int
        The simulation day counter.
    day_of_year : int
        Day of year (1-365). Default 120 places the date inside the default
        breeding season (start_day=90, length=63 → days 90-153).
    current_date : date
        Calendar date used in calving dict ``birth_date`` field.

    Returns
    -------
    MagicMock
        A mock with simulation_day, day_of_year, and current_date attributes.
    """
    t: MagicMock = MagicMock()
    t.simulation_day = simulation_day
    t.day_of_year = day_of_year
    t.current_date = current_date
    return t


def _make_beef_animal(
    animal_type: AnimalType = AnimalType.BEEF_COW,
    body_weight: float = 520.0,
    days_born: int = 730,
    breed: Breed = Breed.AN,
    sex: Sex = Sex.FEMALE,
    times_calved: int = 1,
    is_open: bool = True,
    days_since_calving: int = 100,
    days_in_pregnancy: int = 0,
    body_condition_score_9: float = 5.0,
    breeding_weight_event_fired: bool = False,
    lactation_day: int = 0,
) -> Animal:
    """Construct a minimal beef cow-calf animal via __new__ with all Step 4 attributes pre-set.

    Parameters
    ----------
    animal_type : AnimalType
        Beef animal type (BEEF_COW, BEEF_HEIFER_REPLACEMENT, BEEF_CALF, BEEF_BULL).
    body_weight : float
        Body weight in kg.
    days_born : int
        Age in simulation days.
    breed : Breed
        Animal breed.
    sex : Sex
        Animal sex.
    times_calved : int
        Number of times calved.
    is_open : bool
        Whether the animal is open (not pregnant).
    days_since_calving : int
        Days since last calving (drives postpartum anestrus guard).
    days_in_pregnancy : int
        Current gestation day counter.
    body_condition_score_9 : float
        Body condition on 1-9 NRC beef scale.
    breeding_weight_event_fired : bool
        Dedup guard for REPLACEMENT_HEIFER_REACHED_BREEDING_WEIGHT event.

    Returns
    -------
    Animal
        A minimally constructed Animal instance with all Step 4 attributes set.
    """
    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = animal_type
    animal.body_weight = body_weight
    animal.days_born = days_born
    animal.breed = breed
    animal.sex = sex
    animal.birth_weight = 35.0
    animal.mature_body_weight = 520.0
    animal.wean_weight = 0.0
    animal.body_condition_score_9 = body_condition_score_9
    animal.body_condition_score_5 = 3.0
    animal.times_calved = times_calved
    animal.is_open = is_open
    animal.days_since_calving = days_since_calving
    animal.days_in_breeding_season = None
    animal.calf_at_side = None
    animal.dam = None
    animal.lactation_day = lactation_day
    animal._breeding_weight_event_fired = breeding_weight_event_fired
    animal._days_in_pregnancy = days_in_pregnancy
    animal._future_cull_date = None
    animal._future_death_date = None
    animal.events = AnimalEvents()
    animal.sold_at_day = None
    animal.cull_reason = ""
    animal.om = MagicMock()
    # feedlot tracking defaults (required for all Animal instances)
    animal.days_on_feed = 0
    animal.entry_weight = 0.0
    animal.cumulative_dmi = 0.0
    animal.receiving_stress = False
    animal.step_up_phase = ""
    # private attributes needed by dairy life-stage and reproduction methods
    animal._days_in_milk = 0
    animal._milk_production_output_days_in_milk = 0
    animal.milk_production = MagicMock()
    animal._reproduction = MagicMock()
    animal._reproduction.gestation_length = 285
    return animal


def _event_fired(animal: Animal, event: str) -> bool:
    """Return True if the named event was recorded on the animal at any age."""
    return animal.events.get_most_recent_date(event) != -1


# ── L1–L3, L19: Construction tests ──────────────────────────────────────────


@pytest.mark.unit
def test_L1_beef_cow_constructs_without_error() -> None:
    """L1: BEEF_COW must construct without error; all new Step 4 attrs must be present.

    Verifies that _initialize_beef_cow_calf_animal is correctly wired into
    the __init__ dispatch map for AnimalType.BEEF_COW.
    """
    t = _mock_time()
    args = {
        "id": 1,
        "breed": "AN",
        "animal_type": AnimalType.BEEF_COW.value,
        "days_born": 730,
        "birth_weight": 35.0,
        "body_weight": 520.0,
        "mature_body_weight": 520.0,
        "sex": "FEMALE",
    }
    animal = Animal(args, t)  # type: ignore[arg-type]
    assert animal.animal_type == AnimalType.BEEF_COW
    assert hasattr(animal, "times_calved")
    assert isinstance(animal.times_calved, int)
    assert hasattr(animal, "is_open")
    assert isinstance(animal.is_open, bool)
    assert hasattr(animal, "body_condition_score_9")
    assert isinstance(animal.body_condition_score_9, float)
    assert hasattr(animal, "calf_at_side")
    assert animal.calf_at_side is None
    assert hasattr(animal, "dam")
    assert animal.dam is None
    assert hasattr(animal, "days_since_calving")
    assert isinstance(animal.days_since_calving, int)
    assert hasattr(animal, "lactation_day")
    assert isinstance(animal.lactation_day, int)
    assert hasattr(animal, "wean_weight")
    assert animal.wean_weight == 0.0


@pytest.mark.unit
def test_L2_beef_bull_constructs_without_error() -> None:
    """L2: BEEF_BULL must construct without error; days_in_breeding_season=None, calf_at_side=None.

    Verifies that _initialize_beef_cow_calf_animal handles BEEF_BULL safely
    with appropriate defaults for attributes not used by bulls.
    """
    t = _mock_time()
    args = {
        "id": 2,
        "breed": "AN",
        "animal_type": AnimalType.BEEF_BULL.value,
        "days_born": 365,
        "birth_weight": 35.0,
        "body_weight": 700.0,
        "mature_body_weight": 800.0,
        "sex": "MALE",
    }
    animal = Animal(args, t)  # type: ignore[arg-type]
    assert animal.animal_type == AnimalType.BEEF_BULL
    assert animal.days_in_breeding_season is None
    assert animal.calf_at_side is None


@pytest.mark.unit
def test_L3_beef_calf_in_dispatch_map() -> None:
    """L3: BEEF_CALF must be dispatched through initialize_animal_methods, not the dairy newborn path.

    Verifies that Animal.__init__ wires BEEF_CALF to _initialize_beef_cow_calf_animal
    and that the animal constructs correctly with its birth weight as body weight.
    """
    t = _mock_time()
    args = {
        "id": 3,
        "breed": "AN",
        "animal_type": AnimalType.BEEF_CALF.value,
        "days_born": 0,
        "birth_weight": 35.0,
        "body_weight": 35.0,
        "mature_body_weight": 520.0,
        "sex": "MALE",
        "initial_phosphorus": 0.0,
    }
    animal = Animal(args, t)  # type: ignore[arg-type]
    assert animal.animal_type == AnimalType.BEEF_CALF
    assert animal.body_weight == 35.0


@pytest.mark.unit
def test_L19_beef_calf_skips_dairy_newborn_path(mocker: MockerFixture) -> None:
    """L19: BEEF_CALF construction must NOT call _initialize_newborn_calf.

    The is_newborn_calf guard checks animal_type == AnimalType.CALF, which is
    False for BEEF_CALF. Dairy newborn logic (sex via semen type, still_birth_rate)
    must not run for beef calves.
    """
    t = _mock_time()
    args = {
        "id": 3,
        "breed": "AN",
        "animal_type": AnimalType.BEEF_CALF.value,
        "days_born": 0,
        "birth_weight": 35.0,
        "body_weight": 35.0,
        "mature_body_weight": 520.0,
        "sex": "MALE",
        "initial_phosphorus": 0.0,
    }
    spy = mocker.patch.object(Animal, "_initialize_newborn_calf")
    Animal(args, t)  # type: ignore[arg-type]
    spy.assert_not_called()


# ── L4, L4b: Heifer life-stage update ────────────────────────────────────────


@pytest.mark.unit
def test_L4_breeding_weight_event_fired_exactly_once() -> None:
    """L4: BEEF_HEIFER_REPLACEMENT fires REPLACEMENT_HEIFER_REACHED_BREEDING_WEIGHT exactly once.

    _breeding_weight_event_fired acts as a dedup guard so repeated calls on a
    heifer already above the threshold do not duplicate the event.
    """
    threshold = AnimalModuleConstants.BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE * AnimalConfig.beef_mature_cow_weight_kg
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_HEIFER_REPLACEMENT,
        body_weight=threshold + 10.0,
        times_calved=0,
        breeding_weight_event_fired=False,
    )
    t = _mock_time()

    animal._beef_replacement_heifer_life_stage_update(t)

    assert _event_fired(animal, animal_constants.REPLACEMENT_HEIFER_REACHED_BREEDING_WEIGHT)
    assert animal._breeding_weight_event_fired is True

    # Second call must NOT re-fire the event
    animal.events = AnimalEvents()
    animal._beef_replacement_heifer_life_stage_update(t)
    assert not _event_fired(animal, animal_constants.REPLACEMENT_HEIFER_REACHED_BREEDING_WEIGHT)


@pytest.mark.unit
def test_L4b_heifer_promoted_to_cow_after_calving() -> None:
    """L4b: BEEF_HEIFER_REPLACEMENT with times_calved >= 1 is promoted to BEEF_COW.

    Type promotion must happen in _beef_replacement_heifer_life_stage_update
    (not in _beef_daily_reproduction_update) to avoid same-tick race conditions.
    """
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_HEIFER_REPLACEMENT,
        times_calved=1,
    )
    t = _mock_time()

    status, newborn = animal._beef_replacement_heifer_life_stage_update(t)

    assert animal.animal_type == AnimalType.BEEF_COW
    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert newborn is None
    assert _event_fired(animal, animal_constants.REPLACEMENT_HEIFER_PROMOTED_TO_COW)


# ── L5–L9: Reproduction update ───────────────────────────────────────────────


@pytest.mark.unit
def test_L5_conception_probability_called_in_season(mocker: MockerFixture) -> None:
    """L5: calculate_seasonal_conception_probability is called when cow is open and in season.

    Verifies that _beef_handle_conception_attempt delegates the draw to the
    standalone function (allowing easy mocking / sensitivity testing).
    """
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        is_open=True,
        days_since_calving=60,
        body_condition_score_9=5.0,
    )
    t = _mock_time(day_of_year=120)  # within default season (90–153)

    mock_prob = mocker.patch(
        "RUFAS.biophysical.animal.animal.calculate_seasonal_conception_probability",
        return_value=0.0,  # return 0 so no state changes from conception
    )
    animal._beef_daily_reproduction_update(t)

    mock_prob.assert_called_once()


@pytest.mark.unit
def test_L6_beef_bull_returns_immediately() -> None:
    """L6: BEEF_BULL in daily_reproduction_update must return (None, HerdReproductionStatistics()) immediately.

    Bulls do not participate in the conception or calving logic inside
    _beef_daily_reproduction_update.
    """
    animal = _make_beef_animal(animal_type=AnimalType.BEEF_BULL)
    t = _mock_time()

    newborn, stats = animal._beef_daily_reproduction_update(t)

    assert newborn is None
    assert isinstance(stats, HerdReproductionStatistics)


@pytest.mark.unit
def test_L7_dairy_cow_reproduction_unaffected(mocker: MockerFixture) -> None:
    """L7: LAC_COW daily_reproduction_update must call reproduction.reproduction_update (regression).

    After adding the beef guard at the top of daily_reproduction_update, dairy
    cows must be completely unaffected (guard fires only for is_beef_cow_calf).
    """
    animal = _make_beef_animal(animal_type=AnimalType.LAC_COW)
    animal.nutrients = MagicMock()
    animal.nutrients.phosphorus_for_gestation_required_for_calf = 0.0
    animal.genetics = None
    AnimalConfig.simulate_genetics = False
    mock_repro = MagicMock()
    animal._reproduction = mock_repro
    mock_repro.reproduction_update.return_value.newborn_calf_config = None

    animal.daily_reproduction_update(_mock_time())

    mock_repro.reproduction_update.assert_called_once()


@pytest.mark.unit
def test_L8_calving_triggers_at_gestation_length() -> None:
    """L8: When days_in_pregnancy reaches BEEF_GESTATION_LENGTH_DAYS calving fires.

    Verifies that _beef_handle_calving is called: newborn_calf_config is not
    None, times_calved increments to 1, days_in_pregnancy resets to 0, and
    days_since_calving resets to 0.
    """
    gestation = AnimalModuleConstants.BEEF_GESTATION_LENGTH_DAYS
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        is_open=False,
        days_in_pregnancy=gestation - 1,
        times_calved=0,
        days_since_calving=300,
    )
    t = _mock_time()

    # Patch random so stillbirth does NOT occur (value > BEEF_STILLBIRTH_RATE)
    with patch("RUFAS.biophysical.animal.animal.random", return_value=0.99):
        newborn_config, stats = animal._beef_daily_reproduction_update(t)

    assert newborn_config is not None, "calving must return a non-None calf config dict"
    assert animal.times_calved == 1
    assert animal._days_in_pregnancy == 0
    assert animal.days_since_calving == 0


@pytest.mark.unit
def test_L9_stillbirth_returns_none_calf_config() -> None:
    """L9: When the stillbirth draw fires, _beef_handle_calving must return None for the calf config.

    Stillbirth rate is BEEF_STILLBIRTH_RATE (0.035). Patching random < 0.035
    forces the stillbirth branch.
    """
    gestation = AnimalModuleConstants.BEEF_GESTATION_LENGTH_DAYS
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        is_open=False,
        days_in_pregnancy=gestation - 1,
        times_calved=0,
    )
    t = _mock_time()

    with patch("RUFAS.biophysical.animal.animal.random", return_value=0.001):
        newborn_config, _ = animal._beef_daily_reproduction_update(t)

    assert newborn_config is None, "stillbirth must result in newborn_calf_config=None"


# ── L10–L14b: Life-stage update methods ─────────────────────────────────────


@pytest.mark.unit
def test_L10_calf_below_weaning_age_returns_remain() -> None:
    """L10: _beef_calf_life_stage_update returns REMAIN when days_born < beef_weaning_age_days.

    Verifies that no weaning event fires prematurely.
    """
    weaning_age = AnimalConfig.beef_weaning_age_days
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_CALF,
        days_born=weaning_age - 1,
    )
    t = _mock_time()

    status, newborn = animal._beef_calf_life_stage_update(t)

    assert status == AnimalStatus.REMAIN
    assert newborn is None


@pytest.mark.unit
def test_L11_calf_at_weaning_age_sell_destination() -> None:
    """L11: BEEF_CALF at weaning age with destination 'sell' returns SOLD and sets sold_at_day.

    Verifies the weaning event dispatches correctly for the default sell path.
    """
    weaning_age = AnimalConfig.beef_weaning_age_days
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_CALF,
        days_born=weaning_age,
        sex=Sex.FEMALE,
    )
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.SELL
    t = _mock_time(simulation_day=weaning_age)

    status, newborn = animal._beef_calf_life_stage_update(t)

    assert status == AnimalStatus.SOLD
    assert newborn is None
    assert animal.sold_at_day == weaning_age


@pytest.mark.unit
def test_L12_calf_weaning_replacement_heifer_destination() -> None:
    """L12: BEEF_CALF at weaning with destination 'replacement_heifer' (female) changes type to BEEF_HEIFER_REPLACEMENT.

    Verifies type promotion and LIFE_STAGE_CHANGED return for the heifer-retention path.
    """
    weaning_age = AnimalConfig.beef_weaning_age_days
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_CALF,
        days_born=weaning_age,
        sex=Sex.FEMALE,
    )
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.REPLACEMENT_HEIFER
    t = _mock_time()

    status, newborn = animal._beef_calf_life_stage_update(t)

    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert animal.animal_type == AnimalType.BEEF_HEIFER_REPLACEMENT
    assert newborn is None


@pytest.mark.unit
def test_L13_calf_weaning_feedlot_destination_steer() -> None:
    """L13: BEEF_CALF (male) at weaning with destination 'direct_to_feedlot' changes type to FEEDLOT_STEER.

    Verifies that _beef_weaning_event correctly dispatches male calves to feedlot.
    """
    weaning_age = AnimalConfig.beef_weaning_age_days
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_CALF,
        days_born=weaning_age,
        sex=Sex.MALE,
    )
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.DIRECT_TO_FEEDLOT
    t = _mock_time()

    status, newborn = animal._beef_calf_life_stage_update(t)

    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert animal.animal_type == AnimalType.FEEDLOT_STEER
    assert newborn is None


@pytest.mark.unit
def test_L14_cow_age_cull_returns_sold() -> None:
    """L14: _beef_cow_life_stage_update returns SOLD when days_born >= BEEF_COW_MAX_AGE_DAYS.

    Verifies the hard age ceiling cull path.
    """
    max_age = AnimalModuleConstants.BEEF_COW_MAX_AGE_DAYS
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        days_born=max_age,
    )
    t = _mock_time(simulation_day=max_age)

    status, newborn = animal._beef_cow_life_stage_update(t)

    assert status == AnimalStatus.SOLD
    assert newborn is None
    assert animal.sold_at_day == max_age


@pytest.mark.unit
def test_L14b_open_cow_past_breeding_close_marks_cull_reason() -> None:
    """L14b: Open cow past breeding-season-close gets cull_reason set but returns REMAIN.

    Actual removal from the herd is deferred to Step 7 PR-C (herd_factory);
    this PR only marks cull_reason so the higher layer can act.
    """
    season_start = AnimalConfig.beef_breeding_season_start_day
    season_length = AnimalConfig.beef_breeding_season_length
    past_close = season_start + season_length + 1

    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        is_open=True,
        days_born=730,
    )
    t = _mock_time(day_of_year=past_close)

    status, newborn = animal._beef_cow_life_stage_update(t)

    assert status == AnimalStatus.REMAIN
    assert newborn is None
    assert animal.cull_reason == animal_constants.COW_OPEN_AT_PREGNANCY_CHECK
    assert _event_fired(animal, animal_constants.COW_OPEN_AT_PREGNANCY_CHECK)
    assert animal.sold_at_day is None  # NOT set here; deferred to Step 7


# ── L15–L16: Milking update ──────────────────────────────────────────────────


@pytest.mark.unit
def test_L15_beef_cow_suckling_increments_lactation_day() -> None:
    """L15: daily_milking_update for BEEF_COW with calf_at_side increments lactation_day.

    Verifies that _beef_daily_suckling_update is called and lactation_day ticks.
    """
    calf = _make_beef_animal(animal_type=AnimalType.BEEF_CALF, days_born=30)
    cow = _make_beef_animal(animal_type=AnimalType.BEEF_COW, lactation_day=10)
    cow.calf_at_side = calf
    t = _mock_time()

    cow.daily_milking_update(t)

    assert cow.lactation_day == 11


@pytest.mark.unit
def test_L16_dairy_cow_milking_unaffected(mocker: MockerFixture) -> None:
    """L16: LAC_COW daily_milking_update must call milk_production.perform_daily_milking_update (regression).

    After adding the beef guard at the top of daily_milking_update, dairy cows
    must be completely unaffected.
    """
    animal = _make_beef_animal(animal_type=AnimalType.LAC_COW)
    animal._days_in_milk = 100
    animal._milk_production_output_days_in_milk = 0
    mock_outputs = MagicMock()
    mock_outputs.events = AnimalEvents()
    mock_perform = MagicMock(return_value=mock_outputs)
    animal.milk_production = MagicMock()
    animal.milk_production.perform_daily_milking_update = mock_perform

    animal.daily_milking_update(_mock_time())

    mock_perform.assert_called_once()


# ── L17–L18: Weaning edge cases ─────────────────────────────────────────────


@pytest.mark.unit
def test_L17_dam_calf_at_side_cleared_at_weaning() -> None:
    """L17: Dam's calf_at_side is set to None when the calf is weaned.

    Verifies that _beef_weaning_event properly clears the dam reference.
    """
    weaning_age = AnimalConfig.beef_weaning_age_days
    dam = _make_beef_animal(animal_type=AnimalType.BEEF_COW)
    calf = _make_beef_animal(
        animal_type=AnimalType.BEEF_CALF,
        days_born=weaning_age,
        sex=Sex.FEMALE,
    )
    calf.dam = dam
    dam.calf_at_side = calf
    AnimalConfig.beef_post_weaning_destination = BeefPostWeaningDestination.SELL
    t = _mock_time(simulation_day=weaning_age)

    calf._beef_calf_life_stage_update(t)

    assert dam.calf_at_side is None


@pytest.mark.unit
def test_L18_unknown_weaning_destination_raises_value_error() -> None:
    """L18: An unknown beef_post_weaning_destination must raise ValueError.

    Prevents silent no-ops when new destinations are added to the config
    without updating the dispatch in _beef_weaning_event.
    """
    weaning_age = AnimalConfig.beef_weaning_age_days
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_CALF,
        days_born=weaning_age,
        sex=Sex.FEMALE,
    )
    AnimalConfig.beef_post_weaning_destination = cast(BeefPostWeaningDestination, "not_a_real_destination")
    t = _mock_time()

    with pytest.raises(ValueError, match="beef_post_weaning_destination"):
        animal._beef_calf_life_stage_update(t)


# ── B3: All AnimalType members must be in the life-stage map ─────────────────


@pytest.mark.unit
@pytest.mark.parametrize("animal_type", list(AnimalType))
def test_B3_all_animal_types_in_life_stage_map(animal_type: AnimalType) -> None:
    """B3: Every AnimalType member must have an entry in ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP.

    Guards against future KeyError when new animal types are added to the enum
    without updating the dispatch map in animal_life_stage_update().
    """
    animal = _make_beef_animal(animal_type=animal_type)
    t = _mock_time()
    mock_output = MagicMock()
    mock_output.animal_status = AnimalStatus.REMAIN
    mock_output.newborn_calf_config = None

    # animal_life_stage_update builds the map internally and dispatches;
    # a KeyError before implementation is the expected RED failure
    animal.animal_life_stage_update(t)


# ── Gemini PR #34 review fixes ───────────────────────────────────────────────


@pytest.mark.unit
def test_GA_male_calf_replacement_heifer_destination_sells(mocker: MockerFixture) -> None:
    """GA: Male BEEF_CALF with destination='replacement_heifer' must sell at weaning.

    FIX 1 (PR #35 round 2): males cannot become replacement heifers; they route to
    SOLD so the simulation continues rather than crashing with ValueError.
    """
    weaning_age = AnimalConfig.beef_weaning_age_days
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_CALF,
        days_born=weaning_age,
        sex=Sex.MALE,
    )
    mocker.patch.object(AnimalConfig, "beef_post_weaning_destination", BeefPostWeaningDestination.REPLACEMENT_HEIFER)
    t = _mock_time(simulation_day=weaning_age)

    status, newborn = animal._beef_calf_life_stage_update(t)

    assert status == AnimalStatus.SOLD
    assert newborn is None


@pytest.mark.unit
def test_GA_female_calf_replacement_heifer_destination_transitions(mocker: MockerFixture) -> None:
    """GA: Female BEEF_CALF with destination='replacement_heifer' must transition correctly.

    Regression guard: the sex guard must not block valid female transitions.
    """
    weaning_age = AnimalConfig.beef_weaning_age_days
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_CALF,
        days_born=weaning_age,
        sex=Sex.FEMALE,
    )
    mocker.patch.object(AnimalConfig, "beef_post_weaning_destination", BeefPostWeaningDestination.REPLACEMENT_HEIFER)
    t = _mock_time(simulation_day=weaning_age)

    status, newborn = animal._beef_calf_life_stage_update(t)

    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert animal.animal_type == AnimalType.BEEF_HEIFER_REPLACEMENT
    assert newborn is None


@pytest.mark.unit
def test_GB_open_cow_generates_exactly_one_event_across_multiple_days() -> None:
    """GB: Open cow past breeding-season-close must fire COW_OPEN_AT_PREGNANCY_CHECK exactly once.

    Verifies the dedup guard in Fix B prevents duplicate event entries when
    _beef_cow_life_stage_update is called on consecutive simulation days.
    """
    season_start = AnimalConfig.beef_breeding_season_start_day
    season_length = AnimalConfig.beef_breeding_season_length
    past_close = season_start + season_length + 1

    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        is_open=True,
        days_born=730,
    )

    for day_offset in range(3):
        t = _mock_time(simulation_day=past_close + day_offset, day_of_year=past_close + day_offset)
        animal._beef_cow_life_stage_update(t)

    event_count = sum(
        descriptions.count(animal_constants.COW_OPEN_AT_PREGNANCY_CHECK)
        for descriptions in animal.events.events.values()
    )
    assert event_count == 1, f"Expected exactly 1 event, got {event_count}"


@pytest.mark.unit
def test_GC_breeding_season_year_boundary_wrap(mocker: MockerFixture) -> None:
    """GC: Breeding season starting day 330 with length 63 must wrap across the year boundary.

    Season spans days 330-365 (36 days) + days 1-27 (27 days) = 63 days total.
    Day 15 (inside wrapped portion) must be IN season; day 100 must be OUT.
    Verifies Fix C's year-boundary wrap in _beef_daily_reproduction_update.
    """
    AnimalConfig.beef_breeding_season_start_day = 330
    AnimalConfig.beef_breeding_season_length = 63  # season_end = 393; 393 % 365 = 28 → days 1-27 in wrapped portion

    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        is_open=True,
        days_since_calving=60,
        body_condition_score_9=6.0,
    )

    # day 100 — outside the wrapped season; is_open must stay True
    t_out = _mock_time(day_of_year=100)
    animal._beef_daily_reproduction_update(t_out)
    assert animal.is_open is True, "Day 100 should be outside the wrapped breeding season"

    # day 15 — clearly inside the wrapped portion (days 1-27); patch random to guarantee conception
    mocker.patch("RUFAS.biophysical.animal.animal.random", return_value=0.0)
    t_in = _mock_time(day_of_year=15)
    animal._beef_daily_reproduction_update(t_in)
    assert animal.is_open is False, "Day 15 should be inside the wrapped breeding season"


@pytest.mark.unit
def test_GD_conception_day_days_in_pregnancy_equals_one(mocker: MockerFixture) -> None:
    """GD: A cow that conceives on day X must have _days_in_pregnancy == 1 (not 2) after that day's update.

    Verifies the FIX 1 guard: was_pregnant_at_start prevents the newly-set
    _days_in_pregnancy = 1 from being incremented to 2 on the same day.
    """
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        is_open=True,
        days_since_calving=60,
        days_in_pregnancy=0,
    )
    mocker.patch("RUFAS.biophysical.animal.animal.random", return_value=0.0)
    t = _mock_time(day_of_year=120)  # inside default season (start=90, length=63)
    animal._beef_daily_reproduction_update(t)

    assert (
        animal._days_in_pregnancy == 1
    ), f"Conception day must leave _days_in_pregnancy=1, got {animal._days_in_pregnancy}"
    assert animal.is_open is False


@pytest.mark.unit
def test_GE_freshly_calved_cow_not_flagged_open_outside_season() -> None:
    """GE: A cow with days_since_calving=0 must NOT receive COW_OPEN_AT_PREGNANCY_CHECK even after season close.

    Verifies the FIX 2 rebreeding-opportunity guard: a cow that calves on a day
    that falls outside the breeding season has never had a chance to conceive, so
    it must not be marked open-and-culled on calving day.
    """
    season_start = AnimalConfig.beef_breeding_season_start_day
    season_length = AnimalConfig.beef_breeding_season_length
    past_close = season_start + season_length + 5  # clearly after season close

    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        is_open=True,
        days_since_calving=0,
        days_born=730,
    )
    t = _mock_time(simulation_day=past_close, day_of_year=past_close)
    animal._beef_cow_life_stage_update(t)

    assert (
        animal.cull_reason != animal_constants.COW_OPEN_AT_PREGNANCY_CHECK
    ), "Freshly calved cow (days_since_calving=0) must not be flagged open on calving day"


@pytest.mark.unit
def test_GF_cow_calving_day_after_season_close_not_flagged_after_anestrus() -> None:
    """GF: Cow calving the day after season close must NOT get COW_OPEN_AT_PREGNANCY_CHECK 45 days later.

    Verifies the wrap-aware rebreeding guard (FIX 1): postpartum_eligible_day
    falls on or after season_close_day so has_had_rebreeding_opportunity is False.

    Setup: default season start=90 length=63 → season_end=153 (close day 153).
    Cow calves at day_of_year=154 (sim_day=200). Checked at days_since_calving=45
    → current sim_day=245, day_of_year=199.
    season_close_day = 245 - 199 + 153 = 199.
    postpartum_eligible_day = 245 - 45 + 45 = 245 ≥ 199 → no opportunity → not flagged.
    """
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        is_open=True,
        days_since_calving=45,
        days_born=730,
    )
    t = _mock_time(simulation_day=245, day_of_year=199)
    animal._beef_cow_life_stage_update(t)

    assert (
        animal.cull_reason != animal_constants.COW_OPEN_AT_PREGNANCY_CHECK
    ), "Cow calving day after season close must not be flagged open 45 days later"


@pytest.mark.unit
def test_GG_cow_calving_mid_season_flagged_open_after_season_close() -> None:
    """GG: Cow calving mid-season and still open after season close MUST get COW_OPEN_AT_PREGNANCY_CHECK.

    Verifies the positive case of the wrap-aware guard: postpartum_eligible_day
    falls before season_close_day, so the cow genuinely had a breeding window.

    Setup: default season start=90 length=63 → close day 153.
    Cow calves at day_of_year=60 (sim_day=100). Checked 100 days later:
    sim_day=200, day_of_year=160, days_since_calving=100.
    season_close_day = 200 - 160 + 153 = 193.
    postpartum_eligible_day = 200 - 100 + 45 = 145 < 193 → had opportunity → flagged.
    """
    animal = _make_beef_animal(
        animal_type=AnimalType.BEEF_COW,
        is_open=True,
        days_since_calving=100,
        days_born=730,
    )
    t = _mock_time(simulation_day=200, day_of_year=160)
    animal._beef_cow_life_stage_update(t)

    assert (
        animal.cull_reason == animal_constants.COW_OPEN_AT_PREGNANCY_CHECK
    ), "Cow that calved before season and stayed open past close must be flagged"
