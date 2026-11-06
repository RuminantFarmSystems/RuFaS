from typing import Any

import pytest
from pytest_mock import MockerFixture

from RUFAS.input_manager import InputManager
from RUFAS.biophysical.field.crop.crop_data_factory import CropConfiguration, CropDataFactory
from RUFAS.biophysical.field.crop.crop_data import PlantCategory
from RUFAS.output_manager import OutputManager

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


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
                "harvest_efficiency": 1.0,
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
        harvest_efficiency=1.0,
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


def _crop_config_dict(**overrides: Any) -> dict[str, Any]:
    config: dict[str, Any] = {**SAMPLE_CROP_CONFIGURATION, "plant_category": "perennial_legume"}
    config.update(overrides)
    return config


@pytest.mark.parametrize("wilt_days", [0, 1, 3])
def test_manufacture_crop_configuration_accepts_non_negative_integer_wilt_days(wilt_days: int) -> None:
    """Test that whole-number wilt_days values, including 0 (curing disabled), are accepted unchanged."""
    CropDataFactory._om = OutputManager()

    actual = CropDataFactory._manufacture_crop_configuration(_crop_config_dict(wilt_days=wilt_days))

    assert actual["wilt_days"] == wilt_days


def test_manufacture_crop_configuration_accepts_missing_wilt_days() -> None:
    """Test that wilt_days stays optional: a configuration without it is accepted."""
    CropDataFactory._om = OutputManager()

    actual = CropDataFactory._manufacture_crop_configuration(_crop_config_dict())

    assert "wilt_days" not in actual


@pytest.mark.parametrize("wilt_days", [2.0, 2.5, -1, True, "3", None])
def test_manufacture_crop_configuration_rejects_invalid_wilt_days(
    mocker: MockerFixture, wilt_days: float | int | bool | str | None
) -> None:
    """Test that a schema-valid but non-integer or negative wilt_days raises ValueError and logs the received value.

    2.0 and 2.5 pass the schema (type "number") and DataValidator, but ``Weather.get_conditions_series`` iterates
    ``range(..., wilt_days)`` and ``timedelta`` is built from it, so they must be rejected at configuration time.
    """
    CropDataFactory._om = OutputManager()
    add_error = mocker.patch.object(CropDataFactory._om, "add_error")

    with pytest.raises(ValueError, match="wilt_days"):
        CropDataFactory._manufacture_crop_configuration(_crop_config_dict(wilt_days=wilt_days))

    add_error.assert_called_once()
    assert repr(wilt_days) in add_error.call_args.args[1]


def test_get_available_crop_configurations() -> None:
    """Test that the list of available configurations in CropDataFactory is gathered correctly."""
    config = CropConfiguration(
        name="alfalfa_silage",
        plant_category=PlantCategory.PERENNIAL_LEGUME,
        is_nitrogen_fixer=True,
        harvest_efficiency=1.0,
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
            harvest_efficiency=1.0,
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


def test_create_crop_data_preserves_harvest_efficiency() -> None:
    """Test that a crop configuration's harvest efficiency is carried into the created CropData."""
    CropDataFactory._crop_configurations = {
        "pasture": CropConfiguration(
            name="pasture",
            plant_category=PlantCategory.PERENNIAL,
            is_nitrogen_fixer=False,
            harvest_efficiency=0.5,
            minimum_temperature=0.0,
            optimal_temperature=15.0,
            potential_heat_units=800.0,
            max_leaf_area_index=4.0,
            first_heat_fraction_point=0.15,
            first_leaf_fraction_point=0.01,
            second_heat_fraction_point=0.50,
            second_leaf_fraction_point=0.95,
            senescent_heat_fraction=0.80,
            light_use_efficiency=30.0,
            emergence_nitrogen_fraction=0.0560,
            half_mature_nitrogen_fraction=0.0210,
            mature_nitrogen_fraction=0.0120,
            emergence_phosphorus_fraction=0.0099,
            half_mature_phosphorus_fraction=0.0022,
            mature_phosphorus_fraction=0.0019,
            max_root_depth=2000.0,
            root_distribution_param_da=137.0,
            root_distribution_param_c=-1.144,
            optimal_harvest_index=0.85,
            minimum_harvest_index=0.37,
            dry_matter_percentage=88.331,
            lignin_dry_matter_percentage=4.167,
            crude_protein_percent_at_harvest=13.28,
            non_protein_nitrogen_at_harvest=4.056,
            starch_at_harvest=2.217,
            adf_at_harvest=35.524,
            ndf_at_harvest=58.007,
            sugar_at_harvest=15.235,
            ash_at_harvest=8.567,
            yield_nitrogen_fraction=0.021248,
            yield_phosphorus_fraction=0.00281,
        )
    }

    actual = CropDataFactory.create_crop_data("pasture")

    assert actual.harvest_efficiency == 0.5


def test_crop_crop_data_error() -> None:
    """Test that CropDataFactory raises an error when trying to create an unavailable configuration."""
    with pytest.raises(ValueError):
        CropDataFactory.create_crop_data("unavailble")


def test_create_crop_data_field_curing_fields_default_when_absent() -> None:
    """Test that CropDataFactory falls back to CropData's own defaults when a crop configuration omits the
    optional field-curing keys (wilt_days, swath_density, soil_moisture_at_mowing)."""
    CropDataFactory._crop_configurations = {"alfalfa_silage": SAMPLE_CROP_CONFIGURATION}

    actual = CropDataFactory.create_crop_data("alfalfa_silage")

    assert actual.wilt_days == 0
    assert actual.swath_density == pytest.approx(700.0)
    assert actual.soil_moisture_at_mowing == pytest.approx(17.0)


def test_create_crop_data_field_curing_fields_present() -> None:
    """Test that CropDataFactory forwards a crop configuration's optional field-curing keys into the constructed
    CropData instance when they are present."""
    config: CropConfiguration = CropConfiguration(
        **SAMPLE_CROP_CONFIGURATION,
        wilt_days=3,
        swath_density=550.0,
        soil_moisture_at_mowing=20.0,
    )
    CropDataFactory._crop_configurations = {"alfalfa_silage": config}

    actual = CropDataFactory.create_crop_data("alfalfa_silage")

    assert actual.wilt_days == 3
    assert actual.swath_density == pytest.approx(550.0)
    assert actual.soil_moisture_at_mowing == pytest.approx(20.0)
