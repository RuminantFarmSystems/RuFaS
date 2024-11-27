import pytest
from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any

from RUFAS.data_collection_app_updater import DataCollectionAppUpdater
from RUFAS.util import Utility


@pytest.fixture
def dca_updater() -> DataCollectionAppUpdater:
    return DataCollectionAppUpdater()


def test_init() -> None:
    """Tests that DataCollectionAppUpdater is initialized correctly."""
    actual = DataCollectionAppUpdater()

    assert actual._type_to_schema_map == {
        "number": actual._create_number_schema,
        "bool": actual._create_bool_schema,
        "string": actual._create_string_schema,
        "array": actual._create_array_schema,
        "object": actual._create_object_schema,
    }


def test_update_data_collection_app(dca_updater: DataCollectionAppUpdater, mocker: MockerFixture) -> None:
    """Tests that DCA Updater subroutines are called correctly."""
    rewrite_schemas = mocker.patch.object(dca_updater, "_rewrite_schemas", return_value=(paths := mocker.MagicMock()))
    rewrite_index = mocker.patch.object(dca_updater, "_rewrite_index_page")

    dca_updater.update_data_collection_app()

    rewrite_schemas.assert_called_once()
    rewrite_index.assert_called_once_with(paths)


def test_rewrite_schemas(dca_updater: DataCollectionAppUpdater, mocker: MockerFixture) -> None:
    """Tests that metadata properties are correctly grabbed and have schema written for them."""
    add_log = mocker.patch.object(dca_updater._om, "add_log")
    empty_dir = mocker.patch.object(Utility, "empty_dir")
    dca_updater._im.meta_data = {
        "properties": {
            "animal_properties": "dummy_animal_props",
            "config_properties": "dummy_config_props",
            "unneeded_properties": "dummy_props",
        }
    }
    expected_schema_paths = [
        Path("DataCollectionApp/schema/animal_schema.js"),
        Path("DataCollectionApp/schema/config_schema.js"),
    ]
    dummy_schema: dict[str, str] = {"test?": "test!"}
    create_object_schema = mocker.patch.object(dca_updater, "_create_object_schema", return_value={"test?": "test!"})
    add_filename = mocker.patch.object(dca_updater, "_add_filename_input_field", return_value=dummy_schema)
    expected_create_calls = [
        mocker.call("animal_properties", "dummy_animal_props"),
        mocker.call("config_properties", "dummy_config_props"),
    ]
    mock_open = mocker.patch("RUFAS.data_collection_app_updater.open")

    actual_schemas = dca_updater._rewrite_schemas()

    assert add_log.call_count == 3
    empty_dir.assert_called_once()
    create_object_schema.assert_has_calls(expected_create_calls)
    assert add_filename.call_count == 2
    assert actual_schemas == expected_schema_paths
    assert mock_open.call_count == 2


def test_rewrite_index_page(dca_updater: DataCollectionAppUpdater, mocker: MockerFixture) -> None:
    """Tests that the index page of the Data Collection App is properly rewritten."""
    schema_paths = [Path("dummy_one"), Path("dummy_two")]
    mock_open = mocker.patch("RUFAS.data_collection_app_updater.open")

    dca_updater._rewrite_index_page(schema_paths)

    assert mock_open.call_count == 2


@pytest.mark.parametrize(
    "pattern,expected",
    [
        ("^(kg)$", ["kg"]),
        ("^(default|no_kill)$", ["default", "no_kill"]),
        ("^(TAI|ED|Synch-ED)$", ["TAI", "ED", "Synch-ED"]),
    ],
)
def test_get_list_of_options(dca_updater: DataCollectionAppUpdater, pattern: str, expected: list[str]) -> None:
    """Tests that list of options are produced correctly from a Regex filter."""
    actual = dca_updater._get_list_of_options(pattern)

    assert actual == expected


@pytest.mark.parametrize(
    "pattern", ["(kg)$", "(kg)", "$(kg)^", "[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$"]
)
def test_get_list_of_options_error(dca_updater: DataCollectionAppUpdater, pattern: str) -> None:
    """Tests that an incorrectly structured Regex pattern produces an error."""
    with pytest.raises(ValueError):
        dca_updater._get_list_of_options(pattern)


@pytest.mark.parametrize(
    "title,properties,schema",
    [
        (
            "feed_type",
            {
                "type": "string",
                "description": "The general type or category of the feed (group).",
                "default": "Forage",
                "pattern": "^(Aminoacids|Forage|Conc|Milk|Mineral|Vitamins|Starter)$",
            },
            {
                "title": "Feed Type",
                "type": "string",
                "enum": ["one", "two"],
                "format": "select2",
                "default": "Forage",
                "options": {
                    "infoText": "The general type or category of the feed (group).",
                    "grid_columns": 12,
                    "inputAttributes": {"class": "text-primary form-control", "placeholder": "Forage"},
                },
            },
        ),
        (
            "feed_type",
            {
                "type": "string",
                "description": "The general type or category of the feed (group).",
                "default": "Forage",
                "pattern": "^(Aminoacids|Forage|Conc|Milk|Mineral|Vitamins|Starter)$",
                "nullable": True,
            },
            {
                "title": "Feed Type",
                "type": ["string", "null"],
                "enum": ["one", "two"],
                "format": "select2",
                "default": "Forage",
                "options": {
                    "infoText": "The general type or category of the feed (group).",
                    "grid_columns": 12,
                    "inputAttributes": {"class": "text-primary form-control", "placeholder": "Forage"},
                },
            },
        ),
    ],
)
def test_create_string_schema(
    dca_updater: DataCollectionAppUpdater,
    mocker: MockerFixture,
    title: str,
    properties: dict[str, Any],
    schema: dict[str, Any],
) -> None:
    """Tests that created string schema correctly handles a valid string property."""
    mocked_get_options = mocker.patch.object(dca_updater, "_get_list_of_options", return_value=["one", "two"])
    actual = dca_updater._create_string_schema(title, properties)

    assert mocked_get_options.call_count == 1
    assert actual == schema


@pytest.mark.parametrize(
    "title,properties,schema",
    [
        (
            "start_date",
            {
                "type": "string",
                "description": "The year and Julian day on which the simulation will start.",
                "pattern": "[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$",
                "default": "2009:1",
            },
            {
                "title": "Start Date",
                "type": "string",
                "default": "2009:1",
                "pattern": "[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$",
                "options": {
                    "infoText": "The year and Julian day on which the simulation will start.",
                    "grid_columns": 12,
                    "inputAttributes": {"class": "text-primary form-control", "placeholder": "2009:1"},
                },
            },
        )
    ],
)
def test_create_string_schema_value_error(
    dca_updater: DataCollectionAppUpdater,
    mocker: MockerFixture,
    title: str,
    properties: dict[str, Any],
    schema: dict[str, Any],
) -> None:
    """Tests that create_string_schema handles value errors appropriately."""
    mock_add_warning = mocker.patch.object(dca_updater._om, "add_warning")
    mocked_get_options = mocker.patch.object(
        dca_updater,
        "_get_list_of_options",
        side_effect=ValueError(
            "'[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$' is not a valid pattern. Cannot "
            "create list of valid options."
        ),
    )

    actual = dca_updater._create_string_schema(title, properties)

    assert mocked_get_options.call_count == 1
    mock_add_warning.assert_called_once_with(
        "Could not generate list of valid input options for a string input",
        "Variable start_date will not have drop-down options for Data Collection App users to pick from.",
        {"class": dca_updater.__class__.__name__, "function": dca_updater._create_string_schema.__name__},
    )
    assert actual == schema


@pytest.mark.parametrize(
    "title,properties,schema",
    [
        (
            "pattern_repeat",
            {
                "type": "number",
                "description": "Number of times that this crop schedule should be repeated.",
                "minimum": 0,
                "maximum": 1_000_000,
                "default": 0,
                "nullable": False,
            },
            {
                "title": "Pattern Repeat",
                "type": "number",
                "minimum": 0,
                "maximum": 1_000_000,
                "default": 0,
                "options": {
                    "grid_columns": 12,
                    "infoText": "Number of times that this crop schedule should be repeated.",
                    "inputAttributes": {
                        "class": "text-primary form-control",
                        "placeholder": 1_000_000
                    },
                },
            },
        ),
        (
            "pattern_repeat",
            {
                "type": "number",
                "description": "Number of times that this crop schedule should be repeated.",
                "minimum": 0,
                "maximum": 1_000_000,
                "default": 0,
                "nullable": True,
            },
            {
                "title": "Pattern Repeat",
                "type": ["number", "null"],
                "minimum": 0,
                "maximum": 1_000_000,
                "default": 0,
                "options": {
                    "grid_columns": 12,
                    "infoText": "Number of times that this crop schedule should be repeated.",
                    "inputAttributes": {
                        "class": "text-primary form-control",
                        "placeholder": 1_000_000
                    },
                },
            },
        ),
    ],
)
def test_create_number_schema(
    dca_updater: DataCollectionAppUpdater, title: str, properties: dict[str, Any], schema: dict[str, Any]
) -> None:
    """Tests that number schema are created correctly."""
    actual = dca_updater._create_number_schema(title, properties)

    assert actual == schema


@pytest.mark.parametrize(
    "title,properties,schema",
    [
        (
            "ventilation",
            {
                "type": "bool",
                "description": "Ventilation -- True if the storage unit has appropriate ventilation.",
                "default": True,
            },
            {
                "title": "Ventilation",
                "type": "boolean",
                "default": True,
                "format": "checkbox",
                "options": {
                    "grid_columns": 12,
                    "infoText": "Ventilation -- True if the storage unit has appropriate ventilation.",
                    "inputAttributes": {
                        "class": "text-primary form-control", "placeholder": True
                    },
                },
            },
        ),
        (
            "ventilation",
            {
                "type": "bool",
                "description": "Ventilation -- True if the storage unit has appropriate ventilation.",
                "default": True,
                "nullable": True,
            },
            {
                "title": "Ventilation",
                "type": ["boolean", "null"],
                "default": True,
                "format": "checkbox",
                "options": {
                    "grid_columns": 12,
                    "infoText": "Ventilation -- True if the storage unit has appropriate ventilation.",
                    "inputAttributes": {
                        "class": "text-primary form-control", "placeholder": True
                    },
                },
            },
        ),
    ],
)
def test_create_bool_schema(
    dca_updater: DataCollectionAppUpdater, title: str, properties: dict[str, Any], schema: dict[str, Any]
) -> None:
    """Tests that boolean schema are created correctly."""
    actual = dca_updater._create_bool_schema(title, properties)

    assert actual == schema


@pytest.mark.parametrize(
    "title,properties,schema",
    [
        (
            "parity_death_prob",
            {
                "type": "array",
                "description": "Death rate for first, second, third, and later lactations",
                "properties": {
                    "type": "number",
                    "description": "Death rate for first, second, third, and later lactations",
                    "minimum": 0,
                    "maximum": 1,
                },
            },
            {
                "title": "Parity Death Prob",
                "type": "array",
                "format": "grid",
                "options": {
                    "infoText": "Death rate for first, second, third, and later lactations",
                    "inputAttributes": {"class": "text-primary form-control"},
                },
                "default": None,
                "items": {
                    "title": "Parity Death Prob Element",
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "default": None,
                    "options": {
                        "grid_columns": 12,
                        "infoText": "Death rate for first, second, third, and later lactations",
                        "inputAttributes": {
                            "class": "text-primary form-control", "placeholder": 1
                        },
                    },
                },
            },
        ),
        (
            "manure_management_scenarios",
            {
                "type": "array",
                "description": "Manure Management Scenarios -- Add as many different manure scenarios as needed",
                "properties": {
                    "type": "object",
                    "scenario_id": {
                        "type": "number",
                        "description": "Scenario ID -- An identification number for livestock enclosures.",
                        "minimum": 0,
                    },
                    "bedding_type": {
                        "type": "string",
                        "description": "Bedding Type -- The material used for bedding pack.",
                        "pattern": "^(Sand|Straw|Sawdust|Manure_solids|Other)$",
                    },
                },
            },
            {
                "title": "Manure Management Scenarios",
                "type": "array",
                "format": "grid",
                "options": {
                    "inputAttributes": {"class": "text-primary form-control"},
                    "infoText": "Manure Management Scenarios -- Add as many different manure scenarios as needed",
                },
                "default": None,
                "items": {
                    "title": "Manure Management Scenarios Element",
                    "type": "object",
                    "format": "grid",
                    "default": None,
                    "options": {"infoText": None},
                    "properties": {
                        "scenario_id": {
                            "title": "Scenario Id",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {"class": "text-primary form-control", "placeholder": "null"},
                                "infoText": "Scenario ID -- An identification number for livestock enclosures.",
                            },
                            "minimum": 0,
                            "default": None,
                        },
                        "bedding_type": {
                            "title": "Bedding Type",
                            "type": "string",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {"class": "text-primary form-control", "placeholder": "null"},
                                "infoText": "Bedding Type -- The material used for bedding pack.",
                            },
                            "enum": ["Sand", "Straw", "Sawdust", "Manure_solids", "Other"],
                            "format": "select2",
                            "default": None,
                        },
                    },
                },
            },
        ),
    ],
)
def test_create_array_schema(
    dca_updater: DataCollectionAppUpdater, title: str, properties: dict[str, Any], schema: dict[str, Any]
) -> None:
    """Tests that array schema is created correctly."""
    actual = dca_updater._create_array_schema(title, properties)

    assert actual == schema


@pytest.mark.parametrize(
    "title,properties,schema",
    [
        (
            "life_cycle",
            {
                "type": "object",
                "description": "",
                "still_birth_rate": {"type": "number", "description": "Stillbirth rate", "minimum": 0, "maximum": 1},
            },
            {
                "title": "Life Cycle",
                "type": "object",
                "default": None,
                "format": "grid",
                "options": {"infoText": ""},
                "properties": {
                    "still_birth_rate": {
                        "title": "Still Birth Rate",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": None,
                        "options": {
                            "grid_columns": 12,
                            "infoText": "Stillbirth rate",
                            "inputAttributes": {
                                "class": "text-primary form-control", "placeholder": 1
                            },
                        },
                    }
                },
            },
        ),
        (
            "herd_information",
            {
                "type": "object",
                "description": "Herd Demographics",
                "calf_num": {
                    "type": "number",
                    "description": "Number of Calves (head) -- The initial number of pre-weaned calves",
                    "default": 8,
                    "minimum": 0,
                },
                "breed": {
                    "type": "string",
                    "default": "HO",
                    "pattern": "^(HO|JE)$",
                    "description": "Breed (select one Holstein/Jersey) -- The predominant breed of the herd (Holstein "
                    "or Jersey)",
                },
            },
            {
                "title": "Herd Information",
                "type": "object",
                "default": None,
                "format": "grid",
                "options": {"infoText": "Herd Demographics"},
                "properties": {
                    "calf_num": {
                        "title": "Calf Num",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {"class": "text-primary form-control", "placeholder": 8},
                            "infoText": "Number of Calves (head) -- The initial number of pre-weaned calves",
                        },
                        "minimum": 0,
                        "default": 8,
                    },
                    "breed": {
                        "title": "Breed",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {"class": "text-primary form-control", "placeholder": "HO"},
                            "infoText": "Breed (select one Holstein/Jersey) -- The predominant breed of the herd "
                            "(Holstein or Jersey)",
                        },
                        "default": "HO",
                        "enum": ["HO", "JE"],
                        "format": "select2",
                    },
                },
            },
        ),
    ],
)
def test_create_object_schema(
    dca_updater: DataCollectionAppUpdater, title: str, properties: dict[str, Any], schema: dict[str, Any]
) -> None:
    """Tests that object schema are created correctly."""
    actual = dca_updater._create_object_schema(title, properties)

    assert actual == schema


@pytest.mark.parametrize(
    "name,expected",
    [
        ("snake_case", "Snake Case"),
        ("simple", "Simple"),
        ("tricky Name", "Tricky Name"),
        ("Trickier_Name", "Trickier Name"),
        ("Trickiest name", "Trickiest Name"),
    ],
)
def test_parse_variable_name_into_title(dca_updater: DataCollectionAppUpdater, name: str, expected: str) -> None:
    """Tests that names partially or all in snake case are converted into more readable names."""
    actual = dca_updater._parse_variable_name_into_title(name)

    assert actual == expected


def test_add_filename_input_field(dca_updater: DataCollectionAppUpdater) -> None:
    dummy_schema: dict[str, Any] = {"properties": {}}
    expected = {
        "properties": {
            "fileName": {
                "title": "File Name",
                "type": "string",
                "pattern": r"^[a-zA-Z0-9_\- ]{1,255}$",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {"class": "text-primary form-control", "placeholder": "null"},
                    "infoText": "Used to name the file that saves the data entered. This name will not be included in "
                    "the saved file.",
                },
            }
        }
    }

    actual = dca_updater._add_filename_input_field(dummy_schema)

    assert actual == expected
