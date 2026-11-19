"""Tests for beef cow-calf identity enums: Step 1 of the cow-calf module.

Covers:
- AnimalType: BEEF_CALF, BEEF_HEIFER_REPLACEMENT, BEEF_COW, BEEF_BULL
- AnimalType.is_beef_cow_calf property (all 4 members, exclusivity vs dairy/feedlot)
- AnimalCombination: BEEF_COW_CALF_PAIR, BEEF_GESTATING, BEEF_REPLACEMENT, BEEF_BULL_BATTERY
- AnimalGroupingScenario.BEEF_COW_CALF_HERD scenario structure
"""

import pytest

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario

# ---------------------------------------------------------------------------
# AnimalType — new beef cow-calf members exist
# ---------------------------------------------------------------------------


def test_beef_calf_member_exists() -> None:
    """AnimalType.BEEF_CALF exists with the expected string value."""
    assert AnimalType.BEEF_CALF.value == "BeefCalf"


def test_beef_heifer_replacement_member_exists() -> None:
    """AnimalType.BEEF_HEIFER_REPLACEMENT exists with the expected string value."""
    assert AnimalType.BEEF_HEIFER_REPLACEMENT.value == "BeefHeiferReplacement"


def test_beef_cow_member_exists() -> None:
    """AnimalType.BEEF_COW exists with the expected string value."""
    assert AnimalType.BEEF_COW.value == "BeefCow"


def test_beef_bull_member_exists() -> None:
    """AnimalType.BEEF_BULL exists with the expected string value."""
    assert AnimalType.BEEF_BULL.value == "BeefBull"


# ---------------------------------------------------------------------------
# AnimalType.is_beef_cow_calf — True for all 4 new members
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "animal_type",
    [
        AnimalType.BEEF_CALF,
        AnimalType.BEEF_HEIFER_REPLACEMENT,
        AnimalType.BEEF_COW,
        AnimalType.BEEF_BULL,
    ],
)
def test_is_beef_cow_calf_true(animal_type: AnimalType) -> None:
    """is_beef_cow_calf returns True for all four beef cow-calf types."""
    assert animal_type.is_beef_cow_calf is True


# ---------------------------------------------------------------------------
# AnimalType.is_beef_cow_calf — False for all non-beef-cow-calf types
# ---------------------------------------------------------------------------


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
    ],
)
def test_is_beef_cow_calf_false_for_non_beef_cow_calf_types(animal_type: AnimalType) -> None:
    """is_beef_cow_calf returns False for all dairy and feedlot types."""
    assert animal_type.is_beef_cow_calf is False


# ---------------------------------------------------------------------------
# Mutual exclusivity: beef cow-calf types must not trigger dairy properties
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "animal_type",
    [
        AnimalType.BEEF_CALF,
        AnimalType.BEEF_HEIFER_REPLACEMENT,
        AnimalType.BEEF_COW,
        AnimalType.BEEF_BULL,
    ],
)
def test_beef_cow_calf_types_not_heifer_not_cow_not_feedlot(animal_type: AnimalType) -> None:
    """Beef cow-calf types must not set is_heifer, is_cow, or is_feedlot."""
    assert animal_type.is_heifer is False
    assert animal_type.is_cow is False
    assert animal_type.is_feedlot is False


# ---------------------------------------------------------------------------
# AnimalCombination — new beef cow-calf members exist
# ---------------------------------------------------------------------------


def test_beef_cow_calf_pair_member_exists() -> None:
    """AnimalCombination.BEEF_COW_CALF_PAIR exists with the expected string value."""
    assert AnimalCombination.BEEF_COW_CALF_PAIR.value == "beef_cow_calf_pair"


def test_beef_gestating_member_exists() -> None:
    """AnimalCombination.BEEF_GESTATING exists with the expected string value."""
    assert AnimalCombination.BEEF_GESTATING.value == "beef_gestating"


def test_beef_replacement_member_exists() -> None:
    """AnimalCombination.BEEF_REPLACEMENT exists with the expected string value."""
    assert AnimalCombination.BEEF_REPLACEMENT.value == "beef_replacement"


def test_beef_bull_battery_member_exists() -> None:
    """AnimalCombination.BEEF_BULL_BATTERY exists with the expected string value."""
    assert AnimalCombination.BEEF_BULL_BATTERY.value == "beef_bull_battery"


# ---------------------------------------------------------------------------
# AnimalGroupingScenario.BEEF_COW_CALF_HERD — structure
# ---------------------------------------------------------------------------


def test_beef_cow_calf_herd_scenario_exists() -> None:
    """AnimalGroupingScenario.BEEF_COW_CALF_HERD enum member exists."""
    assert hasattr(AnimalGroupingScenario, "BEEF_COW_CALF_HERD")


def test_beef_cow_calf_herd_contains_all_four_combinations() -> None:
    """BEEF_COW_CALF_HERD scenario maps all four beef cow-calf combinations."""
    scenario = AnimalGroupingScenario.BEEF_COW_CALF_HERD
    assert AnimalCombination.BEEF_COW_CALF_PAIR in scenario.value
    assert AnimalCombination.BEEF_GESTATING in scenario.value
    assert AnimalCombination.BEEF_REPLACEMENT in scenario.value
    assert AnimalCombination.BEEF_BULL_BATTERY in scenario.value


def test_beef_cow_calf_pair_contains_cow_and_calf() -> None:
    """BEEF_COW_CALF_PAIR combination maps to BEEF_COW and BEEF_CALF."""
    scenario = AnimalGroupingScenario.BEEF_COW_CALF_HERD
    types_in_pair = scenario.value[AnimalCombination.BEEF_COW_CALF_PAIR]
    assert AnimalType.BEEF_COW in types_in_pair
    assert AnimalType.BEEF_CALF in types_in_pair


def test_beef_gestating_contains_beef_cow() -> None:
    """BEEF_GESTATING combination maps to BEEF_COW (gestating cows separated from calves)."""
    scenario = AnimalGroupingScenario.BEEF_COW_CALF_HERD
    types_in_gestating = scenario.value[AnimalCombination.BEEF_GESTATING]
    assert AnimalType.BEEF_COW in types_in_gestating


def test_beef_replacement_contains_heifer_replacement() -> None:
    """BEEF_REPLACEMENT combination maps to BEEF_HEIFER_REPLACEMENT."""
    scenario = AnimalGroupingScenario.BEEF_COW_CALF_HERD
    types_in_replacement = scenario.value[AnimalCombination.BEEF_REPLACEMENT]
    assert AnimalType.BEEF_HEIFER_REPLACEMENT in types_in_replacement


def test_beef_bull_battery_contains_beef_bull() -> None:
    """BEEF_BULL_BATTERY combination maps to BEEF_BULL."""
    scenario = AnimalGroupingScenario.BEEF_COW_CALF_HERD
    types_in_bull = scenario.value[AnimalCombination.BEEF_BULL_BATTERY]
    assert AnimalType.BEEF_BULL in types_in_bull


# ---------------------------------------------------------------------------
# all_animal_types exhaustive check — is_beef_cow_calf consistent with enum membership
# ---------------------------------------------------------------------------


def test_all_animal_types_is_beef_cow_calf_consistent() -> None:
    """Every AnimalType returns is_beef_cow_calf consistent with its identity."""
    expected_beef_cow_calf = {
        AnimalType.BEEF_CALF,
        AnimalType.BEEF_HEIFER_REPLACEMENT,
        AnimalType.BEEF_COW,
        AnimalType.BEEF_BULL,
    }
    for animal_type in AnimalType:
        expected = animal_type in expected_beef_cow_calf
        assert (
            animal_type.is_beef_cow_calf == expected
        ), f"Unexpected is_beef_cow_calf={animal_type.is_beef_cow_calf} for {animal_type}"
