import csv
import io
import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from RUFAS.post_processing.file_manager import DISCLAIMER_MESSAGE, FileManager, OriginLabel
from RUFAS.util import Utility

MODULE = "RUFAS.post_processing.file_manager"


@pytest.fixture
def file_manager() -> FileManager:
    """Create a FileManager with test metadata and supported prefixes."""
    return FileManager("test_run", {"report": "report_"})


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MagicMock:
    """Mock the module-level logger."""
    return mocker.patch(f"{MODULE}.logger")


def test_init(file_manager: FileManager) -> None:
    """Test initialization of metadata and supported filter prefixes."""
    assert file_manager.metadata_prefix == "test_run"
    assert file_manager.supported_filter_types_prefixes == {"report": "report_"}


@pytest.mark.parametrize("minify", [False, True])
def test_dict_to_file_json(
    file_manager: FileManager,
    tmp_path: Path,
    mocker: MockerFixture,
    mock_logger: MagicMock,
    minify: bool,
) -> None:
    """Test JSON formatting, serialization, disclaimer, and logging."""
    path = tmp_path / "output.json"
    data = {"temperature": [1, 2], "units": "°C"}
    expected = {"DISCLAIMER": DISCLAIMER_MESSAGE, **data}
    serialize = mocker.patch.object(Utility, "make_serializable", side_effect=lambda data, **kwargs: data)
    file_manager.dict_to_file_json(data, path, minify_output_file=minify)
    text = path.read_text(encoding="utf-8")
    assert json.loads(text) == expected
    if minify:
        assert text == json.dumps(expected, ensure_ascii=False, separators=(",", ":"))
    else:
        assert text == json.dumps(expected, ensure_ascii=False, indent=2)
    serialize.assert_called_once_with(expected, max_depth=FileManager.JSON_OUTPUT_MAX_RECURSIVE_DEPTH)
    assert "DISCLAIMER" not in data
    assert mock_logger.info.call_count == 2


def test_dict_to_file_json_origin(file_manager: FileManager, tmp_path: Path, mocker: MockerFixture) -> None:
    """Test inclusion of detailed origin information in JSON output."""
    mocker.patch.object(Utility, "make_serializable", side_effect=lambda data, **kwargs: data)
    path = tmp_path / "output.json"
    data = {"report": {"values": [3], "info_maps": [{"data_origin": [["Cow", "update"]], "units": "kg"}]}}
    file_manager.dict_to_file_json(data, path, origin_label=OriginLabel.TRUE_ORIGIN)
    assert json.loads(path.read_text())["report"]["detailed_values"] == ["[Cow.update]: 3 (kg)"]


@pytest.mark.parametrize("method, data", [("dict_to_file_json", {}), ("_list_to_file_txt", [])])
@pytest.mark.parametrize("error_type", [PermissionError, OSError])
def test_write_failure(
    file_manager: FileManager,
    tmp_path: Path,
    mocker: MockerFixture,
    method: str,
    data: dict[str, Any] | list[str],
    error_type: type[OSError],
) -> None:
    """Test that write failures preserve the exception type and cause."""
    path = tmp_path / "output"
    error = error_type("write failed")
    mocker.patch(f"{MODULE}.open", side_effect=error, create=True)
    with pytest.raises(error_type, match="An error occurred while saving to") as exc:
        getattr(file_manager, method)(data, path)
    assert str(path) in str(exc.value)
    assert exc.value.__cause__ is error


@pytest.mark.parametrize("label, prefix", [
    (OriginLabel.TRUE_AND_REPORT_ORIGINS, "[Cow.update]->[Reporter.value]: "),
    (OriginLabel.TRUE_ORIGIN, "[Cow.update]: "),
    (OriginLabel.REPORT_ORIGIN, "[Reporter.value]: "),
    (OriginLabel.NONE, ""),
])
@pytest.mark.parametrize("value, units, suffix", [
    (3, "kg", "3 (kg)"),
    ({"min": 1, "max": 3}, {"min": "kg", "max": "kg"}, "min = 1 (kg), max = 3 (kg)"),
    (None, "kg", "None (kg)"),
])
def test_format_detailed_value_str(
    file_manager: FileManager,
    label: OriginLabel,
    prefix: str,
    value: Any,
    units: str | dict[str, str] | None,
    suffix: str,
) -> None:
    """Test formatting of scalar and dictionary values for each origin label."""
    data = {"true_origin_class": "Cow", "true_origin_function": "update", "report_origin": "Reporter.value",
            "value": value, "units": units}
    assert file_manager._format_detailed_value_str(label, data) == prefix + suffix


@pytest.mark.parametrize("data, expected", [
    (None, False), ([], False), ("text", False), ({}, False),
    ({"values": [1]}, False), ({"info_maps": [{}]}, False),
    ({"info_maps": [], "values": [1]}, False),
    ({"info_maps": [{}], "values": []}, False),
    ({"info_maps": [{}], "values": [1, 2]}, False),
    ({"info_maps": [{}], "values": [0]}, True),
    ({"info_maps": [{}], "values": [None]}, True),
])
def test_can_add_detailed_values(file_manager: FileManager, data: Any, expected: bool) -> None:
    """Test validation of data structures for detailed value generation."""
    assert file_manager._can_add_detailed_values(data) is expected


@pytest.mark.parametrize("label, expected", [
    (OriginLabel.NONE, None),
    (OriginLabel.TRUE_ORIGIN, ["[Cow.update]: 3 (kg)", "[Herd.update]: 3 (kg)", "[Cow.update]: 4 (kg)"]),
    (OriginLabel.REPORT_ORIGIN, ["[report]: 3 (kg)", "[report]: 3 (kg)", "[report]: 4 (kg)"]),
    (OriginLabel.TRUE_AND_REPORT_ORIGINS, ["[Cow.update]->[report]: 3 (kg)",
                                          "[Herd.update]->[report]: 3 (kg)", "[Cow.update]->[report]: 4 (kg)"]),
])
def test_add_detailed_values(file_manager: FileManager, label: OriginLabel, expected: list[str] | None) -> None:
    """Test detailed values for multiple origins without removing original values."""
    data = {"report": {"values": [3, 4], "info_maps": [
        {"data_origin": [["Cow", "update"], ["Herd", "update"]], "units": "kg"},
        {"data_origin": [["Cow", "update"]], "units": "kg"},
    ]}, "unrelated": "text"}
    result = file_manager._add_detailed_values(data, label)
    assert result is data
    assert result["report"].get("detailed_values") == expected
    assert result["report"]["values"] == [3, 4]
    assert result["unrelated"] == "text"


@pytest.mark.parametrize("info_map", [{}, {"units": "kg"}, {"data_origin": [["Cow", "update"]]}])
def test_add_detailed_values_missing_metadata(file_manager: FileManager, info_map: dict[str, Any]) -> None:
    """Test that incomplete metadata is skipped without affecting valid data."""
    data = {"bad": {"values": [1], "info_maps": [info_map]},
            "good": {"values": [2], "info_maps": [{"data_origin": [["Cow", "update"]], "units": "kg"}]}}
    result = file_manager._add_detailed_values(data, OriginLabel.TRUE_ORIGIN)
    assert "detailed_values" not in result["bad"]
    assert result["good"]["detailed_values"] == ["[Cow.update]: 2 (kg)"]


@pytest.mark.parametrize("units, subkey, expected, error", [
    (None, None, "", None), ("", None, "", None), ("kg", None, " (kg)", None),
    ({"weight": "kg", "min": "g"}, "min", " (kg)", None),
    ({"min": "g"}, "min", " (g)", None),
    ({"min": "g"}, None, "", "Units Subkey Missing"),
    ({"min": "g"}, "max", "", "Units Key Error"),
])
def test_get_units_substr(
    file_manager: FileManager,
    mock_logger: MagicMock,
    units: str | dict[str, str] | None,
    subkey: str | None,
    expected: str,
    error: str | None,
) -> None:
    """Test unit suffix formatting and logging for missing unit keys."""
    assert file_manager._get_units_substr("weight", units, subkey) == expected
    if error:
        mock_logger.error.assert_called_once()
        assert mock_logger.error.call_args.kwargs["extra"]["rufas_log_name"] == error
    else:
        mock_logger.error.assert_not_called()


@pytest.mark.parametrize("data, expected", [
    ({"values": [1, None, 3], "info_maps": [{"units": "kg"}]}, [("weight (kg)", [1, None, 3])]),
    ({"values": [1, 2]}, [("weight", [1, 2])]),
    ({"values": [], "info_maps": []}, [("weight", [])]),
    ({"values": [{"min": 1, "max": 3}, {"min": 2, "max": 4}],
      "info_maps": [{"units": {"min": "kg", "max": "kg"}}]},
     [("weight.min (kg)", [1, 2]), ("weight.max (kg)", [3, 4])]),
    ({"values": [{"min": 1, "max": 3}], "info_maps": [{"units": "kg"}]},
     [("weight.min (kg)", [1]), ("weight.max (kg)", [3])]),
])
def test_dict_to_csv_column_list(
    file_manager: FileManager,
    data: dict[str, list[Any]],
    expected: list[tuple[str, list[Any]]],
) -> None:
    """Test conversion of scalar and dictionary values into named CSV columns."""
    result = file_manager._dict_to_csv_column_list("weight", data)
    assert len(result) == len(expected)
    for series, (name, values) in zip(result, expected):
        pd.testing.assert_series_equal(series, pd.Series(values, dtype=object, name=name))


@pytest.mark.parametrize("direction", ["portrait", None, "landscape", "invalid"])
def test_dict_to_file_csv(
    file_manager: FileManager,
    tmp_path: Path,
    mock_logger: MagicMock,
    direction: str | None,
) -> None:
    """Test CSV orientations, unequal column lengths, and invalid direction fallback."""
    path = tmp_path / "output.csv"
    data = {"weight": {"values": [1, 2], "info_maps": [{"units": "kg"}]},
            "count": {"values": [3]}}
    file_manager.dict_to_file_csv(data, path, direction)
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))
    if direction == "landscape":
        assert rows == [["", "0", "1"], ["DISCLAIMER", DISCLAIMER_MESSAGE, ""],
                        ["weight (kg)", "1", "2"], ["count", "3", ""]]
    else:
        assert rows == [["DISCLAIMER", "weight (kg)", "count"], [DISCLAIMER_MESSAGE, "1", "3"], ["", "2", ""]]
    if direction == "invalid":
        mock_logger.error.assert_called_once()
        assert mock_logger.error.call_args.kwargs["extra"]["rufas_log_name"] == "Unknown Direction for CSV Output"
    else:
        mock_logger.error.assert_not_called()


def test_dict_to_file_csv_empty(file_manager: FileManager, tmp_path: Path, mock_logger: MagicMock) -> None:
    """Test that empty data produces a warning without creating a CSV file."""
    path = tmp_path / "output.csv"
    file_manager.dict_to_file_csv({}, path)
    assert not path.exists()
    mock_logger.warning.assert_called_once()


def test_write_disclaimer(file_manager: FileManager) -> None:
    """Test that the disclaimer is written with a trailing newline."""
    stream = io.StringIO()
    file_manager._write_disclaimer(stream)
    assert stream.getvalue() == DISCLAIMER_MESSAGE + "\n"


@pytest.mark.parametrize("lines", [[], ["first\n", "second\n"], ["first", "second"]])
def test_list_to_file_txt(file_manager: FileManager, tmp_path: Path, lines: list[str]) -> None:
    """Test writing text lines and the disclaimer to a file."""
    path = tmp_path / "output.txt"
    file_manager._list_to_file_txt(lines, path)
    assert path.read_text() == DISCLAIMER_MESSAGE + "\n" + "".join(lines)


@pytest.mark.parametrize("include_millis", [True, False])
def test_generate_file_name(file_manager: FileManager, mocker: MockerFixture, include_millis: bool) -> None:
    """Test timestamped file naming and millisecond option forwarding."""
    timestamp = mocker.patch.object(Utility, "get_timestamp", return_value="timestamp")
    assert file_manager.generate_file_name("report", "json", include_millis) == "test_run_report_timestamp.json"
    timestamp.assert_called_once_with(include_millis=include_millis)


@pytest.mark.parametrize("content, expected", [
    ({"filters": ["a"]}, ([{"filters": ["a"]}], None)),
    ({"filters": ["a"], "direction": "landscape"}, ([{"filters": ["a"], "direction": "landscape"}], "landscape")),
    ({"multiple": [{"filters": ["a"]}, {"filters": ["b"]}], "direction": "portrait"},
     ([{"filters": ["a"]}, {"filters": ["b"]}], "portrait")),
    ({"multiple": []}, ([], None)),
])
def test_load_filter_file_content_json(
    file_manager: FileManager,
    tmp_path: Path,
    content: dict[str, Any],
    expected: tuple[list[dict[str, Any]], str | None],
) -> None:
    """Test loading single and multiple JSON filters with optional direction."""
    path = tmp_path / "filter.json"
    path.write_text(json.dumps(content))
    assert file_manager.load_filter_file_content(path) == expected


@pytest.mark.parametrize("content, filters, exclude", [
    ("a\n\nb\n", ["a", "b"], False), ("exclude\na\nb\n", ["a", "b"], True),
    ("exclude\n", [], True), ("a\nexclude\n", ["a", "exclude"], False),
])
def test_load_filter_file_content_txt(
    file_manager: FileManager,
    tmp_path: Path,
    content: str,
    filters: list[str],
    exclude: bool,
) -> None:
    """Test text filter loading and exclusion marker handling."""
    path = tmp_path / "filter.txt"
    path.write_text(content)
    assert file_manager.load_filter_file_content(path) == ([{"filters": filters, "filter_by_exclusion": exclude}], None)


@pytest.mark.parametrize("filename, content, error, log_name", [
    ("missing.json", None, FileNotFoundError, "Filter File Not Found Error"),
    ("bad.json", b"{", json.JSONDecodeError, "Filter File JSON Parsing Error"),
    ("bad.txt", b"\xff", UnicodeDecodeError, "Filter File Text Decoding Error"),
    ("bad.csv", b"a,b", Exception, "Filter File Unexpected Error"),
])
def test_load_filter_file_content_errors(
    file_manager: FileManager,
    tmp_path: Path,
    mock_logger: MagicMock,
    filename: str,
    content: bytes | None,
    error: type[Exception],
    log_name: str,
) -> None:
    """Test that filter loading errors are logged and propagated."""
    path = tmp_path / filename
    if content is not None:
        path.write_bytes(content)
    with pytest.raises(error):
        file_manager.load_filter_file_content(path)
    mock_logger.error.assert_called_once()
    assert mock_logger.error.call_args.kwargs["extra"]["rufas_log_name"] == log_name


@pytest.mark.parametrize("filter_file, content, base_name", [
    ("e2e_comparison.json", {"name": "Animal"}, "comparison_Animal"),
    ("report.json", {"name": "Milk", "origin_label": "true origin"}, "saved_variables_Milk"),
    ("report.json", {}, "saved_variables_report.json"),
])
def test_save_to_json(
    file_manager: FileManager,
    tmp_path: Path,
    mocker: MockerFixture,
    filter_file: str,
    content: dict[str, str | int],
    base_name: str,
) -> None:
    """Test output naming and origin label forwarding when saving filtered data."""
    generate = mocker.patch.object(file_manager, "generate_file_name", return_value="output.json")
    write = mocker.patch.object(file_manager, "dict_to_file_json")
    pool = {"variable": {"values": [1]}}
    file_manager.save_to_json(filter_file, tmp_path, pool, content)
    generate.assert_called_once_with(base_name, "json")
    write.assert_called_once_with(pool, tmp_path / "output.json", origin_label=OriginLabel(content.get("origin_label", "none")))


@pytest.mark.parametrize("disclaimer", [True, False])
def test_read_variables_pool_file(file_manager: FileManager, tmp_path: Path, disclaimer: bool) -> None:
    """Test loading pool data with or without a disclaimer."""
    path = tmp_path / "pool.json"
    pool = {"variable": [1, 2]}
    path.write_text(json.dumps({**pool, **({"DISCLAIMER": DISCLAIMER_MESSAGE} if disclaimer else {})}))
    assert file_manager.read_variables_pool_file(path) == pool


@pytest.mark.parametrize("exists, error, log_name", [
    (False, FileNotFoundError, "Pool File Not Found Error"),
    (True, json.JSONDecodeError, "JSON Pool File Parsing Error"),
])
def test_read_variables_pool_file_errors(
    file_manager: FileManager,
    tmp_path: Path,
    mock_logger: MagicMock,
    exists: bool,
    error: type[Exception],
    log_name: str,
) -> None:
    """Test logging and propagation of missing or malformed pool file errors."""
    path = tmp_path / "pool.json"
    if exists:
        path.write_text("{")
    with pytest.raises(error):
        file_manager.read_variables_pool_file(path)
    assert mock_logger.error.call_args.kwargs["extra"]["rufas_log_name"] == log_name


@pytest.mark.parametrize("relative_path, expected", [
    ("output", True), ("output/file.json", True), ("output/nested/file.json", True),
    ("other/file.json", False), ("output_backup/file.json", False),
    ("output/../other/file.json", False), (None, False),
])
def test_is_file_in_dir(file_manager: FileManager, tmp_path: Path, relative_path: str | None, expected: bool) -> None:
    """Test directory containment for nested, sibling, and absent paths."""
    path = tmp_path / relative_path if relative_path is not None else None
    assert file_manager.is_file_in_dir(tmp_path / "output", path) is expected


@pytest.mark.parametrize("inside", [True, False])
def test_clear_output_dir(
    file_manager: FileManager,
    tmp_path: Path,
    mocker: MockerFixture,
    mock_logger: MagicMock,
    inside: bool,
) -> None:
    """Test output clearing while protecting the input file and preserved entries."""
    output = tmp_path / "output"
    path = (output if inside else tmp_path) / "pool.json"
    empty = mocker.patch.object(Utility, "empty_dir")
    file_manager.clear_output_dir(path, output)
    if inside:
        empty.assert_not_called()
        mock_logger.error.assert_called_once()
    else:
        empty.assert_called_once_with(output, keep=[".keep", "output_filters"])
        mock_logger.error.assert_not_called()


def test_create_directory(file_manager: FileManager, tmp_path: Path) -> None:
    """Test nested directory creation and repeated creation of an existing directory."""
    path = tmp_path / "nested" / "output"
    file_manager.create_directory(path)
    assert path.is_dir()
    file_manager.create_directory(path)
    assert path.is_dir()


@pytest.mark.parametrize("error, log_name", [
    (PermissionError("denied"), "Directory Creation Permissions Error"),
    (OSError("failed"), "Directory Creation mkdir Error"),
])
def test_create_directory_errors(
    file_manager: FileManager,
    tmp_path: Path,
    mocker: MockerFixture,
    mock_logger: MagicMock,
    error: Exception,
    log_name: str,
) -> None:
    """Test logging of directory creation failures."""
    mkdir = mocker.patch.object(Path, "mkdir", side_effect=error)
    file_manager.create_directory(tmp_path / "output")
    mkdir.assert_called_once_with(parents=True, exist_ok=True)
    assert mock_logger.error.call_args.kwargs["extra"]["rufas_log_name"] == log_name


@pytest.mark.parametrize("label", list(OriginLabel))
def test_get_origin_label_valid(file_manager: FileManager, mock_logger: MagicMock, label: OriginLabel) -> None:
    """Test conversion of supported origin label strings to enum members."""
    assert file_manager._get_origin_label({"origin_label": label.value}) is label
    mock_logger.error.assert_not_called()


def test_get_origin_label_missing(file_manager: FileManager, mock_logger: MagicMock) -> None:
    """Test that an omitted origin label defaults to NONE without logging an error."""
    assert file_manager._get_origin_label({}) is OriginLabel.NONE
    mock_logger.error.assert_not_called()


@pytest.mark.parametrize("value", [1, None, "invalid", "TRUE ORIGIN", ""])
def test_get_origin_label_invalid(file_manager: FileManager, mock_logger: MagicMock, value: Any) -> None:
    """Test that invalid origin labels default to NONE and log an error."""
    assert file_manager._get_origin_label({"origin_label": value}) is OriginLabel.NONE
    mock_logger.error.assert_called_once()


@pytest.mark.parametrize("key, expected", [
    ("animal.value", "Animal"), ("ANIMAL.value", "Animal"), ("crop_and_soil.value", "CropAndSoil"),
    ("CROP_AND_SOIL.value", "CropAndSoil"), ("manure.value", "Manure"), ("Manure", "Manure"),
    ("Feed.value", "Feed"), ("feed.value", "feed"), ("Unknown.a.b", "Unknown"), ("", ""),
])
def test_normalize_module_header(key: str, expected: str) -> None:
    """Test normalization of known module names and preservation of unknown names."""
    assert FileManager.normalize_module_header(key) == expected


def test_read_e2e_comparison_files(file_manager: FileManager, tmp_path: Path, mock_logger: MagicMock) -> None:
    """Test grouping of comparison files by case-insensitive output prefix."""
    files = {"FREESTALL_comparison_Animal.json": {"animal.pass": True},
             "freestall_COMPARISON_Feed.json": {"Feed.pass": False},
             "open_lot_comparison_Animal.json": {"animal.pass": False},
             "unknown_comparison.json": {}, "freestall_output.json": {}, "freestall_comparison.txt": {}}
    for name, data in files.items():
        (tmp_path / name).write_text(json.dumps(data))
    result = file_manager.read_e2e_comparison_files(tmp_path, ["freestall", "open_lot"])
    assert set(result) == {"freestall", "open_lot"}
    assert len(result["freestall"]) == 2
    assert {"animal.pass": True} in result["freestall"]
    assert {"Feed.pass": False} in result["freestall"]
    assert result["open_lot"] == [{"animal.pass": False}]
    mock_logger.error.assert_called_once()
    assert mock_logger.error.call_args.kwargs["extra"]["rufas_log_name"] == "Invalid E2E Output Prefix"


@pytest.mark.parametrize("failed", [None, [], ["open_lot"]])
def test_read_e2e_comparison_files_failed_groups(
    file_manager: FileManager,
    tmp_path: Path,
    mock_logger: MagicMock,
    failed: list[str] | None,
) -> None:
    """Test exclusion of stale comparison files from failed E2E groups."""
    (tmp_path / "open_lot_comparison.json").write_text('{"pass": false}')
    (tmp_path / "freestall_comparison.json").write_text('{"pass": true}')
    result = file_manager.read_e2e_comparison_files(tmp_path, ["open_lot", "freestall"], failed)
    expected = {"freestall": [{"pass": True}]}
    if not failed:
        expected["open_lot"] = [{"pass": False}]
    assert result == expected
    mock_logger.error.assert_not_called()


def test_read_e2e_comparison_files_read_errors(
    file_manager: FileManager,
    tmp_path: Path,
    mock_logger: MagicMock,
) -> None:
    """Test that unreadable comparison files are logged and skipped."""
    (tmp_path / "run_comparison_bad.json").write_text("{")
    (tmp_path / "run_comparison_directory.json").mkdir()
    (tmp_path / "run_comparison_good.json").write_text('{"pass": true}')
    assert file_manager.read_e2e_comparison_files(tmp_path, ["run"]) == {"run": [{"pass": True}]}
    assert mock_logger.error.call_count == 2
    for call in mock_logger.error.call_args_list:
        assert call.kwargs["extra"]["rufas_log_name"] == "E2E Comparison File Reading Error"


def test_read_e2e_comparison_files_empty(file_manager: FileManager, tmp_path: Path, mock_logger: MagicMock) -> None:
    """Test that an empty comparison directory returns no results."""
    assert file_manager.read_e2e_comparison_files(tmp_path, ["run"]) == {}
    mock_logger.error.assert_not_called()


def test_read_e2e_comparison_files_missing_directory(file_manager: FileManager, tmp_path: Path) -> None:
    """Test that a missing comparison directory raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        file_manager.read_e2e_comparison_files(tmp_path / "missing", ["run"])
