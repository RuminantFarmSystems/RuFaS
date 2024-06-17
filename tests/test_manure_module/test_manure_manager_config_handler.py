import pytest
from unittest.mock import patch
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure.beddings.bedding_classes import BeddingType
from RUFAS.routines.manure.IO_helpers.manure_manager_config_handler import (
    ManureManagerConfigHandler,
)
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import (
    ManureHandlerType,
    ManureHandlerConfig,
)
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ManureSeparatorType, ManureSeparatorConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import (
    ManureTreatmentType,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig

om = OutputManager()


def test_process_bedding_configs(mocker: MockerFixture) -> None:
    """Unit test for the _process_bedding_configs() method in manure_manager_config_handler.py."""
    # Arrange
    bedding_configs = [
        {
            "name": "sawdusty",
            "bedding_type": "sawdust",
            "bedding_mass_per_day": 1.97,
            "bedding_density": 250.0,
            "bedding_dry_matter_content": 0.9,
            "bedding_cleaned_fraction": 1.0,
        },
        {
            "name": "solids",
            "bedding_type": "manure solids",
            "bedding_mass_per_day": 2.50,
            "bedding_density": 400.0,
            "bedding_dry_matter_content": 0.9,
            "bedding_cleaned_fraction": 1.0,
        },
        {
            "name": "sand",
            "bedding_type": "sand",
            "bedding_mass_per_day": 25.0,
            "bedding_density": 1500.0,
            "bedding_dry_matter_content": 0.9,
            "bedding_cleaned_fraction": 1.0,
            "sand_removal_efficiency": 1.0,
        },
    ]
    expected_bedding_config_keys = [config["name"] for config in bedding_configs]

    patch_for_bedding_config_init = mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.BeddingConfig.__init__",
        return_value=None,
    )

    # Act
    actual_bedding_configs = ManureManagerConfigHandler._process_bedding_configs(bedding_configs)

    # Assert
    assert patch_for_bedding_config_init.call_count == 3
    assert patch_for_bedding_config_init.call_args_list == [
        mocker.call(
            bedding_mass_per_day=1.97,
            bedding_density=250.0,
            bedding_dry_matter_content=0.9,
            bedding_cleaned_fraction=1.0,
            bedding_type=BeddingType.SAWDUST,
        ),
        mocker.call(
            bedding_mass_per_day=2.50,
            bedding_density=400.0,
            bedding_dry_matter_content=0.9,
            bedding_cleaned_fraction=1.0,
            bedding_type=BeddingType.MANURE_SOLIDS,
        ),
        mocker.call(
            bedding_mass_per_day=25.0,
            bedding_density=1500.0,
            bedding_dry_matter_content=0.9,
            bedding_cleaned_fraction=1.0,
            sand_removal_efficiency=1.0,
            bedding_type=BeddingType.SAND,
        ),
    ]
    assert list(actual_bedding_configs.keys()) == expected_bedding_config_keys


def test_process_bedding_configs_error(mocker: MockerFixture) -> None:
    """Tests that _process_bedding_configs() raises error when a config is defined multiple times."""
    # Arrange
    bedding_configs = [
        {
            "name": "sawdusty",
            "bedding_type": "sawdust",
            "bedding_mass_per_day": 1.97,
            "bedding_density": 250.0,
            "bedding_dry_matter_content": 0.9,
            "bedding_cleaned_fraction": 1.0,
        },
        {
            "name": "sawdusty",
            "bedding_type": "sawdust",
            "bedding_mass_per_day": 1.97,
            "bedding_density": 250.0,
            "bedding_dry_matter_content": 0.9,
            "bedding_cleaned_fraction": 1.0,
        },
    ]

    mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.BeddingConfig.__init__",
        return_value=None,
    )
    expected_error_message = "Bedding config 'sawdusty' has multiple configurations"

    with pytest.raises(ValueError, match=expected_error_message):
        ManureManagerConfigHandler._process_bedding_configs(bedding_configs)


def test_process_manure_handler_configs(mocker: MockerFixture) -> None:
    """Unit test for the _process_manure_handler_configs() method in manure_manager_config_handler.py."""
    # Arrange
    manure_handler_configs = [
        {
            "name": "flush system",
            "manure_handler_type": "flush system",
            "cleaning_water_use_rate": 757.0,
            "minutes_per_cleaning": 8,
            "cleanings_per_day": 2,
            "daily_tillage_frequency": 0,
            "cleaning_water_recycle_fraction": 0.8,
        },
        {
            "name": "test manual scraping",
            "manure_handler_type": "manual scraping",
            "cleaning_water_use_rate": 10.0,
            "minutes_per_cleaning": 8,
            "cleanings_per_day": 2,
            "daily_tillage_frequency": 0,
            "cleaning_water_recycle_fraction": 0.9,
        },
        {
            "name": "alley scraper",
            "manure_handler_type": "alley scraper",
            "cleaning_water_use_rate": 10.0,
            "minutes_per_cleaning": 8,
            "cleanings_per_day": 2,
            "daily_tillage_frequency": 0,
            "cleaning_water_recycle_fraction": 0.5,
        },
    ]

    patch_for_manure_handler_config_init = mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.ManureHandlerConfig.__init__",
        return_value=None,
    )

    # Act
    actual_manure_handler_configs = ManureManagerConfigHandler._process_manure_handler_configs(manure_handler_configs)

    # Assert
    assert len(actual_manure_handler_configs) == 3
    assert patch_for_manure_handler_config_init.call_count == 3
    assert patch_for_manure_handler_config_init.call_args_list == [
        mocker.call(
            manure_handler_type=ManureHandlerType.FLUSH_SYSTEM,
            cleaning_water_use_rate=757.0,
            minutes_per_cleaning=8,
            cleanings_per_day=2,
            daily_tillage_frequency=0,
            cleaning_water_recycle_fraction=0.8,
        ),
        mocker.call(
            manure_handler_type=ManureHandlerType.MANUAL_SCRAPING,
            cleaning_water_use_rate=10.0,
            minutes_per_cleaning=8,
            cleanings_per_day=2,
            daily_tillage_frequency=0,
            cleaning_water_recycle_fraction=0.9,
        ),
        mocker.call(
            manure_handler_type=ManureHandlerType.ALLEY_SCRAPER,
            cleaning_water_use_rate=10.0,
            minutes_per_cleaning=8,
            cleanings_per_day=2,
            daily_tillage_frequency=0,
            cleaning_water_recycle_fraction=0.5,
        ),
    ]
    assert "flush system" in actual_manure_handler_configs
    assert "test manual scraping" in actual_manure_handler_configs
    assert "alley scraper" in actual_manure_handler_configs


def test_process_manure_separator_configs(mocker: MockerFixture) -> None:
    """Unit test for the _process_manure_separator_configs() method in manure_manager_config_handler.py."""
    # Arrange
    manure_separator_configs = [
        {
            "name": "screener",
            "manure_separator_type": "rotary screen",
            "percent_dry_solids": 0.20,
            "total_solids_removal_efficiency_for_separator": 0.35,
            "volatile_solids_removal_efficiency_for_separator": 0.40,
            "nitrogen_removal_efficiency_for_separator": 0.30,
            "total_ammoniacal_nitrogen_removal_efficiency_for_separator": 0.15,
            "phosphorus_removal_efficiency_for_separator": 0.40,
            "potassium_removal_efficiency_for_separator": 0.15,
        },
        {
            "name": "presser",
            "manure_separator_type": "screw press",
            "percent_dry_solids": 0.35,
            "total_solids_removal_efficiency_for_separator": 0.25,
            "volatile_solids_removal_efficiency_for_separator": 0.30,
            "nitrogen_removal_efficiency_for_separator": 0.30,
            "total_ammoniacal_nitrogen_removal_efficiency_for_separator": 0.10,
            "phosphorus_removal_efficiency_for_separator": 0.20,
            "potassium_removal_efficiency_for_separator": 0.23,
        },
    ]

    patch_for_manure_separator_config_init = mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.ManureSeparatorConfig.__init__",
        return_value=None,
    )

    # Act
    actual_manure_separator_configs = ManureManagerConfigHandler._process_manure_separator_configs(
        manure_separator_configs
    )

    # Assert
    assert len(actual_manure_separator_configs) == 2
    assert patch_for_manure_separator_config_init.call_count == 2
    assert patch_for_manure_separator_config_init.call_args_list == [
        mocker.call(
            manure_separator_type=ManureSeparatorType.ROTARY_SCREEN,
            percent_dry_solids=0.20,
            total_solids_removal_efficiency_for_separator=0.35,
            volatile_solids_removal_efficiency_for_separator=0.40,
            nitrogen_removal_efficiency_for_separator=0.30,
            total_ammoniacal_nitrogen_removal_efficiency_for_separator=0.15,
            phosphorus_removal_efficiency_for_separator=0.40,
            potassium_removal_efficiency_for_separator=0.15,
        ),
        mocker.call(
            manure_separator_type=ManureSeparatorType.SCREW_PRESS,
            percent_dry_solids=0.35,
            total_solids_removal_efficiency_for_separator=0.25,
            volatile_solids_removal_efficiency_for_separator=0.30,
            nitrogen_removal_efficiency_for_separator=0.30,
            total_ammoniacal_nitrogen_removal_efficiency_for_separator=0.10,
            phosphorus_removal_efficiency_for_separator=0.20,
            potassium_removal_efficiency_for_separator=0.23,
        ),
    ]
    assert "screener" in actual_manure_separator_configs
    assert "presser" in actual_manure_separator_configs


def test_process_manure_separator_configs_error(mocker: MockerFixture) -> None:
    """Unit test to check _process_manure_separator_configs() method raises error on invalid input correctly."""
    manure_separator_configs = [
        {
            "name": "screener",
            "manure_separator_type": "rotary screen",
            "percent_dry_solids": 0.20,
            "total_solids_removal_efficiency_for_separator": 0.35,
            "volatile_solids_removal_efficiency_for_separator": 0.40,
            "nitrogen_removal_efficiency_for_separator": 0.30,
            "total_ammoniacal_nitrogen_removal_efficiency_for_separator": 0.15,
            "phosphorus_removal_efficiency_for_separator": 0.40,
            "potassium_removal_efficiency_for_separator": 0.15,
        },
        {
            "name": "screener",
            "manure_separator_type": "screw press",
            "percent_dry_solids": 0.35,
            "total_solids_removal_efficiency_for_separator": 0.25,
            "volatile_solids_removal_efficiency_for_separator": 0.30,
            "nitrogen_removal_efficiency_for_separator": 0.30,
            "total_ammoniacal_nitrogen_removal_efficiency_for_separator": 0.10,
            "phosphorus_removal_efficiency_for_separator": 0.20,
            "potassium_removal_efficiency_for_separator": 0.23,
        },
    ]

    with pytest.raises(ValueError, match="Manure separator 'screener' has multiple configurations"):
        ManureManagerConfigHandler._process_manure_separator_configs(manure_separator_configs)


def test_process_manure_treatment_configs(mocker: MockerFixture) -> None:
    """Unit test for the _process_manure_treatment_configs() method in manure_manager_config_handler.py."""
    manure_treatment_json_configs = [
        {
            "name": "slurry storage underfloor",
            "manure_treatment_type": "slurry storage underfloor",
            "total_solids_removal_efficiency_for_treatment": 0.10,
            "volatile_solids_removal_efficiency_for_treatment": 0.20,
            "nitrogen_removal_efficiency_for_treatment": 0.10,
            "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.45,
            "phosphorus_removal_efficiency_for_treatment": 0.05,
            "potassium_removal_efficiency_for_treatment": 0.05,
            "storage_time_period": 120,
        },
        {
            "name": "slurry storage outdoor",
            "manure_treatment_type": "slurry storage outdoor",
            "total_solids_removal_efficiency_for_treatment": 0.10,
            "volatile_solids_removal_efficiency_for_treatment": 0.20,
            "nitrogen_removal_efficiency_for_treatment": 0.10,
            "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.45,
            "phosphorus_removal_efficiency_for_treatment": 0.05,
            "potassium_removal_efficiency_for_treatment": 0.05,
            "storage_time_period": 120,
            "freeboard_input": 0.3048,
        },
        {
            "name": "anaerobic lagoon",
            "manure_treatment_type": "anaerobic lagoon",
            "total_solids_removal_efficiency_for_treatment": 0.75,
            "volatile_solids_removal_efficiency_for_treatment": 0.85,
            "nitrogen_removal_efficiency_for_treatment": 0.65,
            "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.7,
            "phosphorus_removal_efficiency_for_treatment": 0.6,
            "potassium_removal_efficiency_for_treatment": 0.2,
            "hydraulic_retention_time": 365,
            "sludge_accumulation_period": 10.0,
            "sludge_accumulation_volume_fraction": 0.00251,
            "storage_time_period": 365,
            "freeboard_input": 0.3048,
        },
        {
            "name": "anaerobic digestion",
            "manure_treatment_type": "anaerobic digestion",
            "total_solids_removal_efficiency_for_treatment": 0.45,
            "volatile_solids_removal_efficiency_for_treatment": 0.40,
            "nitrogen_removal_efficiency_for_treatment": 0.0,
            "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.1,
            "phosphorus_removal_efficiency_for_treatment": 0.0,
            "potassium_removal_efficiency_for_treatment": 0.0,
            "hydraulic_retention_time": 25,
            "sludge_accumulation_period": 1.0,
            "sludge_accumulation_volume_fraction": 0.03,
            "top_cover_volume_fraction": 0.2,
            "evaporation_fraction": 0.02,
            "anaerobic_digestion_temperature_set_point": 37.5,
            "anaerobic_digestion_temperature": 37.5,
        },
    ]

    patch_for_manure_treatment_config_init = mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.ManureTreatmentConfig.__init__",
        return_value=None,
    )

    # Act
    actual_manure_treatment_configs = ManureManagerConfigHandler._process_manure_treatment_configs(
        manure_treatment_json_configs
    )

    # Assert
    assert len(actual_manure_treatment_configs) == 6
    assert patch_for_manure_treatment_config_init.call_count == 4
    assert patch_for_manure_treatment_config_init.call_args_list == [
        mocker.call(
            manure_treatment_type=ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR,
            total_solids_removal_efficiency_for_treatment=0.10,
            volatile_solids_removal_efficiency_for_treatment=0.20,
            nitrogen_removal_efficiency_for_treatment=0.10,
            total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.45,
            phosphorus_removal_efficiency_for_treatment=0.05,
            potassium_removal_efficiency_for_treatment=0.05,
            storage_time_period=120,
        ),
        mocker.call(
            manure_treatment_type=ManureTreatmentType.SLURRY_STORAGE_OUTDOOR,
            total_solids_removal_efficiency_for_treatment=0.10,
            volatile_solids_removal_efficiency_for_treatment=0.20,
            nitrogen_removal_efficiency_for_treatment=0.10,
            total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.45,
            phosphorus_removal_efficiency_for_treatment=0.05,
            potassium_removal_efficiency_for_treatment=0.05,
            storage_time_period=120,
            freeboard_input=0.3048,
        ),
        mocker.call(
            manure_treatment_type=ManureTreatmentType.ANAEROBIC_LAGOON,
            total_solids_removal_efficiency_for_treatment=0.75,
            volatile_solids_removal_efficiency_for_treatment=0.85,
            nitrogen_removal_efficiency_for_treatment=0.65,
            total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.7,
            phosphorus_removal_efficiency_for_treatment=0.6,
            potassium_removal_efficiency_for_treatment=0.2,
            hydraulic_retention_time=365,
            sludge_accumulation_period=10.0,
            sludge_accumulation_volume_fraction=0.00251,
            storage_time_period=365,
            freeboard_input=0.3048,
        ),
        mocker.call(
            manure_treatment_type=ManureTreatmentType.ANAEROBIC_DIGESTION,
            total_solids_removal_efficiency_for_treatment=0.45,
            volatile_solids_removal_efficiency_for_treatment=0.40,
            nitrogen_removal_efficiency_for_treatment=0.0,
            total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.1,
            phosphorus_removal_efficiency_for_treatment=0.0,
            potassium_removal_efficiency_for_treatment=0.0,
            hydraulic_retention_time=25,
            sludge_accumulation_period=1.0,
            sludge_accumulation_volume_fraction=0.03,
            top_cover_volume_fraction=0.2,
            evaporation_fraction=0.02,
            anaerobic_digestion_temperature_set_point=37.5,
            anaerobic_digestion_temperature=37.5,
        ),
    ]
    assert "slurry storage underfloor" in actual_manure_treatment_configs
    assert "slurry storage outdoor" in actual_manure_treatment_configs
    assert "anaerobic lagoon" in actual_manure_treatment_configs
    assert "anaerobic digestion" in actual_manure_treatment_configs
    assert actual_manure_treatment_configs["anaerobic digestion and lagoon"] == (
        actual_manure_treatment_configs["anaerobic digestion"],
        actual_manure_treatment_configs["anaerobic lagoon"],
    )
    assert actual_manure_treatment_configs["anaerobic digestion and lagoon with separator"] == (
        actual_manure_treatment_configs["anaerobic digestion"],
        actual_manure_treatment_configs["anaerobic lagoon"],
    )


@pytest.mark.parametrize(
    "treatment_configs",
    [
        [{"name": "lagoon", "manure_treatment_type": "anaerobic lagoon"}],
        [{"name": "digestion", "manure_treatment_type": "anaerobic digestion"}],
        [{"name": "slurry storage", "manure_treatment_type": "slurry storage outdoor"}],
    ]
)
def test_process_manure_treatment_configs_warning(
    mocker: MockerFixture, treatment_configs: list[dict[str, str]]
) -> None:
    """Tests that warnings are raised when anaerobic digestion-lagoon combinations cannot be configured."""
    mocker.patch.object(ManureTreatmentConfig, "__init__", return_value=None)
    mocker.patch.object(ManureManagerConfigHandler, "__init__", return_value=None)
    config_handler = ManureManagerConfigHandler()
    add_warning = mocker.patch.object(om, "add_warning")

    config_handler._process_manure_treatment_configs(treatment_configs)

    add_warning.assert_called_once()


def test_get_bedding_config(mocker: MockerFixture) -> None:
    """Unit test for _get_bedding_config() in manure_manager_config_handler.py."""
    # Arrange
    mock_bedding_name = "default"
    mock_manure_manager_config = mocker.MagicMock()
    patch_for_manure_manager_config_handler_init = mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.ManureManagerConfigHandler.__init__",
        return_value=None,
    )

    manure_manager_config_handler = ManureManagerConfigHandler(manure_manager_config=mock_manure_manager_config)

    mock_bedding_config = mocker.MagicMock()
    mock_bedding_configs = {mock_bedding_name: mock_bedding_config}
    manure_manager_config_handler.bedding_configs = mock_bedding_configs

    # Act
    actual_bedding_config = manure_manager_config_handler.get_bedding_config(bedding_name=mock_bedding_name)

    # Assert
    patch_for_manure_manager_config_handler_init.assert_called_once_with(
        manure_manager_config=mock_manure_manager_config
    )
    assert actual_bedding_config == mock_bedding_config


def test_get_bedding_config_error(mocker: MockerFixture) -> None:
    """Tests that error is properly raised in _get_bedding_config() when a config to get is not there."""
    add_error = mocker.patch.object(om, "add_error")
    mock_manure_manager_config = mocker.MagicMock()
    mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.ManureManagerConfigHandler.__init__",
        return_value=None,
    )
    manure_manager_config_handler = ManureManagerConfigHandler(manure_manager_config=mock_manure_manager_config)
    manure_manager_config_handler.bedding_configs = {}
    expected_error_message = "Attempted to use a non-existent manure bedding configuration called 'not present'"

    with pytest.raises(KeyError, match=expected_error_message):
        manure_manager_config_handler.get_bedding_config("not present")

    add_error.assert_called_once()


@pytest.mark.parametrize(
    "handler_name,expected_config",
    [
        (
            "alley scraper",
            ManureHandlerConfig(
                manure_handler_type=ManureHandlerType.ALLEY_SCRAPER,
                cleaning_water_use_rate=100.0,
                minutes_per_cleaning=10,
                cleanings_per_day=10,
                daily_tillage_frequency=0,
                cleaning_water_recycle_fraction=0.9,
            ),
        ),
        (
            "unorthodox handler",
            ManureHandlerConfig(
                manure_handler_type=ManureHandlerType.FLUSH_SYSTEM,
                cleaning_water_use_rate=20.0,
                minutes_per_cleaning=30,
                cleanings_per_day=2,
                daily_tillage_frequency=0,
                cleaning_water_recycle_fraction=0.5,
            ),
        ),
    ],
)
def test_get_manure_handler_config(
    handler_name: str,
    expected_config: ManureHandlerConfig,
    mocker: MockerFixture,
) -> None:
    """Unit test for _get_manure_handler_config() in manure_manager_config_handler.py."""
    manure_handler_configs = {
        "alley scraper": ManureHandlerConfig(
            manure_handler_type=ManureHandlerType.ALLEY_SCRAPER,
            cleaning_water_use_rate=100.0,
            minutes_per_cleaning=10,
            cleanings_per_day=10,
            daily_tillage_frequency=0,
            cleaning_water_recycle_fraction=0.9,
        ),
        "unorthodox handler": ManureHandlerConfig(
            manure_handler_type=ManureHandlerType.FLUSH_SYSTEM,
            cleaning_water_use_rate=20.0,
            minutes_per_cleaning=30,
            cleanings_per_day=2,
            daily_tillage_frequency=0,
            cleaning_water_recycle_fraction=0.5,
        ),
    }
    mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.ManureManagerConfigHandler.__init__",
        return_value=None,
    )
    mock_manure_config_handler = ManureManagerConfigHandler()
    mock_manure_config_handler.manure_handler_configs = manure_handler_configs

    actual = mock_manure_config_handler.get_manure_handler_config(handler_name)

    assert actual == expected_config


def test_get_manure_handler_config_error(mocker: MockerFixture) -> None:
    """Tests that _get_manure_handler_config() correctly handles errors when missing manure handler types."""
    expected_title = "Unknown manure handler configuration name"
    expected_message = "Attempted to use a non-existent manure handler configuration called 'not there'"
    expected_info_map = {
        "class": "ManureManagerConfigHandler",
        "function": "get_manure_handler_config",
    }

    mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.ManureManagerConfigHandler.__init__",
        return_value=None,
    )
    mock_manure_config_handler = ManureManagerConfigHandler()
    mock_manure_config_handler.manure_handler_configs = {}

    with patch.object(om, "add_error") as mock_add_error, pytest.raises(KeyError):
        mock_manure_config_handler.get_manure_handler_config("not there")

    mock_add_error.assert_called_once_with(expected_title, expected_message, expected_info_map)


@pytest.mark.parametrize(
    "name,expected",
    [
        ("screw press", ManureSeparatorConfig(manure_separator_type=ManureSeparatorType.SCREW_PRESS)),
        ("rotary screen", ManureSeparatorConfig(manure_separator_type=ManureSeparatorType.ROTARY_SCREEN)),
        ("none", None),
    ],
)
def test_get_manure_separator_config(mocker: MockerFixture, name: str, expected: ManureSeparatorConfig | None) -> None:
    """Unit test for _get_manure_separator_config() in manure_manager_config_handler.py."""
    configs = {
        "screw press": ManureSeparatorConfig(manure_separator_type=ManureSeparatorType.SCREW_PRESS),
        "rotary screen": ManureSeparatorConfig(manure_separator_type=ManureSeparatorType.ROTARY_SCREEN),
    }
    mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.ManureManagerConfigHandler.__init__",
        return_value=None,
    )
    handler = ManureManagerConfigHandler()
    handler.manure_separator_configs = configs

    actual = handler.get_manure_separator_config(name)

    assert actual == expected


def test_get_manure_separator_config_error(mocker: MockerFixture) -> None:
    """Unit test for _get_manure_separator_config() raising errors in manure_manager_config_handler.py."""
    configs = {
        "screw press": ManureSeparatorConfig(manure_separator_type=ManureSeparatorType.SCREW_PRESS),
        "rotary screen": ManureSeparatorConfig(manure_separator_type=ManureSeparatorType.ROTARY_SCREEN),
    }
    mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler.ManureManagerConfigHandler.__init__",
        return_value=None,
    )
    handler = ManureManagerConfigHandler()
    handler.manure_separator_configs = configs

    with pytest.raises(KeyError, match="Attempted to use a non-existent manure separator configuration"):
        handler.get_manure_separator_config("not here")


def test_get_manure_treatment_config(mocker: MockerFixture) -> None:
    """Unit test for _get_custom_manure_treatment_config() in manure_manager_config_handler.py."""
    mocker.patch.object(ManureManagerConfigHandler, "__init__", return_value=None)
    config_handler = ManureManagerConfigHandler()
    mock_treatment_config = mocker.MagicMock()
    config_handler.manure_treatment_configs = {"config": mock_treatment_config}

    actual = config_handler.get_manure_treatment_config("config")

    assert actual == mock_treatment_config

    patch_add_error = mocker.patch.object(om, "add_error")
    with pytest.raises(KeyError, match="Attempted to use a non-existent manure treatment configuration"):
        config_handler.get_manure_treatment_config("not present")
    patch_add_error.assert_called_once()


def test_manure_manager_config_handler_init(mocker: MockerFixture) -> None:
    """Unit test for __init__() in manure_manager_config_handler.py."""
    # Arrange
    mock_bedding_json_configs = mocker.MagicMock()
    mock_manure_handler_json_configs = mocker.MagicMock()
    mock_manure_separator_json_configs = mocker.MagicMock()
    mock_manure_treatment_json_configs = mocker.MagicMock()
    mock_manure_manager_config = {
        "bedding_configs": mock_bedding_json_configs,
        "manure_handler_configs": mock_manure_handler_json_configs,
        "manure_separator_configs": mock_manure_separator_json_configs,
        "manure_treatment_configs": mock_manure_treatment_json_configs,
    }

    mock_bedding_configs = mocker.MagicMock()
    mock_manure_handler_configs = mocker.MagicMock()
    mock_manure_separator_configs = mocker.MagicMock()
    mock_manure_treatment_configs = mocker.MagicMock()
    patch_for_process_bedding_configs = mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler"
        ".ManureManagerConfigHandler._process_bedding_configs",
        return_value=mock_bedding_configs,
    )
    patch_for_process_manure_handler_configs = mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler"
        ".ManureManagerConfigHandler._process_manure_handler_configs",
        return_value=mock_manure_handler_configs,
    )
    patch_for_process_manure_separator_configs = mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler"
        ".ManureManagerConfigHandler._process_manure_separator_configs",
        return_value=mock_manure_separator_configs,
    )
    patch_for_process_manure_treatment_configs = mocker.patch(
        "RUFAS.routines.manure.IO_helpers.manure_manager_config_handler"
        ".ManureManagerConfigHandler._process_manure_treatment_configs",
        return_value=mock_manure_treatment_configs,
    )

    # Act
    manure_manager_config_handler = ManureManagerConfigHandler(manure_manager_config=mock_manure_manager_config)

    # Assert
    patch_for_process_bedding_configs.assert_called_once_with(mock_bedding_json_configs)
    patch_for_process_manure_handler_configs.assert_called_once_with(mock_manure_handler_json_configs)
    patch_for_process_manure_separator_configs.assert_called_once_with(mock_manure_separator_json_configs)
    patch_for_process_manure_treatment_configs.assert_called_once_with(mock_manure_treatment_json_configs)
    assert manure_manager_config_handler.bedding_configs == mock_bedding_configs
    assert manure_manager_config_handler.manure_handler_configs == mock_manure_handler_configs
    assert manure_manager_config_handler.manure_separator_configs == mock_manure_separator_configs
    assert manure_manager_config_handler.manure_treatment_configs == mock_manure_treatment_configs
