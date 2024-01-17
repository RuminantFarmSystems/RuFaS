import pytest
from pytest_mock import MockerFixture
from unittest.mock import patch
from mock import mock_open
from typing import Any

from RUFAS.schema_generator import SchemaGenerator
from RUFAS.output_manager import OutputManager

om = OutputManager()

dummy_properties = {
    "properties": {
        "dummy_one": {},
    }
}


@pytest.mark.parametrize("pattern,expected", [
    ("^(kg)$", ["kg"]),
    ("^(default|no_kill)$", ["default", "no_kill"]),
    ("^(TAI|ED|Synch-ED)$", ["TAI", "ED", "Synch-ED"])
])
def test_get_list_of_options(pattern: str, expected: list[str]) -> None:
    """Tests that list of options are produced correctly from a Regex filter."""
    actual = SchemaGenerator._get_list_of_options(pattern)
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
        SchemaGenerator._get_list_of_options(pattern)


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
    mocked_get_options = mocker.patch.object(SchemaGenerator, "_get_list_of_options", return_value=["one", "two"])

    actual = SchemaGenerator.setup_string_schema(title, properties)

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
    mocked_get_options = mocker.patch.object(SchemaGenerator, "_get_list_of_options", side_effect=ValueError(
        "'[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$' is not a valid pattern. Cannot "
        "create list of valid options."))

    actual = SchemaGenerator.setup_string_schema(title, properties)

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
    actual = SchemaGenerator.setup_number_schema(title, properties)
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
            "format": "checkbox",
            "options": {
                "grid_columns": 12,
                "infoText": "Ventilation -- True if the storage unit has appropriate ventilation.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
     })
])
def test_setup_bool_schema(title: str, properties: dict[str, Any], schema: dict[str, Any]) -> None:
    """Tests that boolean schema are setup correctly."""
    actual = SchemaGenerator.setup_bool_schema(title, properties)
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
    actual = SchemaGenerator.setup_array_schema(title, properties)

    assert actual == schema


@pytest.mark.parametrize("title,properties,schema", [
    ("life_cycle", {
        "type": "object",
        "description": "",
        "still_birth_rate": {
          "type": "number",
          "description": "Stillbirth rate",
          "minimum": 0,
          "maximum": 1
        }
     }, {
            "title": "life_cycle",
            "type": "object",
            "format": "grid",
            "options": {
                "infoText": ""
            },
            "properties": {
                "still_birth_rate": {
                    "title": "still_birth_rate",
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "options": {
                        "grid_columns": 12,
                        "infoText": "Stillbirth rate",
                        "inputAttributes": {
                            "class": "text-primary form-control",
                        }
                    }
                }
            }
        })
])
def test_setup_object_schema(title: str, properties: dict[str, Any], schema: dict[str, Any]) -> None:
    """Tests that object schema are setup correctly."""
    actual = SchemaGenerator.setup_object_schema(title, properties)

    assert actual == schema


def test_generate_schema(mocker: MockerFixture) -> None:
    patch_add_log = mocker.patch("RUFAS.output_manager.OutputManager.add_log")
    patch_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    patch_open = mocker.patch("builtins.open", mock_open(read_data="some valid json data"))
    patch_object_schema_setup = mocker.patch("RUFAS.schema_generator.SchemaGenerator.setup_object_schema",
                                             result={"new_schema": "yay"})
    patch_empty_dir = mocker.patch("RUFAS.util.Utility.empty_dir")
    patch_json_load = mocker.patch("json.load", return_value=dummy_properties)
    patch_json_dump = mocker.patch("json.dump")

    schema_generator = SchemaGenerator()
    schema_generator.generate_schemas(None, None)

    assert patch_add_log.call_count == 2
    assert patch_empty_dir.call_count == 1
    assert patch_open.call_count == 2
    assert patch_json_load.call_count == 1
    assert patch_object_schema_setup.call_count == 1
    assert patch_add_error.call_count == 0
    assert patch_json_dump.call_count == 1

    patch_object_schema_setup = mocker.patch("RUFAS.schema_generator.SchemaGenerator.setup_object_schema",
                                             side_effect=ValueError("Oh no!"))

    schema_generator.generate_schemas(None, None)

    assert patch_object_schema_setup.call_count == 1
    assert patch_add_error.call_count == 1
    assert patch_json_dump.call_count == 1
