import collections

from pytest_mock import MockFixture

from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.output_handler.manure_management_output_handler import ManureManagementOutputHandler
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput


def test_manure_management_output_handler_init(mocker: MockFixture) -> None:
    """Unit test for __init__() in manure_management_output_handler.py."""
    # Arrange
    patch_for_empty_main_output_directory = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.empty_main_output_directory',
            return_value=None
    )

    # Act
    manure_management_output_handler = ManureManagementOutputHandler()

    # Assert
    assert manure_management_output_handler._df is None
    patch_for_empty_main_output_directory.assert_called_once()


def test_property_data(mocker: MockFixture) -> None:
    """Unit test for property data() in manure_management_output_handler.py."""
    # Arrange
    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )
    manure_management_output_handler = ManureManagementOutputHandler()
    manure_management_output_handler._df = expected_data = mocker.MagicMock()

    # Act
    actual_data = manure_management_output_handler.data

    # Assert
    assert actual_data == expected_data


def test_convert_dataclass_obj_into_formatted_dict(mocker: MockFixture) -> None:
    """Unit test for _convert_dataclass_obj_into_formatted_dict() in manure_management_output_handler.py."""
    # Arrange
    mock_dataclass_obj = mocker.MagicMock()
    mock_prefix = '<prefix>'
    mock_delimiter = '<delimiter>'

    expected_dataframe_dict = collections.defaultdict(list)
    num_fields = 10
    mock_data_fields = []
    mock_capitalized_data_fields = []
    for i in range(num_fields):
        mock_field = mocker.MagicMock()
        mock_field.name = f'field_num_{i}'
        mock_data_fields.append(mock_field)
        mock_capitalized_data_fields.append(f'Field_Num_{i}')
        setattr(mock_dataclass_obj, mock_field.name, i)
        key_name = f'{mock_prefix}{mock_delimiter}' \
                   f'{mock_capitalized_data_fields[i]}'
        expected_dataframe_dict[key_name].append(i)

    patch_for_capitalize_first_letters = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler._capitalize_first_letters',
            side_effect=mock_capitalized_data_fields
    )

    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )
    manure_management_output_handler = ManureManagementOutputHandler()

    # Act
    actual_dataframe_dict = manure_management_output_handler._convert_dataclass_obj_into_formatted_dict(
            mock_dataclass_obj,
            tuple(mock_data_fields),
            mock_prefix,
            mock_delimiter
    )

    # Assert
    assert actual_dataframe_dict == expected_dataframe_dict
    assert patch_for_capitalize_first_letters.call_count == num_fields
    for i in range(num_fields):
        patch_for_capitalize_first_letters.assert_any_call(mock_data_fields[i].name, '_')


def test_process_pen(mocker: MockFixture) -> None:
    """Unit test for _process_pen() in manure_management_output_handler.py."""
    # Arrange
    mock_manure_management_pen = mocker.MagicMock()
    mock_manure_management_pen.id = pen_id = 1
    mock_manure_management_pen.num_animals = num_animals = 2
    mock_manure_management_pen.num_lactating_cows = num_lactating_cows = 3
    mock_manure_management_pen.classes_in_pen = '{AnimalClass1, AnimalClass2}'
    mock_manure_management_pen.housing_type = housing_type = 'HousingType'
    mock_manure_management_pen.bedding_type = bedding_type = 'BeddingType'
    mock_manure_management_pen.manure_handler = manure_handler = 'ManureHandler'
    mock_manure_management_pen.manure_separator = manure_separator = 'ManureSeparator'
    mock_manure_management_pen.manure_treatment = manure_treatment = 'ManureTreatment'

    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )

    manure_management_output_handler = ManureManagementOutputHandler()
    temp_header_prefixes = ManureManagementOutputHandler.HEADER_PREFIXES
    mock_pen_prefix = '<test_prefix>'
    ManureManagementOutputHandler.HEADER_PREFIXES = {
        ManureManagementPen: mock_pen_prefix
    }
    temp_header_primary_delimiter = ManureManagementOutputHandler.HEADER_PRIMARY_DELIMITER
    mock_header_primary_delimiter = '<test_primary_delimiter>'
    ManureManagementOutputHandler.HEADER_PRIMARY_DELIMITER = mock_header_primary_delimiter
    pen_data = {
        'pen_id': [pen_id],
        'num_animals': [num_animals],
        'num_lactating_cows': [num_lactating_cows],
        'animal_types': ['AnimalClass1, AnimalClass2'],
        'housing_type': [housing_type],
        'bedding_type': [bedding_type],
        'handler_type': [manure_handler],
        'separator_type': [manure_separator],
        'treatment_type': [manure_treatment],
    }

    expected_pen_dataframe_dict = {f'{mock_pen_prefix}{mock_header_primary_delimiter}{k}': v
                                   for k, v in pen_data.items()}

    # Act
    actual_pen_dataframe_dict = manure_management_output_handler._process_pen(mock_manure_management_pen)

    # Assert
    assert actual_pen_dataframe_dict == expected_pen_dataframe_dict

    # Cleanup
    ManureManagementOutputHandler.HEADER_PREFIXES = temp_header_prefixes
    ManureManagementOutputHandler.HEADER_PRIMARY_DELIMITER = temp_header_primary_delimiter


def test_process_dataclass_output_obj(mocker: MockFixture) -> None:
    """Unit test for _process_dataclass_output_obj() in manure_management_output_handler.py."""
    # Arrange
    mock_dataclass_obj = mocker.MagicMock()
    mock_obj_type = mocker.MagicMock()
    mock_extra_prefix = '<test_prefix>'

    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )

    manure_management_output_handler = ManureManagementOutputHandler()

    mock_random_formatted_dict = mocker.MagicMock()
    patch_for_convert_dataclass_obj_into_formatted_dict = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler._convert_dataclass_obj_into_formatted_dict',
            return_value=mock_random_formatted_dict
    )

    mock_dataclass_fields = mocker.MagicMock()
    patch_for_dataclass_fields_method = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'fields',
            return_value=mock_dataclass_fields
    )
    temp_header_prefixes = ManureManagementOutputHandler.HEADER_PREFIXES
    mock_header_prefix = '<test_header_prefix>'
    ManureManagementOutputHandler.HEADER_PREFIXES = {
        mock_obj_type: mock_header_prefix
    }
    temp_header_secondary_delimiter = ManureManagementOutputHandler.HEADER_SECONDARY_DELIMITER
    mock_header_secondary_delimiter = '<test_header_secondary_delimiter>'
    ManureManagementOutputHandler.HEADER_SECONDARY_DELIMITER = mock_header_secondary_delimiter

    temp_header_primary_delimiter = ManureManagementOutputHandler.HEADER_PRIMARY_DELIMITER
    mock_header_primary_delimiter = '<test_header_primary_delimiter>'
    ManureManagementOutputHandler.HEADER_PRIMARY_DELIMITER = mock_header_primary_delimiter

    # Act
    actual_dataframe_dict = manure_management_output_handler._process_dataclass_output_obj(
            dataclass_obj=mock_dataclass_obj,
            obj_type=mock_obj_type,
            extra_prefix=mock_extra_prefix,
    )

    # Assert
    assert actual_dataframe_dict == mock_random_formatted_dict
    patch_for_dataclass_fields_method.assert_called_once_with(mock_obj_type)
    patch_for_convert_dataclass_obj_into_formatted_dict.assert_called_once_with(
            dataclass_obj=mock_dataclass_obj,
            data_fields=mock_dataclass_fields,
            prefix=f'{mock_header_prefix}{mock_header_secondary_delimiter}{mock_extra_prefix}',
            delimiter=mock_header_primary_delimiter
    )

    # Cleanup
    ManureManagementOutputHandler.HEADER_PREFIXES = temp_header_prefixes
    ManureManagementOutputHandler.HEADER_SECONDARY_DELIMITER = temp_header_secondary_delimiter
    ManureManagementOutputHandler.HEADER_PRIMARY_DELIMITER = temp_header_primary_delimiter


def test_append_daily_update_output_for_pen(mocker: MockFixture) -> None:
    # Arrange
    simulation_day = 1
    mock_manure_management_pen = mocker.MagicMock()
    mock_manure_management_pen.id = pen_id = 1
    mock_pen_manure = mocker.MagicMock()
    mock_manure_management_pen.manure = mock_pen_manure
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_reception_pit_daily_output = mocker.MagicMock()
    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_data = (
        mock_manure_management_pen,
        mock_manure_handler_daily_output,
        mock_reception_pit_daily_output,
        mock_manure_separator_daily_output,
        mock_manure_treatment_daily_output,
        mock_anaerobic_digestion_daily_output
    )

    mock_pen_dataframe_dict = {'<test_pen_field>': ['<test_pen_value>']}
    mock_manure_dataframe_dict = {'<test_manure_field>': ['<test_manure_value>']}
    mock_manure_handler_daily_output_dataframe_dict = {
        '<test_manure_handler_daily_output_field>': ['<test_manure_handler_daily_output_value>']
    }
    mock_reception_pit_daily_output_dataframe_dict = {
        '<test_reception_pit_daily_output_field>': ['<test_reception_pit_daily_output_value>']
    }
    mock_manure_separator_daily_output_dataframe_dict = {
        '<test_manure_separator_daily_output_field>': ['<test_manure_separator_daily_output_value>']
    }
    mock_manure_treatment_daily_output_dataframe_dict = {
        '<test_manure_treatment_daily_output_field>': ['<test_manure_treatment_daily_output_value>']
    }
    mock_anaerobic_digestion_daily_output_dataframe_dict = {
        '<test_anaerobic_digestion_daily_output_field>': ['<test_anaerobic_digestion_daily_output_value>']
    }

    patch_for_process_pen = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler._process_pen',
            return_value=mock_pen_dataframe_dict
    )

    patch_for_process_dataclass_output_obj = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler._process_dataclass_output_obj',
            side_effect=[
                mock_manure_dataframe_dict,
                mock_manure_handler_daily_output_dataframe_dict,
                mock_reception_pit_daily_output_dataframe_dict,
                mock_manure_separator_daily_output_dataframe_dict,
                mock_manure_treatment_daily_output_dataframe_dict,
                mock_anaerobic_digestion_daily_output_dataframe_dict
            ]
    )

    manure_management_output_handler = ManureManagementOutputHandler()

    mock_dataframe_with_appended_row = mocker.MagicMock()
    patch_for_append_row = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler._append_row',
            return_value=mock_dataframe_with_appended_row
    )

    mock_row_data = {
        'pen_id': [pen_id],
        'sim_day': [simulation_day],
        **mock_pen_dataframe_dict,
        **mock_manure_dataframe_dict,
        **mock_manure_handler_daily_output_dataframe_dict,
        **mock_reception_pit_daily_output_dataframe_dict,
        **mock_manure_separator_daily_output_dataframe_dict,
        **mock_manure_treatment_daily_output_dataframe_dict,
        **mock_anaerobic_digestion_daily_output_dataframe_dict
    }

    # Act
    manure_management_output_handler.append_daily_update_output_for_pen(
            simulation_day=simulation_day,
            data=mock_data
    )

    # Assert
    patch_for_process_pen.assert_called_once_with(mock_manure_management_pen)
    patch_for_process_dataclass_output_obj.assert_has_calls([
        mocker.call(mock_pen_manure, PenManure),
        mocker.call(mock_manure_handler_daily_output, ManureHandlerDailyOutput),
        mocker.call(mock_reception_pit_daily_output, ReceptionPitDailyOutput),
        mocker.call(mock_manure_separator_daily_output, ManureSeparatorDailyOutput),
        mocker.call(mock_manure_treatment_daily_output, ManureTreatmentDailyOutput),
        mocker.call(mock_anaerobic_digestion_daily_output, ManureTreatmentDailyOutput, 'ad')
    ])
    patch_for_append_row.assert_called_once_with(mock_row_data)
    assert manure_management_output_handler._df == mock_dataframe_with_appended_row

# TODO: Add more tests for the other methods in this PR
