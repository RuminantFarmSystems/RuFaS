"""
Unit tests for feedlot-specific enum additions.

Tests are written before implementation (TDD). They verify:
- FEEDLOT_STEER and FEEDLOT_HEIFER exist in AnimalType
- is_feedlot property returns True for feedlot types, False for dairy types
- is_feedlot is mutually exclusive with is_heifer and is_cow
- Sex.STEER exists with value "steer"
"""

import pytest
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_enums import Breed, Sex
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType

# ---------------------------------------------------------------------------
# AnimalType — new members
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_feedlot_steer_member_exists() -> None:
    """AnimalType.FEEDLOT_STEER must exist."""
    assert hasattr(AnimalType, "FEEDLOT_STEER")


@pytest.mark.unit
def test_feedlot_heifer_member_exists() -> None:
    """AnimalType.FEEDLOT_HEIFER must exist."""
    assert hasattr(AnimalType, "FEEDLOT_HEIFER")


@pytest.mark.unit
def test_feedlot_steer_value() -> None:
    """FEEDLOT_STEER value must be 'FeedlotSteer' (CamelCase, matching dairy convention)."""
    assert AnimalType.FEEDLOT_STEER.value == "FeedlotSteer"


@pytest.mark.unit
def test_feedlot_heifer_value() -> None:
    """FEEDLOT_HEIFER value must be 'FeedlotHeifer'."""
    assert AnimalType.FEEDLOT_HEIFER.value == "FeedlotHeifer"


# ---------------------------------------------------------------------------
# AnimalType.is_feedlot property — True for feedlot types
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("animal_type", [AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER])
def test_is_feedlot_true_for_feedlot_types(animal_type: AnimalType) -> None:
    """is_feedlot must be True for FEEDLOT_STEER and FEEDLOT_HEIFER."""
    assert animal_type.is_feedlot is True


# ---------------------------------------------------------------------------
# AnimalType.is_feedlot property — False for all dairy types
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "dairy_type",
    [
        AnimalType.CALF,
        AnimalType.HEIFER_I,
        AnimalType.HEIFER_II,
        AnimalType.HEIFER_III,
        AnimalType.DRY_COW,
        AnimalType.LAC_COW,
    ],
)
def test_is_feedlot_false_for_dairy_types(dairy_type: AnimalType) -> None:
    """is_feedlot must be False for all existing dairy AnimalType members."""
    assert dairy_type.is_feedlot is False


# ---------------------------------------------------------------------------
# Mutual exclusivity — a feedlot animal is neither a heifer nor a cow
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("animal_type", [AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER])
def test_feedlot_is_not_heifer(animal_type: AnimalType) -> None:
    """Feedlot types must NOT satisfy is_heifer — they are not dairy heifers."""
    assert animal_type.is_heifer is False


@pytest.mark.unit
@pytest.mark.parametrize("animal_type", [AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER])
def test_feedlot_is_not_cow(animal_type: AnimalType) -> None:
    """Feedlot types must NOT satisfy is_cow — they are not dairy cows."""
    assert animal_type.is_cow is False


@pytest.mark.unit
def test_every_animal_type_has_is_feedlot() -> None:
    """is_feedlot property must exist on every AnimalType member (not just feedlot ones)."""
    for member in AnimalType:
        assert hasattr(member, "is_feedlot"), f"Missing is_feedlot on {member}"
        assert isinstance(member.is_feedlot, bool), f"is_feedlot not bool on {member}"


@pytest.mark.unit
def test_at_most_one_of_feedlot_heifer_cow_is_true() -> None:
    """For every AnimalType, at most one of is_feedlot/is_heifer/is_cow is True."""
    for member in AnimalType:
        flags = [member.is_feedlot, member.is_heifer, member.is_cow]
        assert sum(flags) <= 1, f"{member}: more than one of is_feedlot/is_heifer/is_cow is True"


# ---------------------------------------------------------------------------
# Sex enum — new STEER member
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_sex_steer_member_exists() -> None:
    """Sex.STEER must exist for feedlot nutrition equations."""
    assert hasattr(Sex, "STEER")


@pytest.mark.unit
def test_sex_steer_value() -> None:
    """Sex.STEER value must be 'steer' (lowercase, matching existing male/female convention)."""
    assert Sex.STEER.value == "steer"


@pytest.mark.unit
def test_sex_enum_all_values_unique() -> None:
    """All Sex enum values must be unique strings — no two members share a value."""
    values = [member.value for member in Sex]
    assert len(values) == len(set(values)), f"Duplicate Sex values found: {values}"


@pytest.mark.unit
@pytest.mark.parametrize(
    "member,value",
    [
        ("AN", "Angus"),
        ("HE", "Hereford"),
        ("SI", "Simmental"),
        ("CH", "Charolais"),
        ("LM", "Limousin"),
        ("BR", "Brahman"),
        ("XB", "Crossbred"),
    ],
)
def test_beef_breed_members_exist(member: str, value: str) -> None:
    """Beef breed members must exist with correct string values."""
    assert hasattr(Breed, member)
    assert Breed[member].value == value


@pytest.mark.unit
def test_feedlot_finishing_combination_exists() -> None:
    """AnimalCombination.FEEDLOT_FINISHING must exist."""
    assert hasattr(AnimalCombination, "FEEDLOT_FINISHING")
    assert AnimalCombination.FEEDLOT_FINISHING.value == "feedlot_finishing"


@pytest.mark.unit
def test_feedlot_only_scenario_exists() -> None:
    """AnimalGroupingScenario.FEEDLOT_ONLY must exist."""
    assert hasattr(AnimalGroupingScenario, "FEEDLOT_ONLY")


@pytest.mark.unit
def test_feedlot_only_scenario_maps_feedlot_types() -> None:
    """FEEDLOT_ONLY must map FEEDLOT_FINISHING to FEEDLOT_STEER and FEEDLOT_HEIFER."""
    scenario = AnimalGroupingScenario.FEEDLOT_ONLY
    feedlot_types = scenario.value[AnimalCombination.FEEDLOT_FINISHING]
    assert AnimalType.FEEDLOT_STEER in feedlot_types
    assert AnimalType.FEEDLOT_HEIFER in feedlot_types


class _AnimalStub:
    """Minimal stub exposing only animal_type for find_animal_combination tests.

    Parameters
    ----------
    animal_type : AnimalType
        The animal type to expose on the stub.
    """

    def __init__(self, animal_type: AnimalType) -> None:
        self.animal_type = animal_type


@pytest.mark.unit
@pytest.mark.parametrize(
    "animal_type",
    [
        AnimalType.FEEDLOT_STEER,
        AnimalType.FEEDLOT_HEIFER,
    ],
)
def test_feedlot_combination_lookup(animal_type: AnimalType) -> None:
    """find_animal_combination must resolve feedlot types to FEEDLOT_FINISHING."""
    stub = _AnimalStub(animal_type)
    result = AnimalGroupingScenario.FEEDLOT_ONLY.find_animal_combination(stub)  # type: ignore[arg-type]
    assert result == AnimalCombination.FEEDLOT_FINISHING
