"""Tests for the COW_CALF_STOCKER_FEEDLOT full-chain grouping scenario.

Verifies:
- The scenario reuses the six existing AnimalCombination members
- Every combination maps to a distinct, non-shared list object
- BEEF_COW appears under both BEEF_COW_CALF_PAIR and BEEF_GESTATING by design
- find_animal_combination raises NotImplementedError for BEEF_COW, matching
  BEEF_COW_CALF_HERD — the Step 7 runtime-dispatch hook
- Every combination in the scenario resolves to a ration constraint set
- BEEF_STOCKER_ONLY and BEEF_COW_CALF_HERD are unchanged
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_COW_CALF_COMBINATIONS: tuple[AnimalCombination, ...] = (
    AnimalCombination.BEEF_COW_CALF_PAIR,
    AnimalCombination.BEEF_GESTATING,
    AnimalCombination.BEEF_REPLACEMENT,
    AnimalCombination.BEEF_BULL_BATTERY,
)

_EXPECTED_COMBINATIONS: tuple[AnimalCombination, ...] = _COW_CALF_COMBINATIONS + (
    AnimalCombination.BEEF_STOCKER,
    AnimalCombination.FEEDLOT_FINISHING,
)

_EXPECTED_ANIMAL_TYPES: frozenset[AnimalType] = frozenset(
    {
        AnimalType.BEEF_COW,
        AnimalType.BEEF_CALF,
        AnimalType.BEEF_HEIFER_REPLACEMENT,
        AnimalType.BEEF_BULL,
        AnimalType.BEEF_STOCKER_STEER,
        AnimalType.BEEF_STOCKER_HEIFER,
        AnimalType.FEEDLOT_STEER,
        AnimalType.FEEDLOT_HEIFER,
    }
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_animal(animal_type: AnimalType) -> Animal:
    """Construct a minimal Animal carrying only the attribute the lookup reads.

    Parameters
    ----------
    animal_type : AnimalType
        The type the grouping scenario should dispatch on.

    Returns
    -------
    Animal
        A bare Animal with animal_type set.

    """
    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = animal_type
    return animal


# ---------------------------------------------------------------------------
# Scenario membership
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_cow_calf_stocker_feedlot_scenario_exists() -> None:
    """AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT must exist."""
    assert hasattr(AnimalGroupingScenario, "COW_CALF_STOCKER_FEEDLOT")


@pytest.mark.unit
def test_scenario_has_exactly_six_combinations() -> None:
    """The scenario must use six combinations, not three."""
    assert len(AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value) == 6


@pytest.mark.unit
@pytest.mark.parametrize("combination", _EXPECTED_COMBINATIONS)
def test_scenario_contains_expected_combination(combination: AnimalCombination) -> None:
    """Each of the six expected combinations must be a key in the scenario."""
    assert combination in AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value


@pytest.mark.unit
def test_scenario_adds_no_new_animal_combination_member() -> None:
    """The scenario must reuse existing members; no BEEF_COW_CALF member is introduced."""
    assert not hasattr(AnimalCombination, "BEEF_COW_CALF")


@pytest.mark.unit
def test_scenario_covers_all_eight_animal_types() -> None:
    """All eight expected AnimalTypes must appear across the six combinations."""
    covered: set[AnimalType] = set()
    for animal_types in AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value.values():
        covered.update(animal_types)
    assert covered == _EXPECTED_ANIMAL_TYPES


@pytest.mark.unit
def test_stocker_combination_maps_both_stocker_types() -> None:
    """BEEF_STOCKER must map both stocker types."""
    stocker_types = AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value[AnimalCombination.BEEF_STOCKER]
    assert set(stocker_types) == {AnimalType.BEEF_STOCKER_STEER, AnimalType.BEEF_STOCKER_HEIFER}


@pytest.mark.unit
def test_feedlot_combination_maps_both_feedlot_types() -> None:
    """FEEDLOT_FINISHING must map both feedlot types."""
    feedlot_types = AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value[AnimalCombination.FEEDLOT_FINISHING]
    assert set(feedlot_types) == {AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER}


# ---------------------------------------------------------------------------
# BEEF_COW dual membership — expected, not a defect
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_beef_cow_appears_under_cow_calf_pair() -> None:
    """BEEF_COW must be listed under BEEF_COW_CALF_PAIR."""
    pair_types = AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value[AnimalCombination.BEEF_COW_CALF_PAIR]
    assert AnimalType.BEEF_COW in pair_types


@pytest.mark.unit
def test_beef_cow_appears_under_gestating() -> None:
    """BEEF_COW must also be listed under BEEF_GESTATING, matching BEEF_COW_CALF_HERD."""
    gestating_types = AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value[AnimalCombination.BEEF_GESTATING]
    assert AnimalType.BEEF_COW in gestating_types


@pytest.mark.unit
def test_beef_cow_is_the_only_type_in_two_combinations() -> None:
    """Only BEEF_COW may appear under more than one combination."""
    counts: dict[AnimalType, int] = {}
    for animal_types in AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value.values():
        for animal_type in animal_types:
            counts[animal_type] = counts.get(animal_type, 0) + 1
    duplicated = {animal_type for animal_type, count in counts.items() if count > 1}
    assert duplicated == {AnimalType.BEEF_COW}


# ---------------------------------------------------------------------------
# Distinct, non-shared list objects
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_each_combination_maps_to_a_distinct_list_object() -> None:
    """No two combinations may share the same list object."""
    lists = list(AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value.values())
    identities = [id(animal_types) for animal_types in lists]
    assert len(set(identities)) == len(lists)


@pytest.mark.unit
def test_scenario_lists_are_not_shared_with_beef_stocker_only() -> None:
    """The stocker list must not be the same object BEEF_STOCKER_ONLY holds."""
    new_list = AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value[AnimalCombination.BEEF_STOCKER]
    existing_list = AnimalGroupingScenario.BEEF_STOCKER_ONLY.value[AnimalCombination.BEEF_STOCKER]
    assert new_list is not existing_list


@pytest.mark.unit
@pytest.mark.parametrize("combination", _COW_CALF_COMBINATIONS)
def test_scenario_lists_are_not_shared_with_beef_cow_calf_herd(combination: AnimalCombination) -> None:
    """Cow-calf lists must not be the same objects BEEF_COW_CALF_HERD holds."""
    new_list = AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.value[combination]
    existing_list = AnimalGroupingScenario.BEEF_COW_CALF_HERD.value[combination]
    assert new_list is not existing_list


# ---------------------------------------------------------------------------
# find_animal_combination — Step 7 dispatch guard
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_find_animal_combination_raises_for_beef_cow() -> None:
    """BEEF_COW must raise NotImplementedError — runtime dispatch is Step 7 scope."""
    animal = _make_animal(AnimalType.BEEF_COW)
    with pytest.raises(NotImplementedError, match="reproduction-state"):
        AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.find_animal_combination(animal)


@pytest.mark.unit
def test_find_animal_combination_still_raises_for_beef_cow_calf_herd() -> None:
    """The pre-existing BEEF_COW_CALF_HERD guard must be unchanged."""
    animal = _make_animal(AnimalType.BEEF_COW)
    with pytest.raises(NotImplementedError, match="reproduction-state"):
        AnimalGroupingScenario.BEEF_COW_CALF_HERD.find_animal_combination(animal)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("animal_type", "expected"),
    [
        (AnimalType.BEEF_CALF, AnimalCombination.BEEF_COW_CALF_PAIR),
        (AnimalType.BEEF_HEIFER_REPLACEMENT, AnimalCombination.BEEF_REPLACEMENT),
        (AnimalType.BEEF_BULL, AnimalCombination.BEEF_BULL_BATTERY),
        (AnimalType.BEEF_STOCKER_STEER, AnimalCombination.BEEF_STOCKER),
        (AnimalType.BEEF_STOCKER_HEIFER, AnimalCombination.BEEF_STOCKER),
        (AnimalType.FEEDLOT_STEER, AnimalCombination.FEEDLOT_FINISHING),
        (AnimalType.FEEDLOT_HEIFER, AnimalCombination.FEEDLOT_FINISHING),
    ],
)
def test_find_animal_combination_resolves_non_cow_types(animal_type: AnimalType, expected: AnimalCombination) -> None:
    """Every non-BEEF_COW type must resolve to its combination without raising."""
    animal = _make_animal(animal_type)
    assert AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT.find_animal_combination(animal) is expected


# ---------------------------------------------------------------------------
# Ration optimiser — every combination must resolve to a constraint set
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("combination", _EXPECTED_COMBINATIONS)
def test_select_constraints_accepts_every_combination(combination: AnimalCombination) -> None:
    """Each combination must return a constraint set rather than raising ValueError."""
    optimizer = RationOptimizer()
    assert optimizer._select_constraints(combination) is not None


# ---------------------------------------------------------------------------
# Regression guards — existing scenarios unchanged
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_beef_stocker_only_is_unchanged() -> None:
    """BEEF_STOCKER_ONLY must still hold exactly one combination with both stocker types."""
    scenario = AnimalGroupingScenario.BEEF_STOCKER_ONLY.value
    assert len(scenario) == 1
    assert set(scenario[AnimalCombination.BEEF_STOCKER]) == {
        AnimalType.BEEF_STOCKER_STEER,
        AnimalType.BEEF_STOCKER_HEIFER,
    }


@pytest.mark.unit
def test_beef_cow_calf_herd_is_unchanged() -> None:
    """BEEF_COW_CALF_HERD must still hold exactly its four original combinations."""
    scenario = AnimalGroupingScenario.BEEF_COW_CALF_HERD.value
    assert set(scenario.keys()) == set(_COW_CALF_COMBINATIONS)
    assert set(scenario[AnimalCombination.BEEF_COW_CALF_PAIR]) == {
        AnimalType.BEEF_COW,
        AnimalType.BEEF_CALF,
    }


@pytest.mark.unit
def test_beef_stocker_only_lookup_still_resolves() -> None:
    """BEEF_STOCKER_ONLY dispatch must be unaffected by the new scenario."""
    animal = _make_animal(AnimalType.BEEF_STOCKER_STEER)
    result = AnimalGroupingScenario.BEEF_STOCKER_ONLY.find_animal_combination(animal)
    assert result is AnimalCombination.BEEF_STOCKER


# ---------------------------------------------------------------------------
# Selection guard — the mapping is correct, but a run cannot use it yet
# ---------------------------------------------------------------------------


@pytest.mark.component
def test_selecting_the_full_chain_scenario_for_a_run_raises() -> None:
    """The combined scenario cannot be selected to drive a simulation.

    A replacement heifer promoting to BEEF_COW on first calving reaches pen
    assignment, which cannot resolve BEEF_COW without runtime dispatch on
    reproduction state. Failing at selection beats failing part-way through
    a multi-year run.
    """
    with pytest.raises(NotImplementedError, match="reproduction state"):
        HerdManager.set_animal_grouping_scenario(AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT)


@pytest.mark.component
def test_selection_error_names_the_usable_scenarios() -> None:
    """The message says what to use instead, not merely that this is unsupported."""
    with pytest.raises(NotImplementedError) as excinfo:
        HerdManager.set_animal_grouping_scenario(AnimalGroupingScenario.COW_CALF_STOCKER_FEEDLOT)
    message = str(excinfo.value)
    assert "BEEF_COW_CALF_HERD" in message
    assert "BEEF_STOCKER_ONLY" in message


@pytest.mark.component
@pytest.mark.regression
@pytest.mark.parametrize(
    "scenario",
    [
        AnimalGroupingScenario.BEEF_COW_CALF_HERD,
        AnimalGroupingScenario.BEEF_STOCKER_ONLY,
        AnimalGroupingScenario.FEEDLOT_ONLY,
        AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW,
    ],
)
def test_every_other_scenario_is_still_selectable(scenario: AnimalGroupingScenario) -> None:
    """The guard is scenario-specific, not a blanket block."""
    was_set = hasattr(HerdManager, "ANIMAL_GROUPING_SCENARIO")
    saved = HerdManager.ANIMAL_GROUPING_SCENARIO if was_set else None
    try:
        HerdManager.set_animal_grouping_scenario(scenario)
        assert HerdManager.ANIMAL_GROUPING_SCENARIO is scenario
    finally:
        if saved is not None:
            HerdManager.ANIMAL_GROUPING_SCENARIO = saved
        elif was_set is False:
            del HerdManager.ANIMAL_GROUPING_SCENARIO


@pytest.mark.component
@pytest.mark.regression
def test_beef_cow_is_unresolvable_under_the_cow_calf_scenario_too() -> None:
    """BEEF_COW resolution is missing in BEEF_COW_CALF_HERD as well.

    Pins the scope of the gap: the combined scenario is not uniquely affected,
    so the selection guard bounds what this change adds rather than fixing the
    underlying dispatch. BEEF_COW_CALF_HERD carries the same unresolved state
    and predates this work.
    """
    animal = MagicMock()
    animal.animal_type = AnimalType.BEEF_COW
    with pytest.raises(NotImplementedError, match="reproduction-state"):
        AnimalGroupingScenario.BEEF_COW_CALF_HERD.find_animal_combination(animal)
