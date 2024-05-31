import pytest
from pytest import approx

from RUFAS.routines.manure.beddings.bedding_classes import (
    BeddingConfig,
    StrawBedding,
    CBPBSawdustBedding,
    BaseBedding,
)
from RUFAS.routines.manure.beddings.bedding_classes import BeddingFactory
from RUFAS.routines.manure.beddings.bedding_classes import BeddingType
from RUFAS.routines.manure.beddings.bedding_classes import ManureSolidsBedding
from RUFAS.routines.manure.beddings.bedding_classes import SandBedding
from RUFAS.routines.manure.beddings.bedding_classes import SawdustBedding
from RUFAS.routines.manure.beddings.bedding_classes import NoBedding


@pytest.mark.parametrize(
    "bedding_type_name, expected_bedding_type",
    [
        ("sawdust", BeddingType.SAWDUST),
        ("CBPB sawdust", BeddingType.CBPB_SAWDUST),
        ("manure solids", BeddingType.MANURE_SOLIDS),
        ("straw", BeddingType.STRAW),
        ("sand", BeddingType.SAND),
        ("none", BeddingType.NONE),
    ],
)
def test_bedding_type(bedding_type_name: str, expected_bedding_type: BeddingType) -> None:
    """Unit test for class BeddingType in file bedding_classes.py"""

    # Act
    bedding_type = BeddingType(bedding_type_name)

    # Assert
    assert bedding_type == expected_bedding_type


def test_bedding_config_init() -> None:
    """Unit test for BeddingConfig dataclass in file bedding_classes.py"""

    # Act
    bedding_config = BeddingConfig(
        bedding_mass_per_day=1.0,
        bedding_density=2.0,
        bedding_dry_matter_content=3.0,
        bedding_cleaned_fraction=4.0,
        bedding_carbon_fraction=5.0,
        bedding_phosphorus_content=6.0,
        bedding_type=BeddingType.SAND,
        sand_removal_efficiency=7.0,
    )

    # Assert
    assert bedding_config.bedding_mass_per_day == approx(1.0)
    assert bedding_config.bedding_density == approx(2.0)
    assert bedding_config.bedding_dry_matter_content == approx(3.0)
    assert bedding_config.bedding_cleaned_fraction == approx(4.0)
    assert bedding_config.bedding_carbon_fraction == approx(5.0)
    assert bedding_config.bedding_phosphorus_content == approx(6.0)
    assert bedding_config.bedding_type == BeddingType.SAND
    assert bedding_config.sand_removal_efficiency == approx(7.0)


@pytest.fixture
def dummy_bedding_config() -> BeddingConfig:
    """Fixture for BeddingConfig dataclass in file bedding_classes.py"""

    return BeddingConfig(
        bedding_mass_per_day=1.0,
        bedding_density=2.0,
        bedding_dry_matter_content=3.0,
        bedding_cleaned_fraction=4.0,
        bedding_carbon_fraction=5.0,
        bedding_phosphorus_content=6.0,
        bedding_type=BeddingType.SAND,
        sand_removal_efficiency=7.0,
    )


@pytest.mark.parametrize(
    "bedding_type, expected_bedding",
    [
        (BeddingType.SAWDUST, SawdustBedding),
        (BeddingType.CBPB_SAWDUST, CBPBSawdustBedding),
        (BeddingType.MANURE_SOLIDS, ManureSolidsBedding),
        (BeddingType.STRAW, StrawBedding),
        (BeddingType.SAND, SandBedding),
        (BeddingType.NONE, NoBedding),
    ],
)
def test_bedding_factory_get_instance(
    bedding_type: BeddingType, expected_bedding: BaseBedding, dummy_bedding_config: BeddingConfig
) -> None:
    """Unit test for class BeddingFactory in file bedding_classes.py"""
    # Act
    dummy_bedding_config.bedding_type = bedding_type
    name = "dummy_bedding_name"
    bedding = BeddingFactory.get_instance(name, dummy_bedding_config)

    # Assert
    assert isinstance(bedding, expected_bedding)
    assert bedding.name == name
    assert bedding.bedding_mass_per_day == dummy_bedding_config.bedding_mass_per_day
    assert bedding.bedding_density == dummy_bedding_config.bedding_density
    assert bedding.bedding_dry_matter_content == dummy_bedding_config.bedding_dry_matter_content
    assert bedding.bedding_cleaned_fraction == dummy_bedding_config.bedding_cleaned_fraction
    assert bedding.bedding_type is dummy_bedding_config.bedding_type

    if isinstance(bedding, SandBedding):
        assert bedding.sand_removal_efficiency == dummy_bedding_config.sand_removal_efficiency


@pytest.mark.parametrize(
    "bedding_type,sand_removal_efficiency",
    [
        (BeddingType.SAWDUST, 0.0),
        (BeddingType.CBPB_SAWDUST, 0.0),
        (BeddingType.MANURE_SOLIDS, 0.0),
        (BeddingType.STRAW, 0.0),
        (BeddingType.SAND, 0.5),
    ],
)
def test_bedding_public_methods(
    bedding_type: BeddingType, sand_removal_efficiency: float, dummy_bedding_config: BeddingConfig
) -> None:
    """Unit test for calc_total_bedding_mass and calc_total_bedding_volume in file bedding_classes.py"""

    # Arrange
    num_animals = 10
    expected_total_bedding_mass = (
        num_animals * dummy_bedding_config.bedding_mass_per_day * (1 - sand_removal_efficiency)
    )
    expected_total_bedding_volume = expected_total_bedding_mass / dummy_bedding_config.bedding_density
    expected_total_bedding_washed = expected_total_bedding_mass * dummy_bedding_config.bedding_cleaned_fraction
    expected_total_bedding_dry_solids = expected_total_bedding_mass * dummy_bedding_config.bedding_dry_matter_content
    name = "dummy name"
    dummy_bedding_config.bedding_type = bedding_type
    dummy_bedding_config.sand_removal_efficiency = sand_removal_efficiency

    # Act
    bedding = BeddingFactory.get_instance(name, dummy_bedding_config)
    actual_total_bedding_mass = bedding.calc_total_bedding_mass(num_animals)
    actual_total_bedding_volume = bedding.calc_total_bedding_volume(num_animals)
    actual_total_bedding_washed = bedding.calc_total_bedding_washed(num_animals)
    actual_total_bedding_dry_solids = bedding.calc_total_bedding_dry_solids(num_animals)

    # Assert
    assert actual_total_bedding_mass == approx(expected_total_bedding_mass)
    assert actual_total_bedding_volume == approx(expected_total_bedding_volume)
    assert actual_total_bedding_washed == approx(expected_total_bedding_washed)
    assert actual_total_bedding_dry_solids == approx(expected_total_bedding_dry_solids)


def test_no_bedding_public_methods(dummy_bedding_config: BeddingConfig) -> None:
    """Tests that the NONE_BEDDING_CONFIG public methods behave as expected."""
    dummy_bedding_config.bedding_type = BeddingType.NONE

    bedding = BeddingFactory.get_instance("none", dummy_bedding_config)

    assert bedding.calc_total_bedding_washed(8) == 0.0
    assert bedding.calc_total_bedding_mass(10) == 0.0
    assert bedding.calc_total_bedding_volume(100) == 0.0
    assert bedding.calc_total_bedding_volume(1) == 0.0
    assert bedding.calc_total_bedding_dry_solids(-3) == 0.0
