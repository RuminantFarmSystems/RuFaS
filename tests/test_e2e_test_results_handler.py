import json
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from RUFAS.e2e_test_results_handler import E2ETestResultsHandler, ResultPathType


@pytest.mark.parametrize(
    "diff,successful, convert_variable_name",
    [
        ({}, True, None),
        ({"diff": "diff"}, False, None),
        ({}, True, "dummy_path.csv"),
        ({"diff": "diff"}, False, "dummy_path.csv"),
    ],
)
def test_compare_simulation_outputs_to_expected_outputs(
    mocker: MockerFixture, diff: dict[str, str], successful: bool, convert_variable_name: str
) -> None:
    """Tests _compare_simulation_outputs_to_expected_outputs in TaskManager."""
    json_dir_path: Path = Path("json_dir")
    mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)
    results_path = ResultPathType("test_domain", "expected_results", "actual_results", "tolerance")
    get_result_paths = mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=[results_path])
    mocker.patch(
        "pathlib.Path.iterdir",
        return_value=[
            Path("not/the/path"),
            Path("json_dir/actual_results.json"),
            Path("not/the/path/either"),
        ],
    )
    mocked_open = mocker.patch("builtins.open", mocker.mock_open(read_data="file contents"))
    mocked_load = mocker.patch("json.load", side_effect=[{"a": 1}, {"expected_results": {"a": 1}}])
    mocked_deepdiff = mocker.patch("RUFAS.e2e_test_results_handler.DeepDiff", return_value=diff)
    add_log = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_log")
    add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")
    add_var = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_variable")
    mock_convert_variable_name = mocker.patch(
        "RUFAS.e2e_test_results_handler.E2ETestResultsHandler._convert_expected_result_variable_names"
    )

    E2ETestResultsHandler.compare_actual_and_expected_test_results(
        json_dir_path, convert_variable_name if convert_variable_name else None, "dummy_prefix"
    )

    get_result_paths.assert_called_once()
    assert mocked_open.call_count == 2
    assert mocked_load.call_count == 2
    mocked_deepdiff.assert_called_once()
    if successful:
        assert add_log.call_count == 2
        assert add_error.call_count == 0
        assert add_var.call_count == 1
    else:
        assert add_log.call_count == 1
        assert add_error.call_count == 1
        assert add_var.call_count == 2

    if convert_variable_name:
        mock_convert_variable_name.assert_called_once()
    else:
        mock_convert_variable_name.assert_not_called()


@pytest.mark.parametrize(
    "original, convert_variable_name_table, duplicate_exists, expected",
    [
        ({}, pd.DataFrame({"Original": ["a", "b"], "New": ["c", "d"]}), False, {}),
        (
            {"a": 1, "b": 2, "e": 3, "f": 4},
            pd.DataFrame({"Original": ["a", "b"], "New": ["c", "d"]}),
            False,
            {"c": 1, "d": 2, "e": 3, "f": 4},
        ),
        (
            {"a": 1, "b": 2, "e": 3, "f": 4},
            pd.DataFrame({"Original": ["a", "b"], "News": ["c", "d"]}),
            False,
            KeyError("The conversion table CSV should have both 'Original' and 'New' columns."),
        ),
        (
            {"a": 1, "b": 2, "e": 3, "f": 4},
            pd.DataFrame({"Original": ["a", "b"], "New": ["c", "d"]}),
            True,
            ValueError("Duplicate Mapping Error: The conversion table CSV should not contain duplicate mappings."),
        ),
    ],
)
def test_convert_expected_result_variable_names(
    mocker: MockerFixture,
    original: dict[str, Any],
    convert_variable_name_table: pd.DataFrame,
    duplicate_exists: bool,
    expected: dict[str, Any] | KeyError | ValueError,
) -> None:
    """Tests _convert_expected_result_variable_names in TaskManager."""
    mock_read_csv = mocker.patch("RUFAS.e2e_test_results_handler.pd.read_csv", return_value=convert_variable_name_table)
    mock_duplicate_mappings_exist = mocker.patch(
        "RUFAS.e2e_test_results_handler.E2ETestResultsHandler._duplicate_mappings_exist",
        return_value=duplicate_exists,
    )

    if isinstance(expected, KeyError):
        with pytest.raises(KeyError):
            E2ETestResultsHandler._convert_expected_result_variable_names(original, Path(""))
    elif isinstance(expected, ValueError):
        with pytest.raises(ValueError):
            E2ETestResultsHandler._convert_expected_result_variable_names(original, Path(""))
            mock_duplicate_mappings_exist.assert_called_once_with(convert_variable_name_table)
    else:
        actual = E2ETestResultsHandler._convert_expected_result_variable_names(original, Path(""))
        assert actual == expected
        mock_duplicate_mappings_exist.assert_called_once_with(convert_variable_name_table)

    mock_read_csv.assert_called_once()


@pytest.mark.parametrize(
    "dataframe, expected_duplicate_mappings",
    [
        # No duplicates
        (pd.DataFrame({"group": ["A", "B", "C"], "value": ["X", "Y", "Z"]}), {}),
        # Single duplicate group
        (
            pd.DataFrame({"group": ["A", "A", "B", "C", "C"], "value": ["X", "Y", "Z", "W", "V"]}),
            {"A": ["X", "Y"], "C": ["W", "V"]},
        ),
        # Multiple duplicate groups
        (
            pd.DataFrame({"group": ["A", "A", "B", "B", "C", "C", "D"], "value": ["X", "Y", "Z", "W", "V", "U", "T"]}),
            {"A": ["X", "Y"], "B": ["Z", "W"], "C": ["V", "U"]},
        ),
        # Group with identical values (should not be considered a duplicate)
        (
            pd.DataFrame({"group": ["A", "A", "B", "B", "C"], "value": ["X", "X", "Y", "Z", "W"]}),
            {"A": ["X", "X"], "B": ["Y", "Z"]},
        ),
        # Empty DataFrame
        (pd.DataFrame(columns=["group", "value"]), {}),
        # Single row DataFrame
        (pd.DataFrame({"group": ["A"], "value": ["X"]}), {}),
    ],
)
def test_find_duplicate_mappings(
    dataframe: pd.DataFrame,
    expected_duplicate_mappings: dict[str, list[str]],
) -> None:
    """Tests for E2ETestResultsHandler._find_duplicate_mappings()."""
    result = E2ETestResultsHandler._find_duplicate_mappings(dataframe, "group", "value")
    assert result == expected_duplicate_mappings


@pytest.mark.parametrize(
    "duplicate_original, duplicate_new, expected_result",
    [
        ({}, {}, False),
        ({"A": ["X", "Y"]}, {"X": ["A", "B"]}, True),
        ({"A": ["X", "Y"], "B": ["Z", "W"]}, {}, True),  # Multiple original duplicates, no new column duplicates
        ({}, {"X": ["A", "B"], "Y": ["C", "D"]}, True),  # No original duplicates, multiple new column duplicates
        ({"A": ["X", "Y"]}, {"X": ["A", "B"], "Y": ["C"]}, True),  # Unequal duplicates
        ({"A": ["X"]}, {"X": ["A"]}, True),  # Identical mapping
        ({"a": ["X", "Y"], "A": ["Z"]}, {"x": ["A", "B"], "X": ["C"]}, True),  # Case sensitivity test
        ({"$Var!": ["X", "Y"], "@Var": ["Z", "W"]}, {"X": ["$Var!"], "Z": ["@Var"]}, True),  # Special character test
    ],
)
def test_duplicate_mappings_exist(
    duplicate_original: dict[str, list[str]],
    duplicate_new: dict[str, list[str]],
    expected_result: bool,
    mocker: MockerFixture,
) -> None:
    """Tests for E2ETestResultsHandler._duplicate_mappings_exist()."""
    mock_om_init = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)
    mock_find_duplicate_mappings = mocker.patch(
        "RUFAS.e2e_test_results_handler.E2ETestResultsHandler._find_duplicate_mappings",
        side_effect=[duplicate_original, duplicate_new],
    )
    mock_add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")

    info_map: dict[str, str] = {
        "class": E2ETestResultsHandler.__class__.__name__,
        "function": E2ETestResultsHandler._duplicate_mappings_exist.__name__,
    }
    dummy_df = pd.DataFrame({"Original": [], "New": []})

    result = E2ETestResultsHandler._duplicate_mappings_exist(dummy_df)

    assert result == expected_result
    mock_om_init.assert_called_once_with()
    assert mock_find_duplicate_mappings.call_args_list == [
        mocker.call(dummy_df, group_column_name="Original", list_column_name="New"),
        mocker.call(dummy_df, group_column_name="New", list_column_name="Original"),
    ]
    for original_name, new_names in duplicate_original.items():
        assert (
            mocker.call(
                "Duplicate Mapping Error",
                f"Original variable name: '{original_name}' is mapping to multiple new variable names: {new_names}",
                info_map,
            )
            in mock_add_error.call_args_list
        )

    for new_name, original_names in duplicate_new.items():
        assert (
            mocker.call(
                "Duplicate Mapping Error",
                f"New variable name: '{new_name}' is mapped from multiple original variable names: {original_names}",
                info_map,
            )
            in mock_add_error.call_args_list
        )

    assert mock_add_error.call_count == len(duplicate_original) + len(duplicate_new)


def test_get_test_results_paths(mocker: MockerFixture) -> None:
    """Tests that paths for gathering end-to-end test results are processed correctly."""
    get_data = mocker.patch(
        "RUFAS.e2e_test_results_handler.InputManager.get_data",
        return_value=[
            {
                "domain": "one",
                "expected_results_path": "expected_1",
                "actual_results_path": "actual_1",
                "tolerance": 0.01,
            },
            {
                "domain": "two",
                "expected_results_path": "expected_2",
                "actual_results_path": "actual_2",
                "tolerance": 0.01,
            },
        ],
    )
    expected = [
        ResultPathType("one", "expected_1", "actual_1", 0.01),
        ResultPathType("two", "expected_2", "actual_2", 0.01),
    ]

    actual = E2ETestResultsHandler._get_test_result_paths("dummy_prefix")

    assert actual == expected
    get_data.assert_called_once_with("end_to_end_testing_result_paths.end_to_end_test_result_paths.dummy_prefix")


def mock_diff_result() -> dict[str, dict[str, dict[str, float]]]:
    """Return a mock DeepDiff result for testing."""
    return {
        "values_changed": {
            "key1": {"old_value": 100.0, "new_value": 100.0001},
            "key2": {"old_value": 50.0, "new_value": 51.0},
            "nested_key": {
                "nested": {
                    "key3": {"old_value": 200.0, "new_value": 200.0000001},
                    "key4": {"old_value": 30.0, "new_value": 40.0},
                }
            },
        }
    }


@pytest.mark.parametrize(
    "diff_result, tolerance, expected_keys",
    [
        # Case 1: Basic functionality
        (
            {
                "values_changed": {
                    "key1": {"old_value": 100.0, "new_value": 100.0001},
                    "key2": {"old_value": 50.0, "new_value": 51.0},
                }
            },
            1e-1,
            {"key2"},
        ),
        # Case 2: Nested dictionary
        (
            {
                "values_changed": {
                    "nested_key": {
                        "nested": {
                            "key3": {"old_value": 200.0, "new_value": 200.0000001},
                            "key4": {"old_value": 30.0, "new_value": 40.0},
                        }
                    }
                }
            },
            1e-5,
            {"nested_key"},
        ),
        # Case 3: Empty nested dictionary
        (
            {
                "values_changed": {
                    "nested_key": {
                        "nested": {
                            "key1": {"old_value": 10.0, "new_value": 10.000001},
                            "key2": {"old_value": 20.0, "new_value": 20.000001},
                        }
                    }
                }
            },
            1e-3,
            set(),
        ),
        # Case 4: Boundary tolerance
        (
            {
                "values_changed": {
                    "key1": {"old_value": 10.0, "new_value": 10.000001},
                    "key2": {"old_value": 10.0, "new_value": 10.00001},
                    "key3": {"old_value": 10.0, "new_value": 10.0001},
                    "key4": {"old_value": 10.0, "new_value": 10.001},
                }
            },
            1e-3,
            {"key4"},
        ),
        # Case 5: Non-numeric and missing keys
        (
            {
                "values_changed": {
                    "key1": {"old_value": "a", "new_value": "b"},
                    "key2": {"old_value": 10.0},
                    "key3": {"new_value": 20.0},
                    "key4": {},
                }
            },
            1e-1,
            {"key1", "key2", "key3"},
        ),
    ],
)
def test_filter_insignificant_changes(
    diff_result: dict[str, dict[str, dict[str, float | str]]], tolerance: float, expected_keys: set[str]
) -> None:
    """Integration test for filter_insignificant_changes and associated helper functions."""
    filtered_result = E2ETestResultsHandler.filter_insignificant_changes(diff_result, tolerance)
    remaining_keys = set(filtered_result["values_changed"].keys()) if "values_changed" in filtered_result else set()

    # Assert
    assert remaining_keys == expected_keys


def test_is_significant() -> None:
    """Unit test for is_significant()."""
    assert E2ETestResultsHandler.is_significant({"old_value": 10.0, "new_value": 10.2}, 0.01) is True
    assert E2ETestResultsHandler.is_significant({"old_value": 10.0, "new_value": 10.001}, 0.01) is False
    assert E2ETestResultsHandler.is_significant({"old_value": "a", "new_value": "b"}, 0.01) is True


def test_filter_nested() -> None:
    """Unit test for filter_nested()."""
    diff = {
        "key1": {"old_value": 100.0, "new_value": 100.0001},
        "key2": {"old_value": 50.0, "new_value": 51.0},
    }
    E2ETestResultsHandler.filter_nested(diff, 0.001)
    assert "key1" not in diff
    assert "key2" in diff


@pytest.mark.parametrize(
    "diff, should_update, matching_path, raise_exception",
    [
        ({}, False, "output_dir/actual_results.json", None),
        ({"diff": "some_differences"}, True, "output_dir/actual_results.json", None),
        ({}, False, None, None),
        ({}, False, "output_dir/actual_results.json", IOError("File read error")),
        ({}, False, "output_dir/actual_results.json", json.JSONDecodeError("Invalid JSON", doc="", pos=0)),
    ],
)
def test_update_expected_test_results(
    mocker: MockerFixture,
    diff: dict[str, str],
    should_update: bool,
    matching_path: str | None,
    raise_exception: Exception | None,
) -> None:
    """Tests update_expected_test_results in E2ETestResultsHandler."""
    # Arrange
    output_dir = Path("output_dir")
    mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)
    add_log = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_log")
    add_warning = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_warning")
    add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")

    results_path = mocker.MagicMock()
    results_path.domain = "test_domain"
    results_path.actual_results_path = "actual_results.json"
    results_path.expected_results_path = "expected_results.json"

    get_result_paths = mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=[results_path])

    mocker.patch.object(E2ETestResultsHandler, "_get_matching_path", return_value=matching_path)

    if matching_path:
        mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data='{"expected_results": {}}'))
        if isinstance(raise_exception, json.JSONDecodeError):
            mocker.patch("json.load", side_effect=raise_exception)
        elif raise_exception:
            mock_open.side_effect = raise_exception

        if not raise_exception:
            mocker.patch("json.load", side_effect=[{"a": 1}, {"expected_results": {"b": 2}}])

        mocker.patch("RUFAS.e2e_test_results_handler.DeepDiff", return_value=diff)
        mocker.patch("RUFAS.e2e_test_results_handler.Utility.get_timestamp", return_value="2025-01-29T12:00:00")
        mocker.patch("RUFAS.e2e_test_results_handler.Utility.make_serializable", side_effect=lambda x, **kwargs: x)
        mocker.patch("shutil.copy")
        mock_move = mocker.patch("shutil.move")
        mocker.patch("pathlib.Path.exists", return_value=True)
        mocker.patch("pathlib.Path.unlink")
        mock_write_json = mocker.patch.object(E2ETestResultsHandler, "_write_formatted_json")

    # Act
    if raise_exception:
        with pytest.raises(type(raise_exception)):
            E2ETestResultsHandler.update_expected_test_results(output_dir, "dummy_prefix")
    else:
        E2ETestResultsHandler.update_expected_test_results(output_dir, "dummy_prefix")

    # Assert
    get_result_paths.assert_called_once()

    if matching_path:
        if raise_exception:
            add_error.assert_called_once()
            expected_backup_path = str(results_path.expected_results_path) + ".bak"
            mock_move.assert_called_once_with(Path(expected_backup_path), results_path.expected_results_path)
        else:
            assert add_error.call_count == 0
            expected_log_count = 3 if should_update else 2
            assert add_log.call_count == expected_log_count
            mock_write_json.assert_called_once()
            if diff:
                add_warning.assert_called_once()
    else:
        assert add_error.call_count == 1
        assert add_log.call_count == 1


@pytest.mark.parametrize(
    "dir_contents, expected_match",
    [
        (["actual_results.json", "other_file.txt"], "actual_results.json"),
        (["random_file.json", "another_file.txt"], None),
        (["actual_results_2025.json", "actual_results.json", "another.json"], "actual_results.json"),
        ([], None),
    ],
)
def test_get_matching_path(mocker: MockerFixture, dir_contents: list[str], expected_match: str | None) -> None:
    """Tests _get_matching_path in E2ETestResultsHandler."""

    # Arrange
    dir_path = mocker.MagicMock()
    dir_path.iterdir.return_value = [Path(f"test_dir/{file_name}") for file_name in dir_contents]

    path_set = mocker.MagicMock()
    path_set.actual_results_path = "actual_results.json"

    # Act
    result = E2ETestResultsHandler._get_matching_path(dir_path, path_set)

    # Assert
    if expected_match:
        assert result == Path(f"test_dir/{expected_match}")
    else:
        assert result is None


@pytest.mark.parametrize(
    "data, should_raise",
    [
        (
            {
                "name": "Test",
                "filters": {"type": "some_filter"},
                "expected_results_last_updated": "2025-01-29T12:00:00",
                "expected_results": {"key": "value"},
            },
            False,
        ),
        (
            {
                "name": "Test",
                "filters": {"type": "some_filter"},
                "expected_results_last_updated": "2025-01-29T12:00:00",
            },
            True,
        ),
        (
            {
                "name": "Test",
                "expected_results": {"key": "value"},
            },
            True,
        ),
    ],
)
def test_write_formatted_json(data: dict[str, dict[str, str]], should_raise: bool, mocker: MockerFixture) -> None:
    """Tests _write_formatted_json in E2ETestResultsHandler."""

    # Arrange
    file_path = Path("test_output.json")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    if should_raise:
        mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)
        mock_add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")
        with pytest.raises(ValueError):
            E2ETestResultsHandler._write_formatted_json(file_path, data)
        mock_add_error.assert_called_once()
    else:
        # Act
        E2ETestResultsHandler._write_formatted_json(file_path, data)

        # Assert
        mock_open.assert_called_once_with(file_path, "w")

        written_data = "".join(call.args[0] for call in mock_open().write.call_args_list)
        lines = written_data.split("\n", 1)
        if lines[0].startswith("// WARNING:"):
            written_data = lines[1]
        parsed_json = json.loads(written_data)

        assert "expected_results" in parsed_json
        assert "name" in parsed_json
        assert "filters" in parsed_json
        assert "expected_results_last_updated" in parsed_json
        expected_results_str = json.dumps(data["expected_results"], separators=(",", ":"))
        assert written_data.count(expected_results_str) == 1
