import pytest
from pytest_mock import MockerFixture

from RUFAS.input_manager import InputManager
from RUFAS.biophysical.field.crop.crop_data_factory import CropConfiguration, CropDataFactory
from RUFAS.biophysical.field.crop.crop_data import PlantCategory
from RUFAS.output_manager import OutputManager


def test_setup_crop_configurations(mocker: MockerFixture) -> None:
    """Test that the CropDataFactory is initialized correctly."""
    im = InputManager()
    mocker.patch.object(
        im,
        "get_data",
        return_value=[
            {
                "name": "alfalfa_silage",
                "plant_category": "perennial_legume",
                "is_nitrogen_fixer": True,
                "minimum_temperature": 4.0,
                "optimal_temperature": 25.0,
                "potential_heat_units": 400.0,
                "max_leaf_area_index": 4.0,
                "first_heat_fraction_point": 0.15,
                "first_leaf_fraction_point": 0.01,
                "second_heat_fraction_point": 0.50,
                "second_leaf_fraction_point": 0.95,
                "senescent_heat_fraction": 0.90,
                "light_use_efficiency": 20.0,
                "emergence_nitrogen_fraction": 0.0417,
                "half_mature_nitrogen_fraction": 0.0290,
                "mature_nitrogen_fraction": 0.0200,
                "emergence_phosphorus_fraction": 0.0035,
                "half_mature_phosphorus_fraction": 0.0028,
                "mature_phosphorus_fraction": 0.0020,
                "max_root_depth": 3000,
                "root_distribution_param_da": 207.0,
                "root_distribution_param_c": -1.032,
                "optimal_harvest_index": 0.90,
                "minimum_harvest_index": 0.40,
                "dry_matter_percentage": 42.883,
                "lignin_dry_matter_percentage": 7.419,
                "crude_protein_percent_at_harvest": 20.471,
                "non_protein_nitrogen_at_harvest": 10.098,
                "starch_at_harvest": 1.973,
                "adf_at_harvest": 33.683,
                "ndf_at_harvest": 43.195,
                "sugar_at_harvest": 6.274,
                "ash_at_harvest": 10.597,
                "yield_nitrogen_fraction": 0.0327536,
                "yield_phosphorus_fraction": 0.00351,
            }
        ],
    )

    expected = CropConfiguration(
        name="alfalfa_silage",
        plant_category=PlantCategory.PERENNIAL_LEGUME,
        is_nitrogen_fixer=True,
        minimum_temperature=4.0,
        optimal_temperature=25.0,
        potential_heat_units=400.0,
        max_leaf_area_index=4.0,
        first_heat_fraction_point=0.15,
        first_leaf_fraction_point=0.01,
        second_heat_fraction_point=0.50,
        second_leaf_fraction_point=0.95,
        senescent_heat_fraction=0.90,
        light_use_efficiency=20.0,
        emergence_nitrogen_fraction=0.0417,
        half_mature_nitrogen_fraction=0.0290,
        mature_nitrogen_fraction=0.0200,
        emergence_phosphorus_fraction=0.0035,
        half_mature_phosphorus_fraction=0.0028,
        mature_phosphorus_fraction=0.0020,
        max_root_depth=3000,
        root_distribution_param_da=207.0,
        root_distribution_param_c=-1.032,
        optimal_harvest_index=0.90,
        minimum_harvest_index=0.40,
        dry_matter_percentage=42.883,
        lignin_dry_matter_percentage=7.419,
        crude_protein_percent_at_harvest=20.471,
        non_protein_nitrogen_at_harvest=10.098,
        starch_at_harvest=1.973,
        adf_at_harvest=33.683,
        ndf_at_harvest=43.195,
        sugar_at_harvest=6.274,
        ash_at_harvest=10.597,
        yield_nitrogen_fraction=0.0327536,
        yield_phosphorus_fraction=0.00351,
    )

    CropDataFactory.setup_crop_configurations()

    assert list(CropDataFactory._crop_configurations.keys()) == ["alfalfa_silage"]
    assert CropDataFactory._crop_configurations["alfalfa_silage"] == expected


def test_setup_crop_configurations_error(mocker: MockerFixture) -> None:
    """Test that CropDataFactory prevents crop configurations from having the same name."""
    im = InputManager()
    mocker.patch.object(
        im,
        "get_data",
        return_value=[
            {
                "name": "alfalfa_silage",
                "plant_category": "perennial_legume",
                "is_nitrogen_fixer": True,
                "minimum_temperature": 4.0,
                "optimal_temperature": 25.0,
                "potential_heat_units": 400.0,
                "max_leaf_area_index": 4.0,
                "first_heat_fraction_point": 0.15,
                "first_leaf_fraction_point": 0.01,
                "second_heat_fraction_point": 0.50,
                "second_leaf_fraction_point": 0.95,
                "senescent_heat_fraction": 0.90,
                "light_use_efficiency": 20.0,
                "emergence_nitrogen_fraction": 0.0417,
                "half_mature_nitrogen_fraction": 0.0290,
                "mature_nitrogen_fraction": 0.0200,
                "emergence_phosphorus_fraction": 0.0035,
                "half_mature_phosphorus_fraction": 0.0028,
                "mature_phosphorus_fraction": 0.0020,
                "max_root_depth": 3000,
                "root_distribution_param_da": 207.0,
                "root_distribution_param_c": -1.032,
                "optimal_harvest_index": 0.90,
                "minimum_harvest_index": 0.40,
                "dry_matter_percentage": 42.883,
                "lignin_dry_matter_percentage": 7.419,
                "crude_protein_percent_at_harvest": 20.471,
                "non_protein_nitrogen_at_harvest": 10.098,
                "starch_at_harvest": 1.973,
                "adf_at_harvest": 33.683,
                "ndf_at_harvest": 43.195,
                "sugar_at_harvest": 6.274,
                "ash_at_harvest": 10.597,
                "yield_nitrogen_fraction": 0.0327536,
                "yield_phosphorus_fraction": 0.00351,
            },
            {
                "name": "alfalfa_silage",
                "plant_category": "perennial_legume",
                "is_nitrogen_fixer": True,
                "minimum_temperature": 4.0,
                "optimal_temperature": 25.0,
                "potential_heat_units": 400.0,
                "max_leaf_area_index": 4.0,
                "first_heat_fraction_point": 0.15,
                "first_leaf_fraction_point": 0.01,
                "second_heat_fraction_point": 0.50,
                "second_leaf_fraction_point": 0.95,
                "senescent_heat_fraction": 0.90,
                "light_use_efficiency": 20.0,
                "emergence_nitrogen_fraction": 0.0417,
                "half_mature_nitrogen_fraction": 0.0290,
                "mature_nitrogen_fraction": 0.0200,
                "emergence_phosphorus_fraction": 0.0035,
                "half_mature_phosphorus_fraction": 0.0028,
                "mature_phosphorus_fraction": 0.0020,
                "max_root_depth": 3000,
                "root_distribution_param_da": 207.0,
                "root_distribution_param_c": -1.032,
                "optimal_harvest_index": 0.90,
                "minimum_harvest_index": 0.40,
                "dry_matter_percentage": 42.883,
                "lignin_dry_matter_percentage": 7.419,
                "crude_protein_percent_at_harvest": 20.471,
                "non_protein_nitrogen_at_harvest": 10.098,
                "starch_at_harvest": 1.973,
                "adf_at_harvest": 33.683,
                "ndf_at_harvest": 43.195,
                "sugar_at_harvest": 6.274,
                "ash_at_harvest": 10.597,
                "yield_nitrogen_fraction": 0.0327536,
                "yield_phosphorus_fraction": 0.00351,
            },
        ],
    )

    with pytest.raises(ValueError):
        CropDataFactory.setup_crop_configurations()


def test_manufacture_crop_configuration_error() -> None:
    """Test that CropDataFactory prevents crop configurations with invalid category and type combinations."""
    CropDataFactory._om = OutputManager()
    crop_config = {"name": "invalid", "crop_category": "Alfalfa", "plant_category": "annual_grass"}

    with pytest.raises(ValueError):
        CropDataFactory._manufacture_crop_configuration(crop_config)


def test_get_available_crop_configurations() -> None:
    """Test that the list of available configurations in CropDataFactory is gathered correctly."""
    config = CropConfiguration(
        name="alfalfa_silage",
        plant_category=PlantCategory.PERENNIAL_LEGUME,
        is_nitrogen_fixer=True,
        minimum_temperature=4.0,
        optimal_temperature=25.0,
        potential_heat_units=400.0,
        max_leaf_area_index=4.0,
        first_heat_fraction_point=0.15,
        first_leaf_fraction_point=0.01,
        second_heat_fraction_point=0.50,
        second_leaf_fraction_point=0.95,
        senescent_heat_fraction=0.90,
        light_use_efficiency=20.0,
        emergence_nitrogen_fraction=0.0417,
        half_mature_nitrogen_fraction=0.0290,
        mature_nitrogen_fraction=0.0200,
        emergence_phosphorus_fraction=0.0035,
        half_mature_phosphorus_fraction=0.0028,
        mature_phosphorus_fraction=0.0020,
        max_root_depth=3000,
        root_distribution_param_da=207.0,
        root_distribution_param_c=-1.032,
        optimal_harvest_index=0.90,
        minimum_harvest_index=0.40,
        dry_matter_percentage=42.883,
        lignin_dry_matter_percentage=7.419,
        crude_protein_percent_at_harvest=20.471,
        non_protein_nitrogen_at_harvest=10.098,
        starch_at_harvest=1.973,
        adf_at_harvest=33.683,
        ndf_at_harvest=43.195,
        sugar_at_harvest=6.274,
        ash_at_harvest=10.597,
        yield_nitrogen_fraction=0.0327536,
        yield_phosphorus_fraction=0.00351,
    )
    CropDataFactory._crop_configurations = {"config_1": config, "config_2": config, "config_3": config}
    expected = ["config_1", "config_2", "config_3"]

    actual = CropDataFactory.get_available_crop_configurations()

    assert actual == expected


def test_create_crop_data() -> None:
    """Test that CropDataFactory manufactures CropData instances correctly."""
    CropDataFactory._crop_configurations = {
        "alfalfa_silage": CropConfiguration(
            name="alfalfa_silage",
            plant_category=PlantCategory.PERENNIAL_LEGUME,
            is_nitrogen_fixer=True,
            minimum_temperature=4.0,
            optimal_temperature=25.0,
            potential_heat_units=400.0,
            max_leaf_area_index=4.0,
            first_heat_fraction_point=0.15,
            first_leaf_fraction_point=0.01,
            second_heat_fraction_point=0.50,
            second_leaf_fraction_point=0.95,
            senescent_heat_fraction=0.90,
            light_use_efficiency=20.0,
            emergence_nitrogen_fraction=0.0417,
            half_mature_nitrogen_fraction=0.0290,
            mature_nitrogen_fraction=0.0200,
            emergence_phosphorus_fraction=0.0035,
            half_mature_phosphorus_fraction=0.0028,
            mature_phosphorus_fraction=0.0020,
            max_root_depth=3000,
            root_distribution_param_da=207.0,
            root_distribution_param_c=-1.032,
            optimal_harvest_index=0.90,
            minimum_harvest_index=0.40,
            dry_matter_percentage=42.883,
            lignin_dry_matter_percentage=7.419,
            crude_protein_percent_at_harvest=20.471,
            non_protein_nitrogen_at_harvest=10.098,
            starch_at_harvest=1.973,
            adf_at_harvest=33.683,
            ndf_at_harvest=43.195,
            sugar_at_harvest=6.274,
            ash_at_harvest=10.597,
            yield_nitrogen_fraction=0.0327536,
            yield_phosphorus_fraction=0.00351,
        )
    }

    actual = CropDataFactory.create_crop_data("alfalfa_silage")

    for key, expected_value in CropDataFactory._crop_configurations["alfalfa_silage"].items():
        actual_value = getattr(actual, key)

        assert actual_value == expected_value


def test_crop_crop_data_error() -> None:
    """Test that CropDataFactory raises an error when trying to create an unavailable configuration."""
    with pytest.raises(ValueError):
        CropDataFactory.create_crop_data("unavailble")
