import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Type
from unittest.mock import ANY, call

import pandas as pd
import pytest
from mock import MagicMock, Mock, mock_open, patch
from pytest_mock import MockerFixture

from RUFAS.input_manager import ADDRESS_TO_INPUTS, VALID_INPUT_TYPES, InputManager
from RUFAS.data_validator import DataValidator, Modifiability, ElementsCounter, ElementState, CrossValidator
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility


@pytest.fixture
def mock_input_manager() -> InputManager:
    InputManager.__instance = None
    input_manager = InputManager()
    return input_manager


def test_input_manager_singleton() -> None:
    """Unit test to ensure InputManager is a singleton"""
    im1 = InputManager()
    im2 = InputManager()

    assert im1 is im2

    fake_pool = {"a": 1}
    im1.pool = fake_pool
    assert im2.pool is fake_pool

    fake_metadata = {"b": 2}
    im1.meta_data = fake_metadata
    assert im2.meta_data is fake_metadata


@pytest.fixture
def input_manager_original_method_states(
    mock_input_manager: InputManager,
) -> Dict[str, Callable]:
    """Fixture to store original methods of InputManager"""
    return {
        "start_data_processing": mock_input_manager.start_data_processing,
        "_load_metadata": mock_input_manager._load_metadata,
        "_load_properties": mock_input_manager._load_properties,
        "_load_data_from_json": mock_input_manager._load_data_from_json,
        "_load_data_from_csv": mock_input_manager._load_data_from_csv,
        "_populate_pool": mock_input_manager._populate_pool,
        "get_data": mock_input_manager.get_data,
        "get_metadata": mock_input_manager.get_metadata,
        "get_data_keys_by_properties": mock_input_manager.get_data_keys_by_properties,
        "flush_pool": mock_input_manager.flush_pool,
        "_metadata_properties_exist": mock_input_manager._metadata_properties_exist,
        "_add_variable_to_pool": mock_input_manager._add_variable_to_pool,
        "_is_input_required_upon_initialization": mock_input_manager._is_input_required_upon_initialization,
        "_is_modifiable_during_runtime": mock_input_manager._is_modifiable_during_runtime,
        "save_metadata_properties": mock_input_manager.save_metadata_properties,
        "_parse_metadata_properties": mock_input_manager._parse_metadata_properties,
        "_check_property_type_primitive": mock_input_manager._check_property_type_primitive,
        "_create_record": mock_input_manager._create_record,
        "add_runtime_variable_to_pool": mock_input_manager.add_runtime_variable_to_pool,
    }


def test_metadata_setter_getter(mock_input_manager: InputManager) -> None:
    """Unit test for metadata getter and setter methods"""
    test_data = {"foo": "bar", "integer": 1}
    mock_input_manager.meta_data = test_data
    assert mock_input_manager.meta_data == test_data


def test_pool_setter_getter(mock_input_manager: InputManager) -> None:
    """Unit test for metadata getter and setter methods"""
    test_data = {"foo": "bar", "integer": 1}
    mock_input_manager.pool = test_data
    assert mock_input_manager.pool == test_data


def test_load_properties_success(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Unit test for successfully loading properties in _load_properties method."""
    mocker.patch.object(Path, "exists", return_value=True)
    properties_data = {"key1": "value1", "key2": "value2"}
    mocker.patch("builtins.open", mock_open(read_data=json.dumps(properties_data)))
    mocker.patch(
        "RUFAS.input_manager.InputManager._load_data_from_json",
        return_value=properties_data,
    )

    mock_input_manager._InputManager__metadata = {"files": {"properties": {"path": "path/to/properties.json"}}}

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        mock_input_manager._load_properties()
        assert mock_input_manager._InputManager__metadata["properties"] == properties_data
        assert add_log.call_count == 2


def test_load_properties_file_not_found(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Unit test for handling FileNotFoundError in _load_properties method."""
    mocker.patch.object(Path, "exists", return_value=False)
    mock_input_manager._InputManager__metadata = {"files": {"properties": {"path": "path/to/missing_properties.json"}}}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(FileNotFoundError):
            mock_input_manager._load_properties()
        assert add_error.call_count == 1


def test_load_properties_json_decode_error(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Unit test for handling JSONDecodeError in _load_properties method."""
    mocker.patch.object(Path, "exists", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data="invalid_json"))

    mock_input_manager._InputManager__metadata = {"files": {"properties": {"path": "path/to/invalid_json.json"}}}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(json.JSONDecodeError):
            mock_input_manager._load_properties()
        assert add_error.call_count == 1


def test_load_properties_unexpected_error(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Unit test for handling unexpected errors in _load_properties method."""
    mocker.patch.object(Path, "exists", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data="valid_json"))
    mocker.patch(
        "RUFAS.input_manager.InputManager._load_data_from_json",
        side_effect=Exception("Unexpected error"),
    )

    mock_input_manager._InputManager__metadata = {"files": {"properties": {"path": "path/to/properties.json"}}}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(Exception, match="Unexpected error"):
            mock_input_manager._load_properties()
        assert add_error.call_count == 1


def test_load_properties_combines_multiple_files(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """_load_properties should merge properties documents when multiple paths are provided."""

    mocker.patch.object(Path, "exists", return_value=True)
    first_properties = {"key1": "value1"}
    second_properties = {"key2": "value2"}
    mocker.patch(
        "RUFAS.input_manager.InputManager._load_data_from_json",
        side_effect=[first_properties, second_properties],
    )

    mock_input_manager._InputManager__metadata = {
        "files": {
            "properties": {
                "paths": [
                    "path/to/properties.json",
                    "path/to/commodity_properties.json",
                ]
            }
        }
    }

    mock_input_manager._load_properties()

    assert mock_input_manager._InputManager__metadata["properties"] == {
        "key1": "value1",
        "key2": "value2",
    }


def test_load_properties_overlapping_keys_last_file_wins(
    mock_input_manager: InputManager, mocker: MockerFixture
) -> None:
    """_load_properties should allow later files to override earlier keys and remove properties pointer."""

    mocker.patch.object(Path, "exists", return_value=True)
    first_properties = {"key1": "value1", "shared": "original"}
    second_properties = {"shared": "updated"}
    load_json = mocker.patch(
        "RUFAS.input_manager.InputManager._load_data_from_json",
        side_effect=[first_properties, second_properties],
    )

    mock_input_manager._InputManager__metadata = {
        "files": {
            "properties": {
                "paths": ["path/to/properties.json", "path/to/commodity_properties.json"],
            }
        }
    }

    mock_input_manager._load_properties()

    assert mock_input_manager._InputManager__metadata["properties"] == {
        "key1": "value1",
        "shared": "updated",
    }
    assert "properties" not in mock_input_manager._InputManager__metadata["files"]
    assert load_json.call_count == 2


def test_load_properties_empty_paths_list_raises_value_error(
    mock_input_manager: InputManager, mocker: MockerFixture
) -> None:
    mocker.patch.object(Path, "exists", return_value=True)
    mock_input_manager._InputManager__metadata = {"files": {"properties": {"paths": []}}}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(ValueError):
            mock_input_manager._load_properties()
        add_error.assert_called_once()


def test_load_properties_rejects_non_string_paths(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    mocker.patch.object(Path, "exists", return_value=True)
    mock_input_manager._InputManager__metadata = {"files": {"properties": {"paths": ["valid/path.json", 123]}}}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(ValueError):
            mock_input_manager._load_properties()
        add_error.assert_called_once()


def test_load_properties_missing_second_file_triggers_error(
    mock_input_manager: InputManager, mocker: MockerFixture
) -> None:
    """When any properties path is missing the loader should raise FileNotFoundError."""

    mocker.patch.object(Path, "exists", side_effect=[True, False])
    mocker.patch(
        "RUFAS.input_manager.InputManager._load_data_from_json",
        return_value={"key1": "value1"},
    )
    mock_input_manager._InputManager__metadata = {
        "files": {
            "properties": {
                "paths": ["path/to/properties.json", "path/to/missing_properties.json"],
            }
        }
    }

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(FileNotFoundError):
            mock_input_manager._load_properties()
        add_error.assert_called_once()


def test_load_metadata(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_metadata in file input_manager.py"""
    with patch(
        "builtins.open",
        mock_open(read_data='{"dummy_key1": "dummy_value1", "dummy_key2": "dummy_value2"}'),
    ):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            mock_input_manager._load_metadata("path/dummy_metadata.json")
            assert mock_input_manager._InputManager__metadata == {
                "dummy_key1": "dummy_value1",
                "dummy_key2": "dummy_value2",
            }
            assert add_log.call_count == 2


def test_load_metadata_raises_exception(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_metadata raising an exception in file input_manager.py"""
    mock_open_func = Mock()
    mock_open_func.side_effect = Exception("Error opening file")

    with patch("builtins.open", mock_open_func):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(Exception):
                mock_input_manager._load_metadata("path/dummy_metadata.json")
            assert add_log.call_count == 1


def test_load_data_from_json(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_json with valid json file in file input_manager.py"""
    dummy_data = {"files": {"dummy_data_file": {"path": "dummy_data.json", "type": "json"}}}
    file_path = "path/to/json/file"
    dummy_file_content = json.dumps(dummy_data)

    with patch("builtins.open", mock_open(read_data=dummy_file_content)):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            result_data = mock_input_manager._load_data_from_json(file_path)

            assert result_data == dummy_data
            assert add_log.call_count == 2


def test_load_data_from_json_missing_file_raises_error(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_json with missing json file in file input_manager.py"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(FileNotFoundError):
                mock_input_manager._load_data_from_json("non_existent_file.json")
            assert add_log.call_count == 1


def test_load_data_from_json_invalid_data_raises_error(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_json with invalid json data in file input_manager.py"""
    with patch("builtins.open", mock_open(read_data="invalid_json_data")):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(json.JSONDecodeError):
                mock_input_manager._load_data_from_json("dummy_file.json")
            assert add_log.call_count == 1


def test_load_data_from_csv(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_csv with valid csv file in file input_manager.py"""
    dummy_csv_data = "key1,key2\na,1\nb,2\n"
    dummy_expected_data = {"key1": ["a", "b"], "key2": [1, 2]}
    file_path = "path/to/csv/file"
    with patch("builtins.open", mock_open(read_data=dummy_csv_data)):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            result_data = mock_input_manager._load_data_from_csv(file_path)

            assert result_data == dummy_expected_data
            assert add_log.call_count == 2


def test_load_data_from_csv_missing_file_raises_error(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_csv with missing csv file in file input_manager.py"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(FileNotFoundError):
                mock_input_manager._load_data_from_csv("non_existent_file.csv")
            assert add_log.call_count == 1


def test_load_data_from_csv_invalid_data_raises_error(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_json with invalid json data in file input_manager.py"""
    with patch("builtins.open", mock_open(read_data="invalid_csv_data")):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with patch("pandas.read_csv", side_effect=pd.errors.ParserError("Invalid CSV")):
                with pytest.raises(pd.errors.ParserError):
                    mock_input_manager._load_data_from_csv("dummy_file.csv")
                assert add_log.call_count == 1


@pytest.mark.parametrize(
    "cv_scenario, eager_termination, populate_ok, expected_return, expected_cv_calls, expected_fail_blocks",
    [
        ("none", True, True, True, 0, []),
        ("none", False, True, True, 0, []),
        ("all_pass", True, True, True, 2, []),
        ("all_pass", False, True, True, 2, []),
        ("first_fail_eager_true", True, True, False, 1, ["cv1"]),
        ("two_fail_eager_false", False, True, False, 3, ["cv1", "cv2"]),
        ("all_pass", True, False, False, 2, []),
    ],
    ids=[
        "no-cv_eager-true",
        "no-cv_eager-false",
        "cv-pass_eager-true",
        "cv-pass_eager-false",
        "cv-first-fail_eager-true",
        "cv-two-fail_eager-false",
        "populate-false_cv-pass",
    ],
)
def test_start_data_processing(
    mock_input_manager: InputManager,
    mocker: MockerFixture,
    cv_scenario: str,
    eager_termination: bool,
    populate_ok: bool,
    expected_return: bool,
    expected_cv_calls: int,
    expected_fail_blocks: list[str],
) -> None:
    """Covers: metadata/properties valid, populate_pool path, CV blocks (none/pass/fail,
    eager short-circuit vs collect)."""
    mocker.patch.object(mock_input_manager, "_load_metadata")
    mocker.patch.object(mock_input_manager, "_load_properties")
    mocker.patch.object(type(mock_input_manager.data_validator), "validate_metadata", return_value=(True, ""))
    mocker.patch.object(type(mock_input_manager.data_validator), "validate_properties", return_value=(True, ""))
    mocker.patch.object(type(mock_input_manager), "_populate_pool", return_value=populate_ok)

    route_logs = mocker.patch.object(mock_input_manager.om, "route_logs")
    add_error = mocker.patch.object(mock_input_manager.om, "add_error")

    mocker.patch.object(mock_input_manager, "_extract_target_and_save_block", return_value={"dummy": True})

    if cv_scenario == "none":
        cv_blocks = []
        side_effect = []
    elif cv_scenario == "all_pass":
        cv_blocks = [
            {"description": "cv1", "target_and_save": {"x": 1}, "rules": [{"r": 1}]},
            {"description": "cv2", "target_and_save": {"x": 2}, "rules": [{"r": 2}]},
        ]
        side_effect = [True, True]
    elif cv_scenario == "first_fail_eager_true":
        cv_blocks = [
            {"description": "cv1", "target_and_save": {"x": 1}, "rules": [{"r": 1}]},
            {"description": "cv2", "target_and_save": {"x": 2}, "rules": [{"r": 2}]},
        ]
        side_effect = [False, True]
    elif cv_scenario == "two_fail_eager_false":
        cv_blocks = [
            {"description": "cv1", "target_and_save": {"x": 1}, "rules": [{"r": 1}]},
            {"description": "cv2", "target_and_save": {"x": 2}, "rules": [{"r": 2}]},
            {"description": "cv3", "target_and_save": {"x": 3}, "rules": [{"r": 3}]},
        ]
        side_effect = [False, False, True]
    else:
        raise AssertionError("Unknown test setup")

    setattr(mock_input_manager, "_InputManager__metadata", {"cross-validation": cv_blocks})
    cv_mock = mock_input_manager.cross_validator
    cv_call = mocker.patch.object(cv_mock, "cross_validate_data", side_effect=side_effect)
    mock_input_manager.data_validator.event_logs.clear()

    result = mock_input_manager.start_data_processing(Path("mock/metadata/path"), Path(""), eager_termination)

    assert result is expected_return

    assert cv_call.call_count == expected_cv_calls
    for idx, cv_call in enumerate(cv_call.call_args_list[:expected_cv_calls]):
        _, kwargs = cv_call
        target_and_save_result, block, eager = cv_call.args
        assert "target_and_save" in block
        assert eager is eager_termination
        assert isinstance(target_and_save_result, dict)

    if expected_fail_blocks:
        add_error.assert_called_once()
        err, msg, info = add_error.call_args.args
        assert err == "Cross Validation Failure"
        for name in expected_fail_blocks:
            assert name in msg
        assert info.get("class") == mock_input_manager.__class__.__name__
        assert info.get("function") == mock_input_manager.start_data_processing.__name__
    else:
        add_error.assert_not_called()

    route_logs.assert_called_once_with(mock_input_manager.data_validator.event_logs)


def test_start_data_processing_invalid_metadata_raises(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """If validate_metadata returns (False, msg), it should raise ValueError with that message."""
    mocker.patch.object(mock_input_manager, "_load_metadata")
    mocker.patch.object(type(mock_input_manager.data_validator), "validate_metadata", return_value=(False, "bad meta"))
    mock_load_props = mocker.patch.object(mock_input_manager, "_load_properties")
    mock_validate_props = mocker.patch.object(type(mock_input_manager.data_validator), "validate_properties")

    with pytest.raises(ValueError, match="bad meta"):
        mock_input_manager.start_data_processing(Path("meta"), Path(""), eager_termination=True)

    mock_load_props.assert_not_called()
    mock_validate_props.assert_not_called()


def test_start_data_processing_invalid_properties_routes_logs_and_raises(
    mock_input_manager: InputManager, mocker: MockerFixture
) -> None:
    """If validate_properties returns (False, msg), it should route logs and then raise ValueError."""
    mocker.patch.object(mock_input_manager, "_load_metadata")
    mocker.patch.object(type(mock_input_manager.data_validator), "validate_metadata", return_value=(True, ""))
    mocker.patch.object(mock_input_manager, "_load_properties")
    mock_input_manager.data_validator.event_logs[:] = [{"level": "error", "msg": "prop fail"}]
    mocker.patch.object(
        type(mock_input_manager.data_validator), "validate_properties", return_value=(False, "bad props")
    )

    route_logs = mocker.patch.object(mock_input_manager.om, "route_logs")

    with pytest.raises(ValueError, match="bad props"):
        mock_input_manager.start_data_processing(Path("meta"), Path(""), eager_termination=False)

    route_logs.assert_called_once_with(mock_input_manager.data_validator.event_logs)


@pytest.fixture
def mock_metadata(mocker: MockerFixture) -> Dict[str, Dict[str, Any]]:
    return {
        "files": {
            "file1": {
                "type": "json",
                "path": "path/to/json/file1.json",
                "properties": "properties1",
            },
            "file2": {
                "type": "csv",
                "path": "path/to/csv/file2.csv",
                "properties": "properties2",
            },
        },
        "properties": {
            "properties1": {"element1": "some_value1", "element2": "some_value2"},
            "properties2": {"element3": "some_value3", "element4": "some_value4"},
        },
    }


def test_populate_pool_valid(
    mock_metadata: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for valid data for function _populate_pool in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata)
    mocker.patch.object(
        input_manager, "_load_data_from_json", side_effect=lambda _: {"element1": "value1", "element2": "value2"}
    )
    mocker.patch.object(
        input_manager, "_load_data_from_csv", side_effect=lambda _: {"element3": "value3", "element4": "value4"}
    )
    mocker.patch.object(DataValidator, "validate_data_by_type", side_effect=lambda *args, **kwargs: True)
    mocker.patch.object(OutputManager, "add_log")
    mocker.patch.object(OutputManager, "add_warning")

    # Act
    result = input_manager._populate_pool(Path(""), eager_termination=True)

    # Assert
    assert result
    assert "file1" in input_manager.pool
    assert "file2" in input_manager.pool

    input_manager.pool = {}


def test_populate_pool_invalid(
    mock_metadata: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for invalid data for function _populate_pool in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata)
    mocker.patch.object(
        input_manager, "_load_data_from_json", side_effect=lambda _: {"element1": "value1", "element2": "value2"}
    )
    mocker.patch.object(
        input_manager, "_load_data_from_csv", side_effect=lambda _: {"element3": "value3", "element4": "value4"}
    )
    mocker.patch.object(DataValidator, "validate_data_by_type", side_effect=lambda *args, **kwargs: False)
    mocker.patch.object(OutputManager, "add_log")
    mocker.patch.object(OutputManager, "add_warning")
    elements_counter = ElementsCounter()
    elements_counter.increment(ElementState.INVALID)
    mocker.patch.object(input_manager, "elements_counter", elements_counter)

    # Act
    result = input_manager._populate_pool(Path(""), eager_termination=False)

    # Assert
    assert not result
    assert "file1" not in input_manager.pool
    assert "file2" not in input_manager.pool


def test_populate_pool_partial_invalid(
    mock_metadata: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for invalid data for function _populate_pool in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata)
    mocker.patch.object(
        input_manager, "_load_data_from_json", side_effect=lambda _: {"element1": "value1", "element2": "value2"}
    )
    mocker.patch.object(
        input_manager, "_load_data_from_csv", side_effect=lambda _: {"element3": "value3", "element4": "value4"}
    )
    mocker.patch.object(DataValidator, "validate_data_by_type", side_effect=[True, False, True, False])
    mocker.patch.object(OutputManager, "add_log")
    mocker.patch.object(OutputManager, "add_warning")

    # Act
    result = input_manager._populate_pool(Path(""), eager_termination=False)

    # Assert
    assert result is False
    assert "file1" in input_manager.pool
    assert "file2" in input_manager.pool
    assert "element1" in input_manager.pool["file1"]
    assert "element2" not in input_manager.pool["file1"]
    assert "element3" in input_manager.pool["file2"]
    assert "element4" not in input_manager.pool["file2"]

    input_manager.pool = {}


def test_populate_pool_eager_termination(
    mock_metadata: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for invalid data with eager termination for function
    _populate_pool in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata)
    mocker.patch.object(
        input_manager, "_load_data_from_json", side_effect=lambda _: {"element1": "value1", "element2": "value2"}
    )
    mocker.patch.object(
        input_manager, "_load_data_from_csv", side_effect=lambda _: {"element3": "value3", "element4": "value4"}
    )
    mocker.patch.object(DataValidator, "validate_data_by_type", side_effect=lambda *args, **kwargs: False)
    mocker.patch.object(OutputManager, "add_log")
    mocker.patch.object(OutputManager, "add_warning")

    # Act
    result = input_manager._populate_pool(Path(""), eager_termination=True)

    # Assert
    assert result is False
    assert "file1" not in input_manager.pool
    assert "file2" not in input_manager.pool


def test_populate_pool_raises_keyerror(
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Unit test for invalid data file type for function _populate_pool in file input_manager.py"""
    mock_input_manager.meta_data = {
        "files": {
            "dummy_file_key": {
                "type": "invalid_data_type",
                "path": "/path/to/your/file",
                "properties": "some_properties_key",
            }
        }
    }

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            with pytest.raises(KeyError):
                mock_input_manager._populate_pool(Path(""), eager_termination=True)

            assert add_log.call_count == 0
            assert add_warning.call_count == 0

    mock_input_manager._populate_pool = input_manager_original_method_states["_populate_pool"]


@pytest.fixture
def mock_metadata_for_fix_data(mocker: MockerFixture) -> dict[str, dict[str, Any]]:
    return {
        "dummyconfig": {},
        "files": {
            "array": {"properties": "array_properties"},
            "string": {"properties": "string_properties"},
            "number": {"properties": "number_properties"},
            "boolean": {"properties": "boolean_properties"},
        },
        "properties": {
            "array_properties": {
                "element1": {
                    "type": "array",
                    "default": [1, 2, 3, 4, 5],
                    "minimum_length": 5,
                    "maximum_length": 10,
                },
                "element2": {
                    "type": "array",
                    "default": [],
                    "minimum_length": 0,
                    "maximum_length": 5,
                },
                "element3": {
                    "type": "array",
                    "default": [1, 2, 3],
                    "minimum_length": 2,
                    "maximum_length": 5,
                },
                "element4": {
                    "type": "object",
                    "element5": {
                        "type": "array",
                        "default": [1, 2, 3],
                        "minimum_length": 2,
                        "maximum_length": 5,
                    },
                },
                "element6": {
                    "type": "array",
                    "minimum_length": 5,
                    "maximum_length": 10,
                },
                "element7": {
                    "type": "array",
                    "minimum_length": 0,
                    "maximum_length": 5,
                },
                "element8": {
                    "type": "array",
                    "minimum_length": 2,
                    "maximum_length": 5,
                },
                "element9": {
                    "type": "object",
                    "element10": {
                        "type": "array",
                        "minimum_length": 2,
                        "maximum_length": 5,
                    },
                },
            },
            "string_properties": {
                "element1": {
                    "type": "str",
                    "default": "cow",
                    "pattern": r"cow",
                    "minimum_length": 1,
                    "maximum_length": 5,
                },
                "element2": {
                    "type": "str",
                    "default": "",
                    "minimum_length": 0,
                    "maximum_length": 5,
                },
                "element3": {
                    "type": "str",
                    "default": "cow",
                    "pattern": r"cow",
                    "minimum_length": 2,
                    "maximum_length": 5,
                },
                "element4": {
                    "type": "object",
                    "element5": {
                        "type": "str",
                        "default": "cow",
                        "pattern": r"cow",
                        "minimum_length": 2,
                        "maximum_length": 5,
                    },
                },
                "element6": {
                    "type": "str",
                    "pattern": r"cow",
                    "minimum_length": 1,
                    "maximum_length": 5,
                },
                "element7": {
                    "type": "str",
                    "pattern": r"cow",
                    "minimum_length": 1,
                    "maximum_length": 5,
                },
                "element8": {
                    "type": "str",
                    "pattern": r"cow",
                    "minimum_length": 1,
                    "maximum_length": 5,
                },
                "element9": {
                    "type": "object",
                    "element10": {
                        "type": "str",
                        "pattern": r"cow",
                        "minimum_length": 2,
                        "maximum_length": 5,
                    },
                },
            },
            "number_properties": {
                "element1": {
                    "type": "number",
                    "default": 5,
                    "minimum": 0,
                    "maximum": 10,
                },
                "element2": {
                    "type": "number",
                    "default": 0,
                    "minimum": 0,
                    "maximum": 10,
                },
                "element3": {
                    "type": "number",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10,
                },
                "element4": {
                    "type": "object",
                    "element5": {
                        "type": "number",
                        "default": 5,
                        "minimum": 0,
                        "maximum": 10,
                    },
                },
                "element6": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10,
                },
                "element7": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10,
                },
                "element8": {
                    "type": "number",
                    "minimum": 1,
                    "maximum": 10,
                },
                "element9": {
                    "type": "object",
                    "element10": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 10,
                    },
                },
            },
            "boolean_properties": {
                "element1": {"type": "bool", "default": True},
                "element2": {"type": "bool", "default": False},
                "element3": {
                    "type": "object",
                    "element4": {"type": "bool", "default": True},
                },
                "element5": {
                    "type": "bool",
                },
                "element6": {
                    "type": "bool",
                },
                "element7": {
                    "type": "object",
                    "element8": {
                        "type": "bool",
                    },
                },
            },
        },
    }


@pytest.fixture
def mock_pool_for_get_data(mocker: MockerFixture) -> Dict[str, Dict[str, Any]]:
    return {
        "module1": {
            "integer_var": 5,
            "float_var": 0.5,
            "string_var": "dummyvalue1",
            "boolean_var": True,
            "integer_array_var": [1, 2, 3],
            "float_array_var": [0.1, 0.2, 3.14159],
            "string_array_var": ["1", "2", "3", "4", "5"],
            "boolean_array_var": [True, False],
            "submodule1": {"nested_var": "dummyvalue2"},
        },
        "module2": {
            "submodule1": {
                "nested_module1": {
                    "nested_var1": "dummyvalue3",
                    "nested_var2": "dummyvalue4",
                },
            },
        },
    }


@pytest.mark.parametrize(
    "dummy_data_path, expected_result",
    [
        ("module1.integer_var", 5),
        ("module1.float_var", 0.5),
        ("module1.string_var", "dummyvalue1"),
        ("module1.boolean_var", True),
        ("module1.integer_array_var", [1, 2, 3]),
        ("module1.float_array_var", [0.1, 0.2, 3.14159]),
        ("module1.string_array_var", ["1", "2", "3", "4", "5"]),
        ("module1.string_var", "dummyvalue1"),
        ("module1.boolean_array_var", [True, False]),
        ("module1.submodule1.nested_var", "dummyvalue2"),
        ("module2.submodule1.nested_module1.nested_var1", "dummyvalue3"),
        ("module2.submodule1.nested_module1.nested_var2", "dummyvalue4"),
        (
            "module1",
            {
                "integer_var": 5,
                "float_var": 0.5,
                "string_var": "dummyvalue1",
                "boolean_var": True,
                "integer_array_var": [1, 2, 3],
                "float_array_var": [0.1, 0.2, 3.14159],
                "string_array_var": ["1", "2", "3", "4", "5"],
                "boolean_array_var": [True, False],
                "submodule1": {"nested_var": "dummyvalue2"},
            },
        ),
    ],
)
def test_get_data_with_valid_key(
    dummy_data_path: str,
    mock_pool_for_get_data: Dict[str, Dict[str, Any]],
    expected_result: Any,
    mocker: MockerFixture,
) -> None:
    """Unit test for get_data function in file input_manager.py with a valid data_path key"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__pool", mock_pool_for_get_data)

    # Act
    result = input_manager.get_data(dummy_data_path)

    assert result == expected_result


@pytest.mark.parametrize(
    "dummy_data_path, error_key",
    [
        ("module1.dummy_key", "dummy_key"),
        ("module1.submodule1.dummy_key", "dummy_key"),
        ("module2.submodule1.nested_module1.dummy_key", "dummy_key"),
        ("module2.submodule1.dummy_key.nested_var1", "dummy_key"),
        ("module2.dummy_key.nested_module1.nested_var1", "dummy_key"),
    ],
)
def test_get_data_returns_none(
    dummy_data_path: str,
    error_key: str,
    mock_pool_for_get_data: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for function get_data raising an exception in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__pool", mock_pool_for_get_data)
    patch_for_add_error = mocker.patch.object(input_manager.om, "add_error")

    # Act
    result = input_manager.get_data(dummy_data_path)

    # Assert
    assert result is None
    patch_for_add_error.assert_called_once_with(
        "Validation: data not found",
        mocker.ANY,
        mocker.ANY,
    )
    assert error_key in patch_for_add_error.call_args[0][1]


@pytest.fixture
def mock_pool_for_get_metadata(mocker: MockerFixture) -> Dict[str, Dict[str, Any]]:
    return {
        "properties": {
            "dummy_animal_properties": {
                "type": "object",
                "description": "Animal data",
                "herd_information": {
                    "type": "object",
                    "description": "Herd Demographics",
                    "calf_num": {
                        "type": "number",
                        "description": "Number of Calves (head)",
                        "default": 8,
                        "minimum": 0,
                    },
                    "cow_repro_method": {
                        "type": "string",
                        "description": "Cow Reproductive Program (select one)",
                        "default": "ED",
                        "pattern": "^{TAI|ED|ED-TAI}$",
                    },
                    "simulate_animals": {
                        "type": "boolean",
                        "description": "Whether or not to simulate animals during the simulation",
                        "default": True,
                    },
                    "dummy_cow_array": {
                        "type": "array",
                        "description": "dummy array for testing purposes",
                        "default": [1, 2, 3, 4],
                        "maximum_length": 7,
                    },
                },
            },
            "dummy_crop_properties": {
                "crop_species": {
                    "type": "string",
                    "description": "Name of the crop being grown.",
                    "pattern": "^{generic|corn|spring_wheat|winter_wheat|cereal_rye|spring_barley}$",
                },
                "harvest_years": {
                    "type": "array",
                    "description": "Calendar years in which the harvesting occurs",
                    "minimum_length": 0,
                    "default": [],
                    "properties": {"type": "number", "minimum": 1},
                },
                "pattern_skip": {
                    "type": "number",
                    "description": "Number of years to be skipped between schedule repetitions.",
                    "minimum": 0,
                    "default": 0,
                },
                "simulate_crops": {
                    "type": "boolean",
                    "description": "Dummy boolean variable for testing",
                    "default": False,
                },
            },
        }
    }


@pytest.mark.parametrize(
    "dummy_metadata_path, expected_result, expected_warning_call_count",
    [
        ("properties.dummy_animal_properties.herd_information.calf_num.default", 8, 0),
        (
            "properties.dummy_animal_properties.herd_information.calf_num",
            {
                "type": "number",
                "description": "Number of Calves (head)",
                "default": 8,
                "minimum": 0,
            },
            0,
        ),
        (
            "properties.dummy_animal_properties.herd_information.cow_repro_method.type",
            "string",
            0,
        ),
        (
            "properties.dummy_animal_properties.herd_information.cow_repro_method.pattern",
            "^{TAI|ED|ED-TAI}$",
            0,
        ),
        (
            "properties.dummy_animal_properties.herd_information.simulate_animals.type",
            "boolean",
            0,
        ),
        (
            "properties.dummy_animal_properties.herd_information.dummy_cow_array",
            {
                "type": "array",
                "description": "dummy array for testing purposes",
                "default": [1, 2, 3, 4],
                "maximum_length": 7,
            },
            0,
        ),
        (
            "properties.dummy_crop_properties.crop_species.description",
            "Name of the crop being grown.",
            0,
        ),
        ("properties.dummy_crop_properties.harvest_years.type", "array", 0),
        (
            "properties.dummy_crop_properties.harvest_years",
            {
                "type": "array",
                "description": "Calendar years in which the harvesting occurs",
                "minimum_length": 0,
                "default": [],
                "properties": {"type": "number", "minimum": 1},
            },
            0,
        ),
        ("properties.dummy_crop_properties.pattern_skip.minimum", 0, 0),
        (
            "properties.dummy_crop_properties.simulate_crops",
            {
                "type": "boolean",
                "description": "Dummy boolean variable for testing",
                "default": False,
            },
            0,
        ),
        (
            "properties",
            {
                "dummy_animal_properties": {
                    "type": "object",
                    "description": "Animal data",
                    "herd_information": {
                        "type": "object",
                        "description": "Herd Demographics",
                        "calf_num": {
                            "type": "number",
                            "description": "Number of Calves (head)",
                            "default": 8,
                            "minimum": 0,
                        },
                        "cow_repro_method": {
                            "type": "string",
                            "description": "Cow Reproductive Program (select one)",
                            "default": "ED",
                            "pattern": "^{TAI|ED|ED-TAI}$",
                        },
                        "simulate_animals": {
                            "type": "boolean",
                            "description": "Whether or not to simulate animals during the simulation",
                            "default": True,
                        },
                        "dummy_cow_array": {
                            "type": "array",
                            "description": "dummy array for testing purposes",
                            "default": [1, 2, 3, 4],
                            "maximum_length": 7,
                        },
                    },
                },
                "dummy_crop_properties": {
                    "crop_species": {
                        "type": "string",
                        "description": "Name of the crop being grown.",
                        "pattern": "^{generic|corn|spring_wheat|winter_wheat|cereal_rye|spring_barley}$",
                    },
                    "harvest_years": {
                        "type": "array",
                        "description": "Calendar years in which the harvesting occurs",
                        "minimum_length": 0,
                        "default": [],
                        "properties": {"type": "number", "minimum": 1},
                    },
                    "pattern_skip": {
                        "type": "number",
                        "description": "Number of years to be skipped between schedule repetitions.",
                        "minimum": 0,
                        "default": 0,
                    },
                    "simulate_crops": {
                        "type": "boolean",
                        "description": "Dummy boolean variable for testing",
                        "default": False,
                    },
                },
            },
            0,
        ),
    ],
)
def test_get_metadata_with_valid_key(
    dummy_metadata_path: str,
    mock_pool_for_get_metadata: Dict[str, Dict[str, Any]],
    expected_result: Any,
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
) -> None:
    """Unit test for get_metadata function in file input_manager.py with a valid metadata_path key"""

    mock_input_manager.meta_data = mock_pool_for_get_metadata

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager.get_metadata(dummy_metadata_path)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    "dummy_metadata_path, expected_error_parent_address, expected_error_invalid_key, expected_warning_call_count",
    [
        (
            "dummy_animal_properties.herd_information.calf_num.dummy_key",
            "dummy_animal_properties.herd_information.calf_num",
            "dummy_key",
            1,
        ),
        (
            "dummy_animal_properties.herd_information.dummy_key",
            "dummy_animal_properties.herd_information",
            "dummy_key",
            1,
        ),
        (
            "dummy_crop_properties.crop_species.dummy_key",
            "dummy_crop_properties.crop_species",
            "dummy_key",
            1,
        ),
        ("dummy_crop_properties.dummy_key", "dummy_crop_properties", "dummy_key", 1),
        (
            "dummy_crop_properties.pattern_skip.dummy_key",
            "dummy_crop_properties.pattern_skip",
            "dummy_key",
            1,
        ),
    ],
)
def test_get_metadata_raises_exception(
    dummy_metadata_path: str,
    expected_error_parent_address: str,
    expected_error_invalid_key: str,
    mock_pool_for_get_metadata: Dict[str, Dict[str, Any]],
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function get_metadata raising an exception in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_pool_for_get_metadata

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(KeyError) as key_error:
            mock_input_manager.get_metadata(dummy_metadata_path)

        error_message = key_error.value.__str__().strip("'")
        assert (
            error_message == f'Data not found: Cannot find "{dummy_metadata_path}", '
            f'"{expected_error_parent_address}" does not have attribute '
            f'"{expected_error_invalid_key}".'
        )
        assert add_error.call_count == expected_warning_call_count


def test_get_data_by_properties_no_data(
    mock_input_manager: InputManager, input_manager_original_method_states: Dict[str, Any], mocker: MockerFixture
) -> None:
    """Tests that error is handled properly when get_metadata() raises KeyError."""
    mock_input_manager.get_metadata = MagicMock(side_effect=KeyError)

    add_error = mocker.patch.object(mock_input_manager.om, "add_error")

    actual = mock_input_manager.get_data_keys_by_properties("dummy_property")

    assert add_error.call_count == 1
    assert actual == []

    mock_input_manager.get_metadata = input_manager_original_method_states["get_metadata"]


@pytest.mark.parametrize(
    "data,expected_keys",
    [
        (
            {
                "key_1": {"properties": "properties_1"},
                "key_2": {"properties": "properties_2"},
                "key_3": {"properties": "target_properties"},
                "key_4": {"properties": "target_properties"},
                "key_5": {"properties": "target_properties"},
            },
            ["key_3", "key_4", "key_5"],
        ),
        (
            {
                "key_1": {"properties": "target_properties"},
                "key_2": {"properties": "value"},
                "key_3": {"properties": "target_properties"},
                "key_4": {"properties": "properties_4"},
                "key_5": {"properties": "properties_5"},
            },
            ["key_1", "key_3"],
        ),
        ({"key_1": {"properties": "value"}, "key_2": {"properties": "value"}, "key_3": {"properties": "value"}}, []),
        ({}, []),
    ],
)
def test_get_data_keys_by_properties(
    data: dict[str, dict[str, str]],
    expected_keys: list[str],
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test that Input Manager gets data keys by properties correctly."""
    mock_input_manager.get_metadata = MagicMock(return_value=data)

    actual = mock_input_manager.get_data_keys_by_properties("target_properties")

    assert actual == expected_keys

    mock_input_manager.get_metadata = input_manager_original_method_states["get_metadata"]


def test_flush_pool(mock_input_manager: InputManager) -> None:
    """Tests that the InputManager pool is flushed correctly."""

    mock_input_manager._InputManager__pool = {"Key": "I never metadata I didn't like!"}

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        mock_input_manager.flush_pool()

        assert mock_input_manager._InputManager__pool == {}
        assert add_log.call_count == 1


@pytest.mark.parametrize("properties_blob_key", ["properties1", "properties2"])
def test_metadata_properties_exist(
    properties_blob_key: str,
    mock_input_manager: InputManager,
    mock_metadata: Dict[str, Dict[str, Any]],
) -> None:
    mock_input_manager._InputManager__metadata = mock_metadata

    result = mock_input_manager._metadata_properties_exist(
        variable_name="mock_variable", properties_blob_key=properties_blob_key
    )

    assert result is True


def test_metadata_properties_exist_no_metadata(
    mock_input_manager: InputManager,
) -> None:
    mock_input_manager._InputManager__metadata = {}

    with pytest.raises(ValueError):
        mock_input_manager._metadata_properties_exist(
            variable_name="mock_variable",
            properties_blob_key="mock_properties_blob_key",
        )


@pytest.mark.parametrize(
    "variable_name, properties_blob_key",
    [("variable1", "propertiesA"), ("variable2", "propertiesB")],
)
def test_metadata_properties_exists_invalid_properties_blob_key(
    variable_name: str,
    properties_blob_key: str,
    mock_input_manager: InputManager,
    mock_metadata: Dict[str, Dict[str, Any]],
) -> None:
    mock_input_manager._InputManager__metadata = mock_metadata

    with pytest.raises(KeyError):
        mock_input_manager._metadata_properties_exist(
            variable_name=variable_name, properties_blob_key=properties_blob_key
        )


@pytest.fixture
def mock_metadata_for_add_variable_to_pool() -> Dict[str, Dict[str, Any]]:
    return {
        "files": {
            "file1": {
                "type": "json",
                "path": "path/to/json/file1.json",
                "properties": "properties1",
            },
            "file2": {
                "type": "csv",
                "path": "path/to/csv/file2.csv",
                "properties": "properties2",
            },
        },
        "properties": {
            "dict_data": {
                "int": "some_value1",
                "str": "some_value2",
                "float": "some_value1",
                "int_array": "some_value2",
                "float_array": "some_value1",
                "str_arr": "some_value2",
                "type": "object",
                "modifiability": "unrequired unlocked",
            },
            "array_of_int_data": {"array_of_int_data": "some_value3"},
            "array_of_float_data": {"array_of_float_data": "some_value3"},
            "array_of_str_data": {"array_of_str_data": "some_value3"},
            "array_of_dict_data": {"array_of_dict_data": "some_value3"},
            "dict_of_array_data": {
                "array1": "some_value1",
                "array2": "some_value2",
                "array3": "some_value1",
            },
        },
    }


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key, starting_im_pool",
    [
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {},
        ),
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {"dict_data": {"1": 1}},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {"array_of_int_data": [-1, 0, 1]},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {"array_of_float_data": [-1.0, 0.0, 1.0]},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {"array_of_str_data": ["a", "b", "c"]},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {"dict_of_array_data": {"a": [1, 2, 3]}},
        ),
    ],
)
def test_add_variable_to_pool_valid(
    variable_name: str,
    data: Any,
    properties_blob_key: str,
    starting_im_pool: Dict[str, Any],
    mock_metadata_for_add_variable_to_pool: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for add_variable_to_pool() method in file input_manager.py with valid data."""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_add_variable_to_pool)
    mocker.patch.object(input_manager, "_InputManager__pool", starting_im_pool)
    mocker.patch.object(DataValidator, "validate_data_by_type", return_value=True)

    patch_add = mocker.patch("RUFAS.input_manager.InputManager._add_to_pool", wraps=input_manager._add_to_pool)
    input_manager._add_to_pool.__name__ = "_add_to_pool"
    patch_check = mocker.patch("RUFAS.input_manager.InputManager._check_modifiability")
    patch_validate = mocker.patch("RUFAS.input_manager.InputManager._validate_data", wraps=input_manager._validate_data)
    patch_prepare = mocker.patch("RUFAS.input_manager.InputManager._prepare_data", wraps=input_manager._prepare_data)

    expected_add_warning_count = 1 if starting_im_pool else 0
    patch_for_add_warning = mocker.patch.object(OutputManager, "add_warning")
    patch_for_add_error = mocker.patch.object(OutputManager, "add_error")

    # Act
    result = input_manager._add_variable_to_pool(
        variable_name=variable_name,
        input_data=data,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
    )

    # Assert
    assert result
    assert patch_for_add_warning.call_count == expected_add_warning_count
    assert patch_for_add_error.call_count == 0
    assert variable_name in input_manager.pool
    assert input_manager.get_data(variable_name) == data
    patch_add.assert_called_once()
    patch_check.assert_called_once()
    patch_validate.assert_called_once()
    patch_prepare.assert_called_once()


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key, starting_im_pool",
    [
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {},
        ),
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {"dict_data": {"1": 1}},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {"array_of_int_data": [-1, 0, 1]},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {"array_of_float_data": [-1.0, 0.0, 1.0]},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {"array_of_str_data": ["a", "b", "c"]},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {"dict_of_array_data": {"a": [1, 2, 3]}},
        ),
    ],
)
def test_add_variable_to_pool_invalid(
    variable_name: str,
    data: Any,
    properties_blob_key: str,
    starting_im_pool: Dict[str, Any],
    mock_metadata_for_add_variable_to_pool: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for add_variable_to_pool() method in file input_manager.py with invalid data.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_add_variable_to_pool)
    mocker.patch.object(input_manager, "_InputManager__pool", starting_im_pool)
    mocker.patch.object(DataValidator, "validate_data_by_type", return_value=False)
    patch_for_add_warning = mocker.patch.object(OutputManager, "add_warning")
    patch_for_add_error = mocker.patch.object(OutputManager, "add_error")
    mock_elements_counter = mocker.MagicMock()
    mock_elements_counter.invalid_elements = 1
    mocker.patch("RUFAS.input_manager.ElementsCounter", return_value=mock_elements_counter)

    # Act
    result = input_manager._add_variable_to_pool(
        variable_name=variable_name,
        input_data=data,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
    )

    # Assert
    assert result is False
    assert patch_for_add_warning.call_count == 0
    assert patch_for_add_error.call_count == 1

    if starting_im_pool:
        assert starting_im_pool[variable_name] == input_manager.get_data(variable_name)
    else:
        assert variable_name not in input_manager.pool


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key, starting_im_pool",
    [
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {},
        ),
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {"dict_data": {"1": 1}},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {"array_of_int_data": [-1, 0, 1]},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {"array_of_float_data": [-1.0, 0.0, 1.0]},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {"array_of_str_data": ["a", "b", "c"]},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {"dict_of_array_data": {"a": [1, 2, 3]}},
        ),
    ],
)
def test_add_variable_to_pool_eager_termination(
    variable_name: str,
    data: Any,
    properties_blob_key: str,
    starting_im_pool: Dict[str, Any],
    mock_metadata_for_add_variable_to_pool: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for add_variable_to_pool() method in file input_manager.py with eager_termination=True.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_add_variable_to_pool)
    mocker.patch.object(input_manager, "_InputManager__pool", starting_im_pool)
    mocker.patch.object(DataValidator, "validate_data_by_type", return_value=False)
    mock_elements_counter = mocker.MagicMock()
    mock_elements_counter.invalid_elements = 1
    mocker.patch("RUFAS.input_manager.ElementsCounter", return_value=mock_elements_counter)
    patch_for_add_warning = mocker.patch.object(OutputManager, "add_warning")
    patch_for_add_error = mocker.patch.object(OutputManager, "add_error")

    # Act
    with pytest.raises(ValueError):
        input_manager._add_variable_to_pool(
            variable_name=variable_name,
            input_data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=True,
        )

    # Assert
    assert patch_for_add_warning.call_count == 0
    assert patch_for_add_error.call_count == 1
    if starting_im_pool:
        assert starting_im_pool[variable_name] == input_manager.get_data(variable_name)
    else:
        assert variable_name not in input_manager.pool


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key",
    [
        ("var1", {}, "key1"),
        ("var2", {"a": 1}, "key2"),
        ("var3", {"a": "A", "b": 2, "c": True}, "key3"),
        ("var4", {"a": [1, 2, 3], "b": ["a", "b", "c"], "c": [0.0, 1.1, 2.2]}, "key4"),
    ],
)
def test_add_runtime_variable_to_pool(
    variable_name: str,
    data: Dict[str, Any],
    properties_blob_key: str,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_runtime_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

    assert result is True
    assert mock_om_add_error.call_count == 0
    mock_input_manager._metadata_properties_exist.assert_called_once_with(
        variable_name=variable_name, properties_blob_key=properties_blob_key
    )
    mock_input_manager._add_variable_to_pool.assert_called_once_with(
        variable_name=variable_name,
        input_data=data,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
    )

    mock_input_manager.add_variable_to_pool = input_manager_original_method_states["add_runtime_variable_to_pool"]
    mock_input_manager._metadata_properties_exist = input_manager_original_method_states["_metadata_properties_exist"]
    mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key",
    [
        ("var1", "a", "key1"),
        ("var2", [1, 2, 3], "key2"),
        ("var3", 5, "key3"),
    ],
)
def test_add_runtime_variable_to_pool_type_error(
    variable_name: str,
    data: Dict[str, Any],
    properties_blob_key: str,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        with pytest.raises(TypeError):
            mock_input_manager.add_runtime_variable_to_pool(
                variable_name=variable_name,
                data=data,
                properties_blob_key=properties_blob_key,
                eager_termination=False,
            )

        assert mock_om_add_error.call_count == 1
        mock_input_manager._metadata_properties_exist.assert_not_called()
        mock_input_manager._add_variable_to_pool.assert_not_called()

        mock_input_manager.add_variable_to_pool = input_manager_original_method_states["add_runtime_variable_to_pool"]
        mock_input_manager._metadata_properties_exist = input_manager_original_method_states[
            "_metadata_properties_exist"
        ]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key",
    [
        ("var1", {}, "key1"),
        ("var2", {"a": 1}, "key2"),
        ("var3", {"a": "A", "b": 2, "c": True}, "key3"),
    ],
)
def test_add_runtime_variable_to_pool_invalid_data(
    variable_name: str,
    data: Dict[str, Any],
    properties_blob_key: str,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=False)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_runtime_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

        assert result is False
        assert mock_om_add_error.call_count == 0
        mock_input_manager._metadata_properties_exist.assert_called_once_with(
            variable_name=variable_name, properties_blob_key=properties_blob_key
        )
        mock_input_manager._add_variable_to_pool.assert_called_once_with(
            variable_name=variable_name,
            input_data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

        mock_input_manager.add_variable_to_pool = input_manager_original_method_states["add_runtime_variable_to_pool"]
        mock_input_manager._metadata_properties_exist = input_manager_original_method_states[
            "_metadata_properties_exist"
        ]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


def test_add_runtime_variable_to_pool_metadata_properties_do_not_exist(
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=False)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=False)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_runtime_variable_to_pool(
            variable_name="var1",
            data={"a": 1},
            properties_blob_key="key2",
            eager_termination=False,
        )

        assert result is False
        assert mock_om_add_error.call_count == 0
        mock_input_manager._metadata_properties_exist.assert_called_once_with(
            variable_name="var1", properties_blob_key="key2"
        )
        mock_input_manager._add_variable_to_pool.assert_not_called()

        mock_input_manager.add_variable_to_pool = input_manager_original_method_states["add_runtime_variable_to_pool"]
        mock_input_manager._metadata_properties_exist = input_manager_original_method_states[
            "_metadata_properties_exist"
        ]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize(
    "variable_name, variable_properties, expected_modifiability",
    [
        ("var1", {"type": "string", "modifiability": "required locked"}, Modifiability.REQUIRED_LOCKED),
        ("var2", {"type": "number", "modifiability": "required unlocked"}, Modifiability.REQUIRED_UNLOCKED),
        ("var3", {"type": "bool", "modifiability": "unrequired unlocked"}, Modifiability.UNREQUIRED_UNLOCKED),
        ("var4", {"type": "object"}, Modifiability.UNREQUIRED_UNLOCKED),
    ],
)
def test_get_variable_modifiability(
    variable_name: str,
    variable_properties: Dict[str, Any],
    expected_modifiability: Modifiability,
    mock_input_manager: InputManager,
) -> None:
    with patch("RUFAS.output_manager.OutputManager.add_warning") as mock_om_add_warning:
        actual_modifiability = mock_input_manager._get_variable_modifiability(
            variable_name=variable_name, variable_properties=variable_properties
        )

        mock_om_add_warning.assert_not_called()
        assert actual_modifiability == expected_modifiability


@pytest.mark.parametrize(
    "variable_name, variable_properties",
    [
        ("var1", {"type": "string", "modifiability": "a"}),
        ("var2", {"type": "number", "modifiability": "b"}),
        ("var3", {"type": "bool", "modifiability": "c"}),
        ("var4", {"type": "object", "modifiability": "d"}),
    ],
)
def test_get_variable_modifiability_unknown_modifiability(
    variable_name: str,
    variable_properties: Dict[str, Any],
    mock_input_manager: InputManager,
) -> None:
    with patch("RUFAS.output_manager.OutputManager.add_warning") as mock_om_add_warning:
        mock_input_manager._get_variable_modifiability(
            variable_name=variable_name, variable_properties=variable_properties
        )

    mock_om_add_warning.assert_called_once()


@pytest.mark.parametrize(
    "variable_name, variable_properties",
    [
        ("var1", {"type": "string", "modifiability": "unrequired unlocked"}),
        ("var2", {"type": "number", "modifiability": "unrequired unlocked"}),
        ("var3", {"type": "bool", "modifiability": "unrequired unlocked"}),
        ("var4", {"type": "object"}),
    ],
)
def test_log_missing_data_initialization_input_not_required(
    variable_name: str,
    variable_properties: Dict[str, Any],
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")

    mock_input_manager._log_missing_data(
        var_name=variable_name, variable_properties=variable_properties, called_during_initialization=True
    )

    assert mock_add_error.call_count == 0
    assert mock_add_warning.call_count == 1


@pytest.mark.parametrize(
    "variable_name, variable_properties",
    [
        ("var1", {"type": "string", "modifiability": "required locked"}),
        ("var2", {"type": "number", "modifiability": "required unlocked"}),
        ("var3", {"type": "bool", "modifiability": "required unlocked"}),
        ("var4", {"type": "object", "modifiability": "required locked"}),
    ],
)
def test_log_missing_data_initialization_key_error(
    variable_name: str,
    variable_properties: Dict[str, Any],
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")

    with pytest.raises(KeyError):
        mock_input_manager._log_missing_data(
            var_name=variable_name, variable_properties=variable_properties, called_during_initialization=True
        )

    assert mock_add_error.call_count == 1
    assert mock_add_warning.call_count == 0


@pytest.mark.parametrize(
    "variable_name, variable_properties",
    [
        ("var1", {"type": "string", "modifiability": "required locked"}),
        ("var2", {"type": "number", "modifiability": "required locked"}),
        ("var3", {"type": "bool", "modifiability": "unrequired locked"}),
        ("var4", {"type": "object", "modifiability": "unrequired locked"}),
    ],
)
def test_log_missing_data_runtime_key_error(
    variable_name: str,
    variable_properties: Dict[str, Any],
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")

    with pytest.raises(KeyError):
        mock_input_manager._log_missing_data(
            var_name=variable_name, variable_properties=variable_properties, called_during_initialization=False
        )

    assert mock_add_error.call_count == 1
    assert mock_add_warning.call_count == 0


@pytest.fixture
def mock_metadata_for_add_variable_to_pool_nested() -> Dict[str, Dict[str, Any]]:
    return {
        "properties": {
            "dict_data_runtime_modifiable": {
                "type": "object",
                "modifiability": "unrequired unlocked",
                "int": {
                    "type": "number",
                    "modifiability": "unrequired unlocked",
                },
                "str": {
                    "type": "string",
                    "modifiability": "unrequired unlocked",
                },
                "float": {
                    "type": "number",
                    "modifiability": "unrequired unlocked",
                },
                "int_array": {
                    "type": "array",
                    "modifiability": "unrequired unlocked",
                    "properties": {
                        "type": "number",
                        "modifiability": "unrequired unlocked",
                    },
                },
                "float_array": {
                    "type": "array",
                    "modifiability": "unrequired unlocked",
                    "properties": {
                        "type": "number",
                        "modifiability": "unrequired unlocked",
                    },
                },
                "str_arr": {
                    "type": "array",
                    "modifiability": "unrequired unlocked",
                    "properties": {
                        "type": "string",
                        "modifiability": "unrequired unlocked",
                    },
                },
                "nested_dict": {
                    "type": "object",
                    "modifiability": "unrequired unlocked",
                    "a": {
                        "type": "object",
                        "modifiability": "unrequired unlocked",
                        "b": {
                            "type": "object",
                            "modifiability": "unrequired unlocked",
                            "c": {
                                "type": "object",
                                "modifiability": "unrequired unlocked",
                                "d": {
                                    "type": "number",
                                    "modifiability": "unrequired unlocked",
                                },
                            },
                        },
                    },
                    "A": {
                        "type": "object",
                        "modifiability": "unrequired unlocked",
                        "B": {
                            "type": "object",
                            "modifiability": "unrequired unlocked",
                            "C": {
                                "type": "string",
                                "modifiability": "unrequired unlocked",
                            },
                        },
                    },
                },
            },
            "array_of_int_data_runtime_modifiable": {
                "type": "array",
                "modifiability": "required unlocked",
                "properties": {
                    "type": "number",
                    "modifiability": "required unlocked",
                },
            },
            "array_of_float_data_runtime_modifiable": {
                "type": "array",
                "modifiability": "required unlocked",
                "properties": {
                    "type": "number",
                    "modifiability": "required unlocked",
                },
            },
            "array_of_str_data_runtime_modifiable": {
                "type": "array",
                "modifiability": "required unlocked",
                "properties": {
                    "type": "string",
                    "modifiability": "required unlocked",
                },
            },
            "array_of_dict_data_runtime_modifiable": {
                "type": "array",
                "modifiability": "required unlocked",
                "properties": {
                    "type": "object",
                    "modifiability": "required unlocked",
                    "int": {
                        "type": "number",
                        "modifiability": "required unlocked",
                    },
                    "str": {
                        "type": "string",
                        "modifiability": "required unlocked",
                    },
                    "float": {
                        "type": "number",
                        "modifiability": "required unlocked",
                    },
                },
            },
            "dict_of_array_data_runtime_modifiable": {
                "array1": {
                    "type": "array",
                    "modifiability": "required unlocked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required unlocked",
                    },
                },
                "array2": {
                    "type": "array",
                    "modifiability": "required unlocked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required unlocked",
                    },
                },
                "array3": {
                    "type": "array",
                    "modifiability": "required unlocked",
                    "properties": {
                        "type": "string",
                        "modifiability": "required unlocked",
                    },
                },
            },
            "dict_data_runtime_unmodifiable": {
                "type": "object",
                "modifiability": "required locked",
                "int": {
                    "type": "number",
                    "modifiability": "required locked",
                },
                "str": {
                    "type": "string",
                    "modifiability": "required locked",
                },
                "float": {
                    "type": "number",
                    "modifiability": "required locked",
                },
                "int_array": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                },
                "float_array": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                },
                "str_arr": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "string",
                        "modifiability": "required locked",
                    },
                },
                "nested_dict": {
                    "type": "object",
                    "modifiability": "required locked",
                    "a": {
                        "type": "object",
                        "modifiability": "required locked",
                        "b": {
                            "type": "object",
                            "modifiability": "required locked",
                            "c": {
                                "type": "object",
                                "modifiability": "required locked",
                                "d": {
                                    "type": "number",
                                    "modifiability": "required locked",
                                },
                            },
                        },
                    },
                    "A": {
                        "type": "object",
                        "modifiability": "required locked",
                        "B": {
                            "type": "object",
                            "modifiability": "required locked",
                            "C": {
                                "type": "string",
                                "modifiability": "required locked",
                            },
                        },
                    },
                },
            },
            "array_of_int_data_runtime_unmodifiable": {
                "type": "array",
                "modifiability": "required locked",
                "properties": {
                    "type": "number",
                    "modifiability": "required locked",
                },
            },
            "array_of_float_data_runtime_unmodifiable": {
                "type": "array",
                "modifiability": "required locked",
                "properties": {
                    "type": "number",
                    "modifiability": "required locked",
                },
            },
            "array_of_str_data_runtime_unmodifiable": {
                "type": "array",
                "modifiability": "required locked",
                "properties": {
                    "type": "string",
                    "modifiability": "required locked",
                },
            },
            "array_of_dict_data_runtime_unmodifiable": {
                "type": "array",
                "modifiability": "required locked",
                "properties": {
                    "type": "object",
                    "modifiability": "required locked",
                    "int": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                    "str": {
                        "type": "string",
                        "modifiability": "required locked",
                    },
                    "float": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                },
            },
            "dict_of_array_data_runtime_unmodifiable": {
                "array1": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                },
                "array2": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                },
                "array3": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "string",
                        "modifiability": "required locked",
                    },
                },
            },
        }
    }


@pytest.fixture
def mock_pool_for_add_variable_to_pool_nested() -> Dict[str, Dict[str, Any] | List[Any]]:
    return {
        "dict_data_runtime_modifiable": {
            "int": 1,
            "str": "2",
            "float": 3.3,
            "int_array": [4, 5, 6],
            "float_array": [7.7, 8.8, 9.9],
            "str_arr": ["10"],
            "nested_dict": {"a": {"b": {"c": {"d": 11}}}},
        },
        "array_of_int_data_runtime_modifiable": [1, 2, 3, 4, 5],
        "array_of_float_data_runtime_modifiable": [1.1, 2.2, 3.3, 4.4, 5.5],
        "array_of_str_data_runtime_modifiable": ["1.1", "2.2", "3.3", "4.4", "5.5"],
        "array_of_dict_data_runtime_modifiable": [
            {"int": 1, "str": "2", "float": 3.3},
            {"int": 4, "str": "5", "float": 6.6},
            {"int": 7, "str": "8", "float": 9.9},
        ],
        "dict_of_array_data_runtime_modifiable": {
            "array1": [1, 2, 3],
            "array2": [4.4, 5.5, 6.6],
            "array3": ["7.7", "8.8", "9.9"],
        },
        "dict_data_runtime_unmodifiable": {
            "int": 1,
            "str": "2",
            "float": 3.3,
            "int_array": [4, 5, 6],
            "float_array": [7.7, 8.8, 9.9],
            "str_arr": ["10"],
            "nested_dict": {"a": {"b": {"c": {"d": 11}}}, "A": {"B": {"C": "CCCCC!"}}},
        },
        "array_of_int_data_runtime_unmodifiable": [1, 2, 3, 4, 5],
        "array_of_float_data_runtime_unmodifiable": [1.1, 2.2, 3.3, 4.4, 5.5],
        "array_of_str_data_runtime_unmodifiable": ["1.1", "2.2", "3.3", "4.4", "5.5"],
        "array_of_dict_data_runtime_unmodifiable": [
            {"int": 1, "str": "2", "float": 3.3},
            {"int": 4, "str": "5", "float": 6.6},
            {"int": 7, "str": "8", "float": 9.9},
        ],
        "dict_of_array_data_runtime_unmodifiable": {
            "array1": [1, 2, 3],
            "array2": [4.4, 5.5, 6.6],
            "array3": ["7.7", "8.8", "9.9"],
        },
    }


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key, is_modifiable_during_runtime, eager_termination,"
    "expected_add_warning_call_count",
    [
        ("dict_data_runtime_modifiable.nested_dict.a.b.c.d", {"d": 11}, "dict_data_runtime_modifiable", True, False, 0),
        ("dict_data_runtime_modifiable.nested_dict.A.B.C", {"C": None}, "dict_data_runtime_modifiable", True, False, 0),
        (
            "dict_data_runtime_unmodifiable.nested_dict.a.b.c.d",
            {"d": 11},
            "dict_data_runtime_unmodifiable",
            False,
            False,
            1,
        ),
        (
            "dict_data_runtime_unmodifiable.nested_dict.A.B.C",
            {"C": "CCCCC!"},
            "dict_data_runtime_unmodifiable",
            False,
            False,
            1,
        ),
        ("dict_data_runtime_unmodifiable.nested_dict.a.b.c.d", 10, "dict_data_runtime_unmodifiable", False, True, 0),
        ("dict_data_runtime_unmodifiable.nested_dict.A.B.C", "10", "dict_data_runtime_unmodifiable", False, True, 0),
    ],
)
def test_add_variable_to_pool_nested(
    variable_name: str,
    data: Dict[str, Any],
    properties_blob_key: str,
    is_modifiable_during_runtime: bool,
    eager_termination: bool,
    expected_add_warning_call_count: int,
    mock_metadata_for_add_variable_to_pool_nested: Dict[str, Any],
    mock_pool_for_add_variable_to_pool_nested: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the _add_variable_to_pool method of the InputManager class for nested data.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_add_variable_to_pool_nested)
    mocker.patch.object(input_manager, "_InputManager__pool", mock_pool_for_add_variable_to_pool_nested)
    mocker.patch.object(DataValidator, "validate_data_by_type", return_value=True)
    mocker.patch.object(OutputManager, "add_log")
    patch_for_add_warning = mocker.patch.object(OutputManager, "add_warning")
    mocker.patch.object(OutputManager, "add_error")

    if (not is_modifiable_during_runtime) and eager_termination:
        with pytest.raises(PermissionError):
            input_manager._add_variable_to_pool(
                variable_name=variable_name,
                input_data=data,
                properties_blob_key=properties_blob_key,
                eager_termination=eager_termination,
            )
    elif not is_modifiable_during_runtime:
        assert not input_manager._add_variable_to_pool(
            variable_name=variable_name,
            input_data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=eager_termination,
        )
    else:
        result = input_manager._add_variable_to_pool(
            variable_name=variable_name,
            input_data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

        assert result
        assert patch_for_add_warning.call_count == expected_add_warning_call_count
        assert input_manager.get_data(variable_name) == list(data.values())[0]


def test_dump_get_data_logs(
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    mock_input_manager._InputManager__get_data_logs_pool = {
        "14-Feb-2024_Wed_06-15-56.692523": "InputManager.get_data() gets called for ['a'].",
        "14-Feb-2024_Wed_06-15-56.693523": "InputManager.get_data() gets called for ['b'].",
        "14-Feb-2024_Wed_06-15-56.696526": "InputManager.get_data() gets called for ['c'].",
    }
    mock_dir_path = Path("dummy_path")
    mock_generated_file_name = "dummy_file_name.json"
    patch_for_generate_file_name = mocker.patch.object(
        mock_input_manager.om, "generate_file_name", return_value=mock_generated_file_name
    )
    patch_create_dir = mocker.patch("RUFAS.output_manager.OutputManager.create_directory")

    mock_dict_to_file_json = mocker.patch.object(mock_input_manager.om, "dict_to_file_json")

    mock_input_manager.dump_get_data_logs(path=mock_dir_path)

    patch_for_generate_file_name.assert_called_once_with(base_name="InputManager_get_data_log", extension="json")
    patch_create_dir.assert_called_once_with(mock_dir_path)
    mock_dict_to_file_json.assert_called_once_with(
        mock_input_manager._InputManager__get_data_logs_pool, Path("dummy_path", mock_generated_file_name)
    )


def test_dump_delete_data_logs(
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    mock_input_manager._InputManager__delete_data_logs_pool = {
        "14-Feb-2024_Wed_06-15-56.692523": "InputManager.get_data() gets called for ['a'].",
        "14-Feb-2024_Wed_06-15-56.693523": "InputManager.get_data() gets called for ['b'].",
        "14-Feb-2024_Wed_06-15-56.696526": "InputManager.get_data() gets called for ['c'].",
    }
    mock_dir_path = Path("dummy_path")
    mock_generated_file_name = "dummy_file_name.json"
    patch_for_generate_file_name = mocker.patch.object(
        mock_input_manager.om, "generate_file_name", return_value=mock_generated_file_name
    )
    patch_create_dir = mocker.patch("RUFAS.output_manager.OutputManager.create_directory")

    mock_dict_to_file_json = mocker.patch.object(mock_input_manager.om, "dict_to_file_json")

    mock_input_manager.dump_delete_data_logs(path=mock_dir_path)

    patch_for_generate_file_name.assert_called_once_with(base_name="InputManager_delete_data_log", extension="json")
    patch_create_dir.assert_called_once_with(mock_dir_path)
    mock_dict_to_file_json.assert_called_once_with(
        mock_input_manager._InputManager__delete_data_logs_pool, Path("dummy_path", mock_generated_file_name)
    )


@pytest.mark.parametrize(
    "data_address,expected_result,raise_key_error",
    [
        ("animal.herd_information.calf_num", True, False),
        ("animal.herd_information.nonexistent_property", False, True),
    ],
)
def test_check_property_exists_in_pool(
    mocker: MockerFixture, data_address: str, expected_result: bool, raise_key_error: bool
) -> None:
    """
    Unit test for the check_property_exists_in_pool() method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()
    patch_for_extract_value = mocker.patch.object(DataValidator, "extract_value_by_key_list")
    if raise_key_error:
        patch_for_extract_value.side_effect = KeyError("Key Error")

    # Act
    result = input_manager.check_property_exists_in_pool(data_address)

    # Assert
    assert result == expected_result
    patch_for_extract_value.assert_called_once()


def test_save_metadata_properties(mock_input_manager: InputManager) -> None:
    """Tests save_metadata_properties() function in InputManager."""
    mock_records = [{"name": "example", "value": 42}]
    output_dir = Path("/fake/directory")
    metadata = {"properties": "test_properties"}
    mock_input_manager.meta_data = metadata

    with (
        patch.object(mock_input_manager, "_parse_metadata_properties", return_value=mock_records) as mock_parse,
        patch("pandas.DataFrame.to_csv") as mock_to_csv,
        patch(
            "RUFAS.output_manager.OutputManager.generate_file_name", return_value="output.csv"
        ) as mock_generate_file_name,
        patch("RUFAS.output_manager.OutputManager.create_directory", new_callable=MagicMock) as mock_create_dir,
    ):
        mock_input_manager.save_metadata_properties(output_dir)

        mock_parse.assert_called_once_with("test_properties")
        mock_create_dir.assert_called_once_with(output_dir)
        mock_to_csv.assert_called_once_with(output_dir / "output.csv", index=False)
        mock_generate_file_name.assert_called_once_with("InputManager_metadata_properties", extension="csv")


@pytest.mark.parametrize(
    "exception, error_message",
    [(FileNotFoundError, "No such file or directory"), (PermissionError, "Permission denied"), (OSError, "OS error")],
)
def test_save_metadata_properties_errors(
    mock_input_manager: InputManager,
    mocker: MockerFixture,
    exception: Type[FileNotFoundError | PermissionError | OSError],
    error_message: str,
) -> None:
    output_dir = Path("/example/dir")
    generated_filename = "file.csv"
    expected_path = output_dir / generated_filename
    metadata = {"properties": "test_properties"}
    mock_input_manager.meta_data = metadata
    mock_records = [{"key": "value"}]

    mock_parse = mocker.patch.object(mock_input_manager, "_parse_metadata_properties", return_value=mock_records)
    mocker.patch("RUFAS.output_manager.OutputManager.create_directory")
    mocker.patch("pandas.DataFrame.to_csv", side_effect=exception(error_message))
    mocker.patch.object(mock_input_manager.om, "generate_file_name", return_value=generated_filename)
    mock_add_error = mocker.patch.object(mock_input_manager.om, "add_error")

    with pytest.raises(exception) as exc_info:
        mock_input_manager.save_metadata_properties(output_dir)

    assert str(exc_info.value) == error_message

    mock_parse.assert_called_once_with("test_properties")
    mock_add_error.assert_called_once_with(
        "Save CSV failure.", f"Unable to save to {expected_path} because of {error_message}.", ANY
    )


@pytest.mark.parametrize(
    "nested_data, expected_primitive_call_counts, expected_create_record_call_count, expected_results",
    [
        (
            {
                "level1": {
                    "level2": {
                        "property1": {"type": "string", "value": "Hello"},
                        "property2": {"type": "number", "value": 42},
                    },
                    "description": "Level 1 description",
                }
            },
            {"True": 2, "False": 2},
            2,
            [{"mocked": "record"}, {"mocked": "record"}],
        ),
        (
            {
                "level1": {
                    "level2": {
                        "nestedProperty": {
                            "type": "object",
                            "innerProperty": {"type": "string", "value": "Nested", "description": "Deep description"},
                        }
                    },
                    "description": "Level 1 description",
                }
            },
            {"True": 2, "False": 3},
            2,
            [{"mocked": "record"}],
        ),
    ],
)
def test_parse_metadata_properties(
    mock_input_manager: InputManager,
    nested_data: Dict[str, Any],
    expected_primitive_call_counts: Dict[str, int],
    expected_create_record_call_count: int,
    expected_results: List[Dict[str, str]],
) -> None:
    """Tests _parse_metadata_properties() function in InputManager."""

    def side_effect_check_property_type_primitive(value: Any) -> bool:
        """Function to mock check_property_type_primitive dynamically."""
        return value.get("type") in ["string", "number"]

    with (
        patch.object(
            mock_input_manager, "_check_property_type_primitive", side_effect=side_effect_check_property_type_primitive
        ) as mock_primitive,
        patch.object(mock_input_manager, "_create_record", return_value={"mocked": "record"}) as mock_create_record,
    ):
        prefix = ""
        sep = "_"

        result = mock_input_manager._parse_metadata_properties(nested_data, prefix, sep)

        true_count = sum(1 for call in mock_primitive.call_args_list if call[0][0].get("type") in ["string", "number"])
        false_count = len(mock_primitive.call_args_list) - true_count

        assert true_count == expected_primitive_call_counts["True"]
        assert false_count == expected_primitive_call_counts["False"]
        assert mock_create_record.call_count == expected_create_record_call_count
        assert result == expected_results


@pytest.mark.parametrize(
    "property_dict, expected_result",
    [
        # Direct primitive types
        ({"type": "bool"}, True),
        ({"type": "string"}, True),
        ({"type": "number"}, True),
        # Array containing primitive types
        ({"type": "array", "properties": {"type": "bool"}}, True),
        ({"type": "array", "properties": {"type": "string"}}, True),
        ({"type": "array", "properties": {"type": "number"}}, True),
        # Non-primitive type
        ({"type": "object"}, False),
        ({"type": "array", "properties": {"type": "object"}}, False),
        # Invalid or unexpected type cases
        ({"type": "array", "properties": {}}, False),  # Array but properties are empty
        ({"type": "complex"}, False),  # Unsupported type
    ],
)
def test_check_property_type_primitive(
    mock_input_manager: InputManager, property_dict: Dict[str, str], expected_result: bool
) -> None:
    """Tests _check_property_type_primitive() function in InputManager."""
    result = mock_input_manager._check_property_type_primitive(property_dict)
    assert result == expected_result


@pytest.mark.parametrize(
    "data_entry, name, expected_record",
    [
        (
            {
                "type": "string",
                "description": "A simple string",
                "pattern": "[A-Za-z]+",
                "default": "example",
                "maximum": "",
                "minimum": "",
            },
            "user_details_properties_name",
            {
                "properties_group": "user_details_properties",
                "name": "name",
                "type": "string",
                "description": "A simple string",
                "pattern": "[A-Za-z]+",
                "default": "example",
                "maximum": "",
                "minimum": "",
            },
        ),
        (
            {"type": "number", "description": "A simple number"},
            "config_properties_version",
            {
                "properties_group": "config_properties",
                "name": "version",
                "type": "number",
                "description": "A simple number",
                "pattern": "",
                "default": "",
                "maximum": "",
                "minimum": "",
            },
        ),
    ],
)
def test_create_record(
    mock_input_manager: InputManager, data_entry: dict[str, str], name: str, expected_record: dict[str, str]
) -> None:
    """Tests _create_record() function in InputManager."""
    result = mock_input_manager._create_record(data_entry, name)
    assert result == expected_record


@pytest.mark.parametrize(
    "file_exists, error, file_content, modified_properties, expected_diff",
    [
        (
            True,
            None,
            '{"key1": "value1", "key3": "value3"}',
            {"key1": "value1_changed", "key3": "value3"},
            {"values_changed": {"root['key1']": {"old_value": "value1", "new_value": "value1_changed"}}},
        ),
        (
            False,
            OSError,
            '{"key1": "value1", "key3": "value3"}',
            {"key1": "value1_changed", "key3": "value3"},
            {"values_changed": {"root['key1']": {"old_value": "value1", "new_value": "value1_changed"}}},
        ),
        (
            False,
            PermissionError,
            '{"key1": "value1", "key3": "value3"}',
            {"key1": "value1_changed", "key3": "value3"},
            {"values_changed": {"root['key1']": {"old_value": "value1", "new_value": "value1_changed"}}},
        ),
        (True, None, '{"key1": "value1", "key2": "value2"}', {"key1": "value1", "key2": "value2"}, {}),
    ],
)
def test_compare_metadata_properties(
    mocker: MockerFixture,
    file_exists: bool,
    error: Type[PermissionError | OSError],
    file_content: str,
    modified_properties: dict[str, str],
    expected_diff: dict[str, dict[str, str]],
) -> None:
    dummy_properties = {"key1": "value1", "key2": "value2"}
    dummy_properties_modified = modified_properties
    input_manager = InputManager()

    properties_file_path = Path("/fake/dir/original_properties.json")
    comparison_properties_file_path = Path("/fake/dir/comparison_properties.json")
    output_path = Path("path/to/output")

    if file_exists:
        mock_file = mock_open(read_data=file_content)
        mocker.patch("builtins.open", mock_file)
    else:
        mocker.patch("builtins.open", side_effect=error)

    mocker.patch.object(
        input_manager,
        "_load_metadata",
        side_effect=lambda file: setattr(
            input_manager,
            "meta_data",
            dummy_properties_modified if file == comparison_properties_file_path else dummy_properties,
        ),
    )

    mocker.patch("deepdiff.DeepDiff", return_value=expected_diff)

    mock_add_log = mocker.patch("RUFAS.output_manager.OutputManager.add_log")
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_create_directory = mocker.patch("RUFAS.output_manager.OutputManager.create_directory")

    if file_exists:
        input_manager.compare_metadata_properties(properties_file_path, comparison_properties_file_path, output_path)
        mock_file.assert_called()
        mock_add_log.assert_called()
        mock_add_error.assert_not_called()
        mock_create_directory.assert_called()
    else:
        with pytest.raises(error):
            input_manager.compare_metadata_properties(
                properties_file_path, comparison_properties_file_path, output_path
            )
        mock_add_log.assert_called()
        mock_add_error.assert_called()
        mock_create_directory.assert_called()


def test_increment_in_elements_counter() -> None:
    """
    Unit test for the increment() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()

    # Act
    counter.increment(ElementState.VALID)
    counter.increment(ElementState.INVALID)
    counter.increment(ElementState.FIXED)

    # Assert
    assert counter.valid_elements == 1
    assert counter.invalid_elements == 1
    assert counter.fixed_elements == 1
    assert counter.total_elements() == 3


def test_update_increments_correctly() -> None:
    """
    Unit test for the update() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()

    # Act
    counter.update(ElementState.INVALID, 2)
    counter.update(ElementState.VALID, 1)
    counter.update(ElementState.FIXED, 3)

    # Assert
    assert counter.valid_elements == 1
    assert counter.invalid_elements == 2
    assert counter.fixed_elements == 3


def test_update_value_error() -> None:
    """
    Unit test for the update() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()

    # Act
    with pytest.raises(ValueError):
        counter.update("not valid", 2)


def test_reset_method_in_elements_counter() -> None:
    """
    Unit test for the reset() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()
    counter.increment(ElementState.VALID)
    counter.increment(ElementState.INVALID)
    counter.increment(ElementState.FIXED)

    # Assert Before
    assert counter.valid_elements == 1
    assert counter.invalid_elements == 1
    assert counter.fixed_elements == 1

    # Act
    counter.reset()

    # Assert After
    assert counter.valid_elements == 0
    assert counter.invalid_elements == 0
    assert counter.fixed_elements == 0


def test_total_elements_in_elements_counter() -> None:
    """
    Unit test for the total_elements() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()
    counter.increment(ElementState.VALID)
    counter.increment(ElementState.INVALID)
    counter.increment(ElementState.FIXED)
    counter.increment(ElementState.VALID)
    expected_total = 2 + 1 + 1  # 2 valid, 1 invalid, 1 fixed

    # Act
    actual_total = counter.total_elements()

    # Assert
    assert actual_total == expected_total


def test_str_in_elements_counter() -> None:
    """
    Unit test for the __str__ method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()
    counter.valid_elements = 2
    counter.invalid_elements = 1
    counter.fixed_elements = 1
    expected_str = "{'valid_elements': 2, 'invalid_elements': 1, 'fixed_elements': 1, 'total_elements': 4}"

    # Act and Assert
    assert str(counter) == expected_str


def test_add_in_elements_counter() -> None:
    """
    Unit test for the __add__ method of the ElementsCounter class.
    """

    # Arrange
    counter1 = ElementsCounter()
    counter1.valid_elements = 2
    counter1.invalid_elements = 1
    counter1.fixed_elements = 0

    counter2 = ElementsCounter()
    counter2.valid_elements = 1
    counter2.invalid_elements = 1
    counter2.fixed_elements = 2

    # Act
    result_counter = counter1 + counter2

    # Assert result counter values
    assert result_counter.valid_elements == 3
    assert result_counter.invalid_elements == 2
    assert result_counter.fixed_elements == 2
    assert result_counter.total_elements() == 7

    # Assert original counter values
    assert counter1.valid_elements == 2
    assert counter1.invalid_elements == 1
    assert counter1.fixed_elements == 0

    assert counter2.valid_elements == 1
    assert counter2.invalid_elements == 1
    assert counter2.fixed_elements == 2


@pytest.fixture
def mock_metadata_prepare_data() -> dict[Any, Any]:
    return {
        "properties": {
            "example_blob_key": {
                "object_property": {"nested_property": {"type": "string", "description": "An example property"}},
                "example_property": {"type": "string", "description": "An example property"},
            },
            "commodity_prices_blob_key": {
                "fips": {"type": "array", "properties": {"type": "number"}},
                "2003": {"type": "array", "properties": {"type": "number"}},
            },
            "commodity_prices_with_parent_blob_key": {
                "calves_all": {"modifiability": "REQUIRED_AND_LOCKED"},
            },
        }
    }


@pytest.mark.parametrize(
    "variable_name,input_data,properties_blob_key," "expected_data,expected_metadata_properties,is_nested",
    [
        (
            "example_property",
            {"key": "value"},
            "example_blob_key",
            {"key": "value"},
            {
                "example_property": {"description": "An example property", "type": "string"},
                "object_property": {"nested_property": {"description": "An example property", "type": "string"}},
            },
            False,
        ),
        (
            "example_property.object_property.nested_property",
            {"nested_key": "nested_value"},
            "example_blob_key",
            {"object_property": {"nested_property": {"nested_key": "nested_value"}}},
            {"type": "string", "description": "An example property"},
            True,
        ),
        (
            "commodity_prices.calves_all.dollar_per_kilogram",
            {"fips": [1], "2003": [2]},
            "commodity_prices_blob_key",
            {"fips": [1], "2003": [2]},
            {
                "fips": {"properties": {"type": "number"}, "type": "array"},
                "2003": {"properties": {"type": "number"}, "type": "array"},
            },
            False,
        ),
        (
            "commodity_prices.calves_all.dollar_per_kilogram",
            {"fips": [1], "2003": [2]},
            "commodity_prices_with_parent_blob_key",
            {"dollar_per_kilogram": {"fips": [1], "2003": [2]}},
            {"modifiability": "REQUIRED_AND_LOCKED"},
            True,
        ),
    ],
)
def test_prepare_data(
    mock_metadata_prepare_data: dict[Any, Any],
    variable_name: str,
    input_data: dict[Any, Any],
    properties_blob_key: str,
    expected_data: dict[Any, Any],
    expected_metadata_properties: dict[str, Any],
    mocker: MockerFixture,
    is_nested: bool,
) -> None:
    """Unit test for prepare_data to ensure data were extracted correctly"""
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_prepare_data)
    mock_flat_to_nested = mocker.patch.object(
        Utility, "flatten_keys_to_nested_structure", wraps=Utility.flatten_keys_to_nested_structure
    )

    data, metadata_properties = input_manager._prepare_data(variable_name, input_data, properties_blob_key)
    if is_nested:
        mock_flat_to_nested.assert_called_once()
    assert data == expected_data
    assert metadata_properties == expected_metadata_properties


@pytest.mark.parametrize(
    "variable_name,metadata_properties,eager_termination,modifiable",
    [("test", {"test": 12}, False, True)],
)
def test_check_modifiability_valid(
    variable_name: str,
    metadata_properties: dict[Any, Any],
    eager_termination: bool,
    modifiable: bool,
    mocker: MockerFixture,
) -> None:
    """Unit test for _check_modifiability to ensure right warnings or errors were thrown"""
    input_manager = InputManager()
    patch_om_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    patch_om_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")

    mock_modifiable = mocker.patch(
        "RUFAS.input_manager.InputManager._is_modifiable_during_runtime", return_value=modifiable
    )

    result = input_manager._check_modifiability(variable_name, metadata_properties, eager_termination)

    mock_modifiable.assert_called_once_with(variable_name=variable_name, variable_properties=metadata_properties)

    patch_om_error.assert_not_called()
    patch_om_warning.assert_not_called()
    assert result


@pytest.mark.parametrize(
    "variable_name,metadata_properties,eager_termination,modifiable",
    [("test", {"test": 12}, True, False)],
)
def test_check_modifiability_error(
    variable_name: str,
    metadata_properties: dict[Any, Any],
    eager_termination: bool,
    modifiable: bool,
    mocker: MockerFixture,
) -> None:
    """Unit test for _check_modifiability to ensure right errors were thrown"""
    input_manager = InputManager()
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")

    mock_modifiable = mocker.patch(
        "RUFAS.input_manager.InputManager._is_modifiable_during_runtime", return_value=modifiable
    )

    try:
        input_manager._check_modifiability(variable_name, metadata_properties, eager_termination)
    except PermissionError as e:
        mock_modifiable.assert_called_once_with(variable_name=variable_name, variable_properties=metadata_properties)

        mock_add_error.assert_called_once()
        mock_modifiable.assert_called_once_with(variable_name=variable_name, variable_properties=metadata_properties)
        assert e.args[0] == f"IM Runtime Modification Error: {variable_name} is not modifiable during runtime."


@pytest.mark.parametrize(
    "variable_name,metadata_properties,eager_termination,modifiable",
    [("test", {"test": 12}, False, False)],
)
def test_check_modifiability_warning(
    variable_name: str,
    metadata_properties: dict[str, int],
    eager_termination: bool,
    modifiable: bool,
    mocker: MockerFixture,
) -> None:
    """Unit test for _check_modifiability to ensure right warnings were thrown"""
    input_manager = InputManager()
    mock_add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")

    mock_modifiable = mocker.patch(
        "RUFAS.input_manager.InputManager._is_modifiable_during_runtime", return_value=modifiable
    )

    result = input_manager._check_modifiability(variable_name, metadata_properties, eager_termination)
    mock_modifiable.assert_called_once_with(variable_name=variable_name, variable_properties=metadata_properties)
    mock_add_warning.assert_called_once()
    assert not result


@pytest.fixture
def elements_counter() -> ElementsCounter:
    return ElementsCounter()


@pytest.mark.parametrize(
    "data,metadata_properties,eager_termination,properties_blob_key,expected_validated_data,expected_invalid_elements",
    [
        (
            {"prop1": "value1", "prop2": "value2"},
            {"prop1": {"type": "string"}, "prop2": {"type": "string"}},
            False,
            "example_blob_key",
            {"prop1": "value1", "prop2": "value2"},
            0,
        ),
        (
            {"prop1": "value1", "prop2": None},
            {"prop1": {"type": "string"}, "prop2": {"type": "string"}},
            False,
            "example_blob_key",
            {"prop1": "value1"},
            1,
        ),
        (
            {"prop1": None, "prop2": None},
            {"prop1": {"type": "string"}, "prop2": {"type": "string"}},
            False,
            "example_blob_key",
            {},
            2,
        ),
    ],
)
def test_validate_data(
    mocker: MockerFixture,
    elements_counter: ElementsCounter,
    data: dict[str, str],
    metadata_properties: dict[str, Any],
    eager_termination: bool,
    properties_blob_key: str,
    expected_validated_data: dict[str, str],
    expected_invalid_elements: int,
) -> None:
    """Unit test for _validate_data to ensure proper validation"""
    input_manager = InputManager()

    mock_validate_input_by_type = mocker.patch.object(
        DataValidator,
        "validate_data_by_type",
        # fmt: off
        side_effect=lambda variable_path, variable_properties, data, eager_termination, properties_blob_key,
        elements_counter, called_during_initialization, fixable_data_types:
        data.get(variable_path[0]) is not None,
        # fmt: on
    )

    validated_data = input_manager._validate_data(
        data=data,
        metadata_properties=metadata_properties,
        eager_termination=eager_termination,
        properties_blob_key=properties_blob_key,
        elements_counter=elements_counter,
    )

    assert validated_data == expected_validated_data
    assert mock_validate_input_by_type.call_count == 2


@pytest.fixture
def mock_pool_for_add_pool() -> Dict[str, Dict[str, Any]]:
    return {
        "module1": {
            "integer_var": 5,
            "float_var": 0.5,
            "string_var": "dummyvalue1",
            "boolean_var": True,
            "integer_array_var": [1, 2, 3],
            "float_array_var": [0.1, 0.2, 3.14159],
            "string_array_var": ["1", "2", "3", "4", "5"],
            "boolean_array_var": [True, False],
            "submodule1": {"nested_var": "dummyvalue2"},
        },
        "module2": {
            "submodule1": {
                "nested_module1": {
                    "nested_var1": "dummyvalue3",
                    "nested_var2": "dummyvalue4",
                },
            },
        },
    }


@pytest.mark.parametrize("variable_name,validated_data", [("module1", {"test": "random"})])
def test_add_to_pool(
    variable_name: str, validated_data: dict[str, Any], mocker: MockerFixture, mock_pool_for_add_pool: Dict[str, Any]
) -> None:
    """Tests to make sure validated data were added to pool"""
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__pool", mock_pool_for_add_pool)
    mock_add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")
    input_manager._add_to_pool(variable_name, validated_data)
    mock_add_warning.assert_called_once()
    assert input_manager.pool["module1"] == {"test": "random"}


def test_export_pool_to_csv(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Tests export_pool_to_csv() function in InputManager."""
    mock_pool = {"a": {"A": 1}, "b": {"B": 2}, "c": {"C": 3}, "d": {"D": [1, 2, 3]}, "animal_population": {}}
    mock_input_manager.csv_report_generation_list = ["a", "c", "d", "animal_population"]
    mock_input_manager.pool = mock_pool

    output_dir = Path("/fake/directory")

    mock_flatten_dictionary = mocker.patch.object(
        Utility, "flatten_dictionary", side_effect=[{"A": 1}, {"C": 3}, {"D": [1, 2, 3]}]
    )

    mock_create_dir = mocker.patch("RUFAS.output_manager.OutputManager.create_directory")
    mock_add_log = mocker.patch("RUFAS.output_manager.OutputManager.add_log")

    mock_to_csv = mocker.patch("pandas.DataFrame.to_csv")

    mock_input_manager.export_pool_to_csv("dummy_prefix", output_dir)

    mock_flatten_dictionary.assert_has_calls([call({"A": 1}), call({"C": 3}), call({"D": [1, 2, 3]})], any_order=True)
    mock_create_dir.assert_called_once_with(output_dir)
    mock_to_csv.assert_called_once_with(output_dir / "dummy_prefix.csv", index=False)
    mock_add_log.assert_called_once_with(
        "Save input data CSV success.",
        f"Successfully saved to {output_dir}.",
        {
            "class": mock_input_manager.__class__.__name__,
            "function": mock_input_manager.export_pool_to_csv.__name__,
        },
    )


@pytest.mark.parametrize(
    "exception, error_message",
    [(FileNotFoundError, "No such file or directory"), (PermissionError, "Permission denied"), (OSError, "OS error")],
)
def test_export_pool_to_csv_errors(
    mock_input_manager: InputManager,
    mocker: MockerFixture,
    exception: Type[FileNotFoundError | PermissionError | OSError],
    error_message: str,
) -> None:
    """Tests all the possible errors in export_pool_to_csv() function of InputManager."""
    mock_pool = {"a": {"A": 1}, "b": {"B": 2}, "c": {"C": 3}, "d": {"D": [1, 2, 3]}, "animal_population": {}}
    mock_input_manager.csv_report_generation_list = ["a", "c", "d"]
    mock_input_manager.pool = mock_pool

    output_dir = Path("/fake/directory")

    mocker.patch.object(Utility, "flatten_dictionary")
    mocker.patch("RUFAS.output_manager.OutputManager.create_directory")
    mocker.patch("pandas.DataFrame.to_csv", side_effect=exception(error_message))
    mock_add_error = mocker.patch.object(mock_input_manager.om, "add_error")

    with pytest.raises(exception) as exc_info:
        mock_input_manager.export_pool_to_csv("dummy_prefix", output_dir)

    assert str(exc_info.value) == error_message

    mock_add_error.assert_called_once_with(
        "Save CSV failure.", f"Unable to save to {output_dir} because of {error_message}.", ANY
    )


def x_test_load_runtime_metadata_success(
    mock_input_manager: InputManager, mocker: MockerFixture, tmp_path: Path
) -> None:
    # TODO issue #2691
    runtime_metadata = {
        "files": {
            "commodity_prices.calves_all.dollar_per_kilogram": {
                "path": str(tmp_path / "commodity_prices.calves_all.dollar_per_kilogram.csv"),
                "type": "csv",
                "properties": "commodity_prices_calves_all_dollar_per_kilogram_csv_properties",
            }
        }
    }
    runtime_metadata_path = tmp_path / "econ_metadata.json"
    runtime_metadata_path.write_text(json.dumps(runtime_metadata))
    (tmp_path / "commodity_prices.calves_all.dollar_per_kilogram.csv").write_text("value\n1\n")

    mock_input_manager._InputManager__metadata = {
        "properties": {
            "commodity_prices_calves_all_dollar_per_kilogram_csv_properties": {},
        },
        "runtime_metadata": {"EEE_econ": {"path": str(runtime_metadata_path)}},
    }

    mocked_validate = mocker.patch.object(
        mock_input_manager.data_validator, "validate_metadata", return_value=(True, "")
    )
    mocked_loader = mocker.patch.object(mock_input_manager, "_load_data_from_csv", return_value={"value": [1]})
    mocked_add = mocker.patch.object(mock_input_manager, "add_runtime_variable_to_pool", return_value=True)
    metadata_exists_spy = mocker.spy(mock_input_manager, "_metadata_properties_exist")

    assert mock_input_manager.load_runtime_metadata("EEE_econ", eager_termination=True)

    mocked_validate.assert_called_once_with(runtime_metadata, VALID_INPUT_TYPES, ADDRESS_TO_INPUTS)
    mocked_loader.assert_called_once_with(tmp_path / "commodity_prices.calves_all.dollar_per_kilogram.csv")
    mocked_add.assert_called_once_with(
        variable_name="commodity_prices.calves_all.dollar_per_kilogram",
        data={"value": [1]},
        properties_blob_key="commodity_prices_calves_all_dollar_per_kilogram_csv_properties",
        eager_termination=True,
    )
    metadata_exists_spy.assert_called_once_with(
        "commodity_prices.calves_all.dollar_per_kilogram",
        "commodity_prices_calves_all_dollar_per_kilogram_csv_properties",
    )
    assert mock_input_manager._InputManager__metadata["runtime_metadata"] == {
        "EEE_econ": {"path": str(runtime_metadata_path)}
    }


def test_load_runtime_metadata_invalid_key(mock_input_manager: InputManager) -> None:
    mock_input_manager._InputManager__metadata = {
        "properties": {},
        "runtime_metadata": {},
    }

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        assert not mock_input_manager.load_runtime_metadata("EEE_econ", eager_termination=True)

    add_error.assert_called()


def test_load_runtime_metadata_missing_configuration(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    mock_input_manager._InputManager__metadata = {
        "properties": {},
    }

    get_metadata_spy = mocker.spy(mock_input_manager, "get_metadata")

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        assert not mock_input_manager.load_runtime_metadata("EEE_econ", eager_termination=True)

    get_metadata_spy.assert_called_once_with("runtime_metadata")
    assert add_error.call_args_list[-1] == call(
        "Runtime metadata load failure",
        "Runtime metadata configuration could not be resolved from the active metadata document.",
        {"class": "InputManager", "function": "load_runtime_metadata"},
    )


def test_load_runtime_metadata_missing_path(mock_input_manager: InputManager) -> None:
    mock_input_manager._InputManager__metadata = {
        "properties": {},
        "runtime_metadata": {"EEE_econ": {}},
    }

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        assert not mock_input_manager.load_runtime_metadata("EEE_econ", eager_termination=True)

    assert add_error.call_count >= 1


def test_load_runtime_metadata_invalid_metadata(
    mock_input_manager: InputManager, mocker: MockerFixture, tmp_path: Path
) -> None:
    runtime_metadata = {
        "files": {
            "commodity_prices.calves_all.dollar_per_kilogram": {
                "path": str(tmp_path / "commodity_prices.calves_all.dollar_per_kilogram.csv"),
                "type": "csv",
                "properties": "commodity_prices_calves_all_dollar_per_kilogram_csv_properties",
            }
        }
    }
    runtime_metadata_path = tmp_path / "econ_metadata.json"
    runtime_metadata_path.write_text(json.dumps(runtime_metadata))
    (tmp_path / "commodity_prices.calves_all.dollar_per_kilogram.csv").write_text("value\n1\n")

    mock_input_manager._InputManager__metadata = {
        "properties": {},
        "runtime_metadata": {"EEE_econ": {"path": str(runtime_metadata_path)}},
    }

    mocker.patch.object(mock_input_manager.data_validator, "validate_metadata", return_value=(False, "boom"))

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        assert not mock_input_manager.load_runtime_metadata("EEE_econ", eager_termination=True)

    add_error.assert_called_with(
        "Runtime metadata load failure",
        f"Runtime metadata document at '{runtime_metadata_path}' failed validation.",
        {"class": "InputManager", "function": "load_runtime_metadata"},
    )


def test_load_runtime_metadata_eager_termination_stops_processing(
    mock_input_manager: InputManager, mocker: MockerFixture
) -> None:
    mocker.patch.object(mock_input_manager, "_is_metadata_loaded", return_value=True)
    mocker.patch.object(mock_input_manager, "_get_runtime_metadata_map", return_value={})
    mocker.patch.object(
        mock_input_manager,
        "_resolve_runtime_metadata_files",
        return_value={"var_a": {}, "var_b": {}},
    )
    mocker.patch.object(mock_input_manager, "_runtime_data_loader_map", return_value={})
    process_runtime_file = mocker.patch.object(
        mock_input_manager,
        "_process_runtime_file",
        side_effect=[False, True],
    )

    assert not mock_input_manager.load_runtime_metadata("EEE_econ", eager_termination=True)
    process_runtime_file.assert_called_once_with(
        "var_a", {}, {}, True, {"class": "InputManager", "function": "load_runtime_metadata"}
    )


def test_load_runtime_metadata_non_eager_processes_all(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    mocker.patch.object(mock_input_manager, "_is_metadata_loaded", return_value=True)
    mocker.patch.object(mock_input_manager, "_get_runtime_metadata_map", return_value={})
    runtime_files = {"var_a": {}, "var_b": {}}
    mocker.patch.object(
        mock_input_manager,
        "_resolve_runtime_metadata_files",
        return_value=runtime_files,
    )
    mocker.patch.object(mock_input_manager, "_runtime_data_loader_map", return_value={})
    process_runtime_file = mocker.patch.object(
        mock_input_manager,
        "_process_runtime_file",
        side_effect=[False, True],
    )

    assert not mock_input_manager.load_runtime_metadata("EEE_econ", eager_termination=False)
    assert process_runtime_file.call_args_list == [
        call("var_a", {}, {}, False, {"class": "InputManager", "function": "load_runtime_metadata"}),
        call("var_b", {}, {}, False, {"class": "InputManager", "function": "load_runtime_metadata"}),
    ]


@pytest.fixture
def simple_pool_and_meta() -> tuple[dict[Any, Any], dict[Any, Any]]:
    pool = {"a": 1, "b": 2, "c": {"nested": {"level1": 3, "another": 4}}}

    metadata = {
        "files": {
            "a": {"properties": "blob_a", "type": "json", "path": "data/a.json"},
            "b": {"properties": "blob_b", "type": "csv", "delimiter": ","},
            "c": {
                "properties": "blob_c",
                "type": "json",
                "versions": {"v1": "2021-01", "v2": "2022-02"},
                "schema": {"required": ["x", "y"], "optional": ["z"]},
            },
        },
        "properties": {
            "blob_a": {"format": "json", "description": "first blob"},
            "blob_b": {"format": "csv", "has_header": True},
            "blob_c": {
                "format": "json",
                "complex": True,
                "nested": {
                    "level1": {"properties": "blob_level1", "type": "number"},
                    "another": {"properties": "blob_another", "type": "number"},
                },
            },
        },
    }

    return pool, metadata


def test_delete_data_with_valid_key(
    simple_pool_and_meta: tuple[dict[Any, Any], dict[Any, Any]], mocker: MockerFixture
) -> None:
    """delete_data should remove both data and its metadata and return True."""
    pool, metadata = simple_pool_and_meta

    im = InputManager()
    im.pool = pool
    im.meta_data = metadata
    mocker.patch.object(im.data_validator, "extract_value_by_key_list", return_value=pool["c"]["nested"])

    data_delete, metadata_delete = im._InputManager__delete_input_and_metadata("c.nested.level1")

    assert data_delete
    assert metadata_delete
    assert "level1" not in im.pool["c"]["nested"]
    assert "level1" not in im.meta_data["properties"]["blob_c"]["nested"]


def test_delete_data_with_invalid_data_address(
    simple_pool_and_meta: tuple[dict[Any, Any], dict[Any, Any]], mocker: MockerFixture
) -> None:
    """delete_data should return False and log a data-not-found error when key is invalid."""
    pool, metadata = simple_pool_and_meta

    im = InputManager()
    im.pool = pool.copy()
    im.meta_data = metadata.copy()
    mocker.patch.object(im.data_validator, "extract_value_by_key_list", side_effect=KeyError("missing"))
    mock_add_error = mocker.patch.object(im.om, "add_error", autospec=True)

    data_delete, metadata_delete = im._InputManager__delete_input_and_metadata("c.nested.unknown")

    assert not data_delete
    assert metadata_delete
    assert pool["c"]["nested"]["level1"] == 3
    blob_key = metadata["files"]["c"]["properties"]
    assert "level1" in metadata["properties"][blob_key]["nested"]
    mock_add_error.assert_called_once()
    args, kwargs = mock_add_error.call_args
    assert "Validation: data not found" in args[0]


def test_delete_data_metadata_not_found(
    simple_pool_and_meta: tuple[dict[Any, Any], dict[Any, Any]], mocker: MockerFixture
) -> None:
    """delete_data should remove data, return True, but log metadata-not-found if metadata path missing."""
    pool, metadata = simple_pool_and_meta

    im = InputManager()
    im.pool = pool
    im.meta_data = metadata

    blob_key = metadata["files"]["c"]["properties"]
    metadata["properties"][blob_key].pop("nested", None)

    mocker.patch.object(im.data_validator, "extract_value_by_key_list", return_value=pool["c"]["nested"])
    mock_add_error = mocker.patch.object(im.om, "add_error", autospec=True)

    data_delete, metadata_delete = im._InputManager__delete_input_and_metadata("c.nested.another")

    assert data_delete
    assert not metadata_delete

    mock_add_error.assert_called_once()
    args, kwargs = mock_add_error.call_args
    assert args[0] == "Validation: metadata not found"


def test_extract_target_and_save_block(mocker: MockerFixture) -> None:
    """Tests the function to extract the target and save block."""
    im = InputManager()
    mock_check = mocker.patch.object(CrossValidator, "check_target_and_save_block")
    mock_get_data = mocker.patch.object(im, "get_data", return_value=1)
    result = im._extract_target_and_save_block(
        {"variables": {"a": "test.address.1", "b": "test.address.2"}, "constants": {"c": "value"}}, True
    )

    assert result == {"a": 1, "b": 1, "c": "value"}
    mock_check.assert_called_once()
    assert mock_get_data.call_count == 2
