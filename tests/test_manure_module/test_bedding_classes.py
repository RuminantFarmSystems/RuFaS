import pytest
from pytest import approx

from RUFAS.routines.manure.beddings.bedding_classes import (
    BeddingConfig, BeddingFactory, BeddingType, DefaultBeddingConfigFactory,
    ManureSolidsBedding, SandBedding, SawdustBedding)


@pytest.mark.parametrize(
        "bedding_type_name, expected_bedding_type",
        [('sawdust', BeddingType.SAWDUST),
         ('manure solids', BeddingType.MANURE_SOLIDS),
         ('sand', BeddingType.SAND),
         ('dummy', BeddingType.DEFAULT),
         ('dummy', BeddingType.SAND),
         ('default', BeddingType.SAND),
         ])
def test_bedding_type(bedding_type_name, expected_bedding_type) -> None:
    """Unit test for class BeddingType in file bedding_classes.py"""

    # Act
    bedding_type = BeddingType.get_type(bedding_type_name)

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
            bedding_type=BeddingType.DEFAULT,
            sand_removal_efficiency=5.0,
    )

    # Assert
    assert bedding_config.bedding_mass_per_day == 1.0
    assert bedding_config.bedding_density == 2.0
    assert bedding_config.bedding_dry_matter_content == 3.0
    assert bedding_config.bedding_cleaned_fraction == 4.0
    assert bedding_config.bedding_type == BeddingType.DEFAULT
    assert bedding_config.sand_removal_efficiency == 5.0


@pytest.mark.parametrize(
        "bedding_config, expected_bedding_mass_per_day, expected_bedding_density, "
        "expected_bedding_dry_matter_mass, expected_bedding_cleaned_frac, "
        "expected_bedding_type, expected_sand_removal_efficiency",
        [(DefaultBeddingConfigFactory.SAWDUST_BEDDING_CONFIG, 1.97, 250.0, 0.9, 1.0, BeddingType.SAWDUST, 0.0),
         (DefaultBeddingConfigFactory.MANURE_SOLIDS_BEDDING_CONFIG, 2.50, 400.0, 0.9, 1.0, BeddingType.MANURE_SOLIDS,
          0.0),
         (DefaultBeddingConfigFactory.SAND_BEDDING_CONFIG, 25.0, 1500.0, 0.9, 1.0, BeddingType.SAND, 1.0),
         ])
def test_default_bedding_config_values(bedding_config,
                                       expected_bedding_mass_per_day,
                                       expected_bedding_density,
                                       expected_bedding_dry_matter_mass,
                                       expected_bedding_cleaned_frac,
                                       expected_bedding_type,
                                       expected_sand_removal_efficiency) -> None:
    """Unit test for  default bedding config values in file bedding_classes.py"""

    # Assert
    assert bedding_config.bedding_mass_per_day == approx(expected_bedding_mass_per_day)
    assert bedding_config.bedding_density == approx(expected_bedding_density)
    assert bedding_config.bedding_dry_matter_content == approx(expected_bedding_dry_matter_mass)
    assert bedding_config.bedding_cleaned_fraction == approx(expected_bedding_cleaned_frac)
    assert bedding_config.bedding_type is expected_bedding_type
    assert bedding_config.sand_removal_efficiency == approx(expected_sand_removal_efficiency)


@pytest.mark.parametrize(
        "bedding_type, expected_default_bedding_config",
        [(BeddingType.SAWDUST, DefaultBeddingConfigFactory.SAWDUST_BEDDING_CONFIG),
         (BeddingType.MANURE_SOLIDS, DefaultBeddingConfigFactory.MANURE_SOLIDS_BEDDING_CONFIG),
         (BeddingType.SAND, DefaultBeddingConfigFactory.SAND_BEDDING_CONFIG)
         ])
def test_default_bedding_config_factory_get_instance(bedding_type, expected_default_bedding_config) -> None:
    """Unit test for class DefaultBeddingConfigFactory in file bedding_classes.py"""

    # Act
    default_bedding_config = DefaultBeddingConfigFactory.get_instance(bedding_type)

    # Assert
    assert default_bedding_config == expected_default_bedding_config


@pytest.fixture
def dummy_bedding_config() -> BeddingConfig:
    """Fixture for BeddingConfig dataclass in file bedding_classes.py"""

    return BeddingConfig(
            bedding_mass_per_day=1.0,
            bedding_density=2.0,
            bedding_dry_matter_content=3.0,
            bedding_cleaned_fraction=4.0,
            bedding_type=BeddingType.DEFAULT,
            sand_removal_efficiency=5.0,
    )


@pytest.mark.parametrize(
        "bedding_type_name, expected_bedding",
        [('sawdust', SawdustBedding),
         ('manure solids', ManureSolidsBedding),
         ('sand', SandBedding),
         ])
def test_bedding_factory_get_instance(bedding_type_name,
                                      expected_bedding,
                                      dummy_bedding_config) -> None:
    """Unit test for class BeddingFactory in file bedding_classes.py"""

    # Case 1: Use default bedding configs

    # Act
    bedding = BeddingFactory.get_instance(bedding_type_name)

    # Assert
    assert isinstance(bedding, expected_bedding)
    assert bedding.bedding_type == BeddingType.get_type(bedding_type_name)

    default_bedding_config = DefaultBeddingConfigFactory.get_instance(bedding.bedding_type)
    assert bedding.bedding_mass_per_day == default_bedding_config.bedding_mass_per_day
    assert bedding.bedding_density == default_bedding_config.bedding_density
    assert bedding.bedding_dry_matter_content == default_bedding_config.bedding_dry_matter_content
    assert bedding.bedding_cleaned_fraction == default_bedding_config.bedding_cleaned_fraction
    assert bedding.bedding_type is default_bedding_config.bedding_type

    if isinstance(bedding, SandBedding):
        assert bedding.sand_removal_efficiency == default_bedding_config.sand_removal_efficiency

    # ------------------------------

    # Case 2: Use custom bedding configs

    # Act
    bedding = BeddingFactory.get_instance(bedding_type_name, dummy_bedding_config)

    # Assert
    assert isinstance(bedding, expected_bedding)
    assert bedding.bedding_mass_per_day == dummy_bedding_config.bedding_mass_per_day
    assert bedding.bedding_density == dummy_bedding_config.bedding_density
    assert bedding.bedding_dry_matter_content == dummy_bedding_config.bedding_dry_matter_content
    assert bedding.bedding_cleaned_fraction == dummy_bedding_config.bedding_cleaned_fraction
    assert bedding.bedding_type is dummy_bedding_config.bedding_type

    if isinstance(bedding, SandBedding):
        assert bedding.sand_removal_efficiency == dummy_bedding_config.sand_removal_efficiency


@pytest.mark.parametrize(
        "bedding_type_name, bedding_config",
        [('sawdust', DefaultBeddingConfigFactory.SAWDUST_BEDDING_CONFIG),
         ('manure solids', DefaultBeddingConfigFactory.MANURE_SOLIDS_BEDDING_CONFIG),
         ('sand', DefaultBeddingConfigFactory.SAND_BEDDING_CONFIG),
         ])
def test_bedding_public_methods(bedding_type_name, bedding_config) -> None:
    """Unit test for calc_total_bedding_mass and calc_total_bedding_volume in file bedding_classes.py"""

    # Arrange
    num_animals = 10
    expected_total_bedding_mass = (num_animals * bedding_config.bedding_mass_per_day *
                                   (1 - bedding_config.sand_removal_efficiency))
    expected_total_bedding_volume = expected_total_bedding_mass / bedding_config.bedding_density
    expected_total_bedding_washed = expected_total_bedding_mass * bedding_config.bedding_cleaned_fraction
    expected_total_bedding_dry_solids = expected_total_bedding_mass / bedding_config.bedding_dry_matter_content

    # Act
    bedding = BeddingFactory.get_instance(bedding_type_name)
    actual_total_bedding_mass = bedding.calc_total_bedding_mass(num_animals)
    actual_total_bedding_volume = bedding.calc_total_bedding_volume(num_animals)
    actual_total_bedding_washed = bedding.calc_total_bedding_washed(num_animals)
    actual_total_bedding_dry_solids = bedding.calc_total_bedding_dry_solids(num_animals)

    # Assert
    assert actual_total_bedding_mass == approx(expected_total_bedding_mass)
    assert actual_total_bedding_volume == approx(expected_total_bedding_volume)
    assert actual_total_bedding_washed == approx(expected_total_bedding_washed)
    assert actual_total_bedding_dry_solids == approx(expected_total_bedding_dry_solids)
