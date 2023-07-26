from __future__ import annotations

import collections
from datetime import datetime
from pathlib import Path
from typing import Callable, Type

import numpy as np
import pandas as pd
import pytest
from pytest_mock import MockFixture, MockerFixture

from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.output_handler.manure_manager_output_handler import ManureManagerOutputHandler
from RUFAS.routines.manure.pen.manure_manager_pen import ManureManagerPen
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput
from RUFAS.routines.manure.units.units import Units


def test_convert_dataclass_obj_into_formatted_dict(mocker: MockFixture) -> None:
    """
    Unit test for _convert_dataclass_obj_into_formatted_dict() in manure_manager_output_handler.py.

    This test verifies that _convert_dataclass_obj_into_formatted_dict correctly transforms a dataclass object into
    a dictionary with keys formatted as "<prefix><delimiter><field_name><delimiter>(<unit>)".
    The values are stored in lists.

    """
    # Arrange
    mock_dataclass_obj = mocker.MagicMock()
    mock_prefix = '<prefix>'
    mock_delimiter = '<delimiter>'

    expected_dataframe_dict = collections.defaultdict(list)
    num_fields = 10
    mock_data_fields = []
    mock_capitalized_data_fields = []
    mock_units = []
    for i in range(num_fields):
        mock_field = mocker.MagicMock()
        mock_field.name = f'field_num_{i}'
        mock_unit = f'unit_{i}'
        mock_data_fields.append(mock_field)
        mock_capitalized_data_fields.append(f'Field_Num_{i}')
        mock_units.append(mock_unit)
        setattr(mock_dataclass_obj, mock_field.name, i)
        key_name = f'{mock_prefix}{mock_delimiter}' \
                   f'{mock_capitalized_data_fields[i]}{mock_delimiter}({mock_unit})'
        expected_dataframe_dict[key_name].append(i)

    patch_for_capitalize_first_letters = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._capitalize_first_letters',
        side_effect=mock_capitalized_data_fields
    )

    patch_for_vars = mocker.patch(
        'builtins.vars',
        return_value={field.name: unit for field, unit in zip(mock_data_fields, mock_units)}
    )

    mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler.__init__',
        return_value=None
    )
    manure_manager_output_handler = ManureManagerOutputHandler()

    # Act
    actual_dataframe_dict = manure_manager_output_handler._convert_dataclass_obj_into_formatted_dict(
        mock_dataclass_obj,
        tuple(mock_data_fields),
        mock_prefix,
        mock_delimiter
    )

    # Assert
    assert actual_dataframe_dict == expected_dataframe_dict
    assert patch_for_capitalize_first_letters.call_count == num_fields
    assert patch_for_vars.call_count == num_fields
    for i in range(num_fields):
        patch_for_capitalize_first_letters.assert_any_call(mock_data_fields[i].name, '_')
        patch_for_vars.assert_any_call(Units)


def test_process_pen(mocker: MockFixture) -> None:
    """
    Unit test for _process_pen() in manure_manager_output_handler.py.

    This test verifies that _process_pen correctly formats the attributes of a given ManureManagerPen object
    into a dictionary. The dictionary keys follow the "<prefix><delimiter><attribute_name>" format.

    """
    # Arrange
    mock_manure_manager_pen = mocker.MagicMock()
    mock_manure_manager_pen.id = pen_id = 1
    mock_manure_manager_pen.num_animals = num_animals = 3
    mock_manure_manager_pen.num_lactating_cows = num_lactating_cows = 3
    mock_manure_manager_pen.classes_in_pen = '{AnimalClass1, AnimalClass2}'
    mock_manure_manager_pen.housing_type = housing_type = 'HousingType'
    mock_manure_manager_pen.pen_type = pen_type = 'PenType'
    mock_manure_manager_pen.bedding_type = bedding_type = 'BeddingType'
    mock_manure_manager_pen.manure_handler = manure_handler = 'ManureHandler'
    mock_manure_manager_pen.manure_separator = manure_separator = 'ManureSeparator'
    mock_manure_manager_pen.manure_treatment = manure_treatment = 'ManureTreatment'

    mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler.__init__',
        return_value=None
    )

    manure_manager_output_handler = ManureManagerOutputHandler()
    temp_header_prefixes = ManureManagerOutputHandler._HEADER_PREFIXES
    mock_pen_prefix = '<test_prefix>'
    ManureManagerOutputHandler._HEADER_PREFIXES = {
        ManureManagerPen: mock_pen_prefix
    }
    temp_header_primary_delimiter = ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER
    mock_header_primary_delimiter = '<test_primary_delimiter>'
    ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER = mock_header_primary_delimiter
    pen_data = {
        'pen_id': [pen_id],
        'num_animals': [num_animals],
        'num_lactating_cows': [num_lactating_cows],
        'animal_types': ['AnimalClass1, AnimalClass2'],
        'housing_type': [housing_type],
        'pen_type': [pen_type],
        'bedding_type': [bedding_type],
        'handler_type': [manure_handler],
        'separator_type': [manure_separator],
        'treatment_type': [manure_treatment],
    }

    expected_pen_dataframe_dict = {f'{mock_pen_prefix}{mock_header_primary_delimiter}{k}': v
                                   for k, v in pen_data.items()}

    # Act
    actual_pen_dataframe_dict = manure_manager_output_handler._process_pen(mock_manure_manager_pen)

    # Assert
    assert actual_pen_dataframe_dict == expected_pen_dataframe_dict

    # Cleanup
    ManureManagerOutputHandler._HEADER_PREFIXES = temp_header_prefixes
    ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER = temp_header_primary_delimiter


def test_process_dataclass_output_obj(mocker: MockFixture) -> None:
    """
    Unit test for _process_dataclass_output_obj() in manure_manager_output_handler.py.

    This test verifies that _process_dataclass_output_obj correctly processes a dataclass object of a given type and
    formats its attributes into a dictionary suitable for dataframe conversion.

    """
    # Arrange
    mock_dataclass_obj = mocker.MagicMock()
    mock_obj_type = mocker.MagicMock()
    mock_extra_prefix = '<test_prefix>'

    mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler.__init__',
        return_value=None
    )

    manure_manager_output_handler = ManureManagerOutputHandler()

    mock_random_formatted_dict = mocker.MagicMock()
    patch_for_convert_dataclass_obj_into_formatted_dict = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._convert_dataclass_obj_into_formatted_dict',
        return_value=mock_random_formatted_dict
    )

    mock_dataclass_fields = mocker.MagicMock()
    patch_for_dataclass_fields_method = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'fields',
        return_value=mock_dataclass_fields
    )
    temp_header_prefixes = ManureManagerOutputHandler._HEADER_PREFIXES
    mock_header_prefix = '<test_header_prefix>'
    ManureManagerOutputHandler._HEADER_PREFIXES = {
        mock_obj_type: mock_header_prefix
    }
    temp_header_secondary_delimiter = ManureManagerOutputHandler._HEADER_SECONDARY_DELIMITER
    mock_header_secondary_delimiter = '<test_header_secondary_delimiter>'
    ManureManagerOutputHandler._HEADER_SECONDARY_DELIMITER = mock_header_secondary_delimiter

    temp_header_primary_delimiter = ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER
    mock_header_primary_delimiter = '<test_header_primary_delimiter>'
    ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER = mock_header_primary_delimiter

    # Act
    actual_dataframe_dict = manure_manager_output_handler._process_dataclass_output_obj(
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
    ManureManagerOutputHandler._HEADER_PREFIXES = temp_header_prefixes
    ManureManagerOutputHandler._HEADER_SECONDARY_DELIMITER = temp_header_secondary_delimiter
    ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER = temp_header_primary_delimiter


def test_create_dataframe_from_manure_manager_data(mocker: MockFixture) -> None:
    """
    Unit test for _create_dataframe_from_manure_manager_data() in manure_manager_output_handler.py.

    This test verifies that _create_dataframe_from_manure_manager_data correctly transforms a manure manager's data
    into a pandas DataFrame.

    """
    # Arrange
    mock_manure_manager = mocker.MagicMock()
    simulation_day = 1
    mock_pen_id = 1
    mock_pen = mocker.MagicMock(id=mock_pen_id)

    output_keys = ['animal_manure_excretions', 'manure_handler_daily_output', 'reception_pit_daily_output',
                   'manure_separator_daily_output', 'manure_treatment_daily_output',
                   'manure_treatment_accumulated_output', 'anaerobic_digestion_daily_output']
    outputs = {key: mocker.MagicMock() for key in output_keys}
    mock_data = [
        {
            'pen': mock_pen,
            'simulation_day': simulation_day,
            **outputs
        }
    ]
    type(mock_manure_manager).data = mocker.PropertyMock(return_value=mock_data)

    mock_process_pen_results = {'test_pen_key_1': ['test_pen_value_1'], 'test_pen_key_2': ['test_pen_value_2']}
    patch_for_process_pen = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.ManureManagerOutputHandler._process_pen',
        return_value=mock_process_pen_results
    )

    mock_results = {key: {f'test_{key}_key_1': ['test_value_1'], f'test_{key}_key_2': ['test_value_2']}
                    for key in output_keys}
    patch_for_process_dataclass_output_obj = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._process_dataclass_output_obj',
        side_effect=list(mock_results.values())
    )

    expected_dataframe_dict = {'pen_id': [mock_pen_id], 'simulation_day': [simulation_day]}
    for process_result in [mock_process_pen_results, *mock_results.values()]:
        for key, value in process_result.items():
            expected_dataframe_dict.setdefault(key, []).extend(value)

    # Act
    actual_dataframe = ManureManagerOutputHandler._create_dataframe_from_manure_manager_data(mock_manure_manager)

    # Assert
    pd.testing.assert_frame_equal(actual_dataframe, pd.DataFrame(expected_dataframe_dict))
    patch_for_process_pen.assert_called_once_with(mock_pen)
    patch_for_process_dataclass_output_obj.assert_has_calls(
        [
            mocker.call(outputs['animal_manure_excretions'], PenManure, extra_prefix=None),
            mocker.call(outputs['manure_handler_daily_output'], ManureHandlerDailyOutput, extra_prefix=None),
            mocker.call(outputs['reception_pit_daily_output'], ReceptionPitDailyOutput, extra_prefix=None),
            mocker.call(outputs['manure_separator_daily_output'], ManureSeparatorDailyOutput, extra_prefix=None),
            mocker.call(outputs['manure_treatment_daily_output'], ManureTreatmentDailyOutput, extra_prefix=None),
            mocker.call(outputs['manure_treatment_accumulated_output'], ManureTreatmentDailyOutput, extra_prefix='acc'),
            mocker.call(outputs['anaerobic_digestion_daily_output'], ManureTreatmentDailyOutput, extra_prefix='ad'),
        ]
    )


@pytest.mark.parametrize(
    'phrase, delimiter, expected_result',
    [
        ('test phrase', ' ', 'Test Phrase'),  # Regular phrase with space as a delimiter
        ('test phrase', '_', 'Test phrase'),  # Regular phrase with underscore as a delimiter
        ('test', ' ', 'Test'),  # Single-word phrase with space as a delimiter
        ('test', '_', 'Test'),  # Single-word phrase with underscore as a delimiter
        ('', ' ', ''),  # Empty phrase with space as a delimiter
        ('', '_', ''),  # Empty phrase with underscore as a delimiter
    ]
)
def test_capitalize_first_letters(phrase: str, delimiter: str, expected_result: str) -> None:
    """
    Unit test for _capitalize_first_letters() in manure_manager_output_handler.py.

    This test verifies that the _capitalize_first_letters function correctly
    capitalizes the first letter of each word in a given phrase, based on the provided delimiter.

    """
    # Act
    actual_result = ManureManagerOutputHandler._capitalize_first_letters(phrase, delimiter)

    # Assert
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'mock_current_datetime, expected_formatted_time',
    [
        (datetime(2023, 1, 1, 0, 1, 1), '2023_01_01__00_00'),  # The beginning of the day
        (datetime(2023, 1, 1, 12, 1, 1), '2023_01_01__12_00'),  # The middle of the day
        (datetime(2023, 1, 1, 23, 59, 59), '2023_01_01__23_00'),  # The end of the day
    ]
)
def test_get_formatted_current_time(mocker: MockFixture, mock_current_datetime: datetime,
                                    expected_formatted_time: str) -> None:
    """
    Unit test for _get_formatted_current_time() in manure_manager_output_handler.py.

    This test verifies that the _get_formatted_current_time method correctly
    formats the current datetime into a string following the 'yyyy_mm_dd__hh_00' pattern.

    """
    # Arrange
    patch_for_datetime = mocker.patch('RUFAS.routines.manure.output_handler.manure_manager_output_handler.datetime',
                                      wraps=datetime)
    patch_for_datetime.now.return_value = mock_current_datetime

    # Act
    actual_formatted_current_datetime = ManureManagerOutputHandler._get_formatted_current_time()

    # Assert
    patch_for_datetime.now.assert_called_once()
    assert actual_formatted_current_datetime == expected_formatted_time


@pytest.mark.parametrize(
    'sorting_cols_data, non_sorting_cols_data, expected',
    [
        # Empty DataFrame
        (
                {
                    'pen_id': [],
                    'simulation_day': [],
                },
                {},
                False
        ),
        # DataFrame with a single row
        (
                {
                    'pen_id': [1],
                    'simulation_day': [1],
                },
                {
                    'manure_kg': [100],
                    'phosphorus_kg': [10],
                    'ammonia_kg': [5],
                },
                True
        ),
        # DataFrame with multiple rows
        (
                {
                    'pen_id': [1, 2, 1, 2],
                    'simulation_day': [1, 1, 2, 2],
                },
                {
                    'manure_kg': [100, 200, 150, 250],
                    'phosphorus_kg': [10, 20, 15, 25],
                    'ammonia_kg': [5, 10, 7, 12],
                },
                True
        ),
        # DataFrame with multiple rows and NaN/None/0 values
        (
                {
                    'pen_id': [1, 2, 1, 2],
                    'simulation_day': [1, 1, 2, 2],
                },
                {
                    'manure_kg': [100, None, 0, 250],
                    'phosphorus_kg': [10, 20, np.nan, 25],
                    'ammonia_kg': [5, 10, 7, 12],
                    'none_value_col': [None, None, None, None],
                    'nan_value_col': [np.nan, np.nan, np.nan, np.nan],
                    'zero_value_col': [0, 0, 0, 0],
                },
                True
        ),
    ]
)
def test_produce_csv(mocker: MockFixture, tmpdir,
                     sorting_cols_data: dict[str, list[int]],
                     non_sorting_cols_data: dict[str, list[int]],
                     expected: bool) -> None:
    """
    Unit test for produce_csv() in manure_manager_output_handler.py.

    This test verifies that the produce_csv method correctly processes the manure manager's data,
    writes it into CSV files and properly organizes them in the specified directory.

    """
    # Arrange
    mock_manure_manager = mocker.MagicMock()
    df = pd.DataFrame({**sorting_cols_data, **non_sorting_cols_data})
    col_name_format = 'formatted_{}'
    dir_name_format = 'dir_{}'
    csv_filename_format = 'filename_{}'
    aggregate_filename = 'all_manure_module_data'
    dummy_current_time = '1970_01_01__00_00'

    patch_for_create_dataframe = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._create_dataframe_from_manure_manager_data',
        return_value=df
    )

    patch_for_drop_all_zeros = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._drop_all_zeros_nan_none_columns',
        return_value=df
    )

    patch_for_formatted_current_time = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._get_formatted_current_time',
        return_value=dummy_current_time
    )

    patch_for_format_col_name = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._format_col_name',
        side_effect=lambda col_name: col_name_format.format(col_name)
    )

    patch_for_extract_dir_name = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._extract_dir_name_from_col_name',
        side_effect=lambda col_name: dir_name_format.format(col_name)
    )

    patch_for_format_csv_filename = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._format_csv_filename',
        side_effect=lambda filename: csv_filename_format.format(filename)
    )

    temp_dir_path = Path(str(tmpdir))
    csv_dir_path = Path(temp_dir_path, ManureManagerOutputHandler._DEFAULT_OUTPUT_DIR_NAME)
    all_data_file_path = Path(csv_dir_path, f'{aggregate_filename}_{dummy_current_time}.csv')

    # Act
    ManureManagerOutputHandler.produce_csv(temp_dir_path, mock_manure_manager)

    # Assert
    assert csv_dir_path.is_dir() == expected
    assert all_data_file_path.is_file() == expected

    if not expected:
        return

    patch_for_formatted_current_time.assert_called_once()
    patch_for_create_dataframe.assert_called_once_with(mock_manure_manager)
    patch_for_drop_all_zeros.assert_called_once_with(df)

    for col in non_sorting_cols_data:
        patch_for_format_col_name.assert_any_call(col)
        patch_for_extract_dir_name.assert_any_call(col)
        patch_for_format_csv_filename.assert_any_call(col)

        sub_dir_path = Path(csv_dir_path, dir_name_format.format(col))
        assert sub_dir_path.is_dir()
        file_path = Path(sub_dir_path, csv_filename_format.format(col) + '.csv')
        assert file_path.is_file()

        produced_df = pd.read_csv(file_path)
        expected_columns = list(sorting_cols_data.keys()) + [col_name_format.format(col)]
        assert list(produced_df.columns) == expected_columns


@pytest.mark.parametrize(
    'col_name, pipeline, expected, exception',
    [
        ("myColumnName", [lambda x: x.upper()], "MYCOLUMNNAME", None),
        ("anotherColumnName", [lambda x: x[::-1]], "emaNnmuloCrehtona", None),
        ("12345", [lambda x: x[::-1]], "54321", None),
        ("myColumnName", [lambda x: x.lower(), lambda x: x.upper()], "MYCOLUMNNAME", None),
        ("myColumnName", [None], None, TypeError),
        ("myColumnName", [lambda x: 1 / 0], None, Exception),
    ]
)
def test_apply_pipeline_to_col_name(col_name: str, pipeline: list[Callable[[str], str]],
                                    expected: str | None, exception: Type[Exception] | None) -> None:
    """
    Unit test for _apply_pipeline_to_col_name() in manure_manager_output_handler.py.

    This test verifies that the _apply_pipeline_to_col_name method correctly processes a column name
    through a pipeline of transformations, and raises exceptions when expected.

    """
    if exception is not None:
        # Act & Assert
        with pytest.raises(exception):
            ManureManagerOutputHandler._apply_pipeline_to_col_name(col_name, pipeline)
    else:
        # Act
        result = ManureManagerOutputHandler._apply_pipeline_to_col_name(col_name, pipeline)

        # Assert
        assert result == expected


@pytest.mark.parametrize(
    'col_name, mock_results, expected',
    [
        ('ExampleColumnName',
         {'_translate_prefix': 'Translated_Prefix_units',
          '_remove_units': f'TEST{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}NAME_units'},
         'test'),
        ('AnotherExampleColumnName',
         {'_translate_prefix': 'Another_Translated',
          '_remove_units': f'ANOTHER{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}NO_units'},
         'another'),
    ]
)
def test_extract_dir_name_from_col_name(col_name: str, mock_results: dict[str, str],
                                        expected: str, mocker: MockerFixture) -> None:
    """
    Unit test for _extract_dir_name_from_col_name() in manure_manager_output_handler.py.

    This test verifies that the _extract_dir_name_from_col_name method correctly processes a column name
    through a pipeline of transformations and returns the expected directory name.

    """
    # Arrange
    patch_for_translate_prefix = mocker.patch.object(
        ManureManagerOutputHandler, '_translate_prefix',
        side_effect=lambda x: mock_results['_translate_prefix']
    )
    patch_for_remove_units = mocker.patch.object(
        ManureManagerOutputHandler, '_remove_units',
        side_effect=lambda x: mock_results['_remove_units']
    )

    # Act
    result = ManureManagerOutputHandler._extract_dir_name_from_col_name(col_name)

    # Assert
    patch_for_translate_prefix.assert_called_once_with(col_name)
    patch_for_remove_units.assert_called_once_with(mock_results['_translate_prefix'])

    assert result == expected


@pytest.mark.parametrize(
    'col_name, mock_results, expected',
    [
        ('ExampleColumnName',
         {'_remove_prefix': 'Prefix_removed',
          '_remove_units': 'Units_removed',
          '_replace_secondary_header_delimiters_with_spaces': 'Spaces_added',
          '_squeeze_spaces': 'Squeezed_spaces'},
         'squeezed_spaces'),
        ('AnotherExampleColumnName',
         {'_remove_prefix': 'Another_Prefix_removed',
          '_remove_units': 'Another_Units_removed',
          '_replace_secondary_header_delimiters_with_spaces': 'Another_Spaces_added',
          '_squeeze_spaces': 'Another_Squeezed_spaces'},
         'another_squeezed_spaces'),
    ]
)
def test_format_csv_filename(col_name: str, mock_results: dict[str, str],
                             expected: str, mocker: MockerFixture) -> None:
    """
    Unit test for _format_csv_filename() in manure_manager_output_handler.py.

    This test verifies that the _format_csv_filename method correctly processes a column name
    through a pipeline of transformations and returns the expected CSV filename.

    """
    # Arrange
    patch_for_remove_prefix = mocker.patch.object(
        ManureManagerOutputHandler, '_remove_prefix',
        side_effect=lambda x: mock_results['_remove_prefix']
    )
    patch_for_remove_units = mocker.patch.object(
        ManureManagerOutputHandler, '_remove_units',
        side_effect=lambda x: mock_results['_remove_units']
    )
    patch_for_replace_secondary_header_delimiters_with_spaces = mocker.patch.object(
        ManureManagerOutputHandler, '_replace_secondary_header_delimiters_with_spaces',
        side_effect=lambda x: mock_results['_replace_secondary_header_delimiters_with_spaces']
    )
    patch_for_squeeze_spaces = mocker.patch.object(
        ManureManagerOutputHandler, '_squeeze_spaces',
        side_effect=lambda x: mock_results['_squeeze_spaces']
    )

    # Act
    result = ManureManagerOutputHandler._format_csv_filename(col_name)

    # Assert
    patch_for_remove_prefix.assert_called_once_with(col_name)
    patch_for_remove_units.assert_called_once_with(mock_results['_remove_prefix'])
    patch_for_replace_secondary_header_delimiters_with_spaces.assert_called_once_with(
        mock_results['_remove_units']
    )
    patch_for_squeeze_spaces.assert_called_once_with(
        mock_results['_replace_secondary_header_delimiters_with_spaces']
    )

    assert result == expected


@pytest.mark.parametrize(
    'col_name, mock_results, expected',
    [
        ('ExampleColumnName',
         {'_remove_prefix': 'Prefix_removed',
          '_remove_units': 'Units_removed'},
         'units_removed'),
        ('AnotherExampleColumnName',
         {'_remove_prefix': 'Another_Prefix_removed',
          '_remove_units': 'Another_Units_removed'},
         'another_units_removed'),
    ]
)
def test_format_col_name(col_name: str, mock_results: dict[str, str],
                         expected: str, mocker: MockerFixture) -> None:
    """
    Unit test for _format_col_name() in manure_manager_output_handler.py.

    This test verifies that the _format_col_name method correctly processes a column name
    through a pipeline of transformations and returns the expected formatted column name.

    """
    # Arrange
    patch_for_remove_prefix = mocker.patch.object(
        ManureManagerOutputHandler, '_remove_prefix',
        side_effect=lambda x: mock_results['_remove_prefix']
    )
    patch_for_remove_units = mocker.patch.object(
        ManureManagerOutputHandler, '_remove_units',
        side_effect=lambda x: mock_results['_remove_units']
    )

    # Act
    result = ManureManagerOutputHandler._format_col_name(col_name)

    # Assert
    patch_for_remove_prefix.assert_called_once_with(col_name)
    patch_for_remove_units.assert_called_once_with(mock_results['_remove_prefix'])

    assert result == expected


@pytest.mark.parametrize(
    'df, expected_df',
    [
        (
                pd.DataFrame({
                    'column_with_zeros': [0, 0, 0],
                    'column_with_nans': [np.nan, np.nan, np.nan],
                    'column_with_none': [None, None, None],
                    'valid_column': ['A', 'B', 'C']
                }),
                pd.DataFrame({
                    'valid_column': ['A', 'B', 'C']
                })
        ),
        (
                pd.DataFrame({
                    'column_with_zeros_nans': [0, np.nan, 0],
                    'column_with_zeros_none': [0, None, 0],
                    'column_with_nans_none': [np.nan, None, np.nan],
                    'valid_column': [1, 2, 3],
                    'valid_column_2': ['A', 'B', 'C']
                }),
                pd.DataFrame({
                    'column_with_zeros_nans': [0, np.nan, 0],
                    'column_with_zeros_none': [0, None, 0],
                    'valid_column': [1, 2, 3],
                    'valid_column_2': ['A', 'B', 'C']
                })
        ),
        (
                pd.DataFrame({
                    'column_with_mixed_values': [0, np.nan, 'A'],
                    'column_with_valid_values': ['A', 'B', 'C']
                }),
                pd.DataFrame({
                    'column_with_mixed_values': [0, np.nan, 'A'],
                    'column_with_valid_values': ['A', 'B', 'C']
                })
        )
    ]
)
def test_drop_all_zeros_nan_none_columns(df: pd.DataFrame, expected_df: pd.DataFrame) -> None:
    """
    Unit test for _drop_all_zeros_nan_none_columns() in manure_manager_output_handler.py.

    This test verifies that the _drop_all_zeros_nan_none_columns method correctly processes a DataFrame
    and returns a DataFrame with all columns containing only zeros, NaNs, or None dropped. A column that
    contains a mix of NaN and None values should also be dropped.

    """
    # Act
    result_df = ManureManagerOutputHandler._drop_all_zeros_nan_none_columns(df)

    # Assert
    pd.testing.assert_frame_equal(result_df, expected_df)


@pytest.mark.parametrize(
    's, delimiter, expected',
    [
        ('test string', ' ', 'Test String'),
        ('another_test_string', '_', 'Another_Test_String'),
        ('mixed Delimiters', ' ', 'Mixed Delimiters'),
        ('', ' ', ''),
        ('singleWord', ' ', 'SingleWord'),
        (None, ' ', None),
    ],
)
def test_capitalize_first_letters(s: str, delimiter: str, expected: str) -> None:
    """
    Unit test for _capitalize_first_letters() in manure_manager_output_handler.py.

    This test verifies that the _capitalize_first_letters method correctly capitalizes
    the first letter of each word in a string, with words being split at each occurrence
    of a specified delimiter.

    """
    # Act
    result = ManureManagerOutputHandler._capitalize_first_letters(s, delimiter)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    'prefix, expected',
    [
        ('pen', 'Pen Info'),
        ('manure', 'Animal Module Input'),
        ('handler', 'Manure Handler'),
        ('rp', 'Reception Pit'),
        ('sep', 'Manure Separator'),
        ('tx', 'Manure Treatment'),
        ('tx_acc', 'Accumulated Manure Treatment'),
        ('tx_ad', 'Anaerobic Digester'),
        ('dummy_prefix', 'dummy_prefix')
    ]
)
def test_get_full_prefix(prefix: str, expected: str) -> None:
    """
    Unit test for _get_full_prefix() in manure_manager_output_handler.py.

    This test verifies that the _get_full_prefix method correctly maps a given prefix
    to its more descriptive version or returns the original prefix if no match is found
    in the predefined mapping.

    """
    # Act
    result = ManureManagerOutputHandler._get_full_prefix(prefix)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    'header, expected',
    [
        (f'prefix{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}restOfHeader', 'restOfHeader'),
        ('headerNoPrefix', 'headerNoPrefix'),
        (f'prefix1{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}'
         f'prefix2{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}restOfHeader',
         f'prefix2{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}restOfHeader'),
        (f'prefixOnly{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}', ''),
    ]
)
def test_remove_prefix(header: str, expected: str) -> None:
    """
    Unit test for _remove_prefix() in manure_manager_output_handler.py.

    This test verifies that the _remove_prefix method correctly removes the prefix
    from a string at the first occurrence of the primary delimiter. If no delimiter
    is present in the string, it returns the original string.
    If there is no text after the prefix and delimiter, it returns an empty string.

    """
    # Act
    result = ManureManagerOutputHandler._remove_prefix(header)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    'header, mock_get_full_prefix_return_value, expected',
    [
        (f'pen{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}restOfHeader', 'Pen Info',
         f'Pen Info{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}restOfHeader'),
        (f'invalidPrefix{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}restOfHeader', 'invalidPrefix',
         f'invalidPrefix{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}restOfHeader'),
        ('noDelimiter', 'noDelimiter', 'noDelimiter')
    ]
)
def test_translate_prefix(mocker: MockFixture, header: str,
                          mock_get_full_prefix_return_value: str, expected: str) -> None:
    """
    Unit test for _translate_prefix() in manure_manager_output_handler.py.

    This test verifies that the _translate_prefix method correctly translates
    the prefix of a string to its more descriptive version. If no valid prefix
    is present, it returns the original header. If there's no delimiter, it
    also returns the original header.

    """
    # Arrange
    mocker.patch.object(
        ManureManagerOutputHandler, '_get_full_prefix',
        return_value=mock_get_full_prefix_return_value)

    # Act
    result = ManureManagerOutputHandler._translate_prefix(header)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    'header, expected',
    [
        (f'HeaderWithUnits{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}(units)',
         'HeaderWithUnits'),
        ('HeaderWithoutUnits', 'HeaderWithoutUnits'),
        (f'HeaderWithMultiple{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}(units)'
         f'{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}(moreUnits)',
         f'HeaderWithMultiple__(units)'),
        (f'HeaderWithEmptyUnits{ManureManagerOutputHandler._HEADER_PRIMARY_DELIMITER}()',
         'HeaderWithEmptyUnits'),
    ]
)
def test_remove_units(header: str, expected: str) -> None:
    """
    Unit test for _remove_units() in manure_manager_output_handler.py.

    This test verifies that the _remove_units method correctly removes any units
    from the input string. Units are assumed to be enclosed in parentheses. If
    there are no units in the header, the original header is returned. If there
    are multiple sets of units, then only the rightmost set is removed.

    """
    # Act
    result = ManureManagerOutputHandler._remove_units(header)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    'header, expected',
    [
        (f'Header{ManureManagerOutputHandler._HEADER_SECONDARY_DELIMITER}WithDelimiter',
         'Header WithDelimiter'),
        (f'Header{ManureManagerOutputHandler._HEADER_SECONDARY_DELIMITER}'
         f'{ManureManagerOutputHandler._HEADER_SECONDARY_DELIMITER}WithTwoDelimiters',
         'Header WithTwoDelimiters'),
        (f'Header{ManureManagerOutputHandler._HEADER_SECONDARY_DELIMITER}'
         f'{ManureManagerOutputHandler._HEADER_SECONDARY_DELIMITER}'
         f'{ManureManagerOutputHandler._HEADER_SECONDARY_DELIMITER}WithThreeDelimiters',
         'Header WithThreeDelimiters'),
        (f'HeaderWithoutDelimiter',
         'HeaderWithoutDelimiter'),
    ]
)
def test_replace_secondary_header_delimiters_with_spaces(header: str, expected: str) -> None:
    """
    Unit test for _replace_secondary_header_delimiters_with_spaces() in manure_manager_output_handler.py.

    This test verifies that the _replace_secondary_header_delimiters_with_spaces method correctly replaces
    any instances of one or more consecutive secondary header delimiters in the input string with a single space.

    """
    # Act
    result = ManureManagerOutputHandler._replace_secondary_header_delimiters_with_spaces(header)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    'input_string, expected',
    [
        ('StringWithNoSpaces', 'StringWithNoSpaces'),
        (' StringWithLeadingSpace', 'StringWithLeadingSpace'),
        ('StringWithTrailingSpace ', 'StringWithTrailingSpace'),
        (' StringWithLeadingAndTrailingSpaces ', 'StringWithLeadingAndTrailingSpaces'),
        ('String With Multiple Spaces', 'String With Multiple Spaces'),
        ('String  With  Multiple  Extra  Spaces', 'String With Multiple Extra Spaces'),
        ('   String  With  Leading,  Trailing,  And  Extra  Spaces   ',
         'String With Leading, Trailing, And Extra Spaces'),
    ]
)
def test_squeeze_spaces(input_string: str, expected: str) -> None:
    """
    Unit test for _squeeze_spaces() in manure_manager_output_handler.py.

    This test verifies that the _squeeze_spaces method correctly replaces
    instances of one or more consecutive spaces in the input string with a single space,
    and then removes leading and trailing spaces from the resulting string.

    """
    # Act
    result = ManureManagerOutputHandler._squeeze_spaces(input_string)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    'title, translate_prefix_return, remove_units_return, replace_delimiter_return, capitalize_first_letters_return, squeeze_spaces_return, expected',
    [
        ('PREFIX_TitleWithDelimiters:Value', 'TitleWithDelimiters:Value', 'TitleWithDelimiters',
         'Title With Delimiters', 'Title With Delimiters', 'Title With Delimiters', 'Title With Delimiters'),
        ('PREFIXTitleWithoutDelimiters', 'TitleWithoutDelimiters', 'TitleWithoutDelimiters',
         'TitleWithoutDelimiters', 'TitleWithoutDelimiters', 'TitleWithoutDelimiters', 'TitleWithoutDelimiters'),
        ('TitleWithoutPrefixAndDelimiters', 'TitleWithoutPrefixAndDelimiters', 'TitleWithoutPrefixAndDelimiters',
         'TitleWithoutPrefixAndDelimiters', 'TitleWithoutPrefixAndDelimiters', 'TitleWithoutPrefixAndDelimiters',
         'TitleWithoutPrefixAndDelimiters'),
        ('PREFIX_Title_With_Multiple__Delimiters:Value', 'Title_With_Multiple__Delimiters:Value',
         'Title - With - Multiple Delimiters', 'Title - With - Multiple Delimiters',
         'Title - With - Multiple Delimiters', 'Title - With - Multiple Delimiters',
         'Title - With - Multiple Delimiters'),
        ('PREFIX_Title___With___Extra___Spaces:Value', 'Title___With___Extra___Spaces:Value',
         'Title - With - Extra Spaces', 'Title - With - Extra Spaces', 'Title - With - Extra Spaces',
         'Title - With - Extra Spaces', 'Title - With - Extra Spaces'),
        ('', '', '', '', '', '', ''),
    ]
)
def test_format_title(mocker: MockerFixture, title: str, translate_prefix_return: str, remove_units_return: str,
                      replace_delimiter_return: str, capitalize_first_letters_return: str, squeeze_spaces_return: str,
                      expected: str) -> None:
    """
    Unit test for _format_title() in manure_manager_output_handler.py.

    This test verifies that the _format_title method correctly formats a title by
    translating prefix, removing units, replacing primary delimiter with ' - ',
    replacing other delimiters with spaces, capitalizing first letters and squeezing spaces.

    """
    patch_for_translate_prefix = mocker.patch.object(ManureManagerOutputHandler, '_translate_prefix',
                                                     return_value=translate_prefix_return)
    patch_for_remove_units = mocker.patch.object(ManureManagerOutputHandler, '_remove_units',
                                                 return_value=remove_units_return)
    patch_for_replace_delimiter = mocker.patch.object(
        ManureManagerOutputHandler, '_replace_secondary_header_delimiters_with_spaces',
        return_value=replace_delimiter_return)
    patch_for_capitalize_first_letters = mocker.patch.object(ManureManagerOutputHandler, '_capitalize_first_letters',
                                                             return_value=capitalize_first_letters_return)
    patch_for_squeeze_spaces = mocker.patch.object(ManureManagerOutputHandler, '_squeeze_spaces',
                                                   return_value=squeeze_spaces_return)

    # Act
    result = ManureManagerOutputHandler._format_title(title)

    # Assert
    assert result == expected

    patch_for_translate_prefix.assert_called_once_with(title)
    patch_for_remove_units.assert_called_once_with(translate_prefix_return)
    patch_for_replace_delimiter.assert_called_once_with(remove_units_return)
    patch_for_capitalize_first_letters.assert_called_once_with(replace_delimiter_return)
    patch_for_squeeze_spaces.assert_called_once_with(capitalize_first_letters_return)


@pytest.mark.parametrize(
    'fixed_cols_data, non_fixed_cols_data, pen_ids',
    [
        (
                {
                    'pen_id': [1, 2, 3],
                    'simulation_day': [1, 2, 3],
                },
                {
                    'other_col': [4, 5, 6]
                },
                [1, 2, 3],
        ),
        (
                {
                    'pen_id': [1, 1, 1],
                    'simulation_day': [1, 2, 3],
                },
                {
                    'other_col': [np.nan, 5, 6]
                },
                [1],
        ),
    ]
)
def test_produce_graphics(mocker: MockFixture, tmpdir,
                          fixed_cols_data: dict[str, list[int]],
                          non_fixed_cols_data: dict[str, list[int]],
                          pen_ids: list[int]) -> None:
    """
    Unit test for produce_graphics() in manure_manager_output_handler.py.

    This test verifies that the produce_graphics method correctly processes the manure manager's data,
    generates the correct plots, and properly organizes them in the specified directory.

    """
    # Arrange
    mock_manure_manager = mocker.MagicMock()
    df = pd.DataFrame({**fixed_cols_data, **non_fixed_cols_data})

    col_name_format = 'formatted_{}'
    dir_name_format = 'dir_{}'

    patch_for_create_dataframe = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._create_dataframe_from_manure_manager_data',
        return_value=df
    )

    patch_for_format_title = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._format_title',
        side_effect=lambda col_name: col_name_format.format(col_name)
    )

    patch_for_extract_dir_name = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._extract_dir_name_from_col_name',
        side_effect=lambda col_name: dir_name_format.format(col_name)
    )

    patch_for_format_label = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._format_label',
        side_effect=lambda col_name: col_name_format.format(col_name)
    )

    patch_for_make_scatter_plot = mocker.patch(
        'RUFAS.routines.manure.output_handler.manure_manager_output_handler.'
        'ManureManagerOutputHandler._make_simple_scatter_plot_with_matplotlib'
    )

    temp_dir_path = Path(str(tmpdir))
    graphics_dir_path = Path(temp_dir_path, ManureManagerOutputHandler._DEFAULT_OUTPUT_DIR_NAME)

    # Act
    ManureManagerOutputHandler.produce_graphics(temp_dir_path, mock_manure_manager)

    # Assert
    assert graphics_dir_path.is_dir()
    patch_for_create_dataframe.assert_called_once_with(mock_manure_manager)

    for col in non_fixed_cols_data:
        patch_for_extract_dir_name.assert_any_call(col)
        patch_for_format_title.assert_any_call(col)
        patch_for_format_label.assert_any_call(col)
        sub_dir_path = Path(graphics_dir_path, dir_name_format.format(col))
        assert sub_dir_path.is_dir()

        for pen_id in pen_ids:
            output_sub_dir = Path(sub_dir_path, 'Pen' + str(pen_id))
            assert output_sub_dir.is_dir()

        assert patch_for_make_scatter_plot.call_count == len(pen_ids) * len(non_fixed_cols_data)


@pytest.mark.parametrize(
    'x_values, y_values, x_label, y_label, title',
    [
        ([1, 2, 3], [4, 5, 6], 'x', 'y', 'title'),  # normal data
        ([1, 2, 3], [4, None, 6], 'x', 'y', 'title'),  # data with None
        ([1, 2, 3], [4, np.nan, 6], 'x', 'y', 'title'),  # data with NaN
        ([1, 2, 3], [-4, -5, -6], 'x', 'y', 'title'),  # negative data in y_values
        ([1, 2, 3], [0, 0, 0], 'x', 'y', 'title'),  # zero data in y_values
        ([1], [1], 'x', 'y', 'title'),  # only one data point
        ([1.1, 2.2, 3.3], [4.4, 5.5, 6.6], 'x', 'y', 'title'),  # non-integer numbers
        ([], [], 'x', 'y', 'title'),  # empty lists
    ]
)
def test_make_simple_scatter_plot_with_matplotlib(tmpdir, x_values: list[int], y_values: list[int | None | float],
                                                  x_label: str, y_label: str, title: str) -> None:
    """
    Unit test for _make_simple_scatter_plot_with_matplotlib() in manure_manager_output_handler.py.

    This test verifies that the _make_simple_scatter_plot_with_matplotlib method correctly processes the given series,
    generates the correct plot, and properly saves it in the specified directory.

    """
    # Arrange
    output_path = Path(str(tmpdir), 'test_plot.png')
    x = pd.Series(x_values)
    y = pd.Series(y_values)

    # Act
    ManureManagerOutputHandler._make_simple_scatter_plot_with_matplotlib(output_path, x, y, x_label, y_label, title)

    # Assert
    if not x_values or not y_values:
        assert not output_path.exists()
    elif None in y_values or np.nan in y_values:
        assert not output_path.exists()
    else:
        assert output_path.exists()
        assert output_path.stat().st_size > 0  # check that the file is not empty
