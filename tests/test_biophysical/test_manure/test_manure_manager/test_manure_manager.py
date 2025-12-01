import math
from typing import Any, Optional, cast
from unittest.mock import call, MagicMock

import pytest
from pytest_mock import MockerFixture, MockFixture

from RUFAS.biophysical.manure.digester.digester import Digester
from RUFAS.biophysical.manure.field_manure_supplier import FieldManureSupplier
from RUFAS.biophysical.manure.manure_manager import STORAGE_CLASS_TO_TYPE, ManureManager
from RUFAS.biophysical.manure.manure_nutrient_manager import ManureNutrientManager
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.biophysical.manure.storage.composting import Composting
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.manure_nutrients import ManureNutrients
from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequestResults, NutrientRequest
from RUFAS.data_structures.manure_types import ManureType
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from tests.test_biophysical.test_manure.test_manure_manager.manure_manager_fixture import (
    manure_management_input_json,
    processor_connections_input_json,
    manure_manager,
    expected_processor_definitions_by_name,
    expected_processor_connections_by_name,
    expected_all_defined_processor_names,
    expected_all_processor_names_in_connection_map,
    expected_all_separator_names,
    expected_all_processor_connections,
    expected_adjacency_matrix_keys,
    expected_adjacency_matrix,
    expected_empty_adjacency_matrix,
    expected_adjacency_matrix_after_merge,
    invalid_separator_adjacency_matrix,
)

assert manure_management_input_json is not None
assert processor_connections_input_json is not None
assert manure_manager is not None
assert expected_processor_definitions_by_name is not None
assert expected_processor_connections_by_name is not None
assert expected_all_defined_processor_names is not None
assert expected_all_processor_names_in_connection_map is not None
assert expected_all_separator_names is not None
assert expected_all_processor_connections is not None
assert expected_adjacency_matrix_keys is not None
assert expected_adjacency_matrix is not None
assert expected_empty_adjacency_matrix is not None
assert expected_adjacency_matrix_after_merge is not None
assert invalid_separator_adjacency_matrix is not None


def test_init(
    manure_management_input_json: dict[str, list[dict[str, Any]]],
    processor_connections_input_json: dict[str, list[dict[str, Any]]],
    expected_processor_definitions_by_name: dict[str, dict[str, Any]],
    expected_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    mocker: MockerFixture,
) -> None:
    """Test for __init__() method of ManureManager class."""
    im = InputManager()
    mock_get_data = mocker.patch.object(
        im, "get_data", side_effect=[manure_management_input_json, processor_connections_input_json]
    )
    mock_get_processor_configs_by_name = mocker.patch(
        "RUFAS.biophysical.manure.manure_manager.ManureManager._get_processor_configs_by_name",
        return_value=expected_processor_definitions_by_name,
    )
    mock_validate_and_parse_processor_connections = mocker.patch(
        "RUFAS.biophysical.manure.manure_manager.ManureManager._validate_and_parse_processor_connections",
        return_value=expected_processor_connections_by_name,
    )
    mock_create_all_processors = mocker.patch(
        "RUFAS.biophysical.manure.manure_manager.ManureManager._create_all_processors"
    )
    mock_populate_adjacency_matrix = mocker.patch(
        "RUFAS.biophysical.manure.manure_manager.ManureManager._populate_adjacency_matrix"
    )

    ManureManager(0.5, 0.5, 15)

    assert mock_get_data.call_args_list == [call("manure_management"), call("manure_processor_connection")]
    mock_get_processor_configs_by_name.assert_called_once_with(manure_management_input_json)
    mock_validate_and_parse_processor_connections.assert_called_once_with(
        processor_connections_input_json, expected_processor_definitions_by_name
    )
    mock_create_all_processors.assert_called_once_with(
        expected_processor_connections_by_name, expected_processor_definitions_by_name, 0.5, 0.5, 15
    )
    mock_populate_adjacency_matrix.assert_called_once_with(expected_processor_connections_by_name)


def test_get_processor_configs_by_name(
    manure_manager: ManureManager,
    manure_management_input_json: dict[str, list[dict[str, Any]]],
    expected_all_defined_processor_names: list[str],
    expected_processor_definitions_by_name: dict[str, dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Test for _get_processor_configs_by_name() method of ManureManager class."""
    mock_check_for_duplicate_processor_names = mocker.patch.object(
        manure_manager, "_check_for_duplicate_processor_names"
    )

    result = manure_manager._get_processor_configs_by_name(manure_management_input_json)

    mock_check_for_duplicate_processor_names.assert_called_once_with(expected_all_defined_processor_names)
    assert result == expected_processor_definitions_by_name


@pytest.mark.parametrize(
    "all_names, expected_duplicate_names",
    [
        # 1. Empty list
        ([], []),
        # 2. Single name (no duplicates)
        (["processor1"], []),
        # 3. Multiple unique names (no duplicates)
        (["processor1", "processor2", "processor3"], []),
        # 4. Single duplicate name
        (["processor1", "processor1"], ["processor1"]),
        # 5. Single name repeated multiple times
        (["processor1", "processor1", "processor1"], ["processor1"]),
        # 6. Multiple distinct duplicates
        (["processor1", "processor2", "processor1", "processor2"], ["processor1", "processor2"]),
        # 7. Multiple distinct duplicates scattered
        (
            ["processor1", "processor2", "processor3", "processor2", "processor3", "processor4", "processor1"],
            ["processor1", "processor2", "processor3"],
        ),
    ],
)
def test_check_for_duplicate_processor_names(
    manure_manager: ManureManager, all_names: list[str], expected_duplicate_names: list[str], mocker: MockerFixture
) -> None:
    """Test for _check_for_duplicate_processor_names() method of ManureManager class."""
    mock_add_error = mocker.patch.object(manure_manager._om, "add_error")

    if len(expected_duplicate_names) > 0:
        with pytest.raises(ValueError):
            manure_manager._check_for_duplicate_processor_names(all_names)
        mock_add_error.assert_called_once()
    else:
        manure_manager._check_for_duplicate_processor_names(all_names)
        mock_add_error.assert_not_called()


def test_validate_and_parse_processor_connections(
    manure_manager: ManureManager,
    processor_connections_input_json: dict[str, list[dict[str, Any]]],
    expected_processor_definitions_by_name: dict[str, dict[str, Any]],
    expected_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    expected_all_processor_names_in_connection_map: list[str],
    expected_all_processor_connections: list[dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Test for _validate_and_parse_processor_connections() method of ManureManager class."""
    mock_find_all_referenced_processor_names = mocker.patch.object(
        manure_manager,
        "_find_all_processor_names_in_connection_map",
        return_value=expected_all_processor_names_in_connection_map,
    )
    mock_build_processor_connection_map = mocker.patch.object(
        manure_manager, "_build_processor_connection_map", return_value=expected_processor_connections_by_name
    )
    mock_check_for_unknown_processor_names = mocker.patch.object(manure_manager, "_check_for_unknown_processor_names")
    mock_check_for_processors_without_connection_definition = mocker.patch.object(
        manure_manager, "_check_for_processors_without_connection_definition"
    )

    result = manure_manager._validate_and_parse_processor_connections(
        processor_connections_input_json, expected_processor_definitions_by_name
    )

    assert result == expected_processor_connections_by_name
    mock_find_all_referenced_processor_names.assert_called_once_with(expected_all_processor_connections)
    mock_build_processor_connection_map.assert_called_once_with(expected_all_processor_connections)
    mock_check_for_unknown_processor_names.assert_called_once_with(
        expected_all_processor_names_in_connection_map, expected_processor_definitions_by_name
    )
    mock_check_for_processors_without_connection_definition.assert_called_once_with(
        expected_all_processor_names_in_connection_map, expected_processor_connections_by_name
    )


@pytest.mark.parametrize(
    "referenced_names, defined_names, expected_unknown_names",
    [
        # 1. No referenced names; no defined names => no unknowns
        (set(), set(), set()),
        # 2. No referenced names; some defined names => no unknowns
        (set(), {"p1", "p2"}, set()),
        # 3. All referenced are already defined => no unknowns
        ({"p1", "p2"}, {"p1", "p2", "p3"}, set()),
        # 4. All referenced names are missing => all unknown
        ({"p1", "p2"}, set(), {"p1", "p2"}),
        # 5. Some referenced exist, some do not
        ({"p1", "p2", "p3"}, {"p1", "p4"}, {"p2", "p3"}),
        # 6. Multiple unknown names scattered
        ({"p1", "p2", "p3", "p4"}, {"p2", "p5"}, {"p1", "p3", "p4"}),
    ],
)
def test_check_for_unknown_processor_names(
    referenced_names: set[str],
    defined_names: set[str],
    expected_unknown_names: set[str],
    manure_manager: ManureManager,
    mocker: MockerFixture,
) -> None:
    """Test for _check_for_unknown_processor_names() method of ManureManager class."""
    mock_add_error = mocker.patch.object(manure_manager._om, "add_error")

    dummy_processor_definitions_by_name: dict[str, dict[str, Any]] = {
        defined_name: {} for defined_name in defined_names
    }

    if expected_unknown_names:
        with pytest.raises(ValueError):
            manure_manager._check_for_unknown_processor_names(referenced_names, dummy_processor_definitions_by_name)
        mock_add_error.assert_has_calls(
            [
                call(
                    "Unknown Processor Name.",
                    f"No configuration found for {expected_unknown_name}.",
                    {
                        "class": manure_manager.__class__.__name__,
                        "function": manure_manager._check_for_unknown_processor_names.__name__,
                    },
                )
                for expected_unknown_name in expected_unknown_names
            ],
            any_order=True,
        )
    else:
        manure_manager._check_for_unknown_processor_names(referenced_names, dummy_processor_definitions_by_name)
        mock_add_error.assert_not_called()


@pytest.mark.parametrize(
    "referenced_names, connection_names, expected_unknown_names",
    [
        # 1. No referenced names; no defined names => no unknowns
        (set(), set(), set()),
        # 2. No referenced names; some defined names => no unknowns
        (set(), {"p1", "p2"}, set()),
        # 3. All referenced are already defined => no unknowns
        ({"p1", "p2"}, {"p1", "p2", "p3"}, set()),
        # 4. All referenced names are missing => all unknown
        ({"p1", "p2"}, set(), {"p1", "p2"}),
        # 5. Some referenced exist, some do not
        ({"p1", "p2", "p3"}, {"p1", "p4"}, {"p2", "p3"}),
        # 6. Multiple unknown names scattered
        ({"p1", "p2", "p3", "p4"}, {"p2", "p5"}, {"p1", "p3", "p4"}),
    ],
)
def test_check_for_processors_without_connection_definition(
    referenced_names: set[str],
    connection_names: set[str],
    expected_unknown_names: set[str],
    manure_manager: ManureManager,
    mocker: MockerFixture,
) -> None:
    """Test for _check_for_processors_without_connection_definition() method of ManureManager class."""
    mock_add_error = mocker.patch.object(manure_manager._om, "add_error")

    dummy_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]] = {
        name: {} for name in connection_names
    }

    if expected_unknown_names:
        with pytest.raises(ValueError):
            manure_manager._check_for_processors_without_connection_definition(
                referenced_names, dummy_processor_connections_by_name
            )
        mock_add_error.assert_has_calls(
            [
                call(
                    "Undefined Processor Connection.",
                    f"No routing configurations found for {expected_unknown_name}.",
                    {
                        "class": manure_manager.__class__.__name__,
                        "function": manure_manager._check_for_processors_without_connection_definition.__name__,
                    },
                )
                for expected_unknown_name in expected_unknown_names
            ],
            any_order=True,
        )
    else:
        manure_manager._check_for_processors_without_connection_definition(
            referenced_names, dummy_processor_connections_by_name
        )
        mock_add_error.assert_not_called()


def test_find_all_referenced_processor_names(
    expected_all_processor_connections: list[dict[str, Any]],
    expected_all_processor_names_in_connection_map: list[str],
    manure_manager: ManureManager,
) -> None:
    """Test for _find_all_processor_names_in_connection_map() method of ManureManager class."""
    result = manure_manager._find_all_processor_names_in_connection_map(expected_all_processor_connections)
    assert result == set(expected_all_processor_names_in_connection_map)


def test_build_processor_connection_map(
    expected_all_processor_connections: list[dict[str, Any]],
    expected_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    manure_manager: ManureManager,
    mocker: MockerFixture,
) -> None:
    """Test for _build_processor_connection_map() method of ManureManager class."""
    mock_add_error = mocker.patch.object(manure_manager._om, "add_error")

    result = manure_manager._build_processor_connection_map(expected_all_processor_connections)

    assert result == expected_processor_connections_by_name
    mock_add_error.assert_not_called()


def test_build_processor_connection_map_with_duplicate_connection_definition(
    expected_all_processor_connections: list[dict[str, Any]],
    expected_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    manure_manager: ManureManager,
    mocker: MockerFixture,
) -> None:
    """Test for _build_processor_connection_map() method of ManureManager class with duplicate connection definition."""
    mock_add_error = mocker.patch.object(manure_manager._om, "add_error")

    all_processor_connections = expected_all_processor_connections + [
        {"processor_name": "alley_scraper_1", "destinations": []}
    ]

    with pytest.raises(ValueError):
        manure_manager._build_processor_connection_map(all_processor_connections)
    mock_add_error.assert_called_once_with(
        "Duplicate processor connection definitions",
        "Duplicate connection definitions found for alley_scraper_1.",
        {
            "class": manure_manager.__class__.__name__,
            "function": manure_manager._build_processor_connection_map.__name__,
        },
    )


def test_create_all_processors(
    expected_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    expected_processor_definitions_by_name: dict[str, dict[str, Any]],
    manure_manager: ManureManager,
    mocker: MockerFixture,
) -> None:
    """Test for _create_all_processors() method of ManureManager class."""
    mock_separator_init = mocker.patch(
        "RUFAS.biophysical.manure.separator.separator.Separator.__init__", return_value=None
    )
    mock_anaerobic_digester_init = mocker.patch(
        "RUFAS.biophysical.manure.digester.continuous_mix.ContinuousMix.__init__", return_value=None
    )
    mock_parlor_cleaning_handler_init = mocker.patch(
        "RUFAS.biophysical.manure.handler.parlor_cleaning.ParlorCleaningHandler.__init__", return_value=None
    )
    mock_single_stream_handler_init = mocker.patch(
        "RUFAS.biophysical.manure.handler.single_stream_handler.SingleStreamHandler.__init__", return_value=None
    )
    mock_anaerobic_lagoon_init = mocker.patch(
        "RUFAS.biophysical.manure.storage.anaerobic_lagoon.AnaerobicLagoon.__init__", return_value=None
    )
    mock_slurry_storage_outdoor_init = mocker.patch(
        "RUFAS.biophysical.manure.storage.slurry_storage_outdoor.SlurryStorageOutdoor.__init__", return_value=None
    )
    mock_slurry_storage_underfloor_init = mocker.patch(
        "RUFAS.biophysical.manure.storage.slurry_storage_underfloor.SlurryStorageUnderfloor.__init__", return_value=None
    )

    manure_manager._create_all_processors(
        expected_processor_connections_by_name, expected_processor_definitions_by_name, 0.5, 0.5, 0.5
    )

    assert mock_separator_init.call_count == 2
    assert mock_anaerobic_digester_init.call_count == 2
    assert mock_parlor_cleaning_handler_init.call_count == 1
    assert mock_single_stream_handler_init.call_count == 2
    assert mock_anaerobic_lagoon_init.call_count == 1
    assert mock_slurry_storage_outdoor_init.call_count == 1
    assert mock_slurry_storage_underfloor_init.call_count == 0

    assert len(manure_manager.all_processors) == 9
    assert len(manure_manager._all_separators) == 2


def test_populate_adjacency_matrix(
    expected_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    expected_adjacency_matrix_keys: list[str],
    expected_all_processor_names_in_connection_map: list[str],
    expected_all_separator_names: list[str],
    manure_manager: ManureManager,
    mocker: MockerFixture,
) -> None:
    """Test for _populate_adjacency_matrix() method of ManureManager class."""
    manure_manager._all_separators = {name: MagicMock(auto_spec=Separator) for name in expected_all_separator_names}
    expected_all_non_separator_processor_names = [
        name for name in expected_all_processor_names_in_connection_map if name not in expected_all_separator_names
    ]

    mock_generate_adjacency_matrix_keys = mocker.patch.object(
        manure_manager, "_generate_adjacency_matrix_keys", return_value=expected_adjacency_matrix_keys
    )
    mock_create_column_in_adjacency_matrix = mocker.patch.object(manure_manager, "_create_column_in_adjacency_matrix")
    mock_populate_destination_proportions = mocker.patch.object(manure_manager, "_populate_destination_proportions")

    manure_manager._populate_adjacency_matrix(expected_processor_connections_by_name)

    mock_generate_adjacency_matrix_keys.assert_called_once_with()
    mock_create_column_in_adjacency_matrix.assert_has_calls(
        [
            call(
                origin_name,
                expected_adjacency_matrix_keys,
                (True if origin_name in expected_all_separator_names else False),
            )
            for origin_name in expected_all_processor_names_in_connection_map
        ],
        any_order=True,
    )
    mock_populate_destination_proportions.assert_has_calls(
        [
            call(expected_processor_connections_by_name[origin_name]["destinations"], origin_name)
            for origin_name in expected_all_non_separator_processor_names
        ],
        any_order=True,
    )
    mock_populate_destination_proportions.assert_has_calls(
        [
            call(
                expected_processor_connections_by_name[origin_name]["solid_output_destinations"],
                f"{origin_name}_solid_output",
            )
            for origin_name in expected_all_separator_names
        ],
        any_order=True,
    )
    mock_populate_destination_proportions.assert_has_calls(
        [
            call(
                expected_processor_connections_by_name[origin_name]["liquid_output_destinations"],
                f"{origin_name}_liquid_output",
            )
            for origin_name in expected_all_separator_names
        ],
        any_order=True,
    )


def test_create_column_in_adjacency_matrix(
    expected_adjacency_matrix_keys: list[str],
    expected_all_processor_names_in_connection_map: list[str],
    expected_all_separator_names: list[str],
    expected_empty_adjacency_matrix: dict[str, dict[str, float]],
    manure_manager: ManureManager,
) -> None:
    """Test for _create_column_in_adjacency_matrix() method of ManureManager class."""
    manure_manager._adjacency_matrix = {}
    expected_all_non_separator_processor_names = [
        name for name in expected_all_processor_names_in_connection_map if name not in expected_all_separator_names
    ]

    for origin_name in expected_all_non_separator_processor_names:
        manure_manager._create_column_in_adjacency_matrix(origin_name, expected_adjacency_matrix_keys, False)
    for origin_name in expected_all_separator_names:
        manure_manager._create_column_in_adjacency_matrix(origin_name, expected_adjacency_matrix_keys, True)

    assert manure_manager._adjacency_matrix == expected_empty_adjacency_matrix


def test_populate_destination_proportions(
    expected_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    expected_all_processor_names_in_connection_map: list[str],
    expected_all_separator_names: list[str],
    expected_empty_adjacency_matrix: dict[str, dict[str, float]],
    expected_adjacency_matrix: dict[str, dict[str, float]],
    manure_manager: ManureManager,
) -> None:
    """Test for _populate_destination_proportions() method of ManureManager class."""
    manure_manager._adjacency_matrix = expected_empty_adjacency_matrix
    manure_manager._all_separators = {name: MagicMock(auto_spec=Separator) for name in expected_all_separator_names}

    expected_all_non_separator_processor_names = [
        name for name in expected_all_processor_names_in_connection_map if name not in expected_all_separator_names
    ]

    for origin_name in expected_all_non_separator_processor_names:
        connections = expected_processor_connections_by_name[origin_name]["destinations"]
        manure_manager._populate_destination_proportions(connections, origin_name)
    for origin_name in expected_all_separator_names:
        solid_output_connections = expected_processor_connections_by_name[origin_name]["solid_output_destinations"]
        liquid_output_connections = expected_processor_connections_by_name[origin_name]["liquid_output_destinations"]
        manure_manager._populate_destination_proportions(solid_output_connections, f"{origin_name}_solid_output")
        manure_manager._populate_destination_proportions(liquid_output_connections, f"{origin_name}_liquid_output")

    assert manure_manager._adjacency_matrix == expected_adjacency_matrix


def test_generate_adjacency_matrix_keys(
    expected_all_processor_names_in_connection_map: list[str],
    expected_all_separator_names: list[str],
    expected_adjacency_matrix_keys: list[str],
    manure_manager: ManureManager,
) -> None:
    """Test for _generate_adjacency_matrix_keys() method of ManureManager class."""
    manure_manager.all_processors = {
        name: MagicMock(auto_spec=Processor) for name in expected_all_processor_names_in_connection_map
    }
    manure_manager._all_separators = {name: MagicMock(auto_spec=Separator) for name in expected_all_separator_names}

    result = manure_manager._generate_adjacency_matrix_keys()
    assert result == expected_adjacency_matrix_keys


@pytest.mark.parametrize(
    "expect_failure, expected_message, matrix",
    [
        (
            True,
            "The diagonal for origin A is not 0.",
            {
                "A": {"A": 1.0, "B": 0.0, "C": 0.0},  # diagonal is not zero
                "B": {"A": 0.0, "B": 0.0, "C": 1.0},
                "C": {"A": 0.0, "B": 0.0, "C": 0.0},
            },
        ),
        (
            True,
            "Sum for B column must be 0 or 1, but got 2",
            {
                "A": {"A": 0.0, "B": 0.0, "C": 0.0},
                "B": {"A": 1.0, "B": 0.0, "C": 1.0},  # Column does not sum to 0 or 1
                "C": {"A": 0.0, "B": 0.0, "C": 0.0},
            },
        ),
        (
            False,
            None,
            {
                "A": {"A": 0.0, "B": 1.0, "C": 0.0},  # valid case
                "B": {"A": 0.0, "B": 0.0, "C": 1.0},
                "C": {"A": 0.0, "B": 0.0, "C": 0.0},
            },
        ),
    ],
)
def test_validate_adjacency_matrix(
    expect_failure: bool,
    expected_message: Optional[str],
    matrix: dict[str, dict[str, float]],
    manure_manager: ManureManager,
) -> None:
    """Tests _validate_adjacency_matrix()."""
    manure_manager._adjacency_matrix = matrix
    if expect_failure:
        with pytest.raises(ValueError, match=expected_message):
            manure_manager._validate_adjacency_matrix()
    else:
        manure_manager._validate_adjacency_matrix()
        assert True


@pytest.mark.parametrize(
    "matrix, expected_order",
    [
        (
            {
                "A": {"A": 0.0, "B": 1.0, "C": 0.0},  # valid case
                "B": {"A": 0.0, "B": 0.0, "C": 1.0},
                "C": {"A": 0.0, "B": 0.0, "C": 0.0},
            },
            ["A", "B", "C"],
        ),
    ],
)
def test_traverse_adjacency_matrix(
    matrix: dict[str, dict[str, float]],
    expected_order: list[str],
    manure_manager: ManureManager,
) -> None:
    """Tests _traverse_adjacency_matrix() on a simple matrix case."""
    manure_manager._adjacency_matrix = matrix
    assert manure_manager._traverse_adjacency_matrix() == expected_order


def test_traverse_adjacency_matrix_on_expected_matrix(
    manure_manager: ManureManager,
    expected_adjacency_matrix: dict[str, dict[str, float]],
    expected_adjacency_matrix_after_merge: dict[str, dict[str, float]],
    mocker: MockerFixture,
) -> None:
    """Tests _traverse_adjacency_matrix() on the expected matrix."""
    manure_manager._adjacency_matrix = expected_adjacency_matrix
    manure_manager._all_separators = {"screw_press_1": MagicMock(Separator), "rotary_screen_1": MagicMock(Separator)}
    mock_merge = mocker.patch.object(
        manure_manager, "_merge_separator_rows", return_value=expected_adjacency_matrix_after_merge
    )
    assert manure_manager._traverse_adjacency_matrix() == [
        "alley_scraper_1",
        "anaerobic_digester_1",
        "rotary_screen_1",
        "flush_system_1",
        "parlor_cleaning_handler_1",
        "screw_press_1",
        "anaerobic_digester_2",
        "anaerobic_lagoon_1",
        "slurry_storage_outdoor_1",
    ]
    mock_merge.assert_called_once()


@pytest.mark.parametrize(
    "matrix, expected_order",
    [
        (
            {
                "A": {"A": 0.0, "B": 1.0, "C": 0.0},
                "B": {"A": 1.0, "B": 0.0, "C": 1.0},
                "C": {"A": 0.0, "B": 0.0, "C": 0.0},
            },
            ["A", "B", "C"],
        ),
    ],
)
def test_traverse_adjacency_matrix_cycle(
    matrix: dict[str, dict[str, float]],
    expected_order: list[str],
    manure_manager: ManureManager,
) -> None:
    """Tests _traverse_adjacency_matrix() when there's a cycle."""
    with pytest.raises(ValueError, match="Cycle detected — topological sort not possible."):
        manure_manager._adjacency_matrix = matrix
        manure_manager._traverse_adjacency_matrix()


@pytest.mark.parametrize(
    "adjacency_matrix, in_degree, queue, expected_constraints",
    [
        (
            {
                "A": {"A": 0.0, "B": 1.0, "C": 0.0},
                "B": {"A": 0.0, "B": 0.0, "C": 1.0},
                "C": {"A": 0.0, "B": 0.0, "C": 0.0},
            },
            {"A": 0, "B": 1, "C": 1},
            ["A"],
            [("A", "B"), ("B", "C")],
        )
    ],
)
def test_topological_sort_single_case(
    adjacency_matrix: dict[str, dict[str, float]],
    in_degree: dict[str, int],
    queue: list[str],
    expected_constraints: list[tuple[str, str]],
    manure_manager: ManureManager,
) -> None:
    """Tests _perform_topological_sort()."""
    manure_manager._adjacency_matrix = adjacency_matrix
    result = manure_manager._perform_topological_sort(in_degree.copy(), queue, adjacency_matrix)

    for before, after in expected_constraints:
        assert result.index(before) < result.index(after), f"{before} should come before {after}"

    assert set(result) == set(adjacency_matrix.keys())


def test_merge_separator_rows_valid(
    expected_adjacency_matrix: dict[str, dict[str, float]],
    expected_adjacency_matrix_after_merge: dict[str, dict[str, float]],
    manure_manager: ManureManager,
) -> None:
    """Tests _merge_separator_rows()."""
    manure_manager._adjacency_matrix = expected_adjacency_matrix
    manure_manager._all_separators = {"screw_press_1": MagicMock(Separator), "rotary_screen_1": MagicMock(Separator)}
    result = manure_manager._merge_separator_rows()
    assert result == expected_adjacency_matrix_after_merge


def test_merge_invalid_separator_rows(
    invalid_separator_adjacency_matrix: dict[str, dict[str, float]], manure_manager: ManureManager
) -> None:
    """Tests _merge_separator_rows() with invalid separator outputs."""
    with pytest.raises(ValueError):
        manure_manager._adjacency_matrix = invalid_separator_adjacency_matrix
        manure_manager._all_separators = {
            "screw_press_1": MagicMock(Separator),
            "rotary_screen_1": MagicMock(Separator),
        }
        manure_manager._merge_separator_rows()


@pytest.mark.parametrize(
    "manure_streams, processing_order, adjacency_matrix, expected_routing_calls",
    [
        (
            # One stream -> one processor -> one full proportion destination
            {"stream1": MagicMock(spec=ManureStream, pen_manure_data=MagicMock(first_processor="proc1"))},
            ["proc1", "proc2"],
            {"proc1": {"proc2": 1.0}},
            [("proc2", 1.0)],
        ),
        (
            # One stream -> split to two processors
            {"stream1": MagicMock(spec=ManureStream, pen_manure_data=MagicMock(first_processor="proc1"))},
            ["proc1", "proc2", "proc3"],
            {"proc1": {"proc2": 0.3, "proc3": 0.7}},
            [("proc2", 0.3), ("proc3", 0.7)],
        ),
        (
            # One stream -> one processor -> one separator -> one full proportion destination
            {"stream1": MagicMock(spec=ManureStream, pen_manure_data=MagicMock(first_processor="proc1"))},
            ["proc1", "separator1"],
            {"proc1": {"separator1_input": 1.0}},
            [("separator1", 1.0)],
        ),
    ],
)
def test_run_daily_update(
    manure_streams: dict[str, ManureStream],
    processing_order: list[str],
    adjacency_matrix: dict[str, dict[str, float]],
    expected_routing_calls: list[tuple[str, float]],
    manure_manager: ManureManager,
    mocker: MockerFixture,
) -> None:
    """Tests run_daily_update() with different processing orders and adjacency matrices."""
    manure_manager.all_processors = {}
    manure_manager._all_separators = {}
    manure_manager._processing_order = processing_order
    manure_manager._adjacency_matrix = adjacency_matrix

    mock_stream = MagicMock(spec=ManureStream)
    mock_stream.pen_manure_data = MagicMock(first_processor="proc1")
    split_mock = mocker.patch.object(mock_stream, "split_stream", return_value=MagicMock(spec=ManureStream))
    mock_build = mocker.patch.object(manure_manager, "_build_nutrient_pools")

    manure_streams = {"stream1": mock_stream}

    for name in processing_order:
        proc = MagicMock(spec=Separator if name.startswith("separator") else Processor)
        mocker.patch.object(proc, "receive_manure")
        mocker.patch.object(proc, "process_manure", return_value={"manure": mock_stream})
        manure_manager.all_processors[name] = proc

    if "separator1" in processing_order:
        manure_manager._all_separators["separator1"] = cast(Separator, manure_manager.all_processors["separator1"])

    time = MagicMock(spec=RufasTime)
    day_conditions = MagicMock(spec=CurrentDayConditions)
    manure_manager.run_daily_update(manure_streams, time, day_conditions)

    for name, proportion in expected_routing_calls:
        dest_processor = manure_manager.all_processors[name]
        if proportion == 1.0:
            dest_processor.receive_manure.assert_called_with(
                manure_manager.all_processors[processing_order[0]].process_manure.return_value["manure"]
            )
        else:
            split_mock.assert_any_call(proportion)
            dest_processor.receive_manure.assert_called()

        mock_build.assert_called_once()


def test_run_daily_update_missing_first_processor_raises_keyerror(
    mocker: MockerFixture, manure_manager: ManureManager
) -> None:
    """Test that run_daily_update raises KeyError when first processor is missing."""
    mock_stream = MagicMock(spec=ManureStream)
    mock_stream.pen_manure_data = MagicMock(first_processor="nonexistent_proc")

    manure_streams = cast(dict[str, ManureStream], {"stream1": mock_stream})
    manure_manager.all_processors = {}
    manure_manager._processing_order = []
    manure_manager._adjacency_matrix = {}

    mock_om = mocker.patch.object(manure_manager, "_om")
    mock_om.add_error = MagicMock()

    time = MagicMock(spec=RufasTime)
    day_conditions = MagicMock(spec=CurrentDayConditions)

    with pytest.raises(KeyError, match="Processor 'nonexistent_proc' not found in the system."):
        manure_manager.run_daily_update(manure_streams, time, day_conditions)

    mock_om.add_error.assert_called_once()


@pytest.fixture
def storage(mocker: MockerFixture) -> Storage:
    """Storage fixture for testing."""
    mocker.patch.object(Storage, "__init__", return_value=None)
    storage = Storage(
        name="fixture",
        is_housing_emissions_calculator=False,
        cover=StorageCover.COVER,
        storage_time_period=120,
        surface_area=300.0,
    )
    storage.name = "fixture"
    storage.is_housing_emissions_calculator = False
    storage._om = OutputManager()
    storage._cover = StorageCover.COVER
    storage._storage_time_period = 120
    storage._surface_area = 300.0
    storage._received_manure = ManureStream.make_empty_manure_stream()
    storage.stored_manure = ManureStream.make_empty_manure_stream()
    storage._prefix = "Storage.fixture"
    return storage


def test_build_nutrient_pools(mocker: MockerFixture, storage: Storage, manure_manager: ManureManager) -> None:
    """Test that _build_nutrient_pools() correctly adds nutrients to the nutrient manager."""
    mock_storage = storage

    manure_type = ManureType.LIQUID
    STORAGE_CLASS_TO_TYPE[type(mock_storage)] = manure_type

    mock_manager = manure_manager
    mock_manager.all_processors = {"storage1": mock_storage}

    mock_nutrient_manager = mocker.Mock()
    mock_manager._manure_nutrient_manager = mock_nutrient_manager

    mock_manager._build_nutrient_pools()

    mock_nutrient_manager.add_nutrients.assert_called_once()
    args, _ = mock_nutrient_manager.add_nutrients.call_args
    passed_nutrients = args[0]
    assert isinstance(passed_nutrients, ManureNutrients)
    assert passed_nutrients.manure_type == manure_type


def test_normalize_destination_name_separator_input_suffix(manure_manager: ManureManager) -> None:
    """Test that '_input' suffix is removed if base name is a known separator."""
    manure_manager._all_separators = {"separator1": MagicMock()}
    result = manure_manager._normalize_destination_name("separator1_input")
    assert result == "separator1"


def test_normalize_destination_name_suffix_but_not_separator(manure_manager: ManureManager) -> None:
    """Test that '_input' suffix is not removed if base name is not a known separator."""
    manure_manager._all_separators = {}
    result = manure_manager._normalize_destination_name("separator1_input")
    assert result == "separator1_input"


def test_normalize_destination_name_no_suffix(manure_manager: ManureManager) -> None:
    """Test that names without '_input' suffix are returned unchanged."""
    manure_manager._all_separators = {"separator1": MagicMock()}
    result = manure_manager._normalize_destination_name("processorA")
    assert result == "processorA"


@pytest.mark.parametrize(
    "processor_name, output_key, expected_result",
    [
        ("separator1", "manure", "separator1"),
        ("separator1", "solid", "separator1_solid_output"),
        ("separator1", "liquid", "separator1_liquid_output"),
    ],
)
def test_generate_origin_key_valid(
    processor_name: str, output_key: str, expected_result: str, manure_manager: ManureManager
) -> None:
    """Tests _generate_origin_key() with valid processor name and output key."""
    manure_manager._om = MagicMock()
    assert manure_manager._generate_origin_key(processor_name, output_key) == expected_result


def test_generate_origin_key_invalid_logs_and_raises(manure_manager: ManureManager) -> None:
    """Tests _generate_origin_key() with invalid processor name and output key."""
    manure_manager._om = MagicMock()

    with pytest.raises(ValueError, match="Unexpected output key 'gas'"):
        manure_manager._generate_origin_key("procX", "gas")

    manure_manager._om.add_error.assert_called_once_with(
        "Invalid Output Key",
        "Unexpected output key 'gas' from processor 'procX'.",
        {"class": "ManureManager", "function": "run_daily_update"},
    )


@pytest.mark.parametrize("animals_simulated", [True, False])
@pytest.mark.parametrize("use_supplemental_manure", [True, False])
@pytest.mark.parametrize("request_result_is_none", [True, False])
def test_request_nutrients(
    mocker: MockerFixture,
    animals_simulated: bool,
    use_supplemental_manure: bool,
    request_result_is_none: bool,
) -> None:
    """Test request_nutrients for all combinations of simulation, supplemental use, and request fulfillment."""

    # Arrange
    mock_time = mocker.MagicMock()
    mock_time.current_julian_day = 150
    mock_time.current_calendar_year = 2025
    mocker.patch("RUFAS.biophysical.manure.manure_manager.ManureManager.__init__", return_value=None)
    mock_add_log = mocker.patch.object(OutputManager, "add_log")
    manure_manager = ManureManager(0.6, 0.6, 0.6)
    manure_manager._manure_nutrient_manager = ManureNutrientManager()
    manure_manager._om = OutputManager()

    mock_nutrient_request = mocker.MagicMock()

    mock_nutrient_request.use_supplemental_manure = use_supplemental_manure
    mock_nutrient_request.manure_type = ManureType.LIQUID

    request_result = (
        None
        if request_result_is_none
        else NutrientRequestResults(nitrogen=10.0, phosphorus=5.0, total_manure_mass=50.0)
    )
    supplemental_result = NutrientRequestResults(nitrogen=5.0, phosphorus=2.5, total_manure_mass=25.0)
    mocker.patch.object(
        ManureNutrientManager, "handle_nutrient_request", return_value=(request_result, not use_supplemental_manure)
    )

    mocker.patch.object(ManureManager, "_record_manure_request_results")
    mock_field_request = mocker.patch.object(FieldManureSupplier, "request_nutrients", return_value=supplemental_result)
    mock_remove = mocker.patch.object(ManureManager, "_remove_nutrients_from_storage")
    mocker.patch.object(manure_manager, "_calculate_supplemental_manure_needed", return_value="calculated_supplemental")

    # Act
    actual_results = manure_manager.request_nutrients(mock_nutrient_request, animals_simulated, mock_time)

    # Assert
    if animals_simulated:
        if request_result_is_none:
            if use_supplemental_manure:
                mock_field_request.assert_called_once_with("calculated_supplemental")
                mock_remove.assert_not_called()
                assert actual_results == supplemental_result
            else:
                assert actual_results is None
        else:
            mock_remove.assert_called_once()
            if use_supplemental_manure:
                mock_add_log.assert_called_once()
                assert actual_results == request_result + supplemental_result
            else:
                assert actual_results == request_result

    else:
        mock_field_request.assert_called_once_with(mock_nutrient_request)
        assert actual_results == supplemental_result


@pytest.mark.parametrize("is_nitrogen_limiting_nutrient", [True, False])
def test_remove_nutrients_from_storage(
    manure_manager: ManureManager, is_nitrogen_limiting_nutrient: bool, mocker: MockerFixture
) -> None:
    """Tests the function _remove_nutrients_from_storage()."""
    mock_determine_limiting_nutrient = mocker.patch.object(
        ManureManager, "_determine_limiting_nutrient", return_value=is_nitrogen_limiting_nutrient
    )
    mock_proportion = mocker.patch.object(
        manure_manager, "_determine_nutrient_proportion_to_be_removed", return_value=0.8
    )
    mock_remove = mocker.patch.object(ManureNutrientManager, "remove_nutrients")
    mock_compute = mocker.patch.object(
        ManureManager, "_compute_stream_after_removal", return_value=(MagicMock(ManureStream), {"nitrogen": 50})
    )
    composting = MagicMock(Composting)
    composting.stored_manure = MagicMock(ManureStream)
    manure_manager.all_processors = {"non_storage": MagicMock(Digester), "storage": composting}

    manure_manager._remove_nutrients_from_storage(NutrientRequestResults(nitrogen=10, phosphorus=20), ManureType.LIQUID)

    mock_determine_limiting_nutrient.assert_called_once()
    if is_nitrogen_limiting_nutrient:
        mock_proportion.assert_called_once_with(10, 100)
    else:
        mock_proportion.assert_called_once_with(20, 200)
    mock_compute.assert_called_once()
    mock_remove.assert_called_once_with({"nitrogen": 50, "manure_type": None})


@pytest.mark.parametrize(
    "init_n, init_p, limiting_flag, available_limiting, removal_prop, "
    "exp_remain_n, exp_remain_p, exp_removed_n, exp_removed_p",
    [
        (100.0, 80.0, True, 50.0, 0.5, 50.0, 40, 50.0, 40.0),
        (120.0, 60.0, False, 24.0, 0.4, 72.0, 36.0, 48.0, 24.0),
        (50.0, 30.0, True, 50.0, 1.0, 0.0, 0.0, 50.0, 30.0),
    ],
)
def test_compute_stream_after_removal_with_real_manure_stream(
    init_n: float,
    init_p: float,
    limiting_flag: bool,
    available_limiting: float,
    removal_prop: float,
    exp_remain_n: float,
    exp_remain_p: float,
    exp_removed_n: float,
    exp_removed_p: float,
) -> None:
    """
    Verify compute_stream_after_removal() correctly updates only nitrogen and phosphorus
    on a real ManureStream, and leaves all other fields unchanged.
    """

    initial_stream = ManureStream(
        water=0.0,
        ammoniacal_nitrogen=0.0,
        nitrogen=init_n,
        phosphorus=init_p,
        potassium=0.0,
        ash=0.0,
        non_degradable_volatile_solids=0.0,
        degradable_volatile_solids=0.0,
        total_solids=0.0,
        volume=0.0,
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=0.0,
    )

    non_lim_fields: list[str] = []

    new_stream, removed = ManureManager._compute_stream_after_removal(
        stored_manure=initial_stream,
        nutrient_removal_proportion=removal_prop,
        is_nitrogen_limiting_nutrient=limiting_flag,
        non_limiting_fields=non_lim_fields,
    )

    assert pytest.approx(new_stream.nitrogen, rel=1e-6) == exp_remain_n
    assert pytest.approx(new_stream.phosphorus, rel=1e-6) == exp_remain_p

    assert pytest.approx(removed["nitrogen"], rel=1e-6) == exp_removed_n
    assert pytest.approx(removed["phosphorus"], rel=1e-6) == exp_removed_p

    for field_name in [
        "water",
        "ammoniacal_nitrogen",
        "potassium",
        "ash",
        "degradable_volatile_solids",
        "non_degradable_volatile_solids",
        "total_solids",
        "volume",
        "bedding_non_degradable_volatile_solids",
    ]:
        assert getattr(new_stream, field_name) == 0.0

    if limiting_flag:
        assert "phosphorus" in non_lim_fields
        assert "nitrogen" not in non_lim_fields
    else:
        assert "nitrogen" in non_lim_fields
        assert "phosphorus" not in non_lim_fields


@pytest.mark.parametrize(
    "portion, non_limiting, expected_removed",
    [
        (0.1, 50.0, 5.0),
        (0.1, 30.0, 3.0),
        (1.0, 50.0, 50.0),
    ],
)
def test_determine_non_limiting_nutrient_removal_amount(
    portion: float, non_limiting: float, expected_removed: float
) -> None:
    removed = ManureManager._determine_non_limiting_nutrient_removal_amount(
        limiting_nutrient_proportion_to_be_removed=portion,
        non_limiting_nutrients_amount=non_limiting,
    )
    assert pytest.approx(removed, rel=1e-8) == expected_removed


@pytest.mark.parametrize(
    "n_mass, p_mass, expected_is_nitrogen_limiting",
    [
        (10.0, 20.0, True),
        (20.0, 10.0, False),
        (15.0, 15.0, False),
    ],
)
def test_determine_limiting_nutrient_with_patched_scaling(
    mocker,
    n_mass,
    p_mass,
    expected_is_nitrogen_limiting,
) -> None:
    seq = [n_mass, p_mass]
    mocker.patch.object(
        ManureNutrientManager, "calculate_projected_manure_mass", side_effect=lambda requested, fraction: seq.pop(0)
    )

    is_nitrogen_limiting = ManureManager._determine_limiting_nutrient(
        requested_nitrogen_mass=5.0,
        nitrogen_fraction=0.2,
        requested_phosphorus_mass=3.0,
        phosphorus_fraction=0.4,
    )
    assert is_nitrogen_limiting is expected_is_nitrogen_limiting


@pytest.mark.parametrize(
    "requested_mass, available, expected_prop",
    [
        (20.0, 100.0, 0.2),
        (50.0, 50.0, 1.0),
        (120.0, 80.0, 1.0),
        (120.0, 0.0000001, 0.0),
    ],
)
def test_determine_limiting_nutrient_proportion_to_be_removed(
    requested_mass: float,
    available: float,
    expected_prop: float,
):
    prop = ManureManager._determine_nutrient_proportion_to_be_removed(
        limiting_nutrient_requested_mass=requested_mass,
        limited_nutrient_available=available,
    )
    assert pytest.approx(prop, rel=1e-5) == expected_prop


@pytest.mark.parametrize(
    "manure_request_results, expected_request_result_values, expected_log_called",
    [
        # Case 1: manure_request_results is None
        (
            None,
            {
                "dry_matter_mass": 0.0,
                "dry_matter_fraction": 0.0,
                "total_manure_mass": 0.0,
                "organic_nitrogen_fraction": 0.0,
                "inorganic_nitrogen_fraction": 0.0,
                "ammonium_nitrogen_fraction": 0.0,
                "organic_phosphorus_fraction": 0.0,
                "inorganic_phosphorus_fraction": 0.0,
                "nitrogen": 0.0,
                "phosphorus": 0.0,
                "request_julian_day": 150,
                "request_calendar_year": 2025,
            },
            True,
        ),
        # Case 2: manure_request_results has valid data
        (
            MagicMock(
                dry_matter=100.0,
                dry_matter_fraction=0.25,
                total_manure_mass=400.0,
                organic_nitrogen_fraction=0.15,
                inorganic_nitrogen_fraction=0.10,
                ammonium_nitrogen_fraction=0.05,
                organic_phosphorus_fraction=0.08,
                inorganic_phosphorus_fraction=0.02,
                nitrogen=50.0,
                phosphorus=10.0,
            ),
            {
                "dry_matter_mass": 100.0,
                "dry_matter_fraction": 0.25,
                "total_manure_mass": 400.0,
                "organic_nitrogen_fraction": 0.15,
                "inorganic_nitrogen_fraction": 0.10,
                "ammonium_nitrogen_fraction": 0.05,
                "organic_phosphorus_fraction": 0.08,
                "inorganic_phosphorus_fraction": 0.02,
                "nitrogen": 50.0,
                "phosphorus": 10.0,
                "request_julian_day": 150,
                "request_calendar_year": 2025,
            },
            False,
        ),
    ],
)
def test_record_manure_request_results_parametrized(
    mocker: MockerFixture,
    manure_request_results: MagicMock,
    expected_request_result_values: dict[str, float],
    expected_log_called: bool,
) -> None:
    """
    Parametrized unit test for the _record_manure_request_results method of the ManureManager class.
    """
    # Arrange
    manure_source = "on_farm_manure"
    mock_time = mocker.MagicMock()
    mock_time.current_julian_day = 150
    mock_time.current_calendar_year = 2025

    mocker.patch("RUFAS.biophysical.manure.manure_manager.ManureManager.__init__", return_value=None)
    manure_manager = ManureManager(0.5, 0.5, 0.5)

    mock_output_manager = mocker.MagicMock()
    manure_manager._om = mock_output_manager

    # Act
    manure_manager._record_manure_request_results(manure_request_results, manure_source, mock_time)

    # Assert
    if expected_log_called:
        mock_output_manager.add_log.assert_called_once_with(
            "Recording empty manure request result",
            "No manure available on farm to fulfill request.",
            {
                "class": "ManureManager",
                "function": "_record_manure_request_results",
                "units": {
                    "dry_matter_mass": MeasurementUnits.DRY_KILOGRAMS,
                    "dry_matter_fraction": MeasurementUnits.FRACTION,
                    "total_manure_mass": MeasurementUnits.KILOGRAMS,
                    "organic_nitrogen_fraction": MeasurementUnits.FRACTION,
                    "inorganic_nitrogen_fraction": MeasurementUnits.FRACTION,
                    "ammonium_nitrogen_fraction": MeasurementUnits.FRACTION,
                    "organic_phosphorus_fraction": MeasurementUnits.FRACTION,
                    "inorganic_phosphorus_fraction": MeasurementUnits.FRACTION,
                    "nitrogen": MeasurementUnits.KILOGRAMS,
                    "phosphorus": MeasurementUnits.KILOGRAMS,
                    "request_julian_day": MeasurementUnits.ORDINAL_DAY,
                    "request_calendar_year": MeasurementUnits.CALENDAR_YEAR,
                },
            },
        )
    else:
        mock_output_manager.add_log.assert_not_called()

    mock_output_manager.add_variable.assert_called_once()
    actual_manure_source, actual_request_result_values, actual_info_maps = mock_output_manager.add_variable.call_args[0]

    assert actual_manure_source == manure_source
    assert actual_request_result_values == expected_request_result_values

    expected_info_maps = {
        "class": "ManureManager",
        "function": "_record_manure_request_results",
        "units": {
            "dry_matter_mass": MeasurementUnits.DRY_KILOGRAMS,
            "dry_matter_fraction": MeasurementUnits.FRACTION,
            "total_manure_mass": MeasurementUnits.KILOGRAMS,
            "organic_nitrogen_fraction": MeasurementUnits.FRACTION,
            "inorganic_nitrogen_fraction": MeasurementUnits.FRACTION,
            "ammonium_nitrogen_fraction": MeasurementUnits.FRACTION,
            "organic_phosphorus_fraction": MeasurementUnits.FRACTION,
            "inorganic_phosphorus_fraction": MeasurementUnits.FRACTION,
            "nitrogen": MeasurementUnits.KILOGRAMS,
            "phosphorus": MeasurementUnits.KILOGRAMS,
            "request_julian_day": MeasurementUnits.ORDINAL_DAY,
            "request_calendar_year": MeasurementUnits.CALENDAR_YEAR,
        },
    }
    assert actual_info_maps == expected_info_maps


@pytest.mark.parametrize(
    "on_farm_manure, nutrient_request, expected_result",
    [
        # Scenario: No supplemental manure needed (on-farm manure fully satisfies the request)
        (
            NutrientRequestResults(
                nitrogen=10,
                phosphorus=5,
                total_manure_mass=15,
                organic_nitrogen_fraction=0.6,
                inorganic_nitrogen_fraction=0.4,
                ammonium_nitrogen_fraction=0.3,
                organic_phosphorus_fraction=0.5,
                inorganic_phosphorus_fraction=0.5,
                dry_matter=3,
                dry_matter_fraction=0.2,
            ),
            NutrientRequest(
                nitrogen=8,
                phosphorus=4,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=False,
            ),
            NutrientRequest(
                nitrogen=0.0,
                phosphorus=0.0,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=True,
            ),
        ),
        # Scenario: Partial supplemental manure needed (on-farm manure partially satisfies the request)
        (
            NutrientRequestResults(
                nitrogen=5,
                phosphorus=2,
                total_manure_mass=10,
                organic_nitrogen_fraction=0.7,
                inorganic_nitrogen_fraction=0.3,
                ammonium_nitrogen_fraction=0.5,
                organic_phosphorus_fraction=0.6,
                inorganic_phosphorus_fraction=0.4,
                dry_matter=2,
                dry_matter_fraction=0.1,
            ),
            NutrientRequest(
                nitrogen=8,
                phosphorus=5,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=False,
            ),
            NutrientRequest(
                nitrogen=3.0,
                phosphorus=3.0,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=True,
            ),
        ),
        # Scenario: All supplemental manure needed (on-farm manure provides nothing)
        (
            None,
            NutrientRequest(
                nitrogen=10,
                phosphorus=6,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=False,
            ),
            NutrientRequest(
                nitrogen=10.0,
                phosphorus=6.0,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=True,
            ),
        ),
    ],
)
def test_calculate_supplemental_manure_needed(
    on_farm_manure: NutrientRequestResults,
    nutrient_request: NutrientRequest,
    expected_result: NutrientRequest,
    mocker: MockFixture,
) -> None:
    """
    Unit test for the _calculate_supplemental_manure_needed static method.
    """
    # Arrange
    mocker.patch("RUFAS.biophysical.manure.manure_manager.ManureManager.__init__", return_value=None)
    manure_manager = ManureManager(0.6, 0.6, 0.6)
    # Act
    actual_result = manure_manager._calculate_supplemental_manure_needed(on_farm_manure, nutrient_request)

    # Assert
    assert math.isclose(actual_result.nitrogen, expected_result.nitrogen, abs_tol=1e-6)
    assert math.isclose(actual_result.phosphorus, expected_result.phosphorus, abs_tol=1e-6)
    assert actual_result.manure_type == expected_result.manure_type
    assert actual_result.use_supplemental_manure == expected_result.use_supplemental_manure
