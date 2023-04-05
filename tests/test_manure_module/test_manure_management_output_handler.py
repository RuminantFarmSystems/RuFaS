import collections
from datetime import datetime
from pathlib import Path

import pytest
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


# TODO: Fix this test
# def test_process_pen(mocker: MockFixture) -> None:
#     """Unit test for _process_pen() in manure_management_output_handler.py."""
#     # Arrange
#     mock_manure_management_pen = mocker.MagicMock()
#     mock_manure_management_pen.id = pen_id = 1
#     mock_manure_management_pen.num_animals = num_animals = 2
#     mock_manure_management_pen.num_lactating_cows = num_lactating_cows = 3
#     mock_manure_management_pen.classes_in_pen = '{AnimalClass1, AnimalClass2}'
#     mock_manure_management_pen.housing_type = housing_type = 'HousingType'
#     mock_manure_management_pen.bedding_type = bedding_type = 'BeddingType'
#     mock_manure_management_pen.manure_handler = manure_handler = 'ManureHandler'
#     mock_manure_management_pen.manure_separator = manure_separator = 'ManureSeparator'
#     mock_manure_management_pen.manure_treatment = manure_treatment = 'ManureTreatment'
#
#     mocker.patch(
#             'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
#             'ManureManagementOutputHandler.__init__',
#             return_value=None
#     )
#
#     manure_management_output_handler = ManureManagementOutputHandler()
#     temp_header_prefixes = ManureManagementOutputHandler.HEADER_PREFIXES
#     mock_pen_prefix = '<test_prefix>'
#     ManureManagementOutputHandler.HEADER_PREFIXES = {
#         ManureManagementPen: mock_pen_prefix
#     }
#     temp_header_primary_delimiter = ManureManagementOutputHandler.HEADER_PRIMARY_DELIMITER
#     mock_header_primary_delimiter = '<test_primary_delimiter>'
#     ManureManagementOutputHandler.HEADER_PRIMARY_DELIMITER = mock_header_primary_delimiter
#     pen_data = {
#         'pen_id': [pen_id],
#         'num_animals': [num_animals],
#         'num_lactating_cows': [num_lactating_cows],
#         'animal_types': ['AnimalClass1, AnimalClass2'],
#         'housing_type': [housing_type],
#         'bedding_type': [bedding_type],
#         'handler_type': [manure_handler],
#         'separator_type': [manure_separator],
#         'treatment_type': [manure_treatment],
#     }
#
#     expected_pen_dataframe_dict = {f'{mock_pen_prefix}{mock_header_primary_delimiter}{k}': v
#                                    for k, v in pen_data.items()}
#
#     # Act
#     actual_pen_dataframe_dict = manure_management_output_handler._process_pen(mock_manure_management_pen)
#
#     # Assert
#     assert actual_pen_dataframe_dict == expected_pen_dataframe_dict
#
#     # Cleanup
#     ManureManagementOutputHandler.HEADER_PREFIXES = temp_header_prefixes
#     ManureManagementOutputHandler.HEADER_PRIMARY_DELIMITER = temp_header_primary_delimiter


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
    mock_manure_treatment_accumulated_output = mocker.MagicMock()
    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_data = (
        mock_manure_management_pen,
        mock_manure_handler_daily_output,
        mock_reception_pit_daily_output,
        mock_manure_separator_daily_output,
        mock_manure_treatment_daily_output,
        mock_manure_treatment_accumulated_output,
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
    mock_manure_treatment_accumulated_output_dataframe_dict = {
        '<test_manure_treatment_accumulated_output_field>': ['<test_manure_treatment_accumulated_output_value>']
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
                mock_manure_treatment_accumulated_output_dataframe_dict,
                mock_anaerobic_digestion_daily_output_dataframe_dict
            ]
    )

    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
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
        **mock_manure_treatment_accumulated_output_dataframe_dict,
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
        mocker.call(mock_manure_treatment_accumulated_output, ManureTreatmentDailyOutput, 'acc'),
        mocker.call(mock_anaerobic_digestion_daily_output, ManureTreatmentDailyOutput, 'ad')
    ])
    patch_for_append_row.assert_called_once_with(mock_row_data)
    assert manure_management_output_handler._df == mock_dataframe_with_appended_row


@pytest.mark.parametrize(
        'instance_df_exists',
        [
            True,
            False
        ]
)
def test_append_row(instance_df_exists: bool,
                    mocker: MockFixture) -> None:
    """Unit test for _append_row() in manure_management_output_handler.py."""
    # Arrange
    mock_row_data = {'<test_field>': ['<test_value>']}
    mock_row_dataframe = mocker.MagicMock()
    patch_for_pandas_dataframe_init = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'pd.DataFrame',
            return_value=mock_row_dataframe
    )
    mock_concatenated_dataframe = mocker.MagicMock()
    patch_for_pandas_concat = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'pd.concat',
            return_value=mock_concatenated_dataframe
    )
    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )
    manure_management_output_handler = ManureManagementOutputHandler()
    mock_instance_df = mocker.MagicMock()
    if instance_df_exists:
        manure_management_output_handler._df = mock_instance_df
    else:
        manure_management_output_handler._df = None

    # Act
    actual_df = manure_management_output_handler._append_row(mock_row_data)

    # Assert
    patch_for_pandas_dataframe_init.assert_called_once_with(mock_row_data)
    if instance_df_exists:
        patch_for_pandas_concat.assert_called_once_with([mock_instance_df, mock_row_dataframe], ignore_index=True)
        assert actual_df == mock_concatenated_dataframe
    else:
        assert actual_df == mock_row_dataframe


@pytest.mark.parametrize(
        'instance_df_exists',
        [
            True,
            False
        ]
)
def test_sort_by(instance_df_exists: bool,
                 mocker: MockFixture) -> None:
    """Unit test for sort_by() in manure_management_output_handler.py."""
    # Arrange
    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )
    manure_management_output_handler = ManureManagementOutputHandler()

    if instance_df_exists:
        mock_instance_df = mocker.MagicMock()
        mock_instance_df.sort_values.return_value = None
    else:
        mock_instance_df = None

    manure_management_output_handler._df = mock_instance_df
    mock_sort_columns = ['test_field_1', 'test_field_2']

    # Act
    manure_management_output_handler.sort_by(mock_sort_columns)

    # Assert
    if instance_df_exists:
        mock_instance_df.sort_values.assert_called_once_with(by=mock_sort_columns, inplace=True)
    else:
        assert True


@pytest.mark.parametrize(
        'instance_df_exists',
        [
            True,
            False
        ]
)
def test_move_columns_to_front(instance_df_exists: bool,
                               mocker: MockFixture) -> None:
    """Unit test for move_columns_to_front() in manure_management_output_handler.py."""
    # Arrange
    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )
    manure_management_output_handler = ManureManagementOutputHandler()

    mock_instance_df_columns = ['test_field_1', 'test_field_2', 'test_field_3']
    if instance_df_exists:
        mock_instance_df = mocker.MagicMock()
        mock_instance_df.columns = mock_instance_df_columns
        mock_instance_df.pop.return_value = None
        mock_instance_df.insert.return_value = None
    else:
        mock_instance_df = None

    manure_management_output_handler._df = mock_instance_df

    mock_columns_to_move = ['test_field_2', 'test_field_3']

    # Act
    manure_management_output_handler.move_columns_to_front(mock_columns_to_move)

    # Assert
    if instance_df_exists:
        mock_instance_df.pop.assert_has_calls([
            mocker.call('test_field_2'),
            mocker.call('test_field_3')
        ])
        mock_instance_df.insert.assert_has_calls([
            mocker.call(0, 'test_field_2', None),
            mocker.call(1, 'test_field_3', None)
        ])
    else:
        assert True


def test_sort_by_pen_id_and_simulation_day(mocker: MockFixture) -> None:
    """Unit test for sort_by_pen_id_and_simulation_day() in manure_management_output_handler.py."""
    # Arrange
    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )
    manure_management_output_handler = ManureManagementOutputHandler()

    patch_for_sort_by = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.sort_by',
            return_value=None
    )

    patch_for_move_columns_to_front = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.move_columns_to_front',
            return_value=None
    )

    # Act
    manure_management_output_handler.sort_by_pen_id_and_simulation_day()

    # Assert
    patch_for_sort_by.assert_called_once_with(['pen_id', 'sim_day'])
    patch_for_move_columns_to_front.assert_called_once_with(['pen_id', 'sim_day'])


# TODO: Fix this test
# @pytest.mark.parametrize(
#         'instance_df_exists',
#         [
#             True,
#             False
#         ]
# )
# def test_export_to_csv(instance_df_exists: bool,
#                        mocker: MockFixture) -> None:
#     """Unit test for export_to_csv() in manure_management_output_handler.py."""
#     # Arrange
#     mocker.patch(
#             'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
#             'ManureManagementOutputHandler.__init__',
#             return_value=None
#     )
#     manure_management_output_handler = ManureManagementOutputHandler()
#     if instance_df_exists:
#         mock_instance_df = mocker.MagicMock()
#         mock_instance_df.to_csv.return_value = None
#     else:
#         mock_instance_df = None
#     manure_management_output_handler._df = mock_instance_df
#     mock_csv_output_path = mocker.MagicMock()
#     patch_for_get_csv_output_path = mocker.patch(
#             'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
#             'ManureManagementOutputHandler.get_csv_output_file_path',
#             return_value=mock_csv_output_path
#     )
#
#     # Act
#     actual_csv_output_path = manure_management_output_handler.export_to_csv()
#
#     # Assert
#     if instance_df_exists:
#         mock_instance_df.to_csv.assert_called_once_with(mock_csv_output_path, index=False)
#         patch_for_get_csv_output_path.assert_called_once()
#         assert actual_csv_output_path == mock_csv_output_path
#     else:
#         patch_for_get_csv_output_path.assert_not_called()
#         assert actual_csv_output_path is None


@pytest.mark.parametrize(
        'phrase, delimiter, expected_result',
        [
            ('test phrase', ' ', 'Test Phrase'),
            ('test phrase', '_', 'Test phrase'),
            ('test', ' ', 'Test'),
            ('test', '_', 'Test'),
            ('', ' ', ''),
            ('', '_', ''),
        ]
)
def test_capitalize_first_letters(phrase: str,
                                  delimiter: str,
                                  expected_result: str) -> None:
    """Unit test for _capitalize_first_letters() in manure_management_output_handler.py."""
    # Act
    actual_result = ManureManagementOutputHandler._capitalize_first_letters(phrase, delimiter)

    # Assert
    assert actual_result == expected_result

# TODO: Fix this test
# def test_get_main_output_directory(mocker: MockFixture) -> None:
#     """Unit test for get_main_output_directory_path() in manure_management_output_handler.py."""
#     # Arrange
#     mock_main_output_directory_path = mocker.MagicMock()
#     mock_main_output_directory_path.mkdir.return_value = None
#     patch_for_path_init = mocker.patch(
#             'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
#             'Path',
#             return_value=mock_main_output_directory_path
#     )
#
#     # Act
#     actual_main_output_directory = ManureManagementOutputHandler.get_main_output_directory_path()
#
#     # Assert
#     patch_for_path_init.assert_called_once_with('RUFAS/routines/manure/output')
#     mock_main_output_directory_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)
#     assert actual_main_output_directory == mock_main_output_directory_path


def test_get_csv_output_directory(mocker: MockFixture) -> None:
    """Unit test for get_csv_output_directory_path() in manure_management_output_handler.py."""
    # Arrange
    mock_main_output_directory_path = Path('test_main_output_directory')
    patch_for_get_main_output_directory = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.get_main_output_directory_path',
            return_value=mock_main_output_directory_path
    )
    patch_for_path_mkdir = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'Path.mkdir',
            return_value=None,
            side_effect=None
    )
    expected_csv_dir_path = mock_main_output_directory_path / 'csv'

    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )
    manure_management_output_handler = ManureManagementOutputHandler()

    # Act
    actual_csv_dir_path = manure_management_output_handler.get_csv_output_directory_path()

    # Assert
    patch_for_get_main_output_directory.assert_called_once()
    patch_for_path_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    assert actual_csv_dir_path == expected_csv_dir_path


def test_get_csv_output_path(mocker: MockFixture) -> None:
    """Unit test for _get_csv_output_path() in manure_management_output_handler.py."""
    # Arrange
    mock_csv_output_directory_path = Path('test_csv_output_directory')
    patch_for_get_csv_output_directory_path = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.get_csv_output_directory_path',
            return_value=mock_csv_output_directory_path
    )
    mock_formatted_current_datetime = 'test_formatted_current_datetime'
    patch_for_get_formatted_current_time = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler._get_formatted_current_time',
            return_value=mock_formatted_current_datetime
    )
    file_name = f'manure_management_output_{mock_formatted_current_datetime}.csv'
    expected_csv_output_file_path = mock_csv_output_directory_path / file_name

    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )
    manure_management_output_handler = ManureManagementOutputHandler()

    # Act
    actual_csv_output_path = manure_management_output_handler.get_csv_output_file_path()

    # Assert
    patch_for_get_csv_output_directory_path.assert_called_once()
    patch_for_get_formatted_current_time.assert_called_once()
    assert actual_csv_output_path == expected_csv_output_file_path


def test_empty_main_output_directory(mocker: MockFixture) -> None:
    """Unit test for empty_main_output_directory() in manure_management_output_handler.py."""
    # Arrange
    mock_main_output_directory = mocker.MagicMock()
    patch_for_get_main_output_directory = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.get_main_output_directory_path',
            return_value=mock_main_output_directory
    )
    path_for_delete_files_and_subdirectories = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler._delete_files_and_subdirectories',
            return_value=None
    )
    mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'ManureManagementOutputHandler.__init__',
            return_value=None
    )
    manure_management_output_handler = ManureManagementOutputHandler()

    # Act
    manure_management_output_handler.empty_main_output_directory()

    # Assert
    patch_for_get_main_output_directory.assert_called_once()
    path_for_delete_files_and_subdirectories.assert_called_once_with(mock_main_output_directory)


@pytest.mark.parametrize(
        'path_exists',
        [
            True,
            False]
)
def test_delete_files_and_subdirectories(path_exists: bool,
                                         mocker: MockFixture,
                                         ) -> None:
    """Unit test for _delete_files_and_subdirectories() in manure_management_output_handler.py."""
    # Arrange
    mock_path = mocker.MagicMock()
    mock_path.exists.return_value = path_exists

    mock_file = mocker.MagicMock()
    mock_file.is_file.return_value = True
    mock_file.is_dir.return_value = False
    mock_file.unlink.return_value = None

    mock_dir = mocker.MagicMock()
    mock_dir.is_file.return_value = False
    mock_dir.is_dir.return_value = True
    patch_for_shutil_rmtree = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'shutil.rmtree',
            return_value=None
    )

    mock_iterdir = [mock_file, mock_dir]
    mock_path.iterdir.return_value = mock_iterdir

    # Act
    ManureManagementOutputHandler._delete_files_and_subdirectories(mock_path)

    # Assert
    if path_exists:
        mock_path.iterdir.assert_called_once()

        mock_file.is_file.assert_called_once()
        mock_file.unlink.assert_called_once()

        mock_dir.is_file.assert_called_once()
        mock_dir.is_dir.assert_called_once()
        patch_for_shutil_rmtree.assert_called_once_with(mock_dir)
    else:
        mock_path.iterdir.assert_not_called()

        mock_file.is_file.assert_not_called()
        mock_file.unlink.assert_not_called()

        mock_dir.is_file.assert_not_called()
        mock_dir.is_dir.assert_not_called()
        patch_for_shutil_rmtree.assert_not_called()


def test_get_formatted_current_time(mocker: MockFixture) -> None:
    """Unit test for _get_formatted_current_time() in manure_management_output_handler.py."""
    # Arrange
    mock_current_datetime = datetime(2023, 1, 1, 1, 1, 1)
    patch_for_datetime = mocker.patch(
            'RUFAS.routines.manure.output_handler.manure_management_output_handler.'
            'datetime',
            wraps=datetime
    )
    patch_for_datetime.now.return_value = mock_current_datetime
    expected_formatted_current_datetime = '2023_01_01__01_00'

    # Act
    actual_formatted_current_datetime = ManureManagementOutputHandler._get_formatted_current_time()

    # Assert
    patch_for_datetime.now.assert_called_once()
    assert actual_formatted_current_datetime == expected_formatted_current_datetime
