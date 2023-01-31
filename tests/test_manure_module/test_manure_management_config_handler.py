from pytest_mock import MockerFixture

from RUFAS.routines.manure.beddings.bedding_classes import BeddingType
from RUFAS.routines.manure.input_handler.manure_management_config_handler import ManureManagementConfigHandler
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import ManureHandlerType
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ManureSeparatorType
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType


def test_process_bedding_configs(mocker: MockerFixture) -> None:
    """Unit test for the _process_bedding_configs() method in manure_management_config_handler.py."""
    # Arrange
    json_bedding_configs = [
        {
            "bedding_type": 'sawdust',
            "bedding_mass_per_day": 1.97,
            "bedding_density": 250.0,
            "bedding_dry_matter_content": 0.9,
            "bedding_cleaned_fraction": 1.0
        },
        {
            "bedding_type": 'manure solids',
            "bedding_mass_per_day": 2.50,
            "bedding_density": 400.0,
            "bedding_dry_matter_content": 0.9,
            "bedding_cleaned_fraction": 1.0
        },
        {
            "bedding_type": 'sand',
            "bedding_mass_per_day": 25.0,
            "bedding_density": 1500.0,
            "bedding_dry_matter_content": 0.9,
            "bedding_cleaned_fraction": 1.0,
            "sand_removal_efficiency": 1.0
        }
    ]

    patch_for_bedding_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.BeddingType.get_type',
            side_effect=[
                BeddingType.SAWDUST,
                BeddingType.MANURE_SOLIDS,
                BeddingType.SAND
            ]
    )

    patch_for_bedding_config_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.BeddingConfig.__init__',
            return_value=None,
    )

    # Act
    actual_bedding_configs = ManureManagementConfigHandler._process_bedding_configs(json_bedding_configs)

    # Assert
    assert len(actual_bedding_configs) == 3
    assert patch_for_bedding_type_get_type.call_count == 3
    assert patch_for_bedding_type_get_type.call_args_list == [
        mocker.call('sawdust'),
        mocker.call('manure solids'),
        mocker.call('sand')
    ]
    assert patch_for_bedding_config_init.call_count == 3
    assert patch_for_bedding_config_init.call_args_list == [
        mocker.call(
                bedding_mass_per_day=1.97,
                bedding_density=250.0,
                bedding_dry_matter_content=0.9,
                bedding_cleaned_fraction=1.0,
                bedding_type=BeddingType.SAWDUST
        ),
        mocker.call(
                bedding_mass_per_day=2.50,
                bedding_density=400.0,
                bedding_dry_matter_content=0.9,
                bedding_cleaned_fraction=1.0,
                bedding_type=BeddingType.MANURE_SOLIDS
        ),
        mocker.call(
                bedding_mass_per_day=25.0,
                bedding_density=1500.0,
                bedding_dry_matter_content=0.9,
                bedding_cleaned_fraction=1.0,
                sand_removal_efficiency=1.0,
                bedding_type=BeddingType.SAND
        )
    ]
    assert BeddingType.SAWDUST in actual_bedding_configs
    assert BeddingType.MANURE_SOLIDS in actual_bedding_configs
    assert BeddingType.SAND in actual_bedding_configs


def test_process_manure_handler_configs(mocker: MockerFixture) -> None:
    """Unit test for the _process_manure_handler_configs() method in manure_management_config_handler.py."""
    # Arrange
    manure_handler_json_configs = [
        {
            "manure_handler_type": "flush system",
            "cleaning_water_use_rate": 757.0,
            "minutes_per_cleaning": 8,
            "cleanings_per_day": 2
        },
        {
            "manure_handler_type": "manual scraping",
            "cleaning_water_use_rate": 10.0,
            "minutes_per_cleaning": 8,
            "cleanings_per_day": 2
        },
        {
            "manure_handler_type": "alley scraper",
            "cleaning_water_use_rate": 10.0,
            "minutes_per_cleaning": 8,
            "cleanings_per_day": 2
        }
    ]

    patch_for_manure_handler_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureHandlerType.get_type',
            side_effect=[
                ManureHandlerType.FLUSH_SYSTEM,
                ManureHandlerType.MANUAL_SCRAPING,
                ManureHandlerType.ALLEY_SCRAPER
            ]
    )

    patch_for_manure_handler_config_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureHandlerConfig.__init__',
            return_value=None,
    )

    # Act
    actual_manure_handler_configs = ManureManagementConfigHandler._process_manure_handler_configs(
            manure_handler_json_configs
    )

    # Assert
    assert len(actual_manure_handler_configs) == 3
    assert patch_for_manure_handler_type_get_type.call_count == 3
    assert patch_for_manure_handler_type_get_type.call_args_list == [
        mocker.call('flush system'),
        mocker.call('manual scraping'),
        mocker.call('alley scraper')
    ]
    assert patch_for_manure_handler_config_init.call_count == 3
    assert patch_for_manure_handler_config_init.call_args_list == [
        mocker.call(
                cleaning_water_use_rate=757.0,
                minutes_per_cleaning=8,
                cleanings_per_day=2,
        ),
        mocker.call(
                cleaning_water_use_rate=10.0,
                minutes_per_cleaning=8,
                cleanings_per_day=2,
        ),
        mocker.call(
                cleaning_water_use_rate=10.0,
                minutes_per_cleaning=8,
                cleanings_per_day=2,
        )
    ]
    assert ManureHandlerType.FLUSH_SYSTEM in actual_manure_handler_configs
    assert ManureHandlerType.MANUAL_SCRAPING in actual_manure_handler_configs
    assert ManureHandlerType.ALLEY_SCRAPER in actual_manure_handler_configs


def test_process_manure_separator_configs(mocker: MockerFixture) -> None:
    """Unit test for the _process_manure_separator_configs() method in manure_management_config_handler.py."""
    # Arrange
    manure_separator_json_configs = [
        {
            "manure_separator_type": "rotary screen",
            "percent_dry_solids": 0.20,
            "total_solids_removal_efficiency_for_separator": 0.35,
            "volatile_solids_removal_efficiency_for_separator": 0.40,
            "nitrogen_removal_efficiency_for_separator": 0.30,
            "total_ammoniacal_nitrogen_removal_efficiency_for_separator": 0.15,
            "phosphorus_removal_efficiency_for_separator": 0.40,
            "potassium_removal_efficiency_for_separator": 0.15
        },
        {
            "manure_separator_type": "screw press",
            "percent_dry_solids": 0.35,
            "total_solids_removal_efficiency_for_separator": 0.25,
            "volatile_solids_removal_efficiency_for_separator": 0.30,
            "nitrogen_removal_efficiency_for_separator": 0.30,
            "total_ammoniacal_nitrogen_removal_efficiency_for_separator": 0.10,
            "phosphorus_removal_efficiency_for_separator": 0.20,
            "potassium_removal_efficiency_for_separator": 0.23
        }
    ]

    patch_for_manure_separator_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureSeparatorType.get_type',
            side_effect=[
                ManureSeparatorType.ROTARY_SCREEN,
                ManureSeparatorType.SCREW_PRESS
            ]
    )

    patch_for_manure_separator_config_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureSeparatorConfig.__init__',
            return_value=None,
    )

    # Act
    actual_manure_separator_configs = ManureManagementConfigHandler._process_manure_separator_configs(
            manure_separator_json_configs
    )

    # Assert
    assert len(actual_manure_separator_configs) == 2
    assert patch_for_manure_separator_type_get_type.call_count == 2
    assert patch_for_manure_separator_type_get_type.call_args_list == [
        mocker.call('rotary screen'),
        mocker.call('screw press')
    ]
    assert patch_for_manure_separator_config_init.call_count == 2
    assert patch_for_manure_separator_config_init.call_args_list == [
        mocker.call(
                percent_dry_solids=0.20,
                total_solids_removal_efficiency_for_separator=0.35,
                volatile_solids_removal_efficiency_for_separator=0.40,
                nitrogen_removal_efficiency_for_separator=0.30,
                total_ammoniacal_nitrogen_removal_efficiency_for_separator=0.15,
                phosphorus_removal_efficiency_for_separator=0.40,
                potassium_removal_efficiency_for_separator=0.15
        ),
        mocker.call(
                percent_dry_solids=0.35,
                total_solids_removal_efficiency_for_separator=0.25,
                volatile_solids_removal_efficiency_for_separator=0.30,
                nitrogen_removal_efficiency_for_separator=0.30,
                total_ammoniacal_nitrogen_removal_efficiency_for_separator=0.10,
                phosphorus_removal_efficiency_for_separator=0.20,
                potassium_removal_efficiency_for_separator=0.23
        )
    ]
    assert ManureSeparatorType.ROTARY_SCREEN in actual_manure_separator_configs
    assert ManureSeparatorType.SCREW_PRESS in actual_manure_separator_configs


def test_process_manure_treatment_configs(mocker: MockerFixture) -> None:
    """Unit test for the _process_manure_treatment_configs() method in manure_management_config_handler.py."""
    manure_treatment_json_configs = [
        {
            "manure_treatment_type": "slurry storage underfloor",
            "total_solids_removal_efficiency_for_treatment": 0.10,
            "volatile_solids_removal_efficiency_for_treatment": 0.20,
            "nitrogen_removal_efficiency_for_treatment": 0.10,
            "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.45,
            "phosphorus_removal_efficiency_for_treatment": 0.05,
            "potassium_removal_efficiency_for_treatment": 0.05,
            "storage_time_period": 120
        },
        {
            "manure_treatment_type": "slurry storage outdoor",
            "total_solids_removal_efficiency_for_treatment": 0.10,
            "volatile_solids_removal_efficiency_for_treatment": 0.20,
            "nitrogen_removal_efficiency_for_treatment": 0.10,
            "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.45,
            "phosphorus_removal_efficiency_for_treatment": 0.05,
            "potassium_removal_efficiency_for_treatment": 0.05,
            "storage_time_period": 120,
            "freeboard_input": 0.3048
        },
        {
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
            "freeboard_input": 0.3048
        },
        {
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
            "biogas_generation_ratio": 0.38,
            "methane_generation_ratio": 0.65,
            "evaporation_fraction": 0.02,
            "anaerobic_digestion_temperature_set_point": 37.5,
            "anaerobic_digestion_temperature": 37.5
        }
    ]

    patch_for_manure_treatment_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureTreatmentType.get_type',
            side_effect=[
                ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR,
                ManureTreatmentType.SLURRY_STORAGE_OUTDOOR,
                ManureTreatmentType.ANAEROBIC_LAGOON,
                ManureTreatmentType.ANAEROBIC_DIGESTION
            ]
    )

    patch_for_manure_treatment_config_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureTreatmentConfig.__init__',
            return_value=None,
    )

    # Act
    actual_manure_treatment_configs = ManureManagementConfigHandler._process_manure_treatment_configs(
            manure_treatment_json_configs
    )

    # Assert
    assert len(actual_manure_treatment_configs) == 6
    assert patch_for_manure_treatment_type_get_type.call_count == 4
    assert patch_for_manure_treatment_type_get_type.call_args_list == [
        mocker.call('slurry storage underfloor'),
        mocker.call('slurry storage outdoor'),
        mocker.call('anaerobic lagoon'),
        mocker.call('anaerobic digestion')
    ]
    assert patch_for_manure_treatment_config_init.call_count == 4
    assert patch_for_manure_treatment_config_init.call_args_list == [
        mocker.call(
                total_solids_removal_efficiency_for_treatment=0.10,
                volatile_solids_removal_efficiency_for_treatment=0.20,
                nitrogen_removal_efficiency_for_treatment=0.10,
                total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.45,
                phosphorus_removal_efficiency_for_treatment=0.05,
                potassium_removal_efficiency_for_treatment=0.05,
                storage_time_period=120,
        ),
        mocker.call(
                total_solids_removal_efficiency_for_treatment=0.10,
                volatile_solids_removal_efficiency_for_treatment=0.20,
                nitrogen_removal_efficiency_for_treatment=0.10,
                total_ammoniacal_nitrogen_removal_efficiency_for_treatment=0.45,
                phosphorus_removal_efficiency_for_treatment=0.05,
                potassium_removal_efficiency_for_treatment=0.05,
                storage_time_period=120,
                freeboard_input=0.3048
        ),
        mocker.call(
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
                freeboard_input=0.3048
        ),
        mocker.call(
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
                biogas_generation_ratio=0.38,
                methane_generation_ratio=0.65,
                evaporation_fraction=0.02,
                anaerobic_digestion_temperature_set_point=37.5,
                anaerobic_digestion_temperature=37.5
        )
    ]
    assert ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR in actual_manure_treatment_configs
    assert ManureTreatmentType.SLURRY_STORAGE_OUTDOOR in actual_manure_treatment_configs
    assert ManureTreatmentType.ANAEROBIC_LAGOON in actual_manure_treatment_configs
    assert ManureTreatmentType.ANAEROBIC_DIGESTION in actual_manure_treatment_configs
    assert actual_manure_treatment_configs[ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON] == (
        actual_manure_treatment_configs[ManureTreatmentType.ANAEROBIC_DIGESTION],
        actual_manure_treatment_configs[ManureTreatmentType.ANAEROBIC_LAGOON],
    )
    assert actual_manure_treatment_configs[ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT] == (
        actual_manure_treatment_configs[ManureTreatmentType.ANAEROBIC_DIGESTION],
        actual_manure_treatment_configs[ManureTreatmentType.ANAEROBIC_LAGOON],
    )


def test_get_custom_bedding_config(mocker: MockerFixture) -> None:
    """Unit test for _get_custom_bedding_config() in manure_management_config_handler.py."""
    # Case 1: Custom bedding config is provided

    # Arrange
    mock_bedding_type_name = 'default'
    mock_bedding_type = BeddingType.DEFAULT
    patch_for_bedding_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.BeddingType.get_type',
            return_value=mock_bedding_type
    )
    mock_manure_management_config = mocker.MagicMock()
    patch_for_manure_management_config_handler_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler.__init__',
            return_value=None,
    )

    manure_management_config_handler = ManureManagementConfigHandler(
            manure_management_config=mock_manure_management_config
    )

    mock_bedding_config = mocker.MagicMock()
    mock_custom_bedding_configs = {
        mock_bedding_type: mock_bedding_config
    }
    manure_management_config_handler.custom_bedding_configs = mock_custom_bedding_configs

    # Act
    actual_bedding_config = manure_management_config_handler.get_custom_bedding_config(
            bedding_type_name=mock_bedding_type_name
    )

    # Assert
    patch_for_manure_management_config_handler_init.assert_called_once_with(
            manure_management_config=mock_manure_management_config
    )
    patch_for_bedding_type_get_type.assert_called_once_with(mock_bedding_type_name)
    assert actual_bedding_config == mock_bedding_config

    # --------------------

    # Case 2: There is no custom bedding config

    mock_bedding_type_name = 'default'
    mock_bedding_type = BeddingType.DEFAULT
    patch_for_bedding_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.BeddingType.get_type',
            return_value=mock_bedding_type
    )
    mock_manure_management_config = mocker.MagicMock()
    patch_for_manure_management_config_handler_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler.__init__',
            return_value=None,
    )

    manure_management_config_handler = ManureManagementConfigHandler(
            manure_management_config=mock_manure_management_config
    )

    manure_management_config_handler.custom_bedding_configs = {}

    # Act
    actual_bedding_config = manure_management_config_handler.get_custom_bedding_config(
            bedding_type_name=mock_bedding_type_name
    )

    # Assert
    patch_for_manure_management_config_handler_init.assert_called_once_with(
            manure_management_config=mock_manure_management_config
    )
    patch_for_bedding_type_get_type.assert_called_once_with(mock_bedding_type_name)
    assert actual_bedding_config is None


def test_get_custom_manure_handler_config(mocker: MockerFixture) -> None:
    """Unit test for _get_custom_manure_handler_config() in manure_management_config_handler.py."""
    # Case 1: Custom manure handler config is provided

    # Arrange
    mock_manure_handler_type_name = 'default'
    mock_manure_handler_type = ManureHandlerType.DEFAULT
    patch_for_manure_handler_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureHandlerType.get_type',
            return_value=mock_manure_handler_type
    )
    mock_manure_management_config = mocker.MagicMock()
    patch_for_manure_management_config_handler_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler.__init__',
            return_value=None,
    )

    manure_management_config_handler = ManureManagementConfigHandler(
            manure_management_config=mock_manure_management_config
    )

    mock_manure_handler_config = mocker.MagicMock()
    mock_custom_manure_handler_configs = {
        mock_manure_handler_type: mock_manure_handler_config
    }
    manure_management_config_handler.custom_manure_handler_configs = mock_custom_manure_handler_configs

    # Act
    actual_manure_handler_config = manure_management_config_handler.get_custom_manure_handler_config(
            manure_handler_type_name=mock_manure_handler_type_name
    )

    # Assert
    patch_for_manure_management_config_handler_init.assert_called_once_with(
            manure_management_config=mock_manure_management_config
    )
    patch_for_manure_handler_type_get_type.assert_called_once_with(mock_manure_handler_type_name)
    assert actual_manure_handler_config == mock_manure_handler_config

    # --------------------

    # Case 2: There is no custom bedding config

    mock_manure_handler_type_name = 'default'
    mock_manure_handler_type = BeddingType.DEFAULT
    patch_for_manure_handler_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureHandlerType.get_type',
            return_value=mock_manure_handler_type
    )
    mock_manure_management_config = mocker.MagicMock()
    patch_for_manure_management_config_handler_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler.__init__',
            return_value=None,
    )

    manure_management_config_handler = ManureManagementConfigHandler(
            manure_management_config=mock_manure_management_config
    )

    manure_management_config_handler.custom_manure_handler_configs = {}

    # Act
    actual_manure_handler_config = manure_management_config_handler.get_custom_manure_handler_config(
            manure_handler_type_name=mock_manure_handler_type_name
    )

    # Assert
    patch_for_manure_management_config_handler_init.assert_called_once_with(
            manure_management_config=mock_manure_management_config
    )
    patch_for_manure_handler_type_get_type.assert_called_once_with(mock_manure_handler_type_name)
    assert actual_manure_handler_config is None


def test_get_custom_manure_separator_config(mocker: MockerFixture) -> None:
    """Unit test for _get_custom_manure_separator_config() in manure_management_config_handler.py."""
    # Case 1: Custom manure separator config is provided

    # Arrange
    mock_manure_separator_type_name = 'default'
    mock_manure_separator_type = ManureSeparatorType.DEFAULT_ORGANIC
    patch_for_manure_separator_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureSeparatorType.get_type',
            return_value=mock_manure_separator_type
    )
    mock_manure_management_config = mocker.MagicMock()
    patch_for_manure_management_config_handler_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler.__init__',
            return_value=None,
    )

    manure_management_config_handler = ManureManagementConfigHandler(
            manure_management_config=mock_manure_management_config
    )

    mock_manure_separator_config = mocker.MagicMock()
    mock_custom_separator_configs = {
        mock_manure_separator_type: mock_manure_separator_config
    }
    manure_management_config_handler.custom_manure_separator_configs = mock_custom_separator_configs

    # Act
    actual_manure_separator_config = manure_management_config_handler.get_custom_manure_separator_config(
            manure_separator_type_name=mock_manure_separator_type_name
    )

    # Assert
    patch_for_manure_management_config_handler_init.assert_called_once_with(
            manure_management_config=mock_manure_management_config
    )
    patch_for_manure_separator_type_get_type.assert_called_once_with(mock_manure_separator_type_name)
    assert actual_manure_separator_config == mock_manure_separator_config

    # --------------------

    # Case 2: There is no custom bedding config

    mock_manure_separator_type_name = 'default'
    mock_manure_separator_type = BeddingType.DEFAULT
    patch_for_manure_separator_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureSeparatorType.get_type',
            return_value=mock_manure_separator_type
    )
    mock_manure_management_config = mocker.MagicMock()
    patch_for_manure_management_config_handler_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler.__init__',
            return_value=None,
    )

    manure_management_config_handler = ManureManagementConfigHandler(
            manure_management_config=mock_manure_management_config
    )

    manure_management_config_handler.custom_manure_separator_configs = {}

    # Act
    actual_manure_separator_config = manure_management_config_handler.get_custom_manure_separator_config(
            manure_separator_type_name=mock_manure_separator_type_name
    )

    # Assert
    patch_for_manure_management_config_handler_init.assert_called_once_with(
            manure_management_config=mock_manure_management_config
    )
    patch_for_manure_separator_type_get_type.assert_called_once_with(mock_manure_separator_type_name)
    assert actual_manure_separator_config is None


def test_get_custom_manure_treatment_config(mocker: MockerFixture) -> None:
    """Unit test for _get_custom_manure_treatment_config() in manure_management_config_handler.py."""
    # Case 1: Custom manure treatment config is provided

    # Arrange
    mock_manure_treatment_type_name = 'default'
    mock_manure_treatment_type = ManureTreatmentType.DEFAULT
    patch_for_manure_treatment_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureTreatmentType.get_type',
            return_value=mock_manure_treatment_type
    )
    mock_manure_management_config = mocker.MagicMock()
    patch_for_manure_management_config_handler_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler.__init__',
            return_value=None,
    )

    manure_management_config_handler = ManureManagementConfigHandler(
            manure_management_config=mock_manure_management_config
    )

    mock_manure_treatment_config = mocker.MagicMock()
    mock_custom_treatment_configs = {
        mock_manure_treatment_type: mock_manure_treatment_config
    }
    manure_management_config_handler.custom_manure_treatment_configs = mock_custom_treatment_configs

    # Act
    actual_manure_treatment_config = manure_management_config_handler.get_custom_manure_treatment_config(
            manure_treatment_type_name=mock_manure_treatment_type_name
    )

    # Assert
    patch_for_manure_management_config_handler_init.assert_called_once_with(
            manure_management_config=mock_manure_management_config
    )
    patch_for_manure_treatment_type_get_type.assert_called_once_with(mock_manure_treatment_type_name)
    assert actual_manure_treatment_config == mock_manure_treatment_config

    # --------------------

    # Case 2: There is no custom bedding config

    mock_manure_treatment_type_name = 'default'
    mock_manure_treatment_type = BeddingType.DEFAULT
    patch_for_manure_treatment_type_get_type = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler.ManureTreatmentType.get_type',
            return_value=mock_manure_treatment_type
    )
    mock_manure_management_config = mocker.MagicMock()
    patch_for_manure_management_config_handler_init = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler.__init__',
            return_value=None,
    )

    manure_management_config_handler = ManureManagementConfigHandler(
            manure_management_config=mock_manure_management_config
    )

    manure_management_config_handler.custom_manure_treatment_configs = {}

    # Act
    actual_manure_treatment_config = manure_management_config_handler.get_custom_manure_treatment_config(
            manure_treatment_type_name=mock_manure_treatment_type_name
    )

    # Assert
    patch_for_manure_management_config_handler_init.assert_called_once_with(
            manure_management_config=mock_manure_management_config
    )
    patch_for_manure_treatment_type_get_type.assert_called_once_with(mock_manure_treatment_type_name)
    assert actual_manure_treatment_config is None


def test_manure_management_config_handler_init(mocker: MockerFixture) -> None:
    """Unit test for __init__() in manure_management_config_handler.py."""
    # Arrange
    mock_bedding_json_configs = mocker.MagicMock()
    mock_manure_handler_json_configs = mocker.MagicMock()
    mock_manure_separator_json_configs = mocker.MagicMock()
    mock_manure_treatment_json_configs = mocker.MagicMock()
    mock_manure_management_config = {
        'bedding_configs': mock_bedding_json_configs,
        'manure_handler_configs': mock_manure_handler_json_configs,
        'manure_separator_configs': mock_manure_separator_json_configs,
        'manure_treatment_configs': mock_manure_treatment_json_configs,
    }

    mock_custom_bedding_configs = mocker.MagicMock()
    mock_custom_manure_handler_configs = mocker.MagicMock()
    mock_custom_manure_separator_configs = mocker.MagicMock()
    mock_custom_manure_treatment_configs = mocker.MagicMock()
    patch_for_process_bedding_configs = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler._process_bedding_configs',
            return_value=mock_custom_bedding_configs
    )
    patch_for_process_manure_handler_configs = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler._process_manure_handler_configs',
            return_value=mock_custom_manure_handler_configs
    )
    patch_for_process_manure_separator_configs = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler._process_manure_separator_configs',
            return_value=mock_custom_manure_separator_configs
    )
    patch_for_process_manure_treatment_configs = mocker.patch(
            'RUFAS.routines.manure.input_handler.manure_management_config_handler'
            '.ManureManagementConfigHandler._process_manure_treatment_configs',
            return_value=mock_custom_manure_treatment_configs
    )

    # Act
    manure_management_config_handler = ManureManagementConfigHandler(
            manure_management_config=mock_manure_management_config
    )

    # Assert
    patch_for_process_bedding_configs.assert_called_once_with(mock_bedding_json_configs)
    patch_for_process_manure_handler_configs.assert_called_once_with(mock_manure_handler_json_configs)
    patch_for_process_manure_separator_configs.assert_called_once_with(mock_manure_separator_json_configs)
    patch_for_process_manure_treatment_configs.assert_called_once_with(mock_manure_treatment_json_configs)
    assert manure_management_config_handler.custom_bedding_configs == mock_custom_bedding_configs
    assert manure_management_config_handler.custom_manure_handler_configs == mock_custom_manure_handler_configs
    assert manure_management_config_handler.custom_manure_separator_configs == mock_custom_manure_separator_configs
    assert manure_management_config_handler.custom_manure_treatment_configs == mock_custom_manure_treatment_configs
