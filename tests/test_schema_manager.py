import pytest
from pytest_mock import MockerFixture
from unittest.mock import patch
from typing import Any

from RUFAS.schema_manager import SchemaManager

@pytest.mark.parametrize("pattern,expected", [
    ("^(kg)$", ["kg"]),
    ("^(default|no_kill)$", ["default", "no_kill"]),
    ("^(TAI|ED|Synch-ED)$", ["TAI", "ED", "Synch-ED"])
])
def test_get_list_of_options(pattern: str, expected: list[str]) -> None:
    """Tests that list of options are produced correctly from a Regex filter."""
    actual = SchemaManager._get_list_of_options(pattern)
    assert actual == expected


@pytest.mark.parametrize("pattern", [
    "(kg)$",
    "(kg)",
    "$(kg)^",
    "[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$"
])
def test_get_list_of_options_error(pattern: str) -> None:
    """Tests that an incorrectly structured Regex pattern produces an error."""
    with pytest.raises(ValueError):
        SchemaManager._get_list_of_options(pattern)


@pytest.mark.parametrize("title,properties,schema", [
    ("feed_type", {
        "type": "string",
        "description": "The general type or category of the feed (group).",
        "default": "Forage",
        "pattern": "^(Aminoacids|Forage|Conc|Milk|Mineral|Vitamins|Starter)$"
      }, {
            "title": "feed_type",
            "type": "string",
            "enum": ["one", "two"],
            "format": "select2",
            "default": "Forage",
            "options": {
                "infoText": "The general type or category of the feed (group).",
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            }
     })
])
def test_setup_string_schema(mocker: MockerFixture, title: str, properties: dict[str, Any],
                             schema: dict[str, Any]) -> None:
    """Tests that setup string schema correctly handles a valid string property."""
    mocked_get_options = mocker.patch.object(SchemaManager, "_get_list_of_options", return_value=["one", "two"])

    actual = SchemaManager.setup_string_schema(title, properties)

    assert mocked_get_options.call_count == 1
    assert actual == schema


@pytest.mark.parametrize("title,properties,schema", [
    ("start_date", {
        "type": "string",
        "description": "The year and Julian day on which the simulation will start.",
        "pattern": "[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$",
        "default": "2009:1"
    }, {
        "title": "start_date",
        "type": "string",
        "default": "2009:1",
        "options": {
            "infoText": "The year and Julian day on which the simulation will start.",
            "grid_columns": 12,
            "inputAttributes": {
                "class": "text-primary form-control"
            }
        }
    })
])
@patch('builtins.print')
def test_setup_string_schema_value_error(mocked_print, mocker: MockerFixture, title: str, properties: dict[str, Any],
                                         schema: dict[str, Any]) -> None:
    """Tests that setup_string_schema handles value errors appropriately."""
    mocked_get_options = mocker.patch.object(SchemaManager, "_get_list_of_options", side_effect=ValueError(
        "'[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$' is not a valid pattern. Cannot "
        "create list of valid options."))

    actual = SchemaManager.setup_string_schema(title, properties)

    assert mocked_get_options.call_count == 1
    mocked_print.assert_called_once_with("'[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$' is"
                                         " not a valid pattern. Cannot create list of valid options.")
    assert actual == schema


@pytest.mark.parametrize("title,properties,schema", [
    ("pattern_repeat", {
            "type": "number",
            "description": "Number of times that this crop schedule should be repeated.",
            "minimum": 0,
            "maximum": 1_000_000,
            "default": 0
     }, {
            "title": "pattern_repeat",
            "type": "number",
            "minimum": 0,
            "maximum": 1_000_000,
            "default": 0,
            "options": {
                "grid_columns": 12,
                "infoText": "Number of times that this crop schedule should be repeated.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
     })
])
def test_setup_number_schema(title: str, properties: dict[str, Any], schema: dict[str, Any]) -> None:
    """Tests that number schema are setup correctly."""
    actual = SchemaManager.setup_number_schema(title, properties)
    assert actual == schema


@pytest.mark.parametrize("title,properties,schema", [
    ("ventilation", {
            "type": "bool",
            "description": "Ventilation -- True if the storage unit has appropriate ventilation.",
            "default": True
     }, {
            "title": "ventilation",
            "type": "boolean",
            "default": True,
            "options": {
                "grid_columns": 12,
                "format": "select2",
                "infoText": "Ventilation -- True if the storage unit has appropriate ventilation.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
     })
])
def test_setup_bool_schema(title: str, properties: dict[str, Any], schema: dict[str, Any]) -> None:
    """Tests that boolean schema are setup correctly."""
    actual = SchemaManager.setup_bool_schema(title, properties)
    assert actual == schema


@pytest.mark.parametrize("title,properties,schema", [
    ("parity_death_prob", {
      "type": "array",
      "description": "Death rate for first, second, third, and later lactations",
      "properties": {
        "type": "number",
        "description": "Death rate for first, second, third, and later lactations",
        "minimum": 0,
        "maximum": 1
      }
    }, {
        "title": "parity_death_prob",
        "type": "array",
        "format": "grid",
        "options": {
            "infoText": "Death rate for first, second, third, and later lactations",
            "inputAttributes": {
                "class": "text-primary form-control"
            }
        },
        "items": {
            "title": "parity_death_prob_element",
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "options": {
                "grid_columns": 12,
                "infoText": "Death rate for first, second, third, and later lactations",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        }
     })
])
def test_setup_array_schema(title: str, properties: dict[str, Any], schema: dict[str, Any]) -> None:
    """Tests that array schema is setup correctly."""
    actual = SchemaManager.setup_array_schema(title, properties)

    assert actual == schema
