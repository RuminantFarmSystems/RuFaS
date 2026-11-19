"""Tests for beef stocker animal lifecycle — Step 4.

TDD coverage for:
- _initialize_stocker_animal(): attribute presence, entry weight, mature BW, validation
- _stocker_daily_routines(): days_in_stocker/days_born increment, DMI accumulation
- _stocker_life_stage_update(): REMAIN, exit-weight transition, max-days transition
- ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP: BEEF_STOCKER_STEER/HEIFER covered (fixes B3 pre-existing failures)
- calculate_nutrition_requirements(): routes to BeefStockerRequirementsCalculator

RED before Step 4 implementation; GREEN after.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, Breed, Sex
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements, NutritionSupply
from RUFAS.biophysical.animal.nutrients.beef_stocker_requirements_calculator import BeefStockerRequirementsCalculator

# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

_STOCKER_ENTRY_BW = 250.0  # kg — mid-range placement weight
_STOCKER_MATURE_BW = 520.0  # AnimalConfig.beef_mature_cow_weight_kg default
_STOCKER_DAY = 100  # simulation day used in mock_time


def _mock_time(simulation_day: int = _STOCKER_DAY) -> MagicMock:
    t = MagicMock()
    t.simulation_day = simulation_day
    return t


def _make_stocker_animal(
    animal_type: AnimalType = AnimalType.BEEF_STOCKER_STEER,
    body_weight: float = _STOCKER_ENTRY_BW,
    days_in_stocker: int = 0,
    sex: Sex = Sex.STEER,
    stocker_cumulative_dmi: float = 0.0,
) -> Animal:
    """Construct a minimal stocker animal via __new__ with all Step 4 attributes set.

    Parameters
    ----------
    animal_type : AnimalType
        Must be BEEF_STOCKER_STEER or BEEF_STOCKER_HEIFER.
    body_weight : float
        Current body weight (kg).
    days_in_stocker : int
        Days since pen placement.
    sex : Sex
        Animal sex (Sex.STEER for steer, Sex.FEMALE for heifer).
    stocker_cumulative_dmi : float
        Total DMI accumulated so far (kg).

    Returns
    -------
    Animal
        A minimally constructed Animal instance suitable for unit testing.

    """
    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = animal_type
    animal.body_weight = body_weight
    animal.mature_body_weight = _STOCKER_MATURE_BW
    animal.sex = sex
    animal.breed = Breed.AN
    animal.days_born = 365 + days_in_stocker
    animal.birth_weight = 0.0
    animal.wean_weight = 0.0
    # stocker tracking attrs
    animal.days_in_stocker = days_in_stocker
    animal.stocker_entry_weight = body_weight
    animal.stocker_cumulative_dmi = stocker_cumulative_dmi
    animal.days_on_restricted_intake = 0
    animal.is_on_restricted_intake = False
    animal.compensatory_gain_factor = 1.0
    # feedlot tracking defaults (always present on Animal instances)
    animal.days_on_feed = 0
    animal.entry_weight = 0.0
    animal.cumulative_dmi = 0.0
    animal.receiving_stress = False
    animal.step_up_phase = ""
    # general attrs required by animal_life_stage_update / event system
    animal.events = AnimalEvents()
    animal.sold_at_day = None
    animal._future_death_date = None
    animal.cull_reason = ""
    animal.om = MagicMock()
    animal.growth = MagicMock()
    animal.nutrition_supply = NutritionSupply.make_empty_nutrition_supply()
    animal.previous_nutrition_supply = None
    return animal


# ---------------------------------------------------------------------------
# B3: ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP coverage
# (These were the 2 pre-existing RED failures before Step 4)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_B3_stocker_steer_in_life_stage_map() -> None:
    """B3: BEEF_STOCKER_STEER must have an entry in ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP.

    Calls animal_life_stage_update() to prove the map lookup succeeds.
    KeyError before Step 4 (RED); passes after Step 4 (GREEN).
    """
    animal = _make_stocker_animal(animal_type=AnimalType.BEEF_STOCKER_STEER)
    t = _mock_time()
    animal.animal_life_stage_update(t)


@pytest.mark.unit
def test_B3_stocker_heifer_in_life_stage_map() -> None:
    """B3: BEEF_STOCKER_HEIFER must have an entry in ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP.

    Calls animal_life_stage_update() to prove the map lookup succeeds.
    KeyError before Step 4 (RED); passes after Step 4 (GREEN).
    """
    animal = _make_stocker_animal(
        animal_type=AnimalType.BEEF_STOCKER_HEIFER,
        sex=Sex.FEMALE,
    )
    t = _mock_time()
    animal.animal_life_stage_update(t)


# ---------------------------------------------------------------------------
# Attribute presence — new Step 4 stocker tracking attrs
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_steer_has_days_in_stocker() -> None:
    """BEEF_STOCKER_STEER animal must have an integer days_in_stocker attribute.

    Verifies the stocker lifecycle counter is initialised with the correct type.
    """
    animal = _make_stocker_animal()
    assert hasattr(animal, "days_in_stocker")
    assert isinstance(animal.days_in_stocker, int)


@pytest.mark.unit
def test_stocker_steer_has_stocker_entry_weight() -> None:
    """BEEF_STOCKER_STEER animal must have a float stocker_entry_weight attribute.

    Verifies placement weight is captured at initialisation.
    """
    animal = _make_stocker_animal()
    assert hasattr(animal, "stocker_entry_weight")
    assert isinstance(animal.stocker_entry_weight, float)


@pytest.mark.unit
def test_stocker_steer_has_stocker_cumulative_dmi() -> None:
    """BEEF_STOCKER_STEER animal must have a float stocker_cumulative_dmi attribute.

    Verifies total DMI accumulator is initialised with the correct type.
    """
    animal = _make_stocker_animal()
    assert hasattr(animal, "stocker_cumulative_dmi")
    assert isinstance(animal.stocker_cumulative_dmi, float)


@pytest.mark.unit
def test_stocker_entry_weight_equals_body_weight_at_placement() -> None:
    """stocker_entry_weight must equal body_weight at the time of placement.

    Placement weight is the baseline for ADG calculations.
    """
    animal = _make_stocker_animal(body_weight=220.0)
    assert animal.stocker_entry_weight == pytest.approx(220.0)


@pytest.mark.unit
def test_stocker_mature_body_weight_is_beef_mature_cow_weight(mocker: MockerFixture) -> None:
    """mature_body_weight must be AnimalConfig.beef_mature_cow_weight_kg (~520 kg), NOT stocker_exit_weight.

    NRC EQSBW requires the animal's true adult weight.
    Using stocker exit weight (~350 kg) produces biologically incorrect growth energy.
    """
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "stocker_entry_weight", 200.0)
    mocker.patch.object(AnimalConfig, "simulate_genetics", False)
    t = _mock_time()
    args = {
        "id": 99,
        "breed": "AN",
        "animal_type": AnimalType.BEEF_STOCKER_STEER.value,
        "body_weight": 200.0,
        "days_born": 0,
    }
    animal = Animal(args, t)  # type: ignore[arg-type]
    assert animal.mature_body_weight == pytest.approx(520.0)


# ---------------------------------------------------------------------------
# _initialize_stocker_animal validation — math.isfinite + > 0 (staged-atomic)
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("bad_bw", [0.0, -10.0, float("nan"), float("inf")])
def test_initialize_stocker_invalid_body_weight_raises(bad_bw: float) -> None:
    """_initialize_stocker_animal must raise ValueError for non-positive or non-finite body_weight.

    Staged-atomic validation must catch all pathological values before any state is written.
    """
    t = _mock_time()
    args = {
        "id": 1,
        "breed": "AN",
        "animal_type": AnimalType.BEEF_STOCKER_STEER.value,
        "body_weight": bad_bw,
        "days_born": 0,
    }
    with pytest.raises(ValueError, match="body_weight"):
        Animal(args, t)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# _stocker_life_stage_update — REMAIN, exit weight, max days
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_life_stage_remain_below_exit_weight_and_max_days(mocker: MockerFixture) -> None:
    """_stocker_life_stage_update must return (REMAIN, None) when below exit weight and max days.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig class attributes.

    """
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    animal = _make_stocker_animal(body_weight=250.0, days_in_stocker=50)
    t = _mock_time()
    status, newborn = animal._stocker_life_stage_update(t)
    assert status == AnimalStatus.REMAIN
    assert newborn is None


@pytest.mark.unit
def test_stocker_life_stage_exit_at_exit_weight(mocker: MockerFixture) -> None:
    """_stocker_life_stage_update must return LIFE_STAGE_CHANGED when body_weight >= stocker_exit_weight.

    Boundary condition: body_weight exactly equal to exit weight must trigger transition.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig class attributes.

    """
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal(body_weight=350.0, days_in_stocker=100)
    t = _mock_time()
    status, newborn = animal._stocker_life_stage_update(t)
    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert newborn is None


@pytest.mark.unit
def test_stocker_exit_weight_fires_stocker_exit_weight_event(mocker: MockerFixture) -> None:
    """STOCKER_EXIT_WEIGHT event must be recorded when exit weight is reached.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig class attributes.

    """
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal(body_weight=355.0, days_in_stocker=100)
    t = _mock_time(simulation_day=100)
    animal._stocker_life_stage_update(t)
    assert animal.events.get_most_recent_date(animal_constants.STOCKER_EXIT_WEIGHT) != -1


@pytest.mark.unit
def test_stocker_exit_weight_steer_transitions_to_feedlot_steer(mocker: MockerFixture) -> None:
    """On exit-weight exit, BEEF_STOCKER_STEER must transition to FEEDLOT_STEER.

    The animal_type change enables the feedlot daily routine on the next day.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig class attributes.

    """
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal(animal_type=AnimalType.BEEF_STOCKER_STEER, body_weight=355.0, sex=Sex.STEER)
    t = _mock_time()
    animal._stocker_life_stage_update(t)
    assert animal.animal_type == AnimalType.FEEDLOT_STEER


@pytest.mark.unit
def test_stocker_exit_weight_heifer_transitions_to_feedlot_heifer(mocker: MockerFixture) -> None:
    """On exit-weight exit, BEEF_STOCKER_HEIFER must transition to FEEDLOT_HEIFER.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig class attributes.

    """
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal(animal_type=AnimalType.BEEF_STOCKER_HEIFER, body_weight=355.0, sex=Sex.FEMALE)
    t = _mock_time()
    animal._stocker_life_stage_update(t)
    assert animal.animal_type == AnimalType.FEEDLOT_HEIFER


@pytest.mark.unit
def test_stocker_life_stage_exit_at_max_days(mocker: MockerFixture) -> None:
    """_stocker_life_stage_update must return LIFE_STAGE_CHANGED when days_in_stocker >= stocker_max_days.

    Boundary condition: exactly equal to max days must trigger transition.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig class attributes.

    """
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal(body_weight=280.0, days_in_stocker=210)
    t = _mock_time()
    status, newborn = animal._stocker_life_stage_update(t)
    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert newborn is None


@pytest.mark.unit
def test_stocker_max_days_fires_stocker_max_days_event(mocker: MockerFixture) -> None:
    """STOCKER_MAX_DAYS event must be recorded when max days is reached.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig class attributes.

    """
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal(body_weight=280.0, days_in_stocker=210)
    t = _mock_time(simulation_day=_STOCKER_DAY)
    animal._stocker_life_stage_update(t)
    assert animal.events.get_most_recent_date(animal_constants.STOCKER_MAX_DAYS) != -1


# ---------------------------------------------------------------------------
# _stocker_daily_routines — counters and accumulation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_daily_routines_increments_days_in_stocker(mocker: MockerFixture) -> None:
    """_stocker_daily_routines must increment days_in_stocker by 1 each call.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to stub animal_life_stage_update.

    """
    mocker.patch.object(AnimalConfig, "stocker_target_adg", 0.80)
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal(body_weight=250.0, days_in_stocker=5)
    mocker.patch.object(animal, "animal_life_stage_update", return_value=(AnimalStatus.REMAIN, None))
    t = _mock_time()
    animal._stocker_daily_routines(t)
    assert animal.days_in_stocker == 6


@pytest.mark.unit
def test_stocker_daily_routines_increments_days_born(mocker: MockerFixture) -> None:
    """_stocker_daily_routines must increment days_born by 1 each call.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to stub animal_life_stage_update.

    """
    mocker.patch.object(AnimalConfig, "stocker_target_adg", 0.80)
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal(days_in_stocker=0)
    initial_days_born = animal.days_born
    mocker.patch.object(animal, "animal_life_stage_update", return_value=(AnimalStatus.REMAIN, None))
    t = _mock_time()
    animal._stocker_daily_routines(t)
    assert animal.days_born == initial_days_born + 1


@pytest.mark.unit
def test_stocker_cumulative_dmi_accumulates_from_nutrition_supply(mocker: MockerFixture) -> None:
    """stocker_cumulative_dmi must accumulate nutrition_supply.dry_matter each day.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to stub animal_life_stage_update.

    """
    mocker.patch.object(AnimalConfig, "stocker_target_adg", 0.80)
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal(body_weight=250.0, stocker_cumulative_dmi=10.0)
    animal.nutrition_supply = MagicMock()
    animal.nutrition_supply.dry_matter = 7.5
    mocker.patch.object(animal, "animal_life_stage_update", return_value=(AnimalStatus.REMAIN, None))
    t = _mock_time()
    animal._stocker_daily_routines(t)
    assert animal.stocker_cumulative_dmi == pytest.approx(17.5)


@pytest.mark.unit
def test_stocker_cumulative_dmi_no_accumulation_when_zero_dm(mocker: MockerFixture) -> None:
    """stocker_cumulative_dmi must not accumulate when nutrition_supply.dry_matter <= 0.

    Mirrors feedlot behaviour: only accumulate when feed was actually supplied.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to stub animal_life_stage_update.

    """
    mocker.patch.object(AnimalConfig, "stocker_target_adg", 0.80)
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal(body_weight=250.0, stocker_cumulative_dmi=5.0)
    animal.nutrition_supply = MagicMock()
    animal.nutrition_supply.dry_matter = 0.0
    mocker.patch.object(animal, "animal_life_stage_update", return_value=(AnimalStatus.REMAIN, None))
    t = _mock_time()
    animal._stocker_daily_routines(t)
    assert animal.stocker_cumulative_dmi == pytest.approx(5.0)


@pytest.mark.unit
def test_stocker_daily_routines_dispatched_from_daily_routines(mocker: MockerFixture) -> None:
    """daily_routines() must dispatch to _stocker_daily_routines for stocker animals.

    Verifies the independent if-guard (not elif) routes stocker types correctly.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to spy on _stocker_daily_routines.

    """
    mocker.patch.object(AnimalConfig, "stocker_target_adg", 0.80)
    mocker.patch.object(AnimalConfig, "stocker_exit_weight", 350.0)
    mocker.patch.object(AnimalConfig, "stocker_max_days", 210)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)
    mocker.patch.object(AnimalConfig, "feedlot_entry_weight", 250.0)
    animal = _make_stocker_animal()
    mocker.patch.object(animal, "animal_life_stage_update", return_value=(AnimalStatus.REMAIN, None))
    spy = mocker.spy(animal, "_stocker_daily_routines")
    t = _mock_time()
    animal.daily_routines(t, None)
    spy.assert_called_once_with(t)


# ---------------------------------------------------------------------------
# calculate_nutrition_requirements — routes to BeefStockerRequirementsCalculator
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_calculate_nutrition_requirements_routes_to_stocker_calculator(mocker: MockerFixture) -> None:
    """calculate_nutrition_requirements must call BeefStockerRequirementsCalculator for stocker animals.

    Verifies that the stocker branch is present and correctly dispatched,
    mirroring the feedlot branch pattern (early return via BeefNRCRequirementsCalculator).

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to spy on BeefStockerRequirementsCalculator.

    """
    mocker.patch.object(AnimalConfig, "stocker_target_adg", 0.80)
    mocker.patch.object(AnimalConfig, "beef_mature_cow_weight_kg", 520.0)

    spy = mocker.spy(BeefStockerRequirementsCalculator, "calculate_requirements")

    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.BEEF_STOCKER_STEER
    animal.body_weight = 250.0
    animal.mature_body_weight = 520.0
    animal.breed = Breed.AN
    animal.sex = Sex.STEER
    animal.previous_nutrition_supply = None
    animal.compensatory_gain_factor = 1.0

    result = animal.calculate_nutrition_requirements(
        housing="Open_Lot",
        walking_distance=0.0,
        previous_temperature=20.0,
        available_feeds=[],
    )
    spy.assert_called_once()
    assert isinstance(result, NutritionRequirements)
    assert result.pregnancy_energy == pytest.approx(0.0)
    assert result.lactation_energy == pytest.approx(0.0)
    assert result.maintenance_energy > 0.0
    assert result.dry_matter > 0.0


# ---------------------------------------------------------------------------
# Onion-layer guard — no reporter/herd calls from animal.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_no_reporter_or_herd_import_in_animal_py() -> None:
    """animal.py must not import AnimalModuleReporter or HerdManager/HerdFactory.

    The onion-layer rule prohibits upward calls from animal.py to its orchestrators.
    Reporter calls belong in herd_manager._process_daily_herd_updates (Step 7).
    References in comments (e.g. feedlot TODO) are allowed; only import statements are checked.
    """
    import importlib.util
    import ast

    spec = importlib.util.find_spec("RUFAS.biophysical.animal.animal")
    assert spec is not None and spec.origin is not None
    source = open(spec.origin).read()
    tree = ast.parse(source)
    imported_names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.append(alias.name)

    forbidden = ("AnimalModuleReporter", "HerdManager", "HerdFactory")
    for name in forbidden:
        assert name not in imported_names, (
            f"animal.py must not import {name} (onion-layer violation); "
            f"reporter/herd wiring belongs in herd_manager._process_daily_herd_updates()"
        )


# ---------------------------------------------------------------------------
# Scope guard — BeefGEM attribute naming
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_compensatory_gain_factor_defaults_to_one() -> None:
    """stocker animals carry compensatory_gain_factor, neutral until earned.

    This attribute was out of scope for the native stocker module and arrived
    with the compensatory gain work. It defaults to 1.0, so its presence alone
    changes no result.
    """
    animal = _make_stocker_animal()
    assert animal.compensatory_gain_factor == pytest.approx(1.0)


@pytest.mark.unit
def test_no_days_restricted_attribute() -> None:
    """stocker animals must NOT have days_restricted (BeefGEM Phase D scope).

    This attribute is excluded from the native stocker module per the approved plan.
    """
    animal = _make_stocker_animal()
    assert not hasattr(
        animal, "days_restricted"
    ), "days_restricted is BeefGEM Phase D scope and must not appear in Step 4"
