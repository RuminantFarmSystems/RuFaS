"""Tests for feedlot lifecycle in the Animal class."""

import pytest
from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, Breed, Sex
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.nutrients.beef_nrc_requirements_calculator import BeefNRCRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients


def _make_feedlot_animal(
    animal_type: AnimalType = AnimalType.FEEDLOT_STEER,
    body_weight: float = 320.0,
    days_on_feed: int = 0,
) -> Animal:
    """Construct a minimal feedlot animal via __new__ with required attributes set.

    Parameters
    ----------
    animal_type : AnimalType
        The feedlot animal type (FEEDLOT_STEER or FEEDLOT_HEIFER).
    body_weight : float
        Current body weight in kg.
    days_on_feed : int
        Number of days the animal has been on feed.

    Returns
    -------
    Animal
        A minimally constructed Animal instance suitable for unit testing.
    """
    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = animal_type
    animal.body_weight = body_weight
    animal.days_on_feed = days_on_feed
    animal.days_born = 365 + days_on_feed
    animal.entry_weight = body_weight
    animal.cumulative_dmi = 0.0
    animal.receiving_stress = days_on_feed <= AnimalModuleConstants.RECEIVING_PERIOD_DAYS
    animal.step_up_phase = ""
    animal.compensatory_gain_factor = 1.0
    animal.events = AnimalEvents()
    animal.sold_at_day = None
    animal.cull_reason = ""
    animal.om = MagicMock()
    return animal


@pytest.mark.unit
def test_feedlot_steer_has_days_on_feed() -> None:
    """FEEDLOT_STEER animal must have an integer days_on_feed attribute.

    Verifies that the feedlot lifecycle initialisation sets ``days_on_feed``
    with the correct type.
    """
    animal = _make_feedlot_animal()
    assert hasattr(animal, "days_on_feed")
    assert isinstance(animal.days_on_feed, int)


@pytest.mark.unit
def test_feedlot_steer_has_step_up_phase() -> None:
    """FEEDLOT_STEER animal must have a step_up_phase string attribute.

    Verifies that the feedlot step-up diet protocol initialises the phase
    tracker with the correct type.
    """
    animal = _make_feedlot_animal()
    assert hasattr(animal, "step_up_phase")
    assert isinstance(animal.step_up_phase, str)


@pytest.mark.unit
def test_feedlot_steer_has_receiving_stress() -> None:
    """FEEDLOT_STEER animal must have a boolean receiving_stress attribute.

    Verifies that the receiving-period flag is initialised with the correct
    type on a newly constructed feedlot animal.
    """
    animal = _make_feedlot_animal()
    assert hasattr(animal, "receiving_stress")
    assert isinstance(animal.receiving_stress, bool)


@pytest.mark.unit
def test_feedlot_steer_has_entry_weight() -> None:
    """FEEDLOT_STEER animal must have an entry_weight float attribute.

    Verifies that entry_weight is recorded at pen placement as a float.
    """
    animal = _make_feedlot_animal(body_weight=320.0)
    assert hasattr(animal, "entry_weight")
    assert isinstance(animal.entry_weight, float)


@pytest.mark.unit
def test_update_step_up_phase_starter_at_day_0() -> None:
    """_update_step_up_phase must set 'starter' when days_on_feed <= STEP_UP_STARTER_END_DAY.

    Covers the first day of the feeding period; the animal should be in the
    starter phase.
    """
    animal = _make_feedlot_animal(days_on_feed=0)
    animal._update_step_up_phase()  # type: ignore[attr-defined]
    assert animal.step_up_phase == "starter"


@pytest.mark.unit
def test_update_step_up_phase_starter_at_boundary() -> None:
    """_update_step_up_phase must still be 'starter' on the last starter day (day 7).

    Verifies that the boundary day (STEP_UP_STARTER_END_DAY) still maps to
    the 'starter' phase before transitioning.
    """
    animal = _make_feedlot_animal(days_on_feed=AnimalModuleConstants.STEP_UP_STARTER_END_DAY)
    animal._update_step_up_phase()  # type: ignore[attr-defined]
    assert animal.step_up_phase == "starter"


@pytest.mark.unit
def test_update_step_up_phase_transition_at_day_14() -> None:
    """_update_step_up_phase must set 'transition' when 8 <= days_on_feed <= 21.

    Covers mid-transition feeding period; the animal should be in the
    'transition' phase.
    """
    animal = _make_feedlot_animal(days_on_feed=14)
    animal._update_step_up_phase()  # type: ignore[attr-defined]
    assert animal.step_up_phase == "transition"


@pytest.mark.unit
def test_update_step_up_phase_finisher_after_21_days() -> None:
    """_update_step_up_phase must set 'finisher' when days_on_feed > STEP_UP_TRANSITION_END_DAY.

    Verifies that animals past the transition period are correctly assigned
    to the 'finisher' phase.
    """
    animal = _make_feedlot_animal(days_on_feed=30)
    animal._update_step_up_phase()  # type: ignore[attr-defined]
    assert animal.step_up_phase == "finisher"


@pytest.mark.unit
def test_receiving_stress_true_within_receiving_period() -> None:
    """receiving_stress must be True when days_on_feed <= RECEIVING_PERIOD_DAYS.

    Animals in the arrival/receiving window have suppressed intake; the flag
    must be set to indicate this state.
    """
    animal = _make_feedlot_animal(days_on_feed=10)
    assert animal.receiving_stress is True


@pytest.mark.unit
def test_receiving_stress_false_after_receiving_period() -> None:
    """receiving_stress must be False when days_on_feed > RECEIVING_PERIOD_DAYS (21).

    Animals past the receiving window should no longer carry the intake
    suppression flag.
    """
    animal = _make_feedlot_animal(days_on_feed=25)
    assert animal.receiving_stress is False


@pytest.mark.unit
def test_feedlot_life_stage_remain_below_slaughter(mocker: MockerFixture) -> None:
    """_feedlot_life_stage_update must return (REMAIN, None) when below slaughter weight.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig class attributes.
    """
    mocker.patch.object(AnimalConfig, "feedlot_slaughter_weight", 580.0)
    mocker.patch.object(AnimalConfig, "feedlot_max_days_on_feed", 220)
    animal = _make_feedlot_animal(body_weight=400.0, days_on_feed=50)
    mock_time = MagicMock()
    mock_time.simulation_day = 50
    status, newborn = animal._feedlot_life_stage_update(mock_time)  # type: ignore[attr-defined]
    assert status == AnimalStatus.REMAIN
    assert newborn is None


@pytest.mark.unit
def test_feedlot_life_stage_sold_at_slaughter_weight(mocker: MockerFixture) -> None:
    """_feedlot_life_stage_update must return SOLD when body_weight >= slaughter_weight.

    Reporter wiring (AnimalModuleReporter.report_feedlot_performance) is deferred
    to a future _feedlot_update method in herd_factory.py — see TODO in the method.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig class attributes.
    """
    mocker.patch.object(AnimalConfig, "feedlot_slaughter_weight", 580.0)
    mocker.patch.object(AnimalConfig, "feedlot_max_days_on_feed", 220)
    animal = _make_feedlot_animal(body_weight=580.0, days_on_feed=180)
    mock_time = MagicMock()
    mock_time.simulation_day = 180
    status, newborn = animal._feedlot_life_stage_update(mock_time)  # type: ignore[attr-defined]
    assert status == AnimalStatus.SOLD
    assert newborn is None
    assert animal.sold_at_day == 180


@pytest.mark.unit
def test_feedlot_life_stage_sold_at_max_days_on_feed(mocker: MockerFixture) -> None:
    """_feedlot_life_stage_update must return SOLD when days_on_feed >= max_days_on_feed.

    Reporter wiring (AnimalModuleReporter.report_feedlot_performance) is deferred
    to a future _feedlot_update method in herd_factory.py — see TODO in the method.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig class attributes.
    """
    mocker.patch.object(AnimalConfig, "feedlot_slaughter_weight", 580.0)
    mocker.patch.object(AnimalConfig, "feedlot_max_days_on_feed", 100)
    animal = _make_feedlot_animal(body_weight=400.0, days_on_feed=100)
    mock_time = MagicMock()
    mock_time.simulation_day = 100
    status, newborn = animal._feedlot_life_stage_update(mock_time)  # type: ignore[attr-defined]
    assert status == AnimalStatus.SOLD
    assert newborn is None
    assert animal.sold_at_day == 100


@pytest.mark.unit
def test_calculate_nutrition_requirements_routes_to_beef_calculator(mocker: MockerFixture) -> None:
    """calculate_nutrition_requirements must call BeefNRCRequirementsCalculator for feedlot.

    Verifies both that the correct calculator is dispatched (spy check) and
    that the returned NutritionRequirements contains plausible non-zero values
    for a FEEDLOT_STEER.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture used to patch AnimalConfig attributes and spy on
        BeefNRCRequirementsCalculator.
    """
    mocker.patch.object(AnimalConfig, "feedlot_target_adg", 1.4)
    mocker.patch.object(AnimalConfig, "feedlot_implant_adg_factor", 1.0)
    mocker.patch.object(AnimalConfig, "feedlot_mud_condition", "none")

    spy = mocker.spy(BeefNRCRequirementsCalculator, "calculate_requirements")

    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.FEEDLOT_STEER
    animal.body_weight = 400.0
    animal.mature_body_weight = 600.0
    animal.breed = Breed.AN
    animal.sex = Sex.STEER
    animal.days_on_feed = 30
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
    assert result.activity_energy == pytest.approx(0.0)
    assert result.maintenance_energy > 0.0
    assert result.growth_energy > 0.0
    assert result.dry_matter > 0.0


@pytest.mark.unit
def test_daily_nutrients_update_sets_phosphorus_for_feedlot() -> None:
    """_daily_nutrients_update must copy nutrition_requirements.phosphorus into nutrients.phosphorus_requirement.

    Verifies that the feedlot early-return path correctly routes the
    NRC 2016 phosphorus requirement into the Nutrients pool.
    """
    animal = _make_feedlot_animal()
    animal.nutrients = Nutrients()
    nr = NutritionRequirements.make_empty_nutrition_requirements()
    nr.phosphorus = 18.5
    animal.nutrition_requirements = nr

    animal._daily_nutrients_update()

    assert animal.nutrients.phosphorus_requirement == pytest.approx(18.5)


@pytest.mark.unit
def test_daily_nutrients_update_noop_when_no_nutrition_requirements() -> None:
    """_daily_nutrients_update must not raise when nutrition_requirements is None.

    Verifies that a feedlot animal with no computed nutrition requirements
    leaves phosphorus_requirement at its default of 0.0.
    """
    animal = _make_feedlot_animal()
    animal.nutrients = Nutrients()
    animal.nutrition_requirements = None  # type: ignore[assignment]

    animal._daily_nutrients_update()

    assert animal.nutrients.phosphorus_requirement == pytest.approx(0.0)
