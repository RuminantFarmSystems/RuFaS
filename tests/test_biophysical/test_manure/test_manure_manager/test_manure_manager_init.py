from typing import Any
from unittest.mock import call, MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.manure_manager import ManureManager
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.input_manager import InputManager

from tests.test_biophysical.test_manure.test_manure_manager.manure_manager_fixture import (
    manure_management_input_json,
    manure_manager,
    expected_processor_definitions_by_name,
    expected_processor_connections_by_name,
    expected_all_defined_processor_names,
    expected_all_referenced_processor_names,
    expected_all_separator_names,
    expected_all_processor_connections,
    expected_adjacency_matrix_keys,
    expected_adjacency_matrix,
    expected_empty_adjacency_matrix,
)


assert manure_management_input_json is not None
assert manure_manager is not None
assert expected_processor_definitions_by_name is not None
assert expected_processor_connections_by_name is not None
assert expected_all_defined_processor_names is not None
assert expected_all_referenced_processor_names is not None
assert expected_all_separator_names is not None
assert expected_all_processor_connections is not None
assert expected_adjacency_matrix_keys is not None
assert expected_adjacency_matrix is not None
assert expected_empty_adjacency_matrix is not None


def test_init(
    manure_management_input_json: dict[str, list[dict[str, Any]]],
    expected_processor_definitions_by_name: dict[str, dict[str, Any]],
    expected_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    mocker: MockerFixture,
) -> None:
    """Test for __init__() method of ManureManager class."""
    im = InputManager()
    mock_get_data = mocker.patch.object(im, "get_data", return_value=manure_management_input_json)
    mock_validate_unique_processor_names = mocker.patch(
        "RUFAS.biophysical.manure.manure_manager.ManureManager._validate_unique_processor_names",
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

    ManureManager()

    mock_get_data.assert_called_once_with("manure")
    mock_validate_unique_processor_names.assert_called_once_with(manure_management_input_json)
    mock_validate_and_parse_processor_connections.assert_called_once_with(
        manure_management_input_json, expected_processor_definitions_by_name
    )
    mock_create_all_processors.assert_called_once_with(
        expected_processor_connections_by_name, expected_processor_definitions_by_name
    )
    mock_populate_adjacency_matrix.assert_called_once_with(expected_processor_connections_by_name)


def test_validate_unique_processor_names(
    manure_manager: ManureManager,
    manure_management_input_json: dict[str, list[dict[str, Any]]],
    expected_all_defined_processor_names: list[str],
    expected_processor_definitions_by_name: dict[str, dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Test for _validate_unique_processor_names() method of ManureManager class."""
    mock_check_for_duplicate_processor_names = mocker.patch.object(
        manure_manager, "_check_for_duplicate_processor_names"
    )

    result = manure_manager._validate_unique_processor_names(manure_management_input_json)

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
    manure_management_input_json: dict[str, list[dict[str, Any]]],
    expected_processor_definitions_by_name: dict[str, dict[str, Any]],
    expected_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    expected_all_referenced_processor_names: list[str],
    expected_all_processor_connections: list[dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Test for _validate_and_parse_processor_connections() method of ManureManager class."""
    mock_find_all_referenced_processor_names = mocker.patch.object(
        manure_manager,
        "_find_all_processor_names_in_connection_map",
        return_value=expected_all_referenced_processor_names,
    )
    mock_build_processor_connection_map = mocker.patch.object(
        manure_manager, "_build_processor_connection_map", return_value=expected_processor_connections_by_name
    )
    mock_check_for_unknown_processor_names = mocker.patch.object(manure_manager, "_check_for_unknown_processor_names")
    mock_check_for_processors_without_connection_definition = mocker.patch.object(
        manure_manager, "_check_for_processors_without_connection_definition"
    )

    result = manure_manager._validate_and_parse_processor_connections(
        manure_management_input_json, expected_processor_definitions_by_name
    )

    assert result == expected_processor_connections_by_name
    mock_find_all_referenced_processor_names.assert_called_once_with(expected_all_processor_connections)
    mock_build_processor_connection_map.assert_called_once_with(expected_all_processor_connections)
    mock_check_for_unknown_processor_names.assert_called_once_with(
        expected_all_referenced_processor_names, expected_processor_definitions_by_name
    )
    mock_check_for_processors_without_connection_definition.assert_called_once_with(
        expected_all_referenced_processor_names, expected_processor_connections_by_name
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
    expected_all_referenced_processor_names: list[str],
    manure_manager: ManureManager,
) -> None:
    """Test for _find_all_processor_names_in_connection_map() method of ManureManager class."""
    result = manure_manager._find_all_processor_names_in_connection_map(expected_all_processor_connections)
    assert result == set(expected_all_referenced_processor_names)


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
        {"processor_name": "alley_scraper", "destinations": []}
    ]

    with pytest.raises(ValueError):
        manure_manager._build_processor_connection_map(all_processor_connections)
    mock_add_error.assert_called_once_with(
        "Duplicate processor connection definitions",
        "Duplicate connection definitions found for alley_scraper.",
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
        "RUFAS.biophysical.manure.digester.anaerobic_digester.AnaerobicDigester.__init__", return_value=None
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
        expected_processor_connections_by_name, expected_processor_definitions_by_name
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
    expected_all_referenced_processor_names: list[str],
    expected_all_separator_names: list[str],
    manure_manager: ManureManager,
    mocker: MockerFixture,
) -> None:
    """Test for _populate_adjacency_matrix() method of ManureManager class."""
    manure_manager._all_separators = {name: MagicMock(auto_spec=Separator) for name in expected_all_separator_names}
    expected_all_non_separator_processor_names = [
        name for name in expected_all_referenced_processor_names if name not in expected_all_separator_names
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
            for origin_name in expected_all_referenced_processor_names
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
    expected_all_referenced_processor_names: list[str],
    expected_all_separator_names: list[str],
    expected_empty_adjacency_matrix: dict[str, dict[str, float]],
    manure_manager: ManureManager,
) -> None:
    """Test for _create_column_in_adjacency_matrix() method of ManureManager class."""
    manure_manager._adjacency_matrix = {}
    expected_all_non_separator_processor_names = [
        name for name in expected_all_referenced_processor_names if name not in expected_all_separator_names
    ]

    for origin_name in expected_all_non_separator_processor_names:
        manure_manager._create_column_in_adjacency_matrix(origin_name, expected_adjacency_matrix_keys, False)
    for origin_name in expected_all_separator_names:
        manure_manager._create_column_in_adjacency_matrix(origin_name, expected_adjacency_matrix_keys, True)

    assert manure_manager._adjacency_matrix == expected_empty_adjacency_matrix


def test_populate_destination_proportions(
    expected_processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    expected_all_referenced_processor_names: list[str],
    expected_all_separator_names: list[str],
    expected_empty_adjacency_matrix: dict[str, dict[str, float]],
    expected_adjacency_matrix: dict[str, dict[str, float]],
    manure_manager: ManureManager,
) -> None:
    """Test for _populate_destination_proportions() method of ManureManager class."""
    manure_manager._adjacency_matrix = expected_empty_adjacency_matrix
    manure_manager._all_separators = {name: MagicMock(auto_spec=Separator) for name in expected_all_separator_names}

    expected_all_non_separator_processor_names = [
        name for name in expected_all_referenced_processor_names if name not in expected_all_separator_names
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
    expected_all_referenced_processor_names: list[str],
    expected_all_separator_names: list[str],
    expected_adjacency_matrix_keys: list[str],
    manure_manager: ManureManager,
) -> None:
    """Test for _generate_adjacency_matrix_keys() method of ManureManager class."""
    manure_manager.all_processors = {
        name: MagicMock(auto_spec=Processor) for name in expected_all_referenced_processor_names
    }
    manure_manager._all_separators = {name: MagicMock(auto_spec=Separator) for name in expected_all_separator_names}

    result = manure_manager._generate_adjacency_matrix_keys()
    assert result == expected_adjacency_matrix_keys
