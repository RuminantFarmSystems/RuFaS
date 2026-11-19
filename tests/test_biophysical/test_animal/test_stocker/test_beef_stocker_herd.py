"""Tests for Step 7: Stocker herd cohort lists, reporter, nutrients branch, and validator.

Lesson 1 regression guard (distinct list separation) is the FIRST test.

Groups:
  1 — Distinct-list regression (BEEF_STOCKER_STEER ∩ BEEF_STOCKER_HEIFER = ∅)
  2 — HerdFactory.beef_stocker_animals ClassVar and _initialize_beef_stocker_herd guard
  3 — animals_by_type includes stocker keys, backed by instance lists
  4 — _remove_animal_from_current_array removes from stocker lists
  5 — _add_animal_to_new_array routes BEEF_STOCKER_STEER / BEEF_STOCKER_HEIFER correctly
  6 — _process_daily_herd_updates stocker loop: reporter fires at exit (SOLD and LIFE_STAGE_CHANGED)
  7 — validate_beef_stocker_config: numeric, cross-field, diet_system, and None-guard checks
  8 — _daily_nutrients_update stocker branch sets phosphorus_requirement from nutrition_requirements

RED before Step 7 implementation; GREEN after.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.data_validator import DataValidator
from RUFAS.rufas_time import RufasTime

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_time_mock(simulation_day: int = 1) -> MagicMock:
    """Return a RufasTime mock with simulation_day set.

    Parameters
    ----------
    simulation_day : int, optional
        Day counter to assign to the mock.  Default 1.

    Returns
    -------
    MagicMock
        RufasTime mock with simulation_day set.
    """
    t: MagicMock = MagicMock(spec=RufasTime)
    t.simulation_day = simulation_day
    return t


def _make_animal_mock(
    animal_type: AnimalType,
    status: AnimalStatus = AnimalStatus.REMAIN,
) -> MagicMock:
    """Return an Animal mock whose daily_routines returns the given status.

    Parameters
    ----------
    animal_type : AnimalType
        The animal_type to assign to the mock.
    status : AnimalStatus, optional
        The animal_status embedded in the returned DailyRoutinesOutput.

    Returns
    -------
    MagicMock
        Animal mock with daily_routines returning a DailyRoutinesOutput.
    """
    animal: MagicMock = MagicMock()
    animal.animal_type = animal_type
    output = DailyRoutinesOutput(herd_reproduction_statistics=HerdReproductionStatistics())
    output.animal_status = status
    animal.daily_routines.return_value = output
    return animal


def _make_herd_manager_stub(
    beef_stocker_steers: list[MagicMock] | None = None,
    beef_stocker_heifers: list[MagicMock] | None = None,
) -> HerdManager:
    """Return a HerdManager stub with all list attrs pre-set (bypasses __init__).

    Parameters
    ----------
    beef_stocker_steers : list[MagicMock] | None, optional
        Initial steer list; defaults to empty.
    beef_stocker_heifers : list[MagicMock] | None, optional
        Initial heifer list; defaults to empty.

    Returns
    -------
    HerdManager
        Minimally constructed HerdManager with all list attributes initialised.
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
    hm.beef_stocker_steers = beef_stocker_steers if beef_stocker_steers is not None else []  # type: ignore[assignment]
    hm.beef_stocker_heifers = (
        beef_stocker_heifers if beef_stocker_heifers is not None else []  # type: ignore[assignment]
    )
    hm.herd_reproduction_statistics = HerdReproductionStatistics()
    hm.herd_statistics = MagicMock()
    hm.herd_statistics.animals_deaths_by_stage = {}
    return hm


# ---------------------------------------------------------------------------
# Group 1 — Distinct-list regression (LESSON 1 FIRST)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_beef_stocker_lists_are_distinct_non_overlapping() -> None:
    """BEEF_STOCKER_STEER and BEEF_STOCKER_HEIFER must live in separate, non-overlapping lists.

    This is the Lesson 1 regression guard: both stocker types must resolve to DISTINCT list
    objects in HerdManager.animals_by_type, never pooled.  The steer list must contain only
    BEEF_STOCKER_STEER animals and the heifer list only BEEF_STOCKER_HEIFER animals.
    """
    steer: MagicMock = MagicMock()
    steer.animal_type = AnimalType.BEEF_STOCKER_STEER
    heifer: MagicMock = MagicMock()
    heifer.animal_type = AnimalType.BEEF_STOCKER_HEIFER

    hm = _make_herd_manager_stub(beef_stocker_steers=[steer], beef_stocker_heifers=[heifer])

    result = hm.animals_by_type

    assert AnimalType.BEEF_STOCKER_STEER in result, "BEEF_STOCKER_STEER missing from animals_by_type"
    assert AnimalType.BEEF_STOCKER_HEIFER in result, "BEEF_STOCKER_HEIFER missing from animals_by_type"

    assert steer in result[AnimalType.BEEF_STOCKER_STEER]
    assert heifer not in result[AnimalType.BEEF_STOCKER_STEER], "Heifer must NOT appear in steers list"

    assert heifer in result[AnimalType.BEEF_STOCKER_HEIFER]
    assert steer not in result[AnimalType.BEEF_STOCKER_HEIFER], "Steer must NOT appear in heifers list"

    assert (
        result[AnimalType.BEEF_STOCKER_STEER] is not result[AnimalType.BEEF_STOCKER_HEIFER]
    ), "Stocker steer and heifer lists must be distinct objects, not pooled"

    assert result[AnimalType.BEEF_STOCKER_STEER] is hm.beef_stocker_steers
    assert result[AnimalType.BEEF_STOCKER_HEIFER] is hm.beef_stocker_heifers


# ---------------------------------------------------------------------------
# Group 2 — HerdFactory ClassVar and _initialize_beef_stocker_herd guard
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_herd_factory_has_beef_stocker_animals_class_attr() -> None:
    """HerdFactory must expose a beef_stocker_animals class-level list attribute.

    Verifies that the factory uses the same ClassVar staging pattern as
    feedlot_animals and beef_cow_calf_animals so HerdManager can iterate
    at init time.
    """
    assert hasattr(HerdFactory, "beef_stocker_animals")
    assert isinstance(HerdFactory.beef_stocker_animals, list)


@pytest.mark.unit
@pytest.mark.parametrize("bad_value", [None, [], "string", 42])
def test_initialize_beef_stocker_herd_non_dict_config_returns_empty(bad_value: object) -> None:
    """_initialize_beef_stocker_herd must return [] when config value is not a dict.

    Verifies the isinstance(cfg, dict) guard prevents .get() on non-dict
    values such as None, a list, or an int.

    Parameters
    ----------
    bad_value : object
        Non-dict value returned by InputManager.get_data.

    Returns
    -------
    None

    """
    hf: HerdFactory = HerdFactory.__new__(HerdFactory)
    hf.im = MagicMock()
    hf.time = _make_time_mock()
    hf.im.get_data.return_value = bad_value
    result = hf._initialize_beef_stocker_herd()
    assert result == []


@pytest.mark.unit
@pytest.mark.parametrize(("n_steers", "n_heifers"), [(-1, 0), (0, -1), (-5, -3)])
def test_initialize_beef_stocker_herd_raises_on_negative_counts(n_steers: int, n_heifers: int) -> None:
    """_initialize_beef_stocker_herd must raise ValueError for negative cohort counts.

    Parameters
    ----------
    n_steers : int
        Negative steer count.
    n_heifers : int
        Negative heifer count.

    Returns
    -------
    None

    """
    hf: HerdFactory = HerdFactory.__new__(HerdFactory)
    hf.im = MagicMock()
    hf.time = _make_time_mock()
    hf.im.get_data.return_value = {"num_steers": n_steers, "num_heifers": n_heifers, "entry_weight_kg": 250.0}
    with pytest.raises(ValueError, match="non-negative"):
        hf._initialize_beef_stocker_herd()


@pytest.mark.unit
@pytest.mark.parametrize("bad_weight", [0.0, -10.0, float("nan"), float("inf")])
def test_initialize_beef_stocker_herd_raises_on_invalid_entry_weight(bad_weight: float) -> None:
    """_initialize_beef_stocker_herd must raise ValueError for non-positive or non-finite entry_weight.

    Parameters
    ----------
    bad_weight : float
        Invalid entry weight value.

    Returns
    -------
    None

    """
    hf: HerdFactory = HerdFactory.__new__(HerdFactory)
    hf.im = MagicMock()
    hf.time = _make_time_mock()
    hf.im.get_data.return_value = {"num_steers": 1, "num_heifers": 0, "entry_weight_kg": bad_weight}
    with pytest.raises(ValueError, match="entry_weight"):
        hf._initialize_beef_stocker_herd()


# ---------------------------------------------------------------------------
# Group 3 — animals_by_type includes stocker keys
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_animals_by_type_returns_distinct_stocker_lists() -> None:
    """animals_by_type must include BEEF_STOCKER_STEER and BEEF_STOCKER_HEIFER, each backed by its own list.

    Verifies each stocker type maps to its OWN named instance list — never pooled,
    and never aliased to beef_cows or feedlot_animals.
    """
    steer: MagicMock = MagicMock()
    steer.animal_type = AnimalType.BEEF_STOCKER_STEER
    heifer: MagicMock = MagicMock()
    heifer.animal_type = AnimalType.BEEF_STOCKER_HEIFER

    hm = _make_herd_manager_stub(beef_stocker_steers=[steer], beef_stocker_heifers=[heifer])

    result = hm.animals_by_type

    assert result[AnimalType.BEEF_STOCKER_STEER] is hm.beef_stocker_steers
    assert result[AnimalType.BEEF_STOCKER_HEIFER] is hm.beef_stocker_heifers

    assert result[AnimalType.BEEF_STOCKER_STEER] is not hm.feedlot_animals
    assert result[AnimalType.BEEF_STOCKER_HEIFER] is not hm.feedlot_animals
    assert result[AnimalType.BEEF_STOCKER_STEER] is not hm.beef_cows
    assert result[AnimalType.BEEF_STOCKER_HEIFER] is not hm.beef_cows


# ---------------------------------------------------------------------------
# Group 4 — _remove_animal_from_current_array removes from stocker lists
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_remove_animal_from_current_array_removes_stocker_steer() -> None:
    """_remove_animal_from_current_array must remove a BEEF_STOCKER_STEER from beef_stocker_steers."""
    steer: MagicMock = MagicMock()
    steer.animal_type = AnimalType.BEEF_STOCKER_STEER
    hm = _make_herd_manager_stub(beef_stocker_steers=[steer])

    hm._remove_animal_from_current_array(steer)

    assert steer not in hm.beef_stocker_steers


@pytest.mark.unit
def test_remove_animal_from_current_array_removes_stocker_heifer() -> None:
    """_remove_animal_from_current_array must remove a BEEF_STOCKER_HEIFER from beef_stocker_heifers."""
    heifer: MagicMock = MagicMock()
    heifer.animal_type = AnimalType.BEEF_STOCKER_HEIFER
    hm = _make_herd_manager_stub(beef_stocker_heifers=[heifer])

    hm._remove_animal_from_current_array(heifer)

    assert heifer not in hm.beef_stocker_heifers


@pytest.mark.unit
def test_remove_stocker_steer_does_not_affect_heifer_list() -> None:
    """Removing a stocker steer must not alter the beef_stocker_heifers list."""
    steer: MagicMock = MagicMock()
    steer.animal_type = AnimalType.BEEF_STOCKER_STEER
    heifer: MagicMock = MagicMock()
    heifer.animal_type = AnimalType.BEEF_STOCKER_HEIFER

    hm = _make_herd_manager_stub(beef_stocker_steers=[steer], beef_stocker_heifers=[heifer])

    hm._remove_animal_from_current_array(steer)

    assert heifer in hm.beef_stocker_heifers, "Heifer list must be unaffected by steer removal"


# ---------------------------------------------------------------------------
# Group 5 — _add_animal_to_new_array routes stocker types correctly
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_add_animal_to_new_array_routes_stocker_steer_to_steer_list() -> None:
    """_add_animal_to_new_array must append a BEEF_STOCKER_STEER to beef_stocker_steers."""
    hm = _make_herd_manager_stub()
    steer: MagicMock = MagicMock()
    steer.animal_type = AnimalType.BEEF_STOCKER_STEER

    hm._add_animal_to_new_array(steer)

    assert steer in hm.beef_stocker_steers
    assert steer not in hm.beef_stocker_heifers
    assert steer not in hm.feedlot_animals


@pytest.mark.unit
def test_add_animal_to_new_array_routes_stocker_heifer_to_heifer_list() -> None:
    """_add_animal_to_new_array must append a BEEF_STOCKER_HEIFER to beef_stocker_heifers."""
    hm = _make_herd_manager_stub()
    heifer: MagicMock = MagicMock()
    heifer.animal_type = AnimalType.BEEF_STOCKER_HEIFER

    hm._add_animal_to_new_array(heifer)

    assert heifer in hm.beef_stocker_heifers
    assert heifer not in hm.beef_stocker_steers
    assert heifer not in hm.feedlot_animals


# ---------------------------------------------------------------------------
# Group 6 — _process_daily_herd_updates stocker loop and reporter
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_process_daily_herd_updates_does_not_call_reporter_for_stocker_sold(mocker: MockerFixture) -> None:
    """report_stocker_performance must NOT be called for stocker animals returning SOLD status.

    Stocker exits via weight-target or max-days both return LIFE_STAGE_CHANGED (→ feedlot).
    There is no direct-sale path; the sold list is structurally unreachable for stockers.
    Only graduated (LIFE_STAGE_CHANGED) animals trigger the reporter.
    """
    sold_steer: MagicMock = _make_animal_mock(AnimalType.BEEF_STOCKER_STEER, AnimalStatus.SOLD)

    hm = _make_herd_manager_stub(beef_stocker_steers=[sold_steer])

    empty_5: tuple[list[Any], list[Any], list[Any], list[Any], list[Any]] = ([], [], [], [], [])
    sold_5: tuple[list[Any], list[Any], list[Any], list[Any], list[Any]] = ([], [sold_steer], [], [], [])

    def _side_effect(time: Any, animals: list[Any]) -> tuple[list[Any], list[Any], list[Any], list[Any], list[Any]]:
        if animals is hm.beef_stocker_steers:
            return sold_5
        return empty_5

    mocker.patch.object(hm, "_perform_daily_routines_for_animals", side_effect=_side_effect)
    mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)
    reporter_spy = mocker.patch.object(AnimalModuleReporter, "report_stocker_performance", return_value=None)

    hm._process_daily_herd_updates(_make_time_mock(simulation_day=10))

    reporter_spy.assert_not_called()


@pytest.mark.unit
def test_process_daily_herd_updates_calls_reporter_for_stocker_graduated(mocker: MockerFixture) -> None:
    """report_stocker_performance must be called for stocker animals exiting via LIFE_STAGE_CHANGED (→ feedlot).

    Verifies the reporter fires from _process_daily_herd_updates for weight-exit graduates,
    not only for sold animals.
    """
    grad_heifer: MagicMock = _make_animal_mock(AnimalType.BEEF_STOCKER_HEIFER, AnimalStatus.LIFE_STAGE_CHANGED)

    hm = _make_herd_manager_stub(beef_stocker_heifers=[grad_heifer])

    empty_5: tuple[list[Any], list[Any], list[Any], list[Any], list[Any]] = ([], [], [], [], [])
    grad_5: tuple[list[Any], list[Any], list[Any], list[Any], list[Any]] = ([grad_heifer], [], [], [], [])

    def _side_effect(time: Any, animals: list[Any]) -> tuple[list[Any], list[Any], list[Any], list[Any], list[Any]]:
        if animals is hm.beef_stocker_heifers:
            return grad_5
        return empty_5

    mocker.patch.object(hm, "_perform_daily_routines_for_animals", side_effect=_side_effect)
    mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)
    reporter_spy = mocker.patch.object(AnimalModuleReporter, "report_stocker_performance", return_value=None)

    hm._process_daily_herd_updates(_make_time_mock(simulation_day=50))

    reporter_spy.assert_called_once_with(grad_heifer, 50)


@pytest.mark.unit
def test_process_daily_herd_updates_reporter_called_for_graduated_from_both_cohorts(mocker: MockerFixture) -> None:
    """report_stocker_performance must fire for graduated animals from both steer and heifer cohort lists.

    Verifies the stocker loop iterates both beef_stocker_steers and beef_stocker_heifers
    and reports every LIFE_STAGE_CHANGED (→ feedlot) graduation.
    """
    grad_steer: MagicMock = _make_animal_mock(AnimalType.BEEF_STOCKER_STEER, AnimalStatus.LIFE_STAGE_CHANGED)
    grad_heifer: MagicMock = _make_animal_mock(AnimalType.BEEF_STOCKER_HEIFER, AnimalStatus.LIFE_STAGE_CHANGED)

    hm = _make_herd_manager_stub(
        beef_stocker_steers=[grad_steer],
        beef_stocker_heifers=[grad_heifer],
    )

    empty_5: tuple[list[Any], list[Any], list[Any], list[Any], list[Any]] = ([], [], [], [], [])

    def _side_effect(time: Any, animals: list[Any]) -> tuple[list[Any], list[Any], list[Any], list[Any], list[Any]]:
        if animals is hm.beef_stocker_steers:
            return ([grad_steer], [], [], [], [])
        if animals is hm.beef_stocker_heifers:
            return ([grad_heifer], [], [], [], [])
        return empty_5

    mocker.patch.object(hm, "_perform_daily_routines_for_animals", side_effect=_side_effect)
    mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)
    reporter_spy = mocker.patch.object(AnimalModuleReporter, "report_stocker_performance", return_value=None)

    hm._process_daily_herd_updates(_make_time_mock(simulation_day=75))

    assert reporter_spy.call_count == 2, f"Expected 2 reporter calls, got {reporter_spy.call_count}"
    called_animals = [c.args[0] for c in reporter_spy.call_args_list]
    assert grad_steer in called_animals
    assert grad_heifer in called_animals


@pytest.mark.unit
def test_process_daily_herd_updates_does_not_call_stocker_reporter_for_remain_animals(
    mocker: MockerFixture,
) -> None:
    """report_stocker_performance must NOT be called for animals that REMAIN in the pen.

    Verifies the reporter only fires at exit, not on every daily tick.
    """
    remain_steer: MagicMock = _make_animal_mock(AnimalType.BEEF_STOCKER_STEER, AnimalStatus.REMAIN)

    hm = _make_herd_manager_stub(beef_stocker_steers=[remain_steer])

    empty_5: tuple[list[Any], list[Any], list[Any], list[Any], list[Any]] = ([], [], [], [], [])
    mocker.patch.object(hm, "_perform_daily_routines_for_animals", return_value=empty_5)
    mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)
    reporter_spy = mocker.patch.object(AnimalModuleReporter, "report_stocker_performance", return_value=None)

    hm._process_daily_herd_updates(_make_time_mock(simulation_day=5))

    reporter_spy.assert_not_called()


@pytest.mark.unit
def test_process_daily_herd_updates_includes_stocker_groups(mocker: MockerFixture) -> None:
    """_process_daily_herd_updates must call _perform_daily_routines_for_animals for both stocker lists.

    Verifies beef_stocker_steers and beef_stocker_heifers are each passed as
    the animals argument in separate calls.
    """
    steer: MagicMock = _make_animal_mock(AnimalType.BEEF_STOCKER_STEER)
    heifer: MagicMock = _make_animal_mock(AnimalType.BEEF_STOCKER_HEIFER)

    hm = _make_herd_manager_stub(beef_stocker_steers=[steer], beef_stocker_heifers=[heifer])

    empty_5: tuple[list[Any], list[Any], list[Any], list[Any], list[Any]] = ([], [], [], [], [])
    routine_spy = mocker.patch.object(hm, "_perform_daily_routines_for_animals", return_value=empty_5)
    mocker.patch.object(AnimalModuleReporter, "report_cow_calf_performance", return_value=None)
    mocker.patch.object(AnimalModuleReporter, "report_stocker_performance", return_value=None)

    hm._process_daily_herd_updates(_make_time_mock())

    called_animals_args = [c.args[1] for c in routine_spy.call_args_list]
    assert any(
        a is hm.beef_stocker_steers for a in called_animals_args
    ), "beef_stocker_steers not passed to _perform_daily_routines_for_animals"
    assert any(
        a is hm.beef_stocker_heifers for a in called_animals_args
    ), "beef_stocker_heifers not passed to _perform_daily_routines_for_animals"


# ---------------------------------------------------------------------------
# Group 7 — validate_beef_stocker_config
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_validate_beef_stocker_config_accepts_valid_config() -> None:
    """validate_beef_stocker_config must not raise for a complete valid config."""
    DataValidator.validate_beef_stocker_config(
        {
            "entry_weight": 180.0,
            "exit_weight": 350.0,
            "max_days": 210,
            "stocker_diet_system": "pasture",
            "target_adg": 0.80,
        }
    )


@pytest.mark.unit
def test_validate_beef_stocker_config_accepts_empty_config() -> None:
    """validate_beef_stocker_config must not raise for an empty config (all keys optional)."""
    DataValidator.validate_beef_stocker_config({})


@pytest.mark.unit
def test_validate_beef_stocker_config_accepts_none_values() -> None:
    """validate_beef_stocker_config must skip checks when values are explicitly None."""
    DataValidator.validate_beef_stocker_config(
        {
            "entry_weight": None,
            "exit_weight": None,
            "max_days": None,
            "stocker_diet_system": None,
            "target_adg": None,
        }
    )


@pytest.mark.unit
@pytest.mark.parametrize("bad_val", [float("nan"), float("inf"), -1.0, 0.0])
def test_validate_beef_stocker_config_rejects_bad_entry_weight(bad_val: float) -> None:
    """validate_beef_stocker_config must raise ValueError for non-positive or non-finite entry_weight."""
    with pytest.raises(ValueError, match="entry_weight"):
        DataValidator.validate_beef_stocker_config({"entry_weight": bad_val})


@pytest.mark.unit
@pytest.mark.parametrize("bad_val", [float("nan"), float("inf"), -5.0, 0.0])
def test_validate_beef_stocker_config_rejects_bad_exit_weight(bad_val: float) -> None:
    """validate_beef_stocker_config must raise ValueError for non-positive or non-finite exit_weight."""
    with pytest.raises(ValueError, match="exit_weight"):
        DataValidator.validate_beef_stocker_config({"exit_weight": bad_val})


@pytest.mark.unit
def test_validate_beef_stocker_config_rejects_exit_weight_not_exceeding_entry() -> None:
    """validate_beef_stocker_config must raise ValueError when exit_weight <= entry_weight."""
    with pytest.raises(ValueError, match="exit_weight must exceed"):
        DataValidator.validate_beef_stocker_config({"entry_weight": 300.0, "exit_weight": 200.0})


@pytest.mark.unit
def test_validate_beef_stocker_config_rejects_exit_weight_equal_to_entry() -> None:
    """validate_beef_stocker_config must raise ValueError when exit_weight == entry_weight."""
    with pytest.raises(ValueError, match="exit_weight must exceed"):
        DataValidator.validate_beef_stocker_config({"entry_weight": 250.0, "exit_weight": 250.0})


@pytest.mark.unit
@pytest.mark.parametrize("bad_days", [0, -1, -100])
def test_validate_beef_stocker_config_rejects_non_positive_max_days(bad_days: int) -> None:
    """validate_beef_stocker_config must raise ValueError for max_days <= 0."""
    with pytest.raises(ValueError, match="max_days"):
        DataValidator.validate_beef_stocker_config({"max_days": bad_days})


@pytest.mark.unit
@pytest.mark.parametrize("system", ["pasture", "drylot_forage"])
def test_validate_beef_stocker_config_accepts_valid_diet_systems(system: str) -> None:
    """validate_beef_stocker_config must not raise for each valid stocker_diet_system value."""
    DataValidator.validate_beef_stocker_config({"stocker_diet_system": system})


@pytest.mark.unit
def test_validate_beef_stocker_config_rejects_invalid_diet_system() -> None:
    """validate_beef_stocker_config must raise ValueError for an unrecognised stocker_diet_system."""
    with pytest.raises(ValueError, match="stocker_diet_system"):
        DataValidator.validate_beef_stocker_config({"stocker_diet_system": "limit_feeding"})


@pytest.mark.unit
@pytest.mark.parametrize("bad_adg", [float("nan"), float("inf"), -0.5, 0.0])
def test_validate_beef_stocker_config_rejects_bad_target_adg(bad_adg: float) -> None:
    """validate_beef_stocker_config must raise ValueError for non-positive or non-finite target_adg."""
    with pytest.raises(ValueError, match="target_adg"):
        DataValidator.validate_beef_stocker_config({"target_adg": bad_adg})


# ---------------------------------------------------------------------------
# Group 8 — _daily_nutrients_update stocker phosphorus branch
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_daily_nutrients_update_stocker_sets_phosphorus_from_nutrition_requirements(
    mocker: MockerFixture,
) -> None:
    """_daily_nutrients_update sets phosphorus_requirement from nutrition_requirements for stocker animals.

    Verifies the stocker early-return branch (mirroring the feedlot branch) routes
    phosphorus correctly without running the dairy phosphorus calculation chain.
    """
    from RUFAS.biophysical.animal.animal import Animal

    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.BEEF_STOCKER_STEER
    animal.nutrients = Nutrients()

    mock_requirements = MagicMock()
    mock_requirements.phosphorus = 12.5
    animal.nutrition_requirements = mock_requirements

    mocker.patch.object(animal.nutrients, "perform_daily_phosphorus_update")

    animal._daily_nutrients_update()

    assert animal.nutrients.phosphorus_requirement == pytest.approx(12.5)
    animal.nutrients.perform_daily_phosphorus_update.assert_not_called()  # type: ignore[attr-defined]


@pytest.mark.unit
def test_daily_nutrients_update_stocker_skips_dairy_phosphorus_chain_when_none_requirements(
    mocker: MockerFixture,
) -> None:
    """_daily_nutrients_update must not raise when nutrition_requirements is None for a stocker animal."""
    from RUFAS.biophysical.animal.animal import Animal

    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.BEEF_STOCKER_HEIFER
    animal.nutrients = Nutrients()
    animal.nutrition_requirements = None  # type: ignore[assignment]

    mocker.patch.object(animal.nutrients, "perform_daily_phosphorus_update")

    animal._daily_nutrients_update()

    animal.nutrients.perform_daily_phosphorus_update.assert_not_called()  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Group 9 — report_stocker_performance unit test
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_report_stocker_performance_reports_correct_metrics(mocker: MockerFixture) -> None:
    """report_stocker_performance must compute and report all 6 output variables correctly.

    Mock animal: days_in_stocker=120, stocker_entry_weight=240.0, body_weight=336.0,
    stocker_cumulative_dmi=960.0.  Expected: total_gain=96.0, adg=0.8, fcr=10.0.

    Parameters
    ----------
    mocker : MockerFixture
        pytest-mock fixture for patching om.add_variable.

    Returns
    -------
    None

    """
    from RUFAS.biophysical.animal.animal import Animal
    from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter, om

    animal: Animal = Animal.__new__(Animal)
    animal.days_in_stocker = 120
    animal.stocker_entry_weight = 240.0
    animal.body_weight = 336.0
    animal.stocker_cumulative_dmi = 960.0

    add_variable_spy = mocker.patch.object(om, "add_variable")

    AnimalModuleReporter.report_stocker_performance(animal, simulation_day=120)

    reported: dict[str, float] = {call.args[0]: call.args[1] for call in add_variable_spy.call_args_list}

    assert reported.get("stocker_days_in_phase") == 120
    assert reported.get("stocker_total_gain_kg") == pytest.approx(96.0)
    assert reported.get("stocker_adg_kg_d") == pytest.approx(0.8)
    assert reported.get("stocker_fcr") == pytest.approx(10.0)
    assert reported.get("stocker_exit_weight_kg") == pytest.approx(336.0)
    assert reported.get("stocker_cumulative_dmi_kg") == pytest.approx(960.0)
