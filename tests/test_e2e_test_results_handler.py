import json
import math
from pathlib import Path
import re
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
from RUFAS.output_manager import OutputManager
import pytest
from pytest_mock import MockerFixture

from RUFAS.e2e_test_results_handler import E2ETestResultsHandler, MUST_CHANGE_VARIABLES_KEY, ResultPathType


def write_json_file(path: Path, contents: Any) -> None:
    """Writes JSON, or the raw text of a string, to the given path."""
    with open(path, "w", encoding="utf-8") as file:
        if isinstance(contents, str):
            file.write(contents)
        else:
            json.dump(contents, file)


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
        json_dir_path, convert_variable_name if convert_variable_name else None, "dummy_prefix", set()
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


def test_process_test_result_averaging(mocker: MockerFixture, tmp_path: Path) -> None:
    """Tests process_test_result_averaging in E2ETestResultsHandler."""
    e2e_group = "test_e2e_group"
    e2e_runs = [
        {
            "output_prefix": "run_1",
            "e2e_group": e2e_group,
            "json_output_directory": str(tmp_path),
        },
        {
            "output_prefix": "run_2",
            "e2e_group": e2e_group,
            "json_output_directory": str(tmp_path),
        },
    ]

    path_set_1 = mocker.Mock(actual_results_path="test_e2e_group_animal_results.json")
    path_set_2 = mocker.Mock(actual_results_path="test_e2e_group_field_results.json")

    result_paths_1 = [
        tmp_path / "run_1_animal_results.json",
        tmp_path / "run_2_animal_results.json",
    ]
    result_paths_2 = [
        tmp_path / "run_1_field_results.json",
        tmp_path / "run_2_field_results.json",
    ]

    averaged_results_1 = {"animal_output": {"values": [1.0, 2.0]}}
    averaged_results_2 = {"field_output": {"values": [3.0, 4.0]}}

    mocker.patch.object(
        E2ETestResultsHandler,
        "_get_test_result_paths",
        return_value=[path_set_1, path_set_2],
    )
    extract_results_paths = mocker.patch.object(
        E2ETestResultsHandler,
        "_extract_results_paths",
        side_effect=[result_paths_1, result_paths_2],
    )
    average_test_results = mocker.patch.object(
        E2ETestResultsHandler,
        "_average_test_results",
        side_effect=[averaged_results_1, averaged_results_2],
    )

    result = E2ETestResultsHandler.process_test_result_averaging(
        e2e_group,
        e2e_runs,
    )

    expected_directory = tmp_path / "averaged" / e2e_group

    assert result == expected_directory
    assert expected_directory.exists()

    assert extract_results_paths.call_args_list == [
        mocker.call(
            e2e_runs=e2e_runs,
            json_output_directory=tmp_path,
            actual_results_path=Path(path_set_1.actual_results_path),
        ),
        mocker.call(
            e2e_runs=e2e_runs,
            json_output_directory=tmp_path,
            actual_results_path=Path(path_set_2.actual_results_path),
        ),
    ]

    assert average_test_results.call_args_list == [
        mocker.call(result_paths_1),
        mocker.call(result_paths_2),
    ]

    with open(
        expected_directory / "test_e2e_group_animal_results.json_averaged.json",
        "r",
        encoding="utf-8",
    ) as averaged_file:
        assert json.load(averaged_file) == averaged_results_1

    with open(
        expected_directory / "test_e2e_group_field_results.json_averaged.json",
        "r",
        encoding="utf-8",
    ) as averaged_file:
        assert json.load(averaged_file) == averaged_results_2


def test_process_test_result_averaging_raises_error_when_no_runs_are_provided(
    mocker: MockerFixture,
) -> None:
    e2e_group = "test_e2e_group"
    add_error = mocker.patch.object(OutputManager, "add_error")

    with pytest.raises(
        ValueError,
        match=f"Cannot average E2E results for '{e2e_group}' because no runs were provided.",
    ):
        E2ETestResultsHandler.process_test_result_averaging(
            e2e_group,
            [],
        )

    add_error.assert_called_once_with(
        "E2E Results Averaging Error",
        "No E2E runs data sent to 'process_test_result_averaging()' function.",
        info_map={
            "class": E2ETestResultsHandler.__class__.__name__,
            "function": E2ETestResultsHandler.process_test_result_averaging.__name__,
        },
    )


@pytest.mark.parametrize(
    "test_results, validate_values_return, expected_result, expected_warning",
    [
        (
            [
                {"DISCLAIMER": "Test disclaimer"},
                {"DISCLAIMER": "Different disclaimer"},
            ],
            True,
            {"DISCLAIMER": "Test disclaimer"},
            None,
        ),
        (
            [
                {"test_output": {"metadata": "test"}},
                {"test_output": {"metadata": "test"}},
            ],
            True,
            {"test_output": {"metadata": "test"}},
            None,
        ),
        (
            [
                {"test_output": {"metadata": "first"}},
                {"test_output": {"metadata": "second"}},
            ],
            True,
            {},
            "Non-matching data in reference output for test_output",
        ),
        (
            [
                {"test_output": {"values": [1.0]}},
                {"test_output": {"values": [2.0]}},
            ],
            False,
            {},
            None,
        ),
    ],
)
def test_average_test_results_special_cases(
    mocker: MockerFixture,
    test_results: list[dict[str, Any]],
    validate_values_return: bool,
    expected_result: dict[str, Any],
    expected_warning: str | None,
) -> None:
    results_paths = [
        Path("run_1.json"),
        Path("run_2.json"),
    ]

    mocker.patch.object(
        E2ETestResultsHandler,
        "_load_results",
        return_value=test_results,
    )
    mocker.patch.object(
        E2ETestResultsHandler,
        "_validate_results",
    )
    mocker.patch.object(
        E2ETestResultsHandler,
        "_validate_values",
        return_value=validate_values_return,
    )
    average_output_values = mocker.patch.object(
        E2ETestResultsHandler,
        "_average_output_values",
    )
    add_warning = mocker.patch.object(OutputManager, "add_warning")

    actual = E2ETestResultsHandler._average_test_results(results_paths)

    assert actual == expected_result
    average_output_values.assert_not_called()

    if expected_warning is None:
        add_warning.assert_not_called()
    else:
        add_warning.assert_called_once_with(
            "E2E Results Averaging Error",
            expected_warning,
            info_map={
                "class": E2ETestResultsHandler.__class__.__name__,
                "function": E2ETestResultsHandler._average_test_results.__name__,
            },
        )


def test_average_test_results_averages_valid_output_values(mocker: MockerFixture) -> None:
    results_paths = [
        Path("run_1.json"),
        Path("run_2.json"),
    ]
    test_results = [
        {
            "test_output": {
                "values": [1.0, 2.0],
                "units": "kg",
            },
        },
        {
            "test_output": {
                "values": [3.0, 4.0],
                "units": "kg",
            },
        },
    ]
    averaged_values = [2.0, 3.0]

    mocker.patch.object(
        E2ETestResultsHandler,
        "_load_results",
        return_value=test_results,
    )
    mocker.patch.object(
        E2ETestResultsHandler,
        "_validate_results",
    )
    validate_values = mocker.patch.object(
        E2ETestResultsHandler,
        "_validate_values",
        return_value=True,
    )
    average_output_values = mocker.patch.object(
        E2ETestResultsHandler,
        "_average_output_values",
        return_value=averaged_values,
    )

    actual = E2ETestResultsHandler._average_test_results(results_paths)

    assert actual == {
        "test_output": {
            "values": averaged_values,
            "units": "kg",
        },
    }

    validate_values.assert_called_once_with(
        results_paths,
        "test_output",
        [test_results[0]["test_output"], test_results[1]["test_output"]],
        [1.0, 2.0],
    )
    average_output_values.assert_called_once_with(
        "test_output",
        [1.0, 2.0],
        [test_results[0]["test_output"], test_results[1]["test_output"]],
    )


@pytest.mark.parametrize(
    "reference_values, matching_values, expected_values, expected_warning",
    [
        (
            ["test"],
            ["test", "test"],
            ["test"],
            None,
        ),
        (
            ["test"],
            ["test", "different"],
            ["test"],
            "Non-numeric values differ for 'test_output' at index 0.",
        ),
        (
            [1.0],
            [1.0, "invalid"],
            [1.0],
            (
                "Inconsistent numeric value types for 'test_output' at index 0. "
                "Values: [1.0, 'invalid']. "
                "Types: ['float', 'str']."
            ),
        ),
        (
            [1],
            [1, 1],
            [1],
            None,
        ),
        (
            [1.0],
            [1.0, 3.0],
            [2.0],
            None,
        ),
        (
            [float("nan")],
            [float("nan"), float("nan")],
            [float("nan")],
            None,
        ),
    ],
)
def test_average_output_values(
    mocker: MockerFixture,
    reference_values: list[Any],
    matching_values: list[Any],
    expected_values: list[Any],
    expected_warning: str | None,
) -> None:
    output_name = "test_output"
    matching_outputs = [{"values": [value]} for value in matching_values]

    add_warning = mocker.patch.object(OutputManager, "add_warning")

    actual = E2ETestResultsHandler._average_output_values(
        output_name,
        reference_values,
        matching_outputs,
    )

    if all(isinstance(value, float) and math.isnan(value) for value in expected_values):
        assert len(actual) == 1
        assert math.isnan(actual[0])
    else:
        assert actual == expected_values

    if expected_warning is None:
        add_warning.assert_not_called()
    else:
        add_warning.assert_called_once_with(
            "E2E Results Averaging Error",
            expected_warning,
            info_map={
                "class": E2ETestResultsHandler.__class__.__name__,
                "function": E2ETestResultsHandler._average_output_values.__name__,
            },
        )


@pytest.mark.parametrize(
    "matching_output, expected_result, expected_error, expected_warning",
    [
        (
            {"values": [1.0, 2.0]},
            True,
            None,
            None,
        ),
        (
            {},
            False,
            "E2E output 'test_output' in 'run_1.json' does not contain a 'values' list.",
            None,
        ),
        (
            "invalid_output",
            False,
            "E2E output 'test_output' in 'run_1.json' does not contain a 'values' list.",
            None,
        ),
        (
            {"values": [1.0]},
            False,
            None,
            "E2E output 'test_output' has 1 values in 'run_1.json', but 2 were expected.",
        ),
    ],
)
def test_validate_values(
    mocker: MockerFixture,
    matching_output: Any,
    expected_result: bool,
    expected_error: str | None,
    expected_warning: str | None,
) -> None:
    result_paths = [Path("run_1.json")]
    output_name = "test_output"
    reference_values = [1.0, 2.0]
    matching_outputs = [matching_output]

    add_error = mocker.patch.object(OutputManager, "add_error")
    add_warning = mocker.patch.object(OutputManager, "add_warning")

    actual = E2ETestResultsHandler._validate_values(
        result_paths,
        output_name,
        matching_outputs,
        reference_values,
    )

    assert actual is expected_result

    info_map = {
        "class": E2ETestResultsHandler.__class__.__name__,
        "function": E2ETestResultsHandler._validate_values.__name__,
    }

    if expected_error is None:
        add_error.assert_not_called()
    else:
        add_error.assert_called_once_with(
            "E2E Results Averaging Error",
            expected_error,
            info_map=info_map,
        )

    if expected_warning is None:
        add_warning.assert_not_called()
    else:
        add_warning.assert_called_once_with(
            "E2E Results Averaging Error",
            expected_warning,
            info_map=info_map,
        )


@pytest.mark.parametrize(
    "test_results, expected_warnings",
    [
        (
            [
                {"output_1": {}, "output_2": {}},
                {"output_1": {}, "output_2": {}},
            ],
            [],
        ),
        (
            [
                {"output_1": {}, "output_2": {}},
                {"output_1": {}},
            ],
            [
                (
                    Path("run_2.json"),
                    ["output_2"],
                    [],
                ),
            ],
        ),
        (
            [
                {"output_1": {}, "output_2": {}},
                {"output_1": {}, "output_2": {}, "output_3": {}},
            ],
            [
                (
                    Path("run_2.json"),
                    [],
                    ["output_3"],
                ),
            ],
        ),
        (
            [
                {"output_1": {}, "output_2": {}},
                {"output_1": {}, "output_3": {}},
            ],
            [
                (
                    Path("run_2.json"),
                    ["output_2"],
                    ["output_3"],
                ),
            ],
        ),
        (
            [
                {"output_1": {}, "output_2": {}},
                {"output_1": {}},
                {"output_2": {}, "output_3": {}},
            ],
            [
                (
                    Path("run_2.json"),
                    ["output_2"],
                    [],
                ),
                (
                    Path("run_3.json"),
                    ["output_1"],
                    ["output_3"],
                ),
            ],
        ),
    ],
)
def test_validate_results(
    mocker: MockerFixture,
    test_results: list[dict[str, Any]],
    expected_warnings: list[tuple[Path, list[str], list[str]]],
) -> None:
    result_paths = [Path(f"run_{index}.json") for index in range(1, len(test_results) + 1)]
    reference_keys = {"output_1", "output_2"}

    add_warning = mocker.patch.object(OutputManager, "add_warning")

    E2ETestResultsHandler._validate_results(
        result_paths,
        test_results,
        reference_keys,
    )

    expected_calls = [
        mocker.call(
            "E2E Results Averaging Warning",
            (
                f"E2E result structure differs for '{result_path}'. "
                f"Missing keys: {missing_keys}. "
                f"Unexpected keys: {unexpected_keys}."
            ),
            info_map={
                "class": E2ETestResultsHandler.__class__.__name__,
                "function": E2ETestResultsHandler._validate_results.__name__,
            },
        )
        for result_path, missing_keys, unexpected_keys in expected_warnings
    ]

    assert add_warning.call_args_list == expected_calls


def test_load_results(tmp_path: Path) -> None:
    result_1 = {
        "output_1": {"values": [1.0, 2.0]},
        "DISCLAIMER": "First result",
    }
    result_2 = {
        "output_2": {"values": [3.0, 4.0]},
        "DISCLAIMER": "Second result",
    }

    result_path_1 = tmp_path / "run_1.json"
    result_path_2 = tmp_path / "run_2.json"

    result_path_1.write_text(json.dumps(result_1), encoding="utf-8")
    result_path_2.write_text(json.dumps(result_2), encoding="utf-8")

    actual = E2ETestResultsHandler._load_results(
        [result_path_1, result_path_2],
    )

    assert actual == [
        result_1,
        result_2,
    ]


def test_extract_results_paths(tmp_path: Path) -> None:
    e2e_runs = [
        {
            "output_prefix": "run_1",
            "e2e_group": "animals_e2e",
        },
        {
            "output_prefix": "run_2",
            "e2e_group": "animals_e2e",
        },
    ]
    actual_results_path = Path("animals_e2e_animal_results.json")

    result_path_1 = tmp_path / "run_1_animal_results.json"
    result_path_2 = tmp_path / "run_2_animal_results.json"
    unrelated_path = tmp_path / "unrelated_results.json"

    result_path_1.touch()
    result_path_2.touch()
    unrelated_path.touch()

    actual = E2ETestResultsHandler._extract_results_paths(
        e2e_runs,
        tmp_path,
        actual_results_path,
    )

    assert actual == [
        result_path_1,
        result_path_2,
    ]


@pytest.mark.parametrize(
    "matching_filenames, expected_match_count",
    [
        ([], 0),
        (
            [
                "run_1_animal_results.json",
                "run_1_animal_results.json_extra",
            ],
            2,
        ),
    ],
)
def test_extract_results_paths_raises_error_for_invalid_number_of_matches(
    mocker: MockerFixture,
    tmp_path: Path,
    matching_filenames: list[str],
    expected_match_count: int,
) -> None:
    e2e_runs = [
        {
            "output_prefix": "run_1",
            "e2e_group": "animals_e2e",
        },
    ]
    actual_results_path = Path("animals_e2e_animal_results.json")

    for filename in matching_filenames:
        (tmp_path / filename).touch()

    add_error = mocker.patch.object(OutputManager, "add_error")

    expected_message = (
        "Expected exactly one E2E result file for "
        "'run_1' matching "
        "'animal_results.json', but found "
        f"{expected_match_count}."
    )

    with pytest.raises(
        ValueError,
        match=re.escape(expected_message),
    ):
        E2ETestResultsHandler._extract_results_paths(
            e2e_runs,
            tmp_path,
            actual_results_path,
        )

    add_error.assert_called_once_with(
        "E2E Results Averaging Error",
        expected_message,
        info_map={
            "class": E2ETestResultsHandler.__class__.__name__,
            "function": E2ETestResultsHandler._extract_results_paths.__name__,
        },
    )


@pytest.mark.parametrize(
    "test_results, expected_result, expected_warning",
    [
        (
            [
                {"DISCLAIMER": "Test disclaimer"},
                {"DISCLAIMER": "Different disclaimer"},
            ],
            {"DISCLAIMER": "Test disclaimer"},
            None,
        ),
        (
            [
                {"test_output": {"metadata": "test"}},
                {"test_output": {"metadata": "test"}},
            ],
            {"test_output": {"metadata": "test"}},
            None,
        ),
        (
            [
                {"test_output": {"metadata": "first"}},
                {"test_output": {"metadata": "second"}},
            ],
            {},
            "Non-matching data in reference output for test_output",
        ),
    ],
)
def test_average_test_results_handles_non_averaged_outputs(
    mocker: MockerFixture,
    test_results: list[dict[str, Any]],
    expected_result: dict[str, Any],
    expected_warning: str | None,
) -> None:
    results_paths = [
        Path("run_1.json"),
        Path("run_2.json"),
    ]

    mocker.patch.object(
        E2ETestResultsHandler,
        "_load_results",
        return_value=test_results,
    )
    mocker.patch.object(
        E2ETestResultsHandler,
        "_validate_results",
    )
    validate_values = mocker.patch.object(
        E2ETestResultsHandler,
        "_validate_values",
    )
    average_output_values = mocker.patch.object(
        E2ETestResultsHandler,
        "_average_output_values",
    )
    add_warning = mocker.patch.object(OutputManager, "add_warning")

    actual = E2ETestResultsHandler._average_test_results(results_paths)

    assert actual == expected_result
    validate_values.assert_not_called()
    average_output_values.assert_not_called()

    if expected_warning is None:
        add_warning.assert_not_called()
    else:
        add_warning.assert_called_once_with(
            "E2E Results Averaging Error",
            expected_warning,
            info_map={
                "class": E2ETestResultsHandler.__class__.__name__,
                "function": E2ETestResultsHandler._average_test_results.__name__,
            },
        )


def test_average_test_results_excludes_output_missing_from_run(mocker: MockerFixture) -> None:
    results_paths = [
        Path("run_1.json"),
        Path("run_2.json"),
        Path("run_3.json"),
    ]
    test_results = [
        {"test_output": {"values": [1.0]}},
        {},
        {"test_output": {"values": [3.0]}},
    ]

    mocker.patch.object(
        E2ETestResultsHandler,
        "_load_results",
        return_value=test_results,
    )
    mocker.patch.object(
        E2ETestResultsHandler,
        "_validate_results",
    )
    add_warning = mocker.patch.object(OutputManager, "add_warning")
    validate_values = mocker.patch.object(
        E2ETestResultsHandler,
        "_validate_values",
    )
    average_output_values = mocker.patch.object(
        E2ETestResultsHandler,
        "_average_output_values",
    )

    actual = E2ETestResultsHandler._average_test_results(results_paths)

    assert actual == {}

    add_warning.assert_called_once_with(
        "E2E Results Averaging Warning",
        (
            "E2E output 'test_output' is missing from 1 of 3 runs "
            "and will be excluded from the averaged results. "
            f"Missing from: [{results_paths[1]!r}]."
        ),
        info_map={
            "class": E2ETestResultsHandler.__class__.__name__,
            "function": E2ETestResultsHandler._average_test_results.__name__,
        },
    )

    validate_values.assert_not_called()
    average_output_values.assert_not_called()


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
        "class": E2ETestResultsHandler.__name__,
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


@pytest.mark.parametrize(
    ("changes", "tolerance", "expected"),
    [
        # Significant numeric change
        ({"old_value": 10.0, "new_value": 10.2}, 0.01, True),
        # Insignificant numeric change
        ({"old_value": 10.0, "new_value": 10.001}, 0.01, False),
        # Non-numeric values are treated as significant
        ({"old_value": "a", "new_value": "b"}, 0.01, True),
        # Nested dict with only insignificant changes
        (
            {
                "old_value": {
                    "a": 100.0,
                    "b": 200.0,
                },
                "new_value": {
                    "a": 100.0001,
                    "b": 200.0001,
                },
            },
            0.01,
            False,
        ),
        # Nested dict with one significant change
        (
            {
                "old_value": {
                    "a": 100.0,
                    "b": 200.0,
                },
                "new_value": {
                    "a": 100.0001,
                    "b": 250.0,
                },
            },
            0.01,
            True,
        ),
        # Missing key in new_value
        (
            {
                "old_value": {
                    "a": 100.0,
                    "b": 200.0,
                },
                "new_value": {
                    "a": 100.0,
                },
            },
            0.01,
            True,
        ),
        # Missing key in old_value
        (
            {
                "old_value": {
                    "a": 100.0,
                },
                "new_value": {
                    "a": 100.0,
                    "b": 200.0,
                },
            },
            0.01,
            True,
        ),
        # Deep recursive nested dict with insignificant changes
        (
            {
                "old_value": {
                    "outer": {
                        "inner": 50.0,
                    }
                },
                "new_value": {
                    "outer": {
                        "inner": 50.00001,
                    }
                },
            },
            0.01,
            False,
        ),
        # Deep recursive nested dict with significant changes
        (
            {
                "old_value": {
                    "outer": {
                        "inner": 50.0,
                    }
                },
                "new_value": {
                    "outer": {
                        "inner": 60.0,
                    }
                },
            },
            0.01,
            True,
        ),
        # Nested dict with non-numeric change
        (
            {
                "old_value": {
                    "status": "active",
                },
                "new_value": {
                    "status": "inactive",
                },
            },
            0.01,
            True,
        ),
    ],
)
def test_is_significant(
    changes: dict[str, object],
    tolerance: float,
    expected: bool,
) -> None:
    """Unit test for is_significant()."""
    assert E2ETestResultsHandler.is_significant(changes, tolerance) is expected


def test_filter_nested() -> None:
    """Unit test for filter_nested()."""
    diff: dict[str, dict[str, float | str]] = {
        "key1": {"old_value": 100.0, "new_value": 100.0001},
        "key2": {"old_value": 50.0, "new_value": 51.0},
    }
    E2ETestResultsHandler.filter_nested(diff, 0.001)
    assert "key1" not in diff
    assert "key2" in diff


@pytest.mark.parametrize(
    "diff, matching_path, raise_exception",
    [
        ({}, "output_dir/actual_results.json", None),
        ({"diff": "some_differences"}, "output_dir/actual_results.json", None),
        ({}, None, None),
        ({}, "output_dir/actual_results.json", IOError("File read error")),
        ({}, "output_dir/actual_results.json", json.JSONDecodeError("Invalid JSON", doc="", pos=0)),
    ],
)
def test_update_expected_test_results(
    mocker: MockerFixture,
    diff: dict[str, str],
    matching_path: str | None,
    raise_exception: Exception | None,
) -> None:
    """Tests update_expected_test_results in E2ETestResultsHandler."""
    # Arrange
    output_dir = Path("output_dir")
    mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)
    add_log = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_log")
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
            assert add_log.call_count == 1
            mock_write_json.assert_called_once()
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


def make_result_path_set(must_change_variables_path: str) -> ResultPathType:
    """Returns a ResultPathType with dummy paths and the given must-change variables path."""
    return ResultPathType("domain", "expected", "actual_", 0.1, must_change_variables_path)


def test_load_must_change_variables(mocker: MockerFixture, tmp_path: Path) -> None:
    """Tests that _load_must_change_variables unions the files referenced by the path sets."""
    mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)
    add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")
    file_one = tmp_path / "must_change_one.json"
    file_two = tmp_path / "must_change_two.json"
    write_json_file(file_one, {"description": "ignored", MUST_CHANGE_VARIABLES_KEY: ["A.x", "A.y"]})
    write_json_file(file_two, {MUST_CHANGE_VARIABLES_KEY: ["A.y", "B.z"]})
    path_sets = [
        make_result_path_set(str(file_one)),
        make_result_path_set(str(file_one)),
        make_result_path_set(str(file_two)),
        make_result_path_set(""),
    ]

    result = E2ETestResultsHandler._load_must_change_variables(path_sets)

    assert result == {"A.x", "A.y", "B.z"}
    add_error.assert_not_called()


def test_load_must_change_variables_without_configured_paths(mocker: MockerFixture) -> None:
    """Tests that _load_must_change_variables returns an empty set when no paths are configured."""
    mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)

    assert E2ETestResultsHandler._load_must_change_variables([make_result_path_set("")]) == set()


def test_load_must_change_variables_missing_file(mocker: MockerFixture, tmp_path: Path) -> None:
    """Tests that _load_must_change_variables raises when a referenced file does not exist."""
    mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)
    add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")
    path_sets = [make_result_path_set(str(tmp_path / "no_such_file.json"))]

    with pytest.raises(FileNotFoundError):
        E2ETestResultsHandler._load_must_change_variables(path_sets)
    add_error.assert_called_once()


@pytest.mark.parametrize(
    "file_contents",
    [
        "{not valid json",
        ["A.x"],
        {"wrong_key": ["A.x"]},
        {MUST_CHANGE_VARIABLES_KEY: "A.x"},
        {MUST_CHANGE_VARIABLES_KEY: ["A.x", 3]},
    ],
)
def test_load_must_change_variables_invalid_contents(mocker: MockerFixture, tmp_path: Path, file_contents: Any) -> None:
    """Tests that _load_must_change_variables raises for unparsable or malformed files."""
    mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)
    add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")
    file_path = tmp_path / "must_change.json"
    write_json_file(file_path, file_contents)

    with pytest.raises(ValueError):
        E2ETestResultsHandler._load_must_change_variables([make_result_path_set(str(file_path))])
    add_error.assert_called_once()


@pytest.mark.parametrize(
    "expected_value, actual_value, tolerance, expect_satisfied",
    [
        # Change well beyond the tolerance
        ({"values": [1.0]}, {"values": [5.0]}, 0.1, True),
        # Identical values
        ({"values": [1.0]}, {"values": [1.0]}, 0.1, False),
        # Change within the tolerance counts as no change
        ({"values": [100.0]}, {"values": [100.5]}, 1.0, False),
        # Non-numerical change
        ({"values": [["Holstein"]]}, {"values": [["Jersey"]]}, 0.1, True),
        # Structural change
        (
            {"values": [{"field_name": "field_1"}]},
            {"values": [{"field_name": "field_1"}, {"field_name": "f2"}]},
            0.1,
            True,
        ),
    ],
)
def test_evaluate_must_change_variables(
    expected_value: dict[str, Any], actual_value: dict[str, Any], tolerance: float, expect_satisfied: bool
) -> None:
    """Tests _evaluate_must_change_variables against real DeepDiff comparisons."""
    expected_results = {"A.x": expected_value, "A.y": {"values": [2.0]}}
    actual_results = {"A.x": actual_value, "A.y": {"values": [2.0]}}

    satisfied, violations = E2ETestResultsHandler._evaluate_must_change_variables(
        expected_results, actual_results, ["A.x"], tolerance
    )

    if expect_satisfied:
        assert satisfied == ["A.x"]
        assert violations == {}
    else:
        assert satisfied == []
        assert list(violations.keys()) == ["A.x"]


def test_evaluate_must_change_variables_missing_from_actual() -> None:
    """Tests that a must-change variable missing from the actual results is reported as a violation."""
    satisfied, violations = E2ETestResultsHandler._evaluate_must_change_variables(
        {"A.x": {"values": [1.0]}}, {}, ["A.x"], 0.1
    )

    assert satisfied == []
    assert list(violations.keys()) == ["A.x"]
    assert "missing" in violations["A.x"]


@pytest.mark.parametrize(
    "diff_result, expected_names",
    [
        ({}, []),
        (
            {
                "values_changed": {
                    "root['A.x']['values'][0]": {"old_value": 1.0, "new_value": 2.0},
                    "root['A.y']['values'][3]": {"old_value": 1.0, "new_value": 2.0},
                    "root['A.x']['values'][7]": {"old_value": 3.0, "new_value": 4.0},
                }
            },
            ["A.x", "A.y"],
        ),
        (
            {
                "dictionary_item_added": {"root['B.z']": {"values": [1.0]}},
                "dictionary_item_removed": ["root['C.w']", "root"],
            },
            ["B.z", "C.w"],
        ),
        ({"end_to_end_testing_passing": True}, []),
    ],
)
def test_extract_changed_variable_names(diff_result: dict[str, Any], expected_names: list[str]) -> None:
    """Tests _extract_changed_variable_names across DeepDiff change categories."""
    assert E2ETestResultsHandler._extract_changed_variable_names(diff_result) == expected_names


@pytest.mark.parametrize(
    "actual_results, must_change_names, expect_passing, expect_error_count, expect_changed, expect_satisfied,"
    " expect_violations",
    [
        # Must-change variable changed, everything else matches: the run passes.
        ({"A.x": {"values": [5.0]}, "A.y": {"values": [2.0]}}, ["A.x"], True, 0, None, ["A.x"], set()),
        # Must-change variable did not change: the run fails.
        ({"A.x": {"values": [1.0]}, "A.y": {"values": [2.0]}}, ["A.x"], False, 1, None, [], {"A.x"}),
        # Must-change variable missing from the actual results: the run fails.
        ({"A.y": {"values": [2.0]}}, ["A.x"], False, 1, None, [], {"A.x"}),
        # Unflagged variable changed: the run fails and the variable is compiled into changed_variables.
        ({"A.x": {"values": [1.0]}, "A.y": {"values": [9.0]}}, [], False, 1, ["A.y"], None, None),
        # Flagged variable does not exist in the expected results: ignored by the comparison, which relies on
        # validate_comparison_configuration having rejected it before the simulation.
        ({"A.x": {"values": [1.0]}, "A.y": {"values": [2.0]}}, ["A.z"], True, 0, None, None, None),
    ],
)
def test_compare_actual_and_expected_results_with_must_change(
    mocker: MockerFixture,
    tmp_path: Path,
    actual_results: dict[str, Any],
    must_change_names: list[str],
    expect_passing: bool,
    expect_error_count: int,
    expect_changed: list[str] | None,
    expect_satisfied: list[str] | None,
    expect_violations: set[str] | None,
) -> None:
    """End-to-end tests of compare_actual_and_expected_test_results with must-change variables, on real files."""
    expected_results = {"A.x": {"values": [1.0]}, "A.y": {"values": [2.0]}}
    json_output_path = tmp_path / "output"
    json_output_path.mkdir()
    with open(json_output_path / "actual_prefix_results.json", "w", encoding="utf-8") as file:
        json.dump(actual_results, file)
    expected_results_path = tmp_path / "e2e_json_test_filter.json"
    with open(expected_results_path, "w", encoding="utf-8") as file:
        json.dump({"name": "test", "filters": ["A.*"], "expected_results": expected_results}, file)
    path_set = ResultPathType("Animal", str(expected_results_path), "actual_prefix_", 0.1)
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=[path_set])
    mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)
    mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_log")
    add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")
    add_variable = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_variable")

    E2ETestResultsHandler.compare_actual_and_expected_test_results(
        json_output_path, None, "dummy_prefix", set(must_change_names)
    )

    reported = {call.args[0]: call.args[1] for call in add_variable.call_args_list}
    assert reported["end_to_end_testing_passing"] is expect_passing
    assert add_error.call_count == expect_error_count
    if expect_changed is None:
        assert "changed_variables" not in reported
    else:
        assert reported["changed_variables"] == expect_changed
    if expect_satisfied is None:
        assert "must_change_satisfied" not in reported
    else:
        assert reported["must_change_satisfied"] == expect_satisfied
    if expect_violations is None:
        assert "must_change_violations" not in reported
    else:
        assert set(reported["must_change_violations"].keys()) == expect_violations


VALIDATION_OUTPUT_PREFIX = "dummy_prefix"


def patch_output_manager(mocker: MockerFixture) -> tuple[MagicMock, MagicMock]:
    """Stubs the OutputManager used by the handler and returns its add_log and add_error mocks."""
    mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.__init__", return_value=None)
    add_log = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_log")
    add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")
    return add_log, add_error


def write_expected_results_file(path: Path, expected_results: dict[str, Any]) -> None:
    """Writes a valid expected results file, named after the file stem, for the configuration validation tests."""
    write_json_file(
        path,
        {
            "name": path.stem,
            "filters": ["A.*"],
            "expected_results_last_updated": "2026-09-11T00:00:00",
            "expected_results": expected_results,
        },
    )


def make_validation_path_sets(tmp_path: Path, must_change_names: list[str] | None = None) -> list[ResultPathType]:
    """Writes valid expected results and must-change files under tmp_path and returns path sets referencing them."""
    animal_path = tmp_path / "e2e_json_animal_filter.json"
    feed_path = tmp_path / "e2e_json_feed_filter.json"
    must_change_path = tmp_path / "must_change_variables.json"
    write_expected_results_file(animal_path, {"A.x": {"values": [1.0]}, "A.y": {"values": [2.0]}})
    write_expected_results_file(feed_path, {"F.z": {"values": [3.0]}})
    write_json_file(must_change_path, {MUST_CHANGE_VARIABLES_KEY: must_change_names or []})
    return [
        ResultPathType(
            "Animal",
            str(animal_path),
            f"{VALIDATION_OUTPUT_PREFIX}_saved_variables_{animal_path.stem}_",
            0.1,
            str(must_change_path),
        ),
        ResultPathType(
            "Feed",
            str(feed_path),
            f"{VALIDATION_OUTPUT_PREFIX}_saved_variables_{feed_path.stem}_",
            0.1,
            str(must_change_path),
        ),
    ]


@pytest.mark.parametrize("use_conversion_table", [False, True])
def test_validate_comparison_configuration(mocker: MockerFixture, tmp_path: Path, use_conversion_table: bool) -> None:
    """Tests that a valid configuration passes, matching must-change names after any variable name conversion."""
    _, add_error = patch_output_manager(mocker)
    conversion_csv_path: str | None = None
    flagged_feed_name = "F.z"
    if use_conversion_table:
        conversion_csv_path = str(tmp_path / "conversion.csv")
        pd.DataFrame({"Original": ["F.z"], "New": ["F.renamed"]}).to_csv(conversion_csv_path, index=False)
        flagged_feed_name = "F.renamed"
    path_sets = make_validation_path_sets(tmp_path, ["A.y", flagged_feed_name])
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    must_change_variables = E2ETestResultsHandler.validate_comparison_configuration(
        VALIDATION_OUTPUT_PREFIX, conversion_csv_path, tmp_path
    )

    assert must_change_variables == {"A.y", flagged_feed_name}
    add_error.assert_not_called()


def test_validate_comparison_configuration_unknown_must_change_variable(mocker: MockerFixture, tmp_path: Path) -> None:
    """Tests that a must-change name absent from every domain's expected results fails the validation."""
    _, add_error = patch_output_manager(mocker)
    path_sets = make_validation_path_sets(tmp_path, ["A.y", "A.typo"])
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    with pytest.raises(ValueError, match=r"\['A\.typo'\]"):
        E2ETestResultsHandler.validate_comparison_configuration(VALIDATION_OUTPUT_PREFIX, None, tmp_path)
    add_error.assert_called_once()
    assert "A.typo" in add_error.call_args.args[1]
    assert "A.y" not in add_error.call_args.args[1]


def test_validate_comparison_configuration_missing_must_change_file(mocker: MockerFixture, tmp_path: Path) -> None:
    """Tests that a missing must-change variables file fails the validation."""
    _, add_error = patch_output_manager(mocker)
    path_sets = make_validation_path_sets(tmp_path)
    (tmp_path / "must_change_variables.json").unlink()
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    with pytest.raises(ValueError, match="Must-change variables file not found"):
        E2ETestResultsHandler.validate_comparison_configuration(VALIDATION_OUTPUT_PREFIX, None, tmp_path)
    add_error.assert_called_once()


def test_validate_comparison_configuration_missing_expected_results_file(mocker: MockerFixture, tmp_path: Path) -> None:
    """Tests that a missing expected results file fails the validation even when no variable is flagged."""
    _, add_error = patch_output_manager(mocker)
    path_sets = make_validation_path_sets(tmp_path)
    (tmp_path / "e2e_json_feed_filter.json").unlink()
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    with pytest.raises(ValueError, match="could not be loaded"):
        E2ETestResultsHandler.validate_comparison_configuration(VALIDATION_OUTPUT_PREFIX, None, tmp_path)
    add_error.assert_called_once()


@pytest.mark.parametrize(
    "file_contents",
    [
        '// WARNING: This is an autogenerated file. Remove this line for valid JSON.\n{"expected_results": {}}',
        ["A.x"],
        {"name": "e2e_json_feed_filter", "filters": ["A.*"], "expected_results_last_updated": ""},
    ],
)
def test_validate_comparison_configuration_invalid_expected_results_file(
    mocker: MockerFixture, tmp_path: Path, file_contents: Any
) -> None:
    """Tests that an unparsable or malformed expected results file fails the validation without flagged variables."""
    _, add_error = patch_output_manager(mocker)
    path_sets = make_validation_path_sets(tmp_path)
    write_json_file(tmp_path / "e2e_json_feed_filter.json", file_contents)
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    with pytest.raises(ValueError, match="could not be loaded"):
        E2ETestResultsHandler.validate_comparison_configuration(VALIDATION_OUTPUT_PREFIX, None, tmp_path)
    add_error.assert_called_once()


def test_validate_comparison_configuration_expected_results_outside_filters_directory(
    mocker: MockerFixture, tmp_path: Path
) -> None:
    """Tests that expected results files outside the task's filters directory fail the validation."""
    _, add_error = patch_output_manager(mocker)
    path_sets = make_validation_path_sets(tmp_path)
    filters_directory = tmp_path / "filters"
    filters_directory.mkdir()
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    with pytest.raises(ValueError, match="filters directory") as error:
        E2ETestResultsHandler.validate_comparison_configuration(VALIDATION_OUTPUT_PREFIX, None, filters_directory)
    assert "e2e_json_animal_filter.json" in str(error.value)
    assert "e2e_json_feed_filter.json" in str(error.value)
    assert add_error.call_count == 2


@pytest.mark.parametrize(
    "actual_results_path",
    [
        "",
        f"{VALIDATION_OUTPUT_PREFIX}_saved_variables_e2e_json_feeed_filter_",
        "other_prefix_saved_variables_e2e_json_feed_filter_",
    ],
)
def test_validate_comparison_configuration_actual_results_path_mismatch(
    mocker: MockerFixture, tmp_path: Path, actual_results_path: str
) -> None:
    """Tests that an actual_results_path the run's output file names will not start with fails the validation."""
    _, add_error = patch_output_manager(mocker)
    path_sets = make_validation_path_sets(tmp_path)
    path_sets[1] = path_sets[1]._replace(actual_results_path=actual_results_path)
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    with pytest.raises(ValueError, match="actual_results_path"):
        E2ETestResultsHandler.validate_comparison_configuration(VALIDATION_OUTPUT_PREFIX, None, tmp_path)
    add_error.assert_called_once()
    assert "Feed" in add_error.call_args.args[0]


@pytest.mark.parametrize(
    "conversion_table",
    [None, pd.DataFrame({"Original": ["F.z"], "Renamed": ["F.renamed"]})],
)
def test_validate_comparison_configuration_invalid_conversion_table(
    mocker: MockerFixture, tmp_path: Path, conversion_table: pd.DataFrame | None
) -> None:
    """Tests that a missing or malformed conversion table fails the validation."""
    patch_output_manager(mocker)
    conversion_csv_path = tmp_path / "conversion.csv"
    if conversion_table is not None:
        conversion_table.to_csv(conversion_csv_path, index=False)
    path_sets = make_validation_path_sets(tmp_path)
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    with pytest.raises(ValueError, match="could not be loaded"):
        E2ETestResultsHandler.validate_comparison_configuration(
            VALIDATION_OUTPUT_PREFIX, str(conversion_csv_path), tmp_path
        )


def test_validate_comparison_configuration_reports_every_problem(mocker: MockerFixture, tmp_path: Path) -> None:
    """Tests that one validation reports a bad must-change path, expected results path and actual results path."""
    _, add_error = patch_output_manager(mocker)
    path_sets = make_validation_path_sets(tmp_path, ["A.y", "F.z"])
    path_sets[1] = ResultPathType("Feed", "gloop", "glop", 0.1, "gleep")
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    with pytest.raises(ValueError) as error:
        E2ETestResultsHandler.validate_comparison_configuration(VALIDATION_OUTPUT_PREFIX, None, tmp_path)

    message = str(error.value)
    assert "Must-change variables file not found: gleep" in message
    assert "Expected results file gloop for Feed could not be loaded" in message
    assert "actual_results_path 'glop' for Feed" in message
    # "F.z" is flagged and only exists in the file that could not be loaded, so it must not be reported as unknown.
    assert "not found in the expected results" not in message
    assert add_error.call_count == 3


def test_validate_update_configuration(mocker: MockerFixture, tmp_path: Path) -> None:
    """Tests that a valid update configuration passes without reading the must-change variables files."""
    _, add_error = patch_output_manager(mocker)
    path_sets = make_validation_path_sets(tmp_path)
    (tmp_path / "must_change_variables.json").unlink()
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    E2ETestResultsHandler.validate_update_configuration(VALIDATION_OUTPUT_PREFIX, tmp_path)

    add_error.assert_not_called()


@pytest.mark.parametrize(
    "mistake, expected_message",
    [
        ("missing_expected_results_file", "could not be loaded"),
        ("expected_results_file_missing_keys", "Missing required keys"),
        ("actual_results_path_mismatch", "actual_results_path"),
    ],
)
def test_validate_update_configuration_failures(
    mocker: MockerFixture, tmp_path: Path, mistake: str, expected_message: str
) -> None:
    """Tests that a result path set that the update could not resolve after the simulation fails the validation."""
    _, add_error = patch_output_manager(mocker)
    path_sets = make_validation_path_sets(tmp_path)
    feed_path = tmp_path / "e2e_json_feed_filter.json"
    if mistake == "missing_expected_results_file":
        feed_path.unlink()
    elif mistake == "expected_results_file_missing_keys":
        write_json_file(feed_path, {"name": feed_path.stem, "expected_results": {}})
    else:
        path_sets[1] = path_sets[1]._replace(actual_results_path="freestall_e2e_saved_variables_e2e_feed_")
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    with pytest.raises(ValueError, match=expected_message):
        E2ETestResultsHandler.validate_update_configuration(VALIDATION_OUTPUT_PREFIX, tmp_path)
    add_error.assert_called_once()


def test_validate_update_configuration_reports_every_problem(mocker: MockerFixture, tmp_path: Path) -> None:
    """Tests that one update validation reports the problems of every result path set."""
    _, add_error = patch_output_manager(mocker)
    path_sets = make_validation_path_sets(tmp_path)
    (tmp_path / "e2e_json_animal_filter.json").unlink()
    path_sets[1] = path_sets[1]._replace(actual_results_path="glop")
    mocker.patch.object(E2ETestResultsHandler, "_get_test_result_paths", return_value=path_sets)

    with pytest.raises(ValueError) as error:
        E2ETestResultsHandler.validate_update_configuration(VALIDATION_OUTPUT_PREFIX, tmp_path)

    message = str(error.value)
    assert "e2e_json_animal_filter.json for Animal could not be loaded" in message
    assert "actual_results_path 'glop' for Feed" in message
    assert add_error.call_count == 2
