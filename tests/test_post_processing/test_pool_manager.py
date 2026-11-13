import json
import os
import sys
from collections import Counter
from math import inf
from pathlib import Path
from typing import Any, Sequence, Type, cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.post_processing.file_manager import FileManager
from RUFAS.post_processing.pool_manager import PoolManager
from RUFAS.post_processing.shared_data_types import POOL_ELEMENT_TYPE
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


@pytest.fixture
def mock_file_manager(mocker: MockerFixture) -> MagicMock:
    file_manager: MagicMock = mocker.MagicMock(spec=FileManager)
    file_manager.metadata_prefix = "test_prefix"
    return file_manager


@pytest.fixture
def pool_manager(mock_file_manager: MagicMock) -> PoolManager:
    return PoolManager(mock_file_manager)


def assert_logged_once(mock_log_function: MagicMock, expected_name: str, expected_message: str) -> None:
    """Checks that a mocked logger function was called once with the given log name and fully formatted message."""
    mock_log_function.assert_called_once()
    message, *arguments = mock_log_function.call_args.args
    assert (message % tuple(arguments) if arguments else message) == expected_message
    assert mock_log_function.call_args.kwargs == {"extra": {"rufas_log_name": expected_name}}


def test_pool_manager_init(mock_file_manager: MagicMock) -> None:
    """Unit test for the __init__ method of PoolManager."""
    pool_manager = PoolManager(mock_file_manager)

    assert pool_manager.variables_pool == {}
    assert pool_manager.chunkification is False
    assert pool_manager.saved_pool_chunks_num == 0
    assert pool_manager.saved_pool_chunks_path is None
    assert pool_manager.available_memory == 0
    assert pool_manager.average_add_variable_call_addition == 118
    assert pool_manager.add_variable_call == 0
    assert pool_manager.save_chunk_threshold_call_count == 0
    assert pool_manager.current_pool_size == 0
    assert pool_manager.maximum_pool_size == inf
    assert pool_manager._variables_usage_counter == Counter()
    assert pool_manager.file_manager is mock_file_manager
    assert pool_manager.time is None
    assert pool_manager.exclude_info_maps is False


@pytest.mark.parametrize(
    "max_memory_usage, save_chunk_threshold_call_count, expected_threshold, expected_maximum_pool_size,"
    "expected_setting_message",
    [
        # User-defined save_chunk_threshold_call_count
        (0, 15000, 15000, inf, "The threshold add_variable_call count for saving pool chunk is set to 15000"),
        # User-defined save_chunk_threshold_call_count takes priority over max_memory_usage
        (2048, 15000, 15000, inf, "The threshold add_variable_call count for saving pool chunk is set to 15000"),
        # User-defined max_memory_usage
        (1024, 0, 0, 1024, "The maximum output variable pool size is set to 1024 Bytes"),
        (1024, None, 0, 1024, "The maximum output variable pool size is set to 1024 Bytes"),
        # User-defined max_memory_usage_percent
        (0, 0, 0, (80 / 100) * 1024, "The maximum output variable pool size is set to 819.2 Bytes"),
        (None, None, 0, (80 / 100) * 1024, "The maximum output variable pool size is set to 819.2 Bytes"),
    ],
)
def test_setup_pool_overflow_control(
    max_memory_usage: int | None,
    save_chunk_threshold_call_count: int | None,
    expected_threshold: int,
    expected_maximum_pool_size: float,
    expected_setting_message: str,
    pool_manager: PoolManager,
    mock_file_manager: MagicMock,
    mocker: MockerFixture,
) -> None:
    """Unit test for the setup_pool_overflow_control method of PoolManager."""
    mock_logger = mocker.patch("RUFAS.post_processing.pool_manager.logger")
    mocker.patch("RUFAS.post_processing.pool_manager.Utility.get_timestamp", return_value="dummy_timestamp")
    mocker.patch(
        "RUFAS.post_processing.pool_manager.psutil.virtual_memory", return_value=mocker.MagicMock(available=1024)
    )
    output_directory = Path("dummy/path")
    expected_saved_pool_chunks_path = Path.joinpath(output_directory, "saved_pool/test_prefix_dummy_timestamp")
    expected_log_message = (
        f"Created {expected_saved_pool_chunks_path} for saved pools during simulation.\n"
        f"Current system available memory: {1024 / (1024**3):.2f} GB = 1024 Bytes.\n"
        f"{expected_setting_message}"
    )

    pool_manager.setup_pool_overflow_control(output_directory, 80, max_memory_usage, save_chunk_threshold_call_count)

    assert pool_manager.chunkification is True
    assert pool_manager.available_memory == 1024
    assert pool_manager.saved_pool_chunks_path == expected_saved_pool_chunks_path
    assert pool_manager.save_chunk_threshold_call_count == expected_threshold
    assert pool_manager.maximum_pool_size == expected_maximum_pool_size
    mock_file_manager.create_directory.assert_called_once_with(expected_saved_pool_chunks_path)
    assert_logged_once(mock_logger.info, "Pool Overflow Control Setup", expected_log_message)


def test_pool_element_factory(pool_manager: PoolManager) -> None:
    """Unit test for the _pool_element_factory method of PoolManager."""
    first_element = pool_manager._pool_element_factory()
    second_element = pool_manager._pool_element_factory()

    assert first_element == {"info_maps": [], "values": []}
    assert first_element is not second_element
    assert first_element["info_maps"] is not second_element["info_maps"]
    assert first_element["values"] is not second_element["values"]


@pytest.mark.parametrize(
    "dummy_value, exclude_info_maps, first_map_only, is_daily_variable",
    [
        ("dummy_value", False, False, True),
        (2, False, False, False),
        (3.45, False, True, True),
        (True, False, True, False),
        ({"key": "value"}, False, True, True),
        ([1, 2, 3], False, False, False),
        ("dummy_value", True, False, True),
        (2, True, False, False),
        (3.45, True, True, True),
        (True, True, True, False),
        ({"key": "value"}, True, True, True),
        ([1, 2, 3], True, True, False),
    ],
)
def test_add_to_pool(
    pool_manager: PoolManager,
    dummy_value: Any,
    exclude_info_maps: bool,
    first_map_only: bool,
    is_daily_variable: bool,
) -> None:
    """Unit test for the _add_to_pool method of PoolManager."""
    info_map = {
        "class": "dummy_class",
        "function": "dummy_func",
        "context": "dummy_context",
        "units": MeasurementUnits.ANIMALS.value,
        "is_daily_variable": is_daily_variable,
    }
    key = "dummy_key"
    pool: dict[str, POOL_ELEMENT_TYPE] = {}
    pool_manager.exclude_info_maps = exclude_info_maps

    pool_manager._add_to_pool(pool, key, dummy_value, info_map, first_map_only)

    assert pool[key]["values"][0] == dummy_value
    if isinstance(dummy_value, (int, bool, float, str)):
        assert pool[key]["values"][0] is dummy_value
    else:
        assert pool[key]["values"][0] is not dummy_value

    if exclude_info_maps:
        assert pool[key]["info_maps"] == []
    else:
        assert pool[key]["info_maps"] == [
            {
                "context": "dummy_context",
                "units": MeasurementUnits.ANIMALS.value,
            },
        ]
    assert pool[key]["is_daily_variable"] is is_daily_variable

    info_map["more_context"] = "1234567890"

    pool_manager._add_to_pool(pool, key, dummy_value, info_map, first_map_only)

    assert pool[key]["values"][1] == dummy_value
    if isinstance(dummy_value, (int, bool, float, str)):
        assert pool[key]["values"][1] is dummy_value
    else:
        assert pool[key]["values"][1] is not dummy_value

    if exclude_info_maps:
        assert pool[key]["info_maps"] == []
    elif not first_map_only:
        assert pool[key]["info_maps"] == [
            {
                "context": "dummy_context",
                "units": MeasurementUnits.ANIMALS.value,
            },
            {
                "context": "dummy_context",
                "more_context": "1234567890",
                "units": MeasurementUnits.ANIMALS.value,
            },
        ]
    else:
        assert pool[key]["info_maps"] == [
            {
                "context": "dummy_context",
                "units": MeasurementUnits.ANIMALS.value,
            },
        ]
    assert pool[key]["is_daily_variable"] is is_daily_variable


def test_add_to_pool_does_not_keep_reference_to_mutable_value(pool_manager: PoolManager) -> None:
    """Changing a mutable value after it was added does not change the value held in the pool."""
    pool: dict[str, POOL_ELEMENT_TYPE] = {}
    value = {"nested": [1, 2, 3]}
    info_map = {"class": "dummy_class", "function": "dummy_func", "units": MeasurementUnits.ANIMALS.value}

    pool_manager._add_to_pool(pool, "dummy_key", value, info_map)
    value["nested"].append(4)

    assert pool["dummy_key"]["values"] == [{"nested": [1, 2, 3]}]


@pytest.mark.parametrize("daily_flag", ["missing", "True", 1, None])
def test_add_to_pool_defaults_missing_or_invalid_daily_flag_to_false(
    pool_manager: PoolManager, daily_flag: Any
) -> None:
    """Unit test for defaulting missing and non-boolean daily reporting flags to False."""
    pool: dict[str, POOL_ELEMENT_TYPE] = {}
    info_map = {
        "class": "dummy_class",
        "function": "dummy_func",
        "context": "dummy_context",
        "units": MeasurementUnits.ANIMALS.value,
    }
    if daily_flag != "missing":
        info_map["is_daily_variable"] = daily_flag

    pool_manager._add_to_pool(pool, "dummy_key", "dummy_value", info_map)

    assert pool["dummy_key"]["is_daily_variable"] is False
    assert pool["dummy_key"]["info_maps"] == [{"context": "dummy_context", "units": MeasurementUnits.ANIMALS.value}]


def test_add_to_pool_daily_flag_is_sticky_true(pool_manager: PoolManager) -> None:
    """A key marked daily once stays daily even if a later call omits or unsets the flag."""
    pool: dict[str, POOL_ELEMENT_TYPE] = {}
    base_info_map = {
        "class": "dummy_class",
        "function": "dummy_func",
        "context": "dummy_context",
        "units": MeasurementUnits.ANIMALS.value,
    }

    pool_manager._add_to_pool(pool, "k", "v", {**base_info_map, "is_daily_variable": True})
    assert pool["k"]["is_daily_variable"] is True

    pool_manager._add_to_pool(pool, "k", "v", {**base_info_map, "is_daily_variable": False})
    assert pool["k"]["is_daily_variable"] is True

    pool_manager._add_to_pool(pool, "k", "v", base_info_map)
    assert pool["k"]["is_daily_variable"] is True


@pytest.mark.parametrize(
    "manual_day, map_day, time_day, overwrite, expected",
    [
        (100, 80, 50, True, 100),  # overwrite with manual entry
        (100, 80, 50, False, 80),  # keep what's in the map
        (100, None, 50, True, 100),  # use manual entry
        (100, None, 50, False, 100),  # still use manual entry
        (None, None, 50, True, 50),  # use time
        (None, None, 50, False, 50),  # still use time
        (None, 80, 50, True, 50),  # overwrite with time
        (None, 80, 50, False, 80),  # don't overwrite with time
        (None, 80, None, True, 80),  # don't overwrite valid day with None
        (None, None, None, True, "warn"),  # no day available
    ],
)
def test_add_simulation_day_to_info_map(
    manual_day: int | None,
    map_day: int | None,
    time_day: int | None,
    overwrite: bool,
    expected: int | str,
    pool_manager: PoolManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _add_simulation_day_to_info_map method of PoolManager."""
    mock_logger = mocker.patch("RUFAS.post_processing.pool_manager.logger")
    if time_day is not None:
        pool_manager.time = mocker.MagicMock(spec=RufasTime, simulation_day=time_day)
    info_map: dict[str, Any] = {"class": "test", "function": "test_map_simulation_day"}
    if map_day is not None:
        info_map["simulation_day"] = map_day
    original_info_map = dict(info_map)

    actual = pool_manager._add_simulation_day_to_info_map(info_map, overwrite, manual_day, "test_name")

    assert info_map == original_info_map
    assert actual is not info_map
    if expected == "warn":
        assert actual == original_info_map
        assert_logged_once(
            mock_logger.warning,
            "no simulation_day available",
            "no simulation day was available to add to the info_map for variable test_name "
            "(from test.test_map_simulation_day)",
        )
    else:
        assert actual == {**original_info_map, "simulation_day": expected}
        mock_logger.warning.assert_not_called()


def test_add_simulation_day_to_info_map_time_without_simulation_day(
    pool_manager: PoolManager, mocker: MockerFixture
) -> None:
    """A ``time`` object that has no ``simulation_day`` is treated the same as having no ``time``."""
    mock_logger = mocker.patch("RUFAS.post_processing.pool_manager.logger")
    pool_manager.time = mocker.MagicMock(spec=[])
    info_map = {"class": "test", "function": "test_map_simulation_day"}

    actual = pool_manager._add_simulation_day_to_info_map(info_map)

    assert actual == info_map
    assert_logged_once(
        mock_logger.warning,
        "no simulation_day available",
        "no simulation day was available to add to the info_map for variable None (from test.test_map_simulation_day)",
    )


@pytest.mark.parametrize(
    "name, value, info_map, first_map, expected_exception",
    [
        # Everything correct, no exception should be raised, only first info map should be recorded
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, True, None),
        # Everything correct, no exception should be raised
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, False, None),
        # 'units' key missing, should raise KeyError
        ("var2", 200, {"class": "TestClass", "function": "test_function"}, True, KeyError),
        # Value is a dict, should process sub-keys
        (
            "var3",
            {"sub1": 10, "sub2": 20},
            {"class": "TestClass", "function": "test_function", "units": "kg"},
            True,
            None,
        ),
        # 'units' is a dict, but lengths do not match with value, should raise KeyError
        (
            "var4",
            [1, 2, 3],
            {"class": "TestClass", "function": "test_function", "units": {"key1": "kg", "key2": "g"}},
            True,
            KeyError,
        ),
        # 'units' is a dict, lengths match with value, no exception
        (
            "var5",
            [1, 2],
            {"class": "TestClass", "function": "test_function", "units": {"key1": "kg", "key2": "g"}},
            True,
            None,
        ),
        # 'units' is a dict, lengths do not match with value (empty value), no exception
        (
            "var6",
            {},
            {"class": "TestClass", "function": "test_function", "units": {"key1": "kg", "key2": "g"}},
            True,
            None,
        ),
    ],
)
def test_add_variable(
    name: str,
    value: Any,
    info_map: dict[str, Any],
    first_map: bool,
    expected_exception: Type[BaseException] | None,
    pool_manager: PoolManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for the add_variable method of PoolManager."""
    info_map = {**info_map, "simulation_day": 0}
    mocker.patch.object(pool_manager, "_stringify_units", return_value="validated_units")
    mocker.patch.object(pool_manager, "_generate_key", return_value="key_with_prefix")
    patched_add_to_pool = mocker.patch.object(pool_manager, "_add_to_pool")
    patched_save_current_variable_pool = mocker.patch.object(pool_manager, "_save_current_variable_pool")

    if expected_exception:
        with pytest.raises(expected_exception):
            pool_manager.add_variable(name, value, info_map, first_map)

        patched_add_to_pool.assert_not_called()
    else:
        pool_manager.add_variable(name, value, info_map, first_map)

        patched_add_to_pool.assert_called_once_with(
            pool_manager.variables_pool,
            "key_with_prefix",
            value,
            {**info_map, "units": "validated_units"},
            first_map,
        )
        expected_counter = {f"key_with_prefix.{k}": 0 for k in value} if isinstance(value, dict) else {}
        assert pool_manager._variables_usage_counter == expected_counter
    assert pool_manager.add_variable_call == 1
    assert pool_manager.current_pool_size == 0
    patched_save_current_variable_pool.assert_not_called()


def test_add_variable_adds_to_variables_pool(pool_manager: PoolManager) -> None:
    """Variables are stored under their generated key with stringified units and without the class and function."""
    info_map = {
        "class": "dummy_class",
        "function": "dummy_func",
        "context": "dummy_context",
        "units": {"first": MeasurementUnits.ANIMALS, "second": MeasurementUnits.DAYS},
        "simulation_day": 3,
        "is_daily_variable": True,
    }
    expected_info_map = {
        "context": "dummy_context",
        "units": {"first": MeasurementUnits.ANIMALS.value, "second": MeasurementUnits.DAYS.value},
        "simulation_day": 3,
    }

    pool_manager.add_variable("dummy_name", {"first": 1, "second": 2}, info_map)
    pool_manager.add_variable("dummy_name", {"first": 3, "second": 4}, info_map)

    assert pool_manager.variables_pool == {
        "dummy_class.dummy_func.dummy_name": {
            "info_maps": [expected_info_map, expected_info_map],
            "values": [{"first": 1, "second": 2}, {"first": 3, "second": 4}],
            "is_daily_variable": True,
        }
    }
    assert pool_manager._variables_usage_counter == {
        "dummy_class.dummy_func.dummy_name.first": 0,
        "dummy_class.dummy_func.dummy_name.second": 0,
    }
    assert pool_manager.add_variable_call == 2


# fully factorial parameterization:
@pytest.mark.parametrize("manual_day", [100, None])
@pytest.mark.parametrize("map_day", [80, None])
@pytest.mark.parametrize("time_day", [50, None])
@pytest.mark.parametrize("overwrite", [True, False])
def test_add_variable_info_map_simulation_day(
    manual_day: int | None,
    map_day: int | None,
    time_day: int | None,
    overwrite: bool,
    pool_manager: PoolManager,
    mocker: MockerFixture,
) -> None:
    """
    Test that add_variable properly adds simulation_day to the info map and respects previously specified
    simulation_day value, unless the overwrite_simulation_day option is used.
    """
    mocker.patch("RUFAS.post_processing.pool_manager.logger")
    if time_day is not None:
        pool_manager.time = mocker.MagicMock(spec=RufasTime, simulation_day=time_day)
    info_map: dict[str, Any] = {
        "class": "test",
        "function": "test_map_simulation_day",
        "units": MeasurementUnits.UNITLESS,
    }
    if map_day is not None:
        info_map["simulation_day"] = map_day

    pool_manager.add_variable("test_var", "time flies!", info_map, False, overwrite, manual_day)

    saved_info_map = pool_manager.variables_pool["test.test_map_simulation_day.test_var"]["info_maps"][0]
    observed_day = saved_info_map.get("simulation_day")

    if overwrite and manual_day is not None:
        assert observed_day == manual_day
    elif overwrite and time_day is not None:
        assert observed_day == time_day
    elif map_day is not None:
        assert observed_day == map_day
    elif manual_day is not None:
        assert observed_day == manual_day
    elif time_day is not None:
        assert observed_day == time_day
    else:
        assert observed_day is None


@pytest.mark.parametrize(
    "add_variable_call, save_chunk_threshold_call_count, maximum_pool_size, is_pool_saved",
    [
        # The threshold add_variable_call count is specified and reached
        (9, 10, inf, True),
        # The threshold add_variable_call count is specified and not reached
        (8, 10, inf, False),
        # The threshold add_variable_call count is specified, the maximum pool size is not checked
        (8, 10, 2000, False),
        # The threshold add_variable_call count is not specified and the maximum pool size is reached
        (9, 0, 2000, True),
        (9, 0, 2048, True),
        # The threshold add_variable_call count is not specified and the maximum pool size is not reached
        (9, 0, 4096, False),
    ],
)
@pytest.mark.parametrize(
    "name, value, first_map",
    [
        ("var1", 100, True),
        ("var1", 100, False),
        ("var3", {"sub1": 10, "sub2": 20}, True),
    ],
)
def test_add_variable_chunkification(
    name: str,
    value: Any,
    first_map: bool,
    add_variable_call: int,
    save_chunk_threshold_call_count: int,
    maximum_pool_size: float,
    is_pool_saved: bool,
    pool_manager: PoolManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for the add_variable method of PoolManager when chunkification is on."""
    info_map = {"class": "TestClass", "function": "test_function", "units": "kg", "simulation_day": 0}
    pool_manager.chunkification = True
    pool_manager.current_pool_size = 1024
    pool_manager.average_add_variable_call_addition = 1024
    pool_manager.maximum_pool_size = maximum_pool_size
    pool_manager.add_variable_call = add_variable_call
    pool_manager.save_chunk_threshold_call_count = save_chunk_threshold_call_count
    mocker.patch.object(pool_manager, "_stringify_units", return_value="validated_units")
    mocker.patch.object(pool_manager, "_generate_key", return_value="key_with_prefix")
    patched_add_to_pool = mocker.patch.object(pool_manager, "_add_to_pool")
    patched_save_current_variable_pool = mocker.patch.object(pool_manager, "_save_current_variable_pool")

    pool_manager.add_variable(name, value, info_map, first_map)

    patched_add_to_pool.assert_called_once_with(
        pool_manager.variables_pool,
        "key_with_prefix",
        value,
        {**info_map, "units": "validated_units"},
        first_map,
    )
    expected_counter = {f"key_with_prefix.{k}": 0 for k in value} if isinstance(value, dict) else {}
    assert pool_manager._variables_usage_counter == expected_counter
    assert pool_manager.current_pool_size == 1024 + 1024
    assert pool_manager.add_variable_call == add_variable_call + 1
    assert patched_save_current_variable_pool.call_count == (1 if is_pool_saved else 0)


@pytest.mark.parametrize(
    "variables, info_maps, first_info_map_only",
    [
        (
            {"var1": 100, "var2": 200},
            [
                {"class": "TestClass", "function": "test_function", "units": "kg"},
                {"class": "TestClass", "function": "test_function", "units": "kg"},
            ],
            True,
        ),
        ({}, [], False),
        (
            {"var1": 100, "var2": 200},
            [
                {"class": "TestClass", "function": "test_function", "units": "kg"},
                {"class": "TestClass", "function": "test_function", "units": "m"},
            ],
            True,
        ),
        (
            {f"var{i}": i for i in range(1000)},
            [{"class": "TestClass", "function": "test_function", "units": "kg"}] * 1000,
            False,
        ),
        ({"var1": 100}, [{"class": "TestClass", "function": "test_function", "units": "kg"}], False),
    ],
)
def test_add_variable_bulk(
    variables: dict[str, Any],
    info_maps: list[dict[str, Any]],
    first_info_map_only: bool,
    pool_manager: PoolManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for the add_variable_bulk method of PoolManager."""
    mock_add_variable = mocker.patch.object(pool_manager, "add_variable")
    inputs = [({name: value}, info_maps[index]) for index, (name, value) in enumerate(variables.items())]

    pool_manager.add_variable_bulk(inputs, first_info_map_only)

    assert mock_add_variable.call_args_list == [
        mocker.call(name, value, info_maps[index], first_info_map_only, False)
        for index, (name, value) in enumerate(variables.items())
    ]


@pytest.mark.parametrize(
    "values_and_days, record_day",
    [
        # Included simulation day matches the current (recording) day
        ([(212.6, 132), (200.01, 132), (198.6, 132)], 132),
        # No day provided in info map
        ([(212.6, None), (200.01, None), (198.6, None)], 132),
        # Provided days are different and don't match the recording day
        ([(212.6, 25), (200.01, 200), (198.6, 365)], 366),
        # Different and complex data types
        (
            [
                ([1, 2, 3, 4, 5], 115),
                ((1, 2, 3), 120),
                ("hello!", 100),
                ({"speak": "woof"}, 118),
                ({"x": 235, "y": (1, 2), "z": [10, 9, 8]}, 45),
            ],
            132,
        ),
    ],
)
@pytest.mark.parametrize("overwrite", [True, False])
def test_add_variable_bulk_info_map_simulation_day(
    values_and_days: list[tuple[Any, int | None]],
    record_day: int,
    overwrite: bool,
    pool_manager: PoolManager,
    mocker: MockerFixture,
) -> None:
    """Test that add_variable_bulk adds the recording day to info maps, overwriting provided days only when asked."""
    pool_manager.time = mocker.MagicMock(spec=RufasTime, simulation_day=record_day)
    variables: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for index, (value, day) in enumerate(values_and_days):
        info_map: dict[str, Any] = {
            "class": "testClass",
            "function": "test_function",
            "units": MeasurementUnits.UNITLESS,
        }
        if day is not None:
            info_map["simulation_day"] = day
        variables.append(({f"var_{index}": value}, info_map))

    pool_manager.add_variable_bulk(variables=variables, first_info_map_only=False, overwrite_simulation_day=overwrite)

    if overwrite:
        expected_days = [record_day] * len(variables)
    else:
        expected_days = [day if day is not None else record_day for _, day in values_and_days]
    assert [
        pool_manager.variables_pool[f"testClass.test_function.var_{index}"]["info_maps"][0]["simulation_day"]
        for index in range(len(variables))
    ] == expected_days


def test_save_current_variable_pool(
    pool_manager: PoolManager, mock_file_manager: MagicMock, mocker: MockerFixture
) -> None:
    """Unit test for the _save_current_variable_pool method of PoolManager."""
    mock_logger = mocker.patch("RUFAS.post_processing.pool_manager.logger")
    dummy_variable_pool: dict[str, POOL_ELEMENT_TYPE] = {
        "a": {"values": [1]},
        "b": {"values": ["B"]},
        "c": {"values": [True]},
    }
    pool_manager.saved_pool_chunks_path = Path("dummy_path")
    pool_manager.saved_pool_chunks_num = 0
    pool_manager.variables_pool = dummy_variable_pool
    pool_manager.current_pool_size = 1024
    mock_file_manager.generate_file_name.return_value = "dummy_file.json"
    dummy_file_path = Path("dummy_path", "dummy_file.json")

    pool_manager._save_current_variable_pool()

    mock_file_manager.generate_file_name.assert_called_once_with("saved_pool_0", "json")
    mock_file_manager.dict_to_file_json.assert_called_once_with(
        data_dict=dummy_variable_pool, path=dummy_file_path, minify_output_file=True
    )
    assert_logged_once(
        mock_logger.info, "save_current_variable_pool", f"Saved the current variable pool to {dummy_file_path}"
    )
    assert pool_manager.variables_pool == {}
    assert pool_manager.variables_pool is not dummy_variable_pool
    assert pool_manager.current_pool_size == sys.getsizeof({}.__repr__())
    assert pool_manager.saved_pool_chunks_num == 1


@pytest.mark.parametrize(
    "units, expected_result",
    [
        (MeasurementUnits.ANIMALS, MeasurementUnits.ANIMALS.value),
        (
            {
                "first": MeasurementUnits.ANIMALS,
                "second": MeasurementUnits.ANIMALS,
                "nested": {"third": MeasurementUnits.DAYS},
            },
            {
                "first": MeasurementUnits.ANIMALS.value,
                "second": MeasurementUnits.ANIMALS.value,
                "nested": {"third": MeasurementUnits.DAYS.value},
            },
        ),
        ({}, {}),
    ],
)
def test_stringify_units(
    pool_manager: PoolManager,
    units: dict[str, Any] | MeasurementUnits,
    expected_result: dict[str, Any] | str,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _stringify_units method of PoolManager."""
    mock_logger = mocker.patch("RUFAS.post_processing.pool_manager.logger")

    assert pool_manager._stringify_units(units) == expected_result
    mock_logger.error.assert_not_called()


@pytest.mark.parametrize(
    "units, expected_message",
    [
        (
            "invalid_unit",
            "The following unit does not have the type MeasurementUnits: invalid_unit (type <class 'str'>).",
        ),
        (
            {"first": MeasurementUnits.ANIMALS, "invalid": "not_a_unit"},
            "The following unit does not have the type MeasurementUnits: not_a_unit (type <class 'str'>).",
        ),
        (
            {"first": {"nested_invalid": "definitely_not_a_unit"}, "second": MeasurementUnits.ANIMALS},
            "The following unit does not have the type MeasurementUnits: definitely_not_a_unit (type <class 'str'>).",
        ),
        (
            {"first": MeasurementUnits.ANIMALS, "invalid_type": 123},
            "The following unit does not have the type MeasurementUnits: 123 (type <class 'int'>).",
        ),
        (
            {"first": {"nested_invalid_type": True}, "second": MeasurementUnits.ANIMALS},
            "The following unit does not have the type MeasurementUnits: True (type <class 'bool'>).",
        ),
    ],
)
def test_stringify_units_invalid_units(
    pool_manager: PoolManager, units: Any, expected_message: str, mocker: MockerFixture
) -> None:
    """Unit test for the _stringify_units method of PoolManager when a unit is not a ``MeasurementUnits``."""
    mock_logger = mocker.patch("RUFAS.post_processing.pool_manager.logger")

    with pytest.raises(TypeError) as error:
        pool_manager._stringify_units(units)

    assert str(error.value) == expected_message
    assert_logged_once(mock_logger.error, "invalid_units_type", expected_message)


def test_generate_key(pool_manager: PoolManager) -> None:
    """Unit test for the _generate_key method of PoolManager."""
    with pytest.raises(KeyError, match="'class' was not found in info_map"):
        pool_manager._generate_key("name", {})

    with pytest.raises(KeyError, match="'function' was not found in info_map"):
        pool_manager._generate_key("name", {"class": "test"})

    info_map: dict[str, str | bool] = {"class": "dummy_class", "function": "dummy_func"}
    assert pool_manager._generate_key("key_name", info_map) == "dummy_class.dummy_func.key_name"

    info_map["suppress_prefix"] = True
    assert pool_manager._generate_key("key_name", info_map) == "key_name"

    info_map["suppress_prefix"] = False
    assert pool_manager._generate_key("key_name", info_map) == "dummy_class.dummy_func.key_name"

    info_map["suppress_prefix"] = True
    info_map["prefix"] = "dummy_prefix"
    assert pool_manager._generate_key("key_name", info_map) == "dummy_prefix.key_name"

    info_map["suffix"] = "dummy_suffix"
    assert pool_manager._generate_key("key_name", info_map) == "dummy_prefix.key_name.dummy_suffix"

    del info_map["prefix"]
    info_map["suppress_prefix"] = False
    assert pool_manager._generate_key("key_name", info_map) == "dummy_class.dummy_func.key_name.dummy_suffix"


@pytest.mark.parametrize(
    "info_map",
    [{"class": True, "function": "dummy_func"}, {"class": "dummy_class", "function": True}],
)
def test_generate_key_class_or_function_not_a_string(
    pool_manager: PoolManager, info_map: dict[str, str | bool]
) -> None:
    """No prefix is generated when the class or the function in the info map is not a string."""
    assert pool_manager._generate_key("key_name", info_map) == "key_name"


def test_get_prefix(pool_manager: PoolManager) -> None:
    """Unit test for the _get_prefix method of PoolManager."""
    assert pool_manager._get_prefix("class", "func") == "class.func"


def test_sort_saved_chunk_files(pool_manager: PoolManager, tmp_path: Path) -> None:
    """Unit test for the _sort_saved_chunk_files method of PoolManager."""
    (tmp_path / "saved_pool_1_dummy_timestamp.json").write_text("File 1 content")
    (tmp_path / "saved_pool_10_dummy_timestamp.json").write_text("File 10 content")
    (tmp_path / "saved_pool_0_dummy_timestamp.json").write_text("File 0 content")
    (tmp_path / "saved_pool_3_dummy_timestamp.json").write_text("File 3 content")
    (tmp_path / "saved_pool_2_dummy_timestamp.txt").write_text("File 2 content")
    (tmp_path / "saved_pool_4_dummy_timestamp.json").mkdir()
    pool_manager.saved_pool_chunks_path = tmp_path

    result = pool_manager._sort_saved_chunk_files()

    assert result == [
        tmp_path / "saved_pool_0_dummy_timestamp.json",
        tmp_path / "saved_pool_1_dummy_timestamp.json",
        tmp_path / "saved_pool_3_dummy_timestamp.json",
        tmp_path / "saved_pool_10_dummy_timestamp.json",
    ]


def test_load_saved_pools(pool_manager: PoolManager, mocker: MockerFixture) -> None:
    """Unit test for the load_saved_pools method of PoolManager."""
    expected = {
        "a": {"values": [0, 1, 2, 3, 4, 5, 6, 7, 8], "info_maps": [{}, {}, {}, {}, {}, {}]},
        "b": {"values": ["a", "b", "c", "d", "e", "f"], "info_maps": [{}, {}, {}, {}, {}, {}]},
        "c": {"values": [True, True, True], "info_maps": [{}, {}, {}]},
        "d": {"values": [1.1, 2.2, 3.3], "info_maps": [{}, {}, {}]},
    }
    sorted_files = [Path("file1.json"), Path("file2.json")]
    mock_pools: dict[Path, dict[str, POOL_ELEMENT_TYPE]] = {
        Path("file1.json"): {
            "a": {"info_maps": [{}, {}], "values": [0, 1]},
            "b": {"info_maps": [{}, {}], "values": ["a", "b"]},
            "c": {"info_maps": [{}], "values": [True]},
        },
        Path("file2.json"): {
            "a": {"info_maps": [{}, {}, {}, {}], "values": [2, 3, 4, 5, 6, 7, 8]},
            "b": {"info_maps": [{}, {}, {}, {}], "values": ["c", "d", "e", "f"]},
            "c": {"info_maps": [{}, {}], "values": [True, True]},
            "d": {"info_maps": [{}, {}, {}], "values": [1.1, 2.2, 3.3]},
        },
    }
    mocker.patch.object(pool_manager, "_sort_saved_chunk_files", return_value=sorted_files)
    mock_load = mocker.patch.object(
        pool_manager,
        "load_variables_pool_from_file",
        side_effect=lambda file: setattr(pool_manager, "variables_pool", mock_pools[file]),
    )

    pool_manager.load_saved_pools()

    assert mock_load.call_args_list == [mocker.call(Path("file1.json")), mocker.call(Path("file2.json"))]
    assert pool_manager.variables_pool == expected
    assert pool_manager.current_pool_size == sys.getsizeof(expected)


def test_load_saved_pools_no_saved_chunks(pool_manager: PoolManager, mocker: MockerFixture) -> None:
    """Unit test for the load_saved_pools method of PoolManager when there are no saved chunks to load."""
    pool_manager.variables_pool = {"a": {"values": [1], "info_maps": [{}]}}
    mocker.patch.object(pool_manager, "_sort_saved_chunk_files", return_value=[])
    mock_load = mocker.patch.object(pool_manager, "load_variables_pool_from_file")

    pool_manager.load_saved_pools()

    mock_load.assert_not_called()
    assert pool_manager.variables_pool == {}
    assert pool_manager.current_pool_size == sys.getsizeof({})


def test_load_variables_pool_from_file(pool_manager: PoolManager, mock_file_manager: MagicMock) -> None:
    """Unit test for the load_variables_pool_from_file method of PoolManager."""
    dummy_data = {
        "var1": {"values": [1, 2, 3], "info_maps": [{"units": "kg"}]},
        "var2": {"values": [{"a": 1, "b": 2}], "info_maps": []},
    }
    mock_file_manager._read_variables_pool_file.return_value = dummy_data

    pool_manager.load_variables_pool_from_file(Path("path/to/file"))

    mock_file_manager._read_variables_pool_file.assert_called_once_with(
        Path("path/to/file"), {"class": "PoolManager", "function": "load_variables_pool_from_file"}
    )
    assert pool_manager.variables_pool is dummy_data
    assert pool_manager.current_pool_size == sys.getsizeof(dummy_data.__repr__())


@pytest.mark.parametrize(
    "exception",
    [FileNotFoundError("The file does not exist."), json.JSONDecodeError("Expecting value", "not valid JSON", 0)],
)
def test_load_variables_pool_from_file_raises_exception(
    exception: Exception, pool_manager: PoolManager, mock_file_manager: MagicMock
) -> None:
    """The exceptions raised while reading the file are not caught and the ``variables_pool`` is left unchanged."""
    original_pool: dict[str, POOL_ELEMENT_TYPE] = {"var1": {"values": [1], "info_maps": [{"units": "kg"}]}}
    pool_manager.variables_pool = original_pool
    pool_manager.current_pool_size = 1024
    mock_file_manager._read_variables_pool_file.side_effect = exception

    with pytest.raises(type(exception)):
        pool_manager.load_variables_pool_from_file(Path("bad/file/path"))

    assert pool_manager.variables_pool is original_pool
    assert pool_manager.current_pool_size == 1024


def test_load_multiple_variables_pools_from_files_mixed_descriptors(
    pool_manager: PoolManager, mock_file_manager: MagicMock, mocker: MockerFixture
) -> None:
    """Loads pools from a tuple(Path) and a dict(str path), passes correct info_map, and namespaces results."""
    pools_input: Sequence[tuple[str, Path] | dict[str, Any]] = [
        ("poolA", Path("a.json")),
        {"name": "poolB", "path": "b.json"},
    ]
    loaded_pool_a: dict[str, POOL_ELEMENT_TYPE] = {"varA": {"values": [1], "info_maps": [{"units": "kg"}]}}
    loaded_pool_b: dict[str, POOL_ELEMENT_TYPE] = {"varB": {"values": [2], "info_maps": [{"units": "m"}]}}
    mock_file_manager._read_variables_pool_file.side_effect = [loaded_pool_a, loaded_pool_b]
    set_pool_mock = mocker.patch.object(pool_manager, "_set_variables_pool")

    pool_manager.load_multiple_variables_pools_from_files(pools_input)

    expected_info_map = {"class": "PoolManager", "function": "load_multiple_variables_pools_from_files"}
    assert mock_file_manager._read_variables_pool_file.call_args_list == [
        mocker.call(Path("a.json"), {**expected_info_map, "pool_name": "poolA"}),
        mocker.call(Path("b.json"), {**expected_info_map, "pool_name": "poolB"}),
    ]
    set_pool_mock.assert_called_once_with({"poolA": loaded_pool_a, "poolB": loaded_pool_b})


def test_load_multiple_variables_pools_from_files_only_tuples(
    pool_manager: PoolManager, mock_file_manager: MagicMock
) -> None:
    """Loads pools when all descriptors are (name, Path) tuples and preserves namespacing."""
    pools_input = [
        ("X", Path("x.json")),
        ("Y", Path("y.json")),
    ]
    loaded_x: dict[str, POOL_ELEMENT_TYPE] = {"vx": {"values": [10], "info_maps": [{"units": "kg"}]}}
    loaded_y: dict[str, POOL_ELEMENT_TYPE] = {"vy": {"values": [20], "info_maps": [{"units": "kg"}]}}
    mock_file_manager._read_variables_pool_file.side_effect = [loaded_x, loaded_y]

    pool_manager.load_multiple_variables_pools_from_files(pools_input)

    assert mock_file_manager._read_variables_pool_file.call_count == 2
    assert mock_file_manager._read_variables_pool_file.call_args_list[0].args[0] == Path("x.json")
    assert mock_file_manager._read_variables_pool_file.call_args_list[1].args[0] == Path("y.json")
    expected_pool = {"X": loaded_x, "Y": loaded_y}
    assert pool_manager.variables_pool == expected_pool
    assert pool_manager.current_pool_size == sys.getsizeof(expected_pool.__repr__())


def test_load_multiple_variables_pools_from_files_empty_input(
    pool_manager: PoolManager, mock_file_manager: MagicMock, mocker: MockerFixture
) -> None:
    """If no pools are provided, _set_variables_pool is called with an empty dict."""
    set_pool_mock = mocker.patch.object(pool_manager, "_set_variables_pool")

    pool_manager.load_multiple_variables_pools_from_files([])

    mock_file_manager._read_variables_pool_file.assert_not_called()
    set_pool_mock.assert_called_once_with({})


@pytest.mark.parametrize(
    "usage_counter, expected_variable_names, expected_usage_counts",
    [
        (Counter(), [], []),
        (Counter({"var_b": 2, "var_a.sub": 0, "var_c": 5}), ["var_c", "var_b", "var_a.sub"], [5, 2, 0]),
    ],
)
def test_report_variables_usage_counts(
    usage_counter: Counter[str],
    expected_variable_names: list[str],
    expected_usage_counts: list[int],
    pool_manager: PoolManager,
    mock_file_manager: MagicMock,
    mocker: MockerFixture,
) -> None:
    """Unit test for the report_variables_usage_counts method of PoolManager."""
    path = Path("/fake/directory")
    pool_manager._variables_usage_counter = usage_counter
    pool_manager.variables_pool = {
        "daily_variable": {"values": [1, 2], "info_maps": [], "is_daily_variable": True},
        "non_daily_variable": {"values": [1, 2, 3], "info_maps": [], "is_daily_variable": False},
    }
    mock_file_manager.generate_file_name.side_effect = [
        "variables_usage_counts.csv",
        "variables_reported_daily.csv",
        "variables_not_reported_daily.csv",
    ]

    pool_manager.report_variables_usage_counts(path)

    assert mock_file_manager.generate_file_name.call_args_list == [
        mocker.call("variables_usage_counts", "csv"),
        mocker.call("variables_reported_daily", "csv"),
        mocker.call("variables_not_reported_daily", "csv"),
    ]
    assert mock_file_manager._dict_to_file_csv.call_args_list == [
        mocker.call(
            {"variable_name": {"values": expected_variable_names}, "usage_count": {"values": expected_usage_counts}},
            Path(path, "variables_usage_counts.csv"),
        ),
        mocker.call({"variable_name": {"values": ["daily_variable"]}}, Path(path, "variables_reported_daily.csv")),
        mocker.call(
            {"variable_name": {"values": ["non_daily_variable"]}, "report_count": {"values": [3]}},
            Path(path, "variables_not_reported_daily.csv"),
        ),
    ]


def test_get_variables_reported_daily(pool_manager: PoolManager) -> None:
    """Unit test for reporting variables explicitly marked as daily."""
    pool_manager.variables_pool = {
        "daily_variable": {
            "values": [1, 2, 3, 4],
            "info_maps": [{"units": "kg"}] * 4,
            "is_daily_variable": True,
        },
        "daily_nested_variable": {
            "values": [{"a": 1, "b": 2}, {"a": 3, "b": 4}, {"a": 5, "b": 6}, {"a": 7, "b": 8}],
            "info_maps": [{"units": {"a": "kg", "b": "kg"}}] * 4,
            "is_daily_variable": True,
        },
        "non_daily_variable": {
            "values": [10, 20, 30, 40],
            "info_maps": [{"units": "kg"}] * 4,
            "is_daily_variable": False,
        },
        "daily_variable_without_list_of_values": {
            "values": 1,
            "info_maps": [{"units": "kg"}],
            "is_daily_variable": True,
        },
    }

    actual = pool_manager._get_variables_reported_daily()

    assert actual == {
        "variable_name": {"values": ["daily_nested_variable.a", "daily_nested_variable.b", "daily_variable"]}
    }


def test_get_variables_not_reported_daily(pool_manager: PoolManager) -> None:
    """Unit test for reporting variables explicitly marked as non-daily."""
    pool_manager.variables_pool = {
        "daily_variable": {
            "values": [1, 2],
            "info_maps": [{"units": "kg"}] * 2,
            "is_daily_variable": True,
        },
        "every_other_day_variable": {
            "values": [10, 20, 30, 40],
            "info_maps": [{"units": "kg"}] * 4,
            "is_daily_variable": False,
        },
        "irregular_nested_variable": {
            "values": [{"a": 1, "b": 2}, {"a": 3, "b": 4}],
            "info_maps": [{"units": {"a": "kg", "b": "kg"}}] * 2,
            "is_daily_variable": False,
        },
        "non_daily_variable_without_list_of_values": {
            "values": 1,
            "info_maps": [{"units": "kg"}],
            "is_daily_variable": False,
        },
    }

    actual = pool_manager._get_variables_not_reported_daily()

    assert actual == {
        "variable_name": {
            "values": [
                "every_other_day_variable",
                "irregular_nested_variable.a",
                "irregular_nested_variable.b",
            ]
        },
        "report_count": {"values": [4, 2, 2]},
    }


def test_missing_daily_flag_defaults_to_non_daily(pool_manager: PoolManager) -> None:
    """Unit test for treating variables without an explicit daily flag as non-daily."""
    pool_manager.variables_pool = {
        "unmarked_variable": {
            "values": [1, 2, 3],
            "info_maps": [{"units": "kg"}] * 3,
        },
    }

    assert pool_manager._get_variables_reported_daily() == {"variable_name": {"values": []}}
    assert pool_manager._get_variables_not_reported_daily() == {
        "variable_name": {"values": ["unmarked_variable"]},
        "report_count": {"values": [3]},
    }


def test_get_variables_reported_daily_and_not_daily_multiple_pools(pool_manager: PoolManager) -> None:
    """Variables from multiple loaded pools are reported with their pool name as prefix."""
    pool_manager.variables_pool = {
        "poolA": {
            "daily_variable": {"values": [1, 2], "info_maps": [], "is_daily_variable": True},
            "non_daily_variable": {"values": [1], "info_maps": [], "is_daily_variable": False},
        },
        "poolB": {"daily_variable": {"values": [3, 4], "info_maps": [], "is_daily_variable": True}},
    }

    assert pool_manager._get_variables_reported_daily() == {
        "variable_name": {"values": ["poolA.daily_variable", "poolB.daily_variable"]}
    }
    assert pool_manager._get_variables_not_reported_daily() == {
        "variable_name": {"values": ["poolA.non_daily_variable"]},
        "report_count": {"values": [1]},
    }


@pytest.mark.parametrize(
    "variable_data, expected",
    [
        ({"values": [1], "is_daily_variable": True}, True),
        ({"values": [1], "is_daily_variable": False}, False),
        ({"values": [1]}, False),
        ({"values": [1], "is_daily_variable": "True"}, False),
        ({"values": [1], "is_daily_variable": 1}, False),
        ({"values": [1], "is_daily_variable": None}, False),
    ],
)
def test_is_reported_daily(pool_manager: PoolManager, variable_data: dict[str, Any], expected: bool) -> None:
    """Unit test for the _is_reported_daily method of PoolManager."""
    assert pool_manager._is_reported_daily(variable_data) is expected


@pytest.mark.parametrize(
    "values, expected",
    [
        # No values
        ([], ["variable"]),
        # Values that are not dictionaries
        ([1, 2, 3], ["variable"]),
        # A mix of dictionaries and other values
        ([{"a": 1}, 2], ["variable"]),
        # Dictionaries without keys
        ([{}, {}], ["variable"]),
        # Dictionaries with the same keys
        ([{"b": 1, "a": 2}, {"b": 3, "a": 4}], ["variable.a", "variable.b"]),
        # Dictionaries with different keys
        ([{"b": 1}, {"a": 2, "c": 3}, {}], ["variable.a", "variable.b", "variable.c"]),
    ],
)
def test_get_reported_variable_names(pool_manager: PoolManager, values: list[Any], expected: list[str]) -> None:
    """Unit test for the _get_reported_variable_names method of PoolManager."""
    assert pool_manager._get_reported_variable_names("variable", values) == expected


@pytest.mark.parametrize(
    "expected_result, exclude_info_maps, format_option",
    [
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1 (units1)" + os.linesep,
                "var1.info_maps: timestamp (units1)" + os.linesep,
                "var1.info_maps: units" + os.linesep,
                "var2.info_maps: map1 (units1)" + os.linesep,
                "var2.info_maps: units" + os.linesep,
                "var2.values: v1 (units1)" + os.linesep,
                "var2.values: v2 (units1)" + os.linesep,
                "var3 ({'key1': 'unit1', 'key2': 'unit2'})" + os.linesep,
                "var3.info_maps: key1 (unit1)" + os.linesep,
                "var3.info_maps: key2 (unit2)" + os.linesep,
                "var3.info_maps: units" + os.linesep,
            ],
            False,
            "verbose",
        ),
        (
            [
                "_exclude_info_maps=True, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var2.values: v1" + os.linesep,
                "var2.values: v2" + os.linesep,
                "var3" + os.linesep,
            ],
            True,
            "verbose",
        ),
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1 (units1)" + os.linesep,
                "var1" + os.linesep,
                "    .info_maps: timestamp (units1)" + os.linesep,
                "    .info_maps: units" + os.linesep,
                "var2" + os.linesep,
                "    .info_maps: map1 (units1)" + os.linesep,
                "    .info_maps: units" + os.linesep,
                "    .values: v1 (units1)" + os.linesep,
                "    .values: v2 (units1)" + os.linesep,
                "var3 ({'key1': 'unit1', 'key2': 'unit2'})" + os.linesep,
                "var3" + os.linesep,
                "    .info_maps: key1 (unit1)" + os.linesep,
                "    .info_maps: key2 (unit2)" + os.linesep,
                "    .info_maps: units" + os.linesep,
            ],
            False,
            "block",
        ),
        (
            [
                "_exclude_info_maps=True, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var2" + os.linesep,
                "    .values: v1" + os.linesep,
                "    .values: v2" + os.linesep,
                "var3" + os.linesep,
            ],
            True,
            "block",
        ),
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1 (units1)" + os.linesep,
                "var1.info_maps: ['timestamp', 'units']" + os.linesep,
                "var2.info_maps: ['map1', 'units']" + os.linesep,
                "var2.values: ['v1', 'v2'] (units1)" + os.linesep,
                "var3 ({'key1': 'unit1', 'key2': 'unit2'})" + os.linesep,
                "var3.info_maps: ['key1', 'key2', 'units']" + os.linesep,
            ],
            False,
            "inline",
        ),
        (
            [
                "_exclude_info_maps=True, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var2.values: ['v1', 'v2']" + os.linesep,
                "var3" + os.linesep,
            ],
            True,
            "inline",
        ),
        (
            [
                "_exclude_info_maps=True, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var2.v1" + os.linesep,
                "var2.v2" + os.linesep,
                "var3" + os.linesep,
            ],
            True,
            "basic",
        ),
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1 (units1)" + os.linesep,
                "var1.timestamp (units1)" + os.linesep,
                "var1.units" + os.linesep,
                "var2.map1 (units1)" + os.linesep,
                "var2.units" + os.linesep,
                "var2.v1 (units1)" + os.linesep,
                "var2.v2 (units1)" + os.linesep,
                "var3 ({'key1': 'unit1', 'key2': 'unit2'})" + os.linesep,
                "var3.key1 (unit1)" + os.linesep,
                "var3.key2 (unit2)" + os.linesep,
                "var3.units" + os.linesep,
            ],
            False,
            "basic",
        ),
    ],
)
def test_dump_variable_names_and_contexts(
    pool_manager: PoolManager,
    mock_file_manager: MagicMock,
    expected_result: list[str],
    exclude_info_maps: bool,
    format_option: str,
) -> None:
    """Unit test for the dump_variable_names_and_contexts method of PoolManager."""
    pool_manager.variables_pool = {
        "var1": {
            "values": [1],
            "info_maps": [{"timestamp": "value1", "units": "units1"}, {"simulation_day": "value2", "units": "units2"}],
        },
        "var2": {
            "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
            "info_maps": [{"map1": "value1", "units": "units1"}, {"map1": "value2", "units": "units2"}],
        },
        "var3": {
            "values": [1],
            "info_maps": [{"key1": "value1", "key2": "value2", "units": {"key1": "unit1", "key2": "unit2"}}],
        },
    }
    mock_file_manager.generate_file_name.return_value = "dummy_name"

    pool_manager.dump_variable_names_and_contexts(Path("dummy_path"), exclude_info_maps, format_option)

    mock_file_manager.generate_file_name.assert_called_once_with("variable_names", "txt")
    mock_file_manager._list_to_file_txt.assert_called_once_with(expected_result, Path("dummy_path", "dummy_name"))


def test_dump_variable_names_and_contexts_no_values(
    pool_manager: PoolManager, mock_file_manager: MagicMock, mocker: MockerFixture
) -> None:
    """Unit test for the dump_variable_names_and_contexts method of PoolManager when no values are present."""
    mock_flat_pool: dict[str, dict[str, list[Any]]] = {
        "var1": {
            "no_values": [1],
            "info_maps": [{"test": "value1"}, {"test": "value2"}],
        },
    }
    expected_output = [
        "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
        "var1: **NO VARIABLES**" + os.linesep,
    ]
    mocker.patch.object(pool_manager, "_get_flat_variables_pool", return_value=mock_flat_pool)
    mock_file_manager.generate_file_name.return_value = "dummy_name"

    pool_manager.dump_variable_names_and_contexts(Path("dummy_path"), False, format_option="verbose")

    mock_file_manager.generate_file_name.assert_called_once_with("variable_names", "txt")
    mock_file_manager._list_to_file_txt.assert_called_once_with(expected_output, Path("dummy_path", "dummy_name"))


def test_dump_variable_names_and_contexts_multiple_pools(
    pool_manager: PoolManager, mock_file_manager: MagicMock
) -> None:
    """Variables from multiple loaded pools are dumped with their pool name as prefix."""
    pool_manager.variables_pool = {
        "poolA": {"var1": {"values": [1], "info_maps": [{"units": "kg"}]}},
        "poolB": {"var1": {"values": [{"v1": 1}], "info_maps": [{"units": {"v1": "m"}}]}},
    }
    mock_file_manager.generate_file_name.return_value = "dummy_name"

    pool_manager.dump_variable_names_and_contexts(Path("dummy_path"), True, "basic")

    mock_file_manager._list_to_file_txt.assert_called_once_with(
        [
            "_exclude_info_maps=True, expect info_maps accordingly." + os.linesep,
            "poolA.var1" + os.linesep,
            "poolB.var1.v1" + os.linesep,
        ],
        Path("dummy_path", "dummy_name"),
    )


def test_get_parsable_dicts_excludes_info_maps(pool_manager: PoolManager) -> None:
    """Returns empty lists when exclude_info_maps is True."""
    variable_data: dict[str, Any] = {
        "values": [1],
        "info_maps": [{"units": "kg"}],
    }

    parsable_dicts, var_data_info_maps = pool_manager._get_parsable_dicts(variable_data, exclude_info_maps=True)

    assert parsable_dicts == []
    assert var_data_info_maps == []


def test_get_parsable_dicts_includes_info_maps(pool_manager: PoolManager) -> None:
    """Returns info_maps key and data when exclude_info_maps is False and info_maps present."""
    info_maps_data = [{"units": "kg"}, {"units": "lb"}]
    variable_data: dict[str, Any] = {
        "values": [1],
        "info_maps": info_maps_data,
    }

    parsable_dicts, var_data_info_maps = pool_manager._get_parsable_dicts(variable_data, exclude_info_maps=False)

    assert parsable_dicts == ["info_maps"]
    assert var_data_info_maps == info_maps_data


def test_get_parsable_dicts_no_info_maps_key(pool_manager: PoolManager) -> None:
    """Returns empty lists when info_maps key is absent."""
    variable_data: dict[str, Any] = {"values": [1]}

    parsable_dicts, var_data_info_maps = pool_manager._get_parsable_dicts(variable_data, exclude_info_maps=False)

    assert parsable_dicts == []
    assert var_data_info_maps == []


def test_format_variable_entry_no_values(pool_manager: PoolManager) -> None:
    """Returns NO VARIABLES line when values key is absent."""
    result = pool_manager._format_variable_entry("myvar", {"info_maps": []}, False, "verbose")

    assert result == [f"myvar: **NO VARIABLES**{os.linesep}"]


def test_format_variable_entry_flat_with_units(pool_manager: PoolManager) -> None:
    """Non-nested values with units emits name-with-units line."""
    variable_data: dict[str, Any] = {
        "values": [1],
        "info_maps": [{"units": "kg"}],
    }

    result = pool_manager._format_variable_entry("weight", variable_data, False, "verbose")

    assert result == [f"weight (kg){os.linesep}", f"weight.info_maps: units{os.linesep}"]


def test_format_variable_entry_flat_no_units(pool_manager: PoolManager) -> None:
    """Non-nested values without units emits bare name line."""
    variable_data: dict[str, Any] = {"values": [1]}

    result = pool_manager._format_variable_entry("weight", variable_data, True, "verbose")

    assert result == [f"weight{os.linesep}"]


def test_format_variable_entry_nested_values_appends_values_to_parsable_dicts(
    pool_manager: PoolManager, mocker: MockerFixture
) -> None:
    """Nested values causes values dict to be passed to _format_parsable_dict_lines."""
    variable_data: dict[str, Any] = {
        "values": [{"k1": 1, "k2": 2}],
    }
    mock_format_lines = mocker.patch.object(pool_manager, "_format_parsable_dict_lines", return_value=["line"])

    result = pool_manager._format_variable_entry("myvar", variable_data, True, "verbose")

    mock_format_lines.assert_called_once_with(
        "myvar", "myvar", "values", variable_data["values"][0].keys(), "", "verbose"
    )
    assert result == ["line"]


def test_format_variable_entry_block_flat_no_units_no_duplicate(
    pool_manager: PoolManager, mocker: MockerFixture
) -> None:
    """Block format with flat no-units variable: bare name line not duplicated."""
    variable_data: dict[str, Any] = {"values": [1]}
    mocker.patch.object(pool_manager, "_format_parsable_dict_lines", return_value=[])

    result = pool_manager._format_variable_entry("myvar", variable_data, True, "block")

    assert result == [f"myvar{os.linesep}"]


def test_format_variable_entry_block_flat_with_units_appends_bare_name(
    pool_manager: PoolManager, mocker: MockerFixture
) -> None:
    """Block format with flat variable that has units: bare name line appended after name(units) line."""
    variable_data: dict[str, Any] = {
        "values": [1],
        "info_maps": [{"units": "kg"}],
    }
    mocker.patch.object(pool_manager, "_format_parsable_dict_lines", return_value=[])

    result = pool_manager._format_variable_entry("myvar", variable_data, False, "block")

    assert result == [f"myvar (kg){os.linesep}", f"myvar{os.linesep}"]


def test_format_variable_entry_block_nested_appends_bare_name(pool_manager: PoolManager, mocker: MockerFixture) -> None:
    """Block format with nested values: bare name line appended (lines starts empty), prefix is spaces."""
    variable_data: dict[str, Any] = {"values": [{"k1": 1}]}
    mock_format_lines = mocker.patch.object(pool_manager, "_format_parsable_dict_lines", return_value=[])

    result = pool_manager._format_variable_entry("myvar", variable_data, True, "block")

    assert result == [f"myvar{os.linesep}"]
    assert mock_format_lines.call_args.args[1] == " " * len("myvar")


@pytest.mark.parametrize(
    "keys, units, parsable_dict, expected_line",
    [
        (["k1", "k2"], "kg", "values", "myvar.values: ['k1', 'k2'] (kg)"),
        (["k1", "k2"], "", "values", "myvar.values: ['k1', 'k2']"),
        (["k1"], "kg", "info_maps", "myvar.info_maps: ['k1']"),
    ],
)
def test_format_parsable_dict_lines_inline(
    pool_manager: PoolManager,
    keys: list[str],
    units: str,
    parsable_dict: str,
    expected_line: str,
) -> None:
    """Inline format emits single line with key list."""
    result = pool_manager._format_parsable_dict_lines("myvar", "myvar", parsable_dict, keys, units, "inline")

    assert result == [expected_line + os.linesep]


@pytest.mark.parametrize(
    "format_option, units, key, expected_line",
    [
        ("basic", "kg", "my_key", "myvar.my_key (kg)"),
        ("basic", "kg", "units", "myvar.units"),
        ("basic", "kg", "timestep", "myvar.timestep"),
        ("basic", "", "my_key", "myvar.my_key"),
        ("verbose", "kg", "my_key", "myvar.values: my_key (kg)"),
        ("verbose", "kg", "units", "myvar.values: units"),
        ("verbose", "", "my_key", "myvar.values: my_key"),
    ],
)
def test_format_parsable_dict_lines_units_suppressed_for_ignored_keys(
    pool_manager: PoolManager,
    format_option: str,
    units: str,
    key: str,
    expected_line: str,
) -> None:
    """Units omitted for keys in _VARIABLE_DUMP_KEYS_TO_IGNORE or when units empty."""
    result = pool_manager._format_parsable_dict_lines("myvar", "myvar", "values", [key], units, format_option)

    assert result == [expected_line + os.linesep]


def test_format_parsable_dict_lines_basic_per_key_lines(pool_manager: PoolManager) -> None:
    """Basic format emits one line per key using name.key pattern."""
    result = pool_manager._format_parsable_dict_lines("myvar", "myvar", "values", ["k1", "k2"], "kg", "basic")

    assert result == [f"myvar.k1 (kg){os.linesep}", f"myvar.k2 (kg){os.linesep}"]


def test_format_parsable_dict_lines_verbose_uses_prefix(pool_manager: PoolManager) -> None:
    """Verbose/block format uses prefix and parsable_dict in each line."""
    result = pool_manager._format_parsable_dict_lines("myvar", "    ", "values", ["k1"], "kg", "verbose")

    assert result == [f"    .values: k1 (kg){os.linesep}"]


def test_format_parsable_dict_lines_dict_units(pool_manager: PoolManager) -> None:
    """Per-key dict units resolved correctly; missing key gets empty string."""
    units_dict = {"k1": "kg", "k2": "lb"}

    result = pool_manager._format_parsable_dict_lines(
        "myvar", "myvar", "values", ["k1", "k2", "k3"], units_dict, "basic"
    )

    assert result == [f"myvar.k1 (kg){os.linesep}", f"myvar.k2 (lb){os.linesep}", f"myvar.k3{os.linesep}"]


def test_set_variables_pool_with_override(pool_manager: PoolManager) -> None:
    """Sets variables_pool and uses the explicit override for current_pool_size."""
    new_pool: dict[str, POOL_ELEMENT_TYPE] = {"a": {"values": [1], "info_maps": []}}

    pool_manager._set_variables_pool(new_pool, pool_size_override=999)

    assert pool_manager.variables_pool is new_pool
    assert pool_manager.current_pool_size == 999


def test_set_variables_pool_with_override_of_zero(pool_manager: PoolManager) -> None:
    """An override of 0 is used for current_pool_size instead of calculating the size."""
    new_pool: dict[str, POOL_ELEMENT_TYPE] = {"a": {"values": [1], "info_maps": []}}
    pool_manager.current_pool_size = 1024

    pool_manager._set_variables_pool(new_pool, pool_size_override=0)

    assert pool_manager.variables_pool is new_pool
    assert pool_manager.current_pool_size == 0


def test_set_variables_pool_without_override(pool_manager: PoolManager, mocker: MockerFixture) -> None:
    """Sets variables_pool and calculates current_pool_size via sys.getsizeof on repr(new_pool)."""
    new_pool: dict[str, POOL_ELEMENT_TYPE] = {"x": {"values": [1, 2, 3], "info_maps": [{"u": "kg"}]}}
    mocked_getsizeof = mocker.patch("RUFAS.post_processing.pool_manager.sys.getsizeof", return_value=1234)

    pool_manager._set_variables_pool(new_pool)

    assert pool_manager.variables_pool is new_pool
    mocked_getsizeof.assert_called_once_with(new_pool.__repr__())
    assert pool_manager.current_pool_size == 1234


def test_get_flat_variables_pool_empty_returns_empty(pool_manager: PoolManager) -> None:
    """Returns {} when variables_pool is empty/falsy."""
    pool_manager.variables_pool = {}

    result = pool_manager._get_flat_variables_pool()

    assert result == {}


def test_get_flat_variables_pool_already_flat_returns_self(pool_manager: PoolManager) -> None:
    """If all values are dicts containing 'values', return the mapping as-is."""
    flat_pool: dict[str, POOL_ELEMENT_TYPE] = {
        "var1": {"values": [1], "info_maps": [{"units": "kg"}]},
        "var2": {"values": [2, 3], "info_maps": [{"units": "kg"}]},
    }
    pool_manager.variables_pool = flat_pool

    result = pool_manager._get_flat_variables_pool()

    assert result is flat_pool


def test_get_flat_variables_pool_nested_is_flattened_and_non_dict_skipped(pool_manager: PoolManager) -> None:
    """Flattens nested pools and skips non-dict entries at the pool level."""
    pool_manager.variables_pool = cast(
        Any,
        {
            "poolA": {
                "var1": {"values": [1], "info_maps": [{"units": "kg"}]},
                "var2": {"values": [2], "info_maps": [{"units": "kg"}]},
            },
            "poolB": {
                "v3": {"values": [3], "info_maps": [{"units": "m"}]},
            },
            "not_a_pool": 42,
        },
    )

    result = pool_manager._get_flat_variables_pool()

    assert result == {
        "poolA.var1": {"values": [1], "info_maps": [{"units": "kg"}]},
        "poolA.var2": {"values": [2], "info_maps": [{"units": "kg"}]},
        "poolB.v3": {"values": [3], "info_maps": [{"units": "m"}]},
    }


def test_flush_pools(pool_manager: PoolManager) -> None:
    """Unit test for the flush_pools method of PoolManager."""
    info_map = {
        "class": "dummy_class",
        "function": "dummy_func",
        "units": MeasurementUnits.ANIMALS,
        "simulation_day": 1,
    }
    pool_manager.add_variable("dummy_name", "dummy_value", info_map)
    pool_manager.current_pool_size = 1024
    assert pool_manager.variables_pool != {}

    pool_manager.flush_pools()

    assert pool_manager.variables_pool == {}
    assert pool_manager.current_pool_size == sys.getsizeof({}.__repr__())
