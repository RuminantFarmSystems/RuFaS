"""Tests for beef stocker/backgrounding identity enums: Step 1 of the stocker module.

Covers:
- StockerDietSystem: PASTURE, DRYLOT_FORAGE values and invalid-input rejection
- AnimalType: BEEF_STOCKER_STEER, BEEF_STOCKER_HEIFER values
- AnimalType.is_beef_stocker property (both members True; all others False)
- Mutual exclusivity: stocker types absent from is_feedlot and is_beef_cow_calf
- AnimalCombination.BEEF_STOCKER value
- AnimalGroupingScenario.BEEF_STOCKER_ONLY structure
- animal_constants stocker event strings
"""

import pytest

from RUFAS.biophysical.animal.animal_constants import (
    STOCKER_ARRIVAL,
    STOCKER_EXIT_WEIGHT,
    STOCKER_MAX_DAYS,
    STOCKER_TO_FEEDLOT,
)
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_enums import StockerDietSystem
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType

# ---------------------------------------------------------------------------
# StockerDietSystem — values and invalid-input rejection
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_diet_system_pasture_value() -> None:
    """StockerDietSystem.PASTURE value must be 'pasture'."""
    assert StockerDietSystem.PASTURE.value == "pasture"


@pytest.mark.unit
def test_stocker_diet_system_drylot_forage_value() -> None:
    """StockerDietSystem.DRYLOT_FORAGE value must be 'drylot_forage'."""
    assert StockerDietSystem.DRYLOT_FORAGE.value == "drylot_forage"


@pytest.mark.unit
def test_stocker_diet_system_invalid_raises_value_error() -> None:
    """Constructing StockerDietSystem from an invalid string must raise ValueError."""
    with pytest.raises(ValueError, match="is not a valid StockerDietSystem"):
        StockerDietSystem("grass_only")


@pytest.mark.unit
def test_stocker_diet_system_pasture_roundtrip() -> None:
    """StockerDietSystem('pasture') round-trips to PASTURE member."""
    assert StockerDietSystem("pasture") is StockerDietSystem.PASTURE


@pytest.mark.unit
def test_stocker_diet_system_drylot_roundtrip() -> None:
    """StockerDietSystem('drylot_forage') round-trips to DRYLOT_FORAGE member."""
    assert StockerDietSystem("drylot_forage") is StockerDietSystem.DRYLOT_FORAGE


@pytest.mark.unit
def test_stocker_diet_system_exactly_three_members() -> None:
    """StockerDietSystem must have exactly three members (pasture, drylot_forage, limit_feed)."""
    assert len(StockerDietSystem) == 3


# ---------------------------------------------------------------------------
# AnimalType — new stocker members exist
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_beef_stocker_steer_member_exists() -> None:
    """AnimalType.BEEF_STOCKER_STEER must exist."""
    assert hasattr(AnimalType, "BEEF_STOCKER_STEER")


@pytest.mark.unit
def test_beef_stocker_heifer_member_exists() -> None:
    """AnimalType.BEEF_STOCKER_HEIFER must exist."""
    assert hasattr(AnimalType, "BEEF_STOCKER_HEIFER")


@pytest.mark.unit
def test_beef_stocker_steer_value() -> None:
    """BEEF_STOCKER_STEER value must be 'BeefStockerSteer' (CamelCase convention)."""
    assert AnimalType.BEEF_STOCKER_STEER.value == "BeefStockerSteer"


@pytest.mark.unit
def test_beef_stocker_heifer_value() -> None:
    """BEEF_STOCKER_HEIFER value must be 'BeefStockerHeifer'."""
    assert AnimalType.BEEF_STOCKER_HEIFER.value == "BeefStockerHeifer"


# ---------------------------------------------------------------------------
# AnimalType.is_beef_stocker — True for stocker types
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "animal_type",
    [AnimalType.BEEF_STOCKER_STEER, AnimalType.BEEF_STOCKER_HEIFER],
)
def test_is_beef_stocker_true(animal_type: AnimalType) -> None:
    """is_beef_stocker returns True for BEEF_STOCKER_STEER and BEEF_STOCKER_HEIFER."""
    assert animal_type.is_beef_stocker is True


# ---------------------------------------------------------------------------
# AnimalType.is_beef_stocker — False for all pre-existing types
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "animal_type",
    [
        AnimalType.CALF,
        AnimalType.HEIFER_I,
        AnimalType.HEIFER_II,
        AnimalType.HEIFER_III,
        AnimalType.DRY_COW,
        AnimalType.LAC_COW,
        AnimalType.FEEDLOT_STEER,
        AnimalType.FEEDLOT_HEIFER,
        AnimalType.BEEF_CALF,
        AnimalType.BEEF_HEIFER_REPLACEMENT,
        AnimalType.BEEF_COW,
        AnimalType.BEEF_BULL,
    ],
)
def test_is_beef_stocker_false_for_all_non_stocker_types(animal_type: AnimalType) -> None:
    """is_beef_stocker returns False for every non-stocker AnimalType."""
    assert animal_type.is_beef_stocker is False


# ---------------------------------------------------------------------------
# Mutual exclusivity — stocker types absent from is_feedlot and is_beef_cow_calf
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "animal_type",
    [AnimalType.BEEF_STOCKER_STEER, AnimalType.BEEF_STOCKER_HEIFER],
)
def test_stocker_not_feedlot_not_cow_calf_not_heifer_not_cow(animal_type: AnimalType) -> None:
    """Stocker types must not set is_feedlot, is_beef_cow_calf, is_heifer, or is_cow."""
    assert animal_type.is_feedlot is False
    assert animal_type.is_beef_cow_calf is False
    assert animal_type.is_heifer is False
    assert animal_type.is_cow is False


@pytest.mark.unit
def test_all_animal_types_is_beef_stocker_consistent() -> None:
    """Every AnimalType.is_beef_stocker is True iff the type is a stocker type."""
    expected_stocker = {AnimalType.BEEF_STOCKER_STEER, AnimalType.BEEF_STOCKER_HEIFER}
    for animal_type in AnimalType:
        expected = animal_type in expected_stocker
        assert (
            animal_type.is_beef_stocker == expected
        ), f"Unexpected is_beef_stocker={animal_type.is_beef_stocker} for {animal_type}"


@pytest.mark.unit
def test_at_most_one_category_flag_per_type() -> None:
    """For every AnimalType, at most one of is_feedlot/is_beef_cow_calf/is_beef_stocker/is_heifer/is_cow is True."""
    for member in AnimalType:
        flags = [member.is_feedlot, member.is_beef_cow_calf, member.is_beef_stocker, member.is_heifer, member.is_cow]
        assert sum(flags) <= 1, f"{member}: more than one category flag is True: {flags}"


# ---------------------------------------------------------------------------
# AnimalCombination.BEEF_STOCKER
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_beef_stocker_combination_exists() -> None:
    """AnimalCombination.BEEF_STOCKER must exist."""
    assert hasattr(AnimalCombination, "BEEF_STOCKER")


@pytest.mark.unit
def test_beef_stocker_combination_value() -> None:
    """AnimalCombination.BEEF_STOCKER value must be 'beef_stocker'."""
    assert AnimalCombination.BEEF_STOCKER.value == "beef_stocker"


# ---------------------------------------------------------------------------
# AnimalGroupingScenario.BEEF_STOCKER_ONLY
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_beef_stocker_only_scenario_exists() -> None:
    """AnimalGroupingScenario.BEEF_STOCKER_ONLY must exist."""
    assert hasattr(AnimalGroupingScenario, "BEEF_STOCKER_ONLY")


@pytest.mark.unit
def test_beef_stocker_only_contains_beef_stocker_combination() -> None:
    """BEEF_STOCKER_ONLY maps AnimalCombination.BEEF_STOCKER."""
    scenario = AnimalGroupingScenario.BEEF_STOCKER_ONLY
    assert AnimalCombination.BEEF_STOCKER in scenario.value


@pytest.mark.unit
def test_beef_stocker_only_maps_both_stocker_types() -> None:
    """BEEF_STOCKER_ONLY must map BEEF_STOCKER to both BEEF_STOCKER_STEER and BEEF_STOCKER_HEIFER."""
    scenario = AnimalGroupingScenario.BEEF_STOCKER_ONLY
    stocker_types = scenario.value[AnimalCombination.BEEF_STOCKER]
    assert AnimalType.BEEF_STOCKER_STEER in stocker_types
    assert AnimalType.BEEF_STOCKER_HEIFER in stocker_types


# ---------------------------------------------------------------------------
# animal_constants — stocker event strings
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stocker_arrival_constant() -> None:
    """STOCKER_ARRIVAL event string must be 'stocker_arrival'."""
    assert STOCKER_ARRIVAL == "stocker_arrival"


@pytest.mark.unit
def test_stocker_exit_weight_constant() -> None:
    """STOCKER_EXIT_WEIGHT event string must be 'stocker_exit_weight_reached'."""
    assert STOCKER_EXIT_WEIGHT == "stocker_exit_weight_reached"


@pytest.mark.unit
def test_stocker_max_days_constant() -> None:
    """STOCKER_MAX_DAYS event string must be 'stocker_max_days_reached'."""
    assert STOCKER_MAX_DAYS == "stocker_max_days_reached"


@pytest.mark.unit
def test_stocker_to_feedlot_constant() -> None:
    """STOCKER_TO_FEEDLOT event string must be 'stocker_transferred_to_feedlot'."""
    assert STOCKER_TO_FEEDLOT == "stocker_transferred_to_feedlot"
