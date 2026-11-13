import collections
import os
import sys
from copy import deepcopy
from math import inf
from pathlib import Path
from typing import Any, Counter, Sequence, Union

import psutil

from RUFAS.general_constants import GeneralConstants
from RUFAS.post_processing.file_manager import FileManager
from RUFAS.post_processing.rufas_logger import get_logger
from RUFAS.post_processing.shared_data_types import POOL_ELEMENT_TYPE
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility

logger = get_logger(__name__)


class PoolManager:
    """
    Class overseeing the management of the variables pool including chunkification.

    Parameters
    ----------
    file_manager : FileManager
        The ``FileManager`` used to create the directory for saved pool chunks and to save and load pools.

    Attributes
    ----------
    variables_pool : dict[str, POOL_ELEMENT_TYPE]
        Contains variables reported during the simulation.
    chunkification : bool
        Set to ``True`` to enable chunkification of the output ``variables_pool``.
    saved_pool_chunks_num : int
        The number of saved pool chunks.
    saved_pool_chunks_path : Path | None
        The path to the directory where saved pool chunks are stored.
    available_memory : int
        The available memory on the system, bytes.
    average_add_variable_call_addition : int, default 118
        The average memory usage increases per call to ``add_variable()``.
    add_variable_call : int
        The number of calls to ``add_variable()``.
    save_chunk_threshold_call_count : int
        The threshold ``add_variable_call`` count for saving pool chunk.
    current_pool_size : int
        The current size of the variable pool, bytes.
    maximum_pool_size : float
        The maximum allowed variable pool size, bytes.
    _variables_usage_counter : Counter[str]
        A ``Counter``-like registry of filtered variable keys. Dictionary-valued variables pre-seed subkeys at 0, and
        counts increase when post-processing filters select matching variables or subkeys. The pre-seeding exists
        because dictionary-valued variables can later be filtered by subkey (for example ``variable.min``), even though
        those subkeys are not stored as standalone top-level variables in the pool. Non-dictionary variables are not
        pre-seeded; they only appear here once a filter actually selects them.
    file_manager : FileManager
        The ``FileManager`` used to create the directory for saved pool chunks and to save and load pools.
    time : RufasTime | None
        A ``RufasTime`` object used to track the simulation time. Set by ``OutputManager``.
    exclude_info_maps : bool
        Set to ``True`` to exclude ``info_maps`` when adding variables to the ``variables_pool``. Set by
        ``OutputManager``.
    """

    _VARIABLE_DUMP_KEYS_TO_IGNORE = frozenset(
        ["units", "timestep", "info_maps", "prefix", "suffix", "data_origin", "number_animals_in_pen", "simulation_day"]
    )

    def __init__(self, file_manager: FileManager) -> None:
        self.variables_pool: dict[str, POOL_ELEMENT_TYPE] = {}
        self.chunkification: bool = False
        self.saved_pool_chunks_num: int = 0
        self.saved_pool_chunks_path: Path | None = None
        self.available_memory: int = 0
        self.average_add_variable_call_addition: int = 118
        self.add_variable_call = 0
        self.save_chunk_threshold_call_count: int = 0
        self.current_pool_size: int = 0
        self.maximum_pool_size: float = inf
        self._variables_usage_counter: Counter[str] = collections.Counter()
        self.file_manager = file_manager
        self.time: RufasTime | None = None
        self.exclude_info_maps: bool = False

    def setup_pool_overflow_control(
        self,
        output_dir: Path,
        max_memory_usage_percent: int,
        max_memory_usage: int | None = None,
        save_chunk_threshold_call_count: int | None = None,
    ) -> None:
        """
        Sets up the mechanism by which chunkification of the output ``variables_pool`` is controlled.

        Parameters
        ----------
        output_dir : Path
            The path to the output directory where chunks will be saved.
        max_memory_usage_percent : int
            The setting for the maximum output ``variables_pool`` size as a percentage of the ``available_memory``.
        max_memory_usage : int | None, optional
            The setting for the maximum output ``variables_pool`` size, bytes.
        save_chunk_threshold_call_count : int | None, optional
            The setting for the threshold ``add_variable_call`` count for saving pool chunk.
        """
        self.chunkification = True

        self.available_memory = psutil.virtual_memory().available
        available_memory_gb = self.available_memory / GeneralConstants.BYTES_PER_GB

        self.saved_pool_chunks_path = Path.joinpath(
            output_dir,
            f"saved_pool/{self.file_manager.metadata_prefix}_{Utility.get_timestamp(include_millis=True)}",
        )
        self.file_manager.create_directory(self.saved_pool_chunks_path)

        log_message = (
            f"Created {self.saved_pool_chunks_path} for saved pools during simulation.\n"
            f"Current system available memory: {available_memory_gb:.2f} GB = "
            f"{self.available_memory} Bytes.\n"
        )

        if save_chunk_threshold_call_count is not None and save_chunk_threshold_call_count > 0:
            self.save_chunk_threshold_call_count = save_chunk_threshold_call_count
            log_message += (
                "The threshold add_variable_call count for saving pool chunk is set to "
                f"{self.save_chunk_threshold_call_count}"
            )
        elif max_memory_usage:
            self.maximum_pool_size = max_memory_usage
            log_message += "The maximum output variable pool size is set to " f"{self.maximum_pool_size} Bytes"
        else:
            self.maximum_pool_size = (
                max_memory_usage_percent * GeneralConstants.PERCENTAGE_TO_FRACTION
            ) * self.available_memory
            log_message += "The maximum output variable pool size is set to " f"{self.maximum_pool_size} Bytes"
        logger.info(log_message, extra={"rufas_log_name": "Pool Overflow Control Setup"})

    def _pool_element_factory(self) -> POOL_ELEMENT_TYPE:
        """Factory for elements added to pools"""
        info_maps: list[dict[str, Any]] = []
        values: list[Any] = []
        return {"info_maps": info_maps, "values": values}

    def _add_to_pool(
        self,
        pool: dict[str, POOL_ELEMENT_TYPE],
        key: str,
        value: Any,
        info_map: dict[str, Any],
        first_info_map_only: bool = False,
    ) -> None:
        """
        Adds ``value`` and ``info_map`` at ``key`` in the given ``pool``.

        Parameters
        ----------
        pool : dict[str, dict[str, list[dict[str, Any]]]
            The pool to add the ``value`` and ``info_map`` to.
        key : str
            The key to add the ``value`` and ``info_map`` at.
        value : Any
            The value to be added to the ``pool``.
        info_map : dict[str, Any]
            The info map to be added to the ``pool``.
        first_info_map_only : bool, default False
            If ``True``, records only the first ``info_map`` passed for that variable. Otherwise, records all
            ``info_map``s passed for that variable.

        Notes
        -----
        The use of ``deepcopy`` is necessary here because ``value`` may be a mutable object,
        and storing a reference would allow external modifications to corrupt the data
        held in the pool.
        """
        discard_info_map = first_info_map_only

        key_not_exists_in_pool = pool.get(key) is None
        if key_not_exists_in_pool:
            pool[key] = self._pool_element_factory()
            discard_info_map = False

        new_daily_flag = info_map.get("is_daily_variable", False)
        new_daily_flag = new_daily_flag if isinstance(new_daily_flag, bool) else False
        pool[key]["is_daily_variable"] = bool(pool[key].get("is_daily_variable", False)) or new_daily_flag

        if not self.exclude_info_maps and not discard_info_map:
            reduced_info_map = {
                k: v for k, v in info_map.items() if k not in ["class", "function", "is_daily_variable"]
            }
            pool[key]["info_maps"].append(reduced_info_map)

        if isinstance(value, (int, bool, float, str)):
            pool[key]["values"].append(value)
        else:
            pool[key]["values"].append(deepcopy(value))

    def _add_simulation_day_to_info_map(
        self,
        info_map: dict[str, Any],
        overwrite: bool = False,
        simulation_day: int | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """
        Update an ``info_map`` to include ``simulation_day``

        Parameters
        ----------
        info_map: dict[str, Any]
            The original ``info_map`` to copy and optionally update
        overwrite: bool, default False
            Whether to overwrite an existing ``simulation_day`` entry
        simulation_day: optional int
            The simulation day to insert. If None, ``self.time.simulation_day`` is used when available.
        name: optional str
            The name of the variable for which ``simulation_day`` is added to the ``info_map`` (used for warnings)

        Returns
        -------
        dict[str, Any]
            The ``info_map``, updated to include ``simulation_day``, if it is available.

        Notes
        -----
        A warning is triggered if the resulting ``info_map`` has no ``simulation_day`` value (or a value of None)
        """
        info_map_copy = dict(info_map)

        time_day = self.time.simulation_day if hasattr(self.time, "simulation_day") else None

        map_has_valid_day = info_map_copy.get("simulation_day") is not None

        day_to_use = simulation_day if simulation_day is not None else time_day

        # Don't overwrite a valid simulation_day with None
        if day_to_use is None and map_has_valid_day:
            return info_map_copy

        should_add_sim_day = overwrite or "simulation_day" not in info_map_copy

        if day_to_use is not None and should_add_sim_day:
            info_map_copy["simulation_day"] = day_to_use

        if day_to_use is None and not map_has_valid_day:
            logger.warning(
                "no simulation day was available to add to the info_map for variable %s (from %s.%s)",
                name,
                info_map_copy.get("class"),
                info_map_copy.get("function"),
                extra={"rufas_log_name": "no simulation_day available"},
            )

        return info_map_copy

    def add_variable(
        self,
        name: str,
        value: Any,
        info_map: dict[str, Any],
        first_info_map_only: bool = False,
        overwrite_simulation_day: bool = False,
        simulation_day: int | None = None,
    ) -> None:
        """
        Adds a variable to the pool.

        Parameters
        ----------
        name : str
            The name of the variable
        value : Any
            The value of the variable
        info_map : dict[str, Any]
            Additional arguments, some are required
        first_info_map_only : bool, default False
            If ``True``, records only the first ``info_map`` passed for that variable. Otherwise, records all
            ``info_map``s passed for that variable.
        overwrite_simulation_day: bool, default False
            If ``True``, an existing ``simulation_day`` value in the ``info_map`` will be replaced.
            The replacement value will be the ``simulation_day`` argument provided to this function
            (if it is not ``None``), if it is available;
            otherwise, ``self.time.simulation_day`` will be used, if available.
            If neither value is available, the ``info_map`` is returned unchanged (no ``simulation_day`` is
            added or updated).
        simulation_day: optional int
            If present, this ``simulation_day`` will be used, otherwise the ``simulation_day`` will be taken from
            ``self.time.simulation_day``, if present. This option is provided to allow variables created outside the
            main simulation loop (i.e., herd initialization) to be padded.

        Raises
        ------
        KeyError
            - If either ``info_map["class"]`` or ``info_map["function"]`` are not present
            - If '`units`' is not found in ``info_map``
            - If '`units`' is a ``dict`` and is missing entries for the variable's values.

        Notes
        -----
        ``info_map`` is a dictionary containing additional information about the variable. It can include:
        - ``class`` : str
            The name of the class which called this function
        - ``function`` : str
            The name of the function which called this function
        - ``prefix`` : str, optional
            If present, overrides the automated prefix
        - ``suppress_prefix`` : bool, optional
            If present and ``True``, suppresses the automated prefix generation.
            Has no effect on manual prefix overrides.
        - ``suffix`` : str, optional
            If present, gets appended to the key
        - ``is_daily_variable`` : bool, optional
            If present, marks whether the variable should be treated as daily for reporting diagnostics. Defaults to
            ``False``, and is persisted on the stored variable entry before ``info_maps`` may be excluded.
        """
        self.add_variable_call += 1
        units = info_map.get("units")
        if units is None:
            raise KeyError(f"'units' was not found in info_map for call to 'add_variable()' for {name}.")
        if isinstance(units, dict) and len(info_map["units"]) != len(value) and value != {}:
            raise KeyError(f"'units' missing in units dict for a variable in {name}.")
        units = self._stringify_units(units)

        updated_info_map = self._add_simulation_day_to_info_map(
            info_map, overwrite_simulation_day, simulation_day, name
        )

        key = self._generate_key(name, updated_info_map)
        self._add_to_pool(self.variables_pool, key, value, {**updated_info_map, "units": units}, first_info_map_only)

        if isinstance(value, dict):
            for k, v in value.items():
                self._variables_usage_counter[f"{key}.{k}"] = 0

        if self.chunkification:
            self.current_pool_size += self.average_add_variable_call_addition
            is_save_chunk_threshold_reached = (
                self.save_chunk_threshold_call_count > 0
                and self.add_variable_call % self.save_chunk_threshold_call_count == 0
            )
            is_pool_size_at_maximum_capacity = (
                self.save_chunk_threshold_call_count == 0 and self.current_pool_size >= self.maximum_pool_size
            )
            if is_save_chunk_threshold_reached or is_pool_size_at_maximum_capacity:
                self._save_current_variable_pool()

    def add_variable_bulk(
        self,
        variables: list[tuple[dict[str, Any], dict[str, Any]]],
        first_info_map_only: bool = False,
        overwrite_simulation_day: bool = False,
    ) -> None:
        """
        Iterate through all variables and call ``add_variable()`` on each of them.

        Parameters
        ----------
        variables : list[tuple[dict[str, Any], dict[str, Any]]
            Variables to add in bulk packages in a list of tuples. Each tuple contains a dictionary with the key
            being the variable name and the value being the output value, and its corresponding ``info_map``.
        first_info_map_only : bool, default False
            If ``True``, records only the first ``info_map`` passed for each variable.
        overwrite_simulation_day: bool, default False
            Passed to ``add_variable()``. If ``True``, any ``simulation_day`` value provided in the ``info_maps`` is
            overwritten.

        """
        for variable, info_map in variables:
            name, value = list(variable.items())[0]
            self.add_variable(name, value, info_map, first_info_map_only, overwrite_simulation_day)

    def _save_current_variable_pool(self) -> None:
        """
        Save the current ``variables_pool`` into a JSON file. Flush the ``variables_pool`` and reset the pool size.
        """
        saved_pool_file_name = self.file_manager.generate_file_name(f"saved_pool_{self.saved_pool_chunks_num}", "json")
        saved_pool_file_path = Path.joinpath(self.saved_pool_chunks_path, saved_pool_file_name)
        self.file_manager.dict_to_file_json(
            data_dict=self.variables_pool, path=saved_pool_file_path, minify_output_file=True
        )
        logger.info(
            "Saved the current variable pool to %s",
            saved_pool_file_path,
            extra={"rufas_log_name": "save_current_variable_pool"},
        )
        self._set_variables_pool({})
        self.saved_pool_chunks_num += 1

    def _stringify_units(self, units: dict[str, Any] | MeasurementUnits) -> dict[str, Any] | str:
        """
        Recursively validates that units is either a valid ``MeasurementUnits`` enum member or a dictionary with
        valid ``MeasurementUnits`` enum members (including nested dictionaries). Converts the ``MeasurementUnits``
        enum values to their string representations.

        Parameters
        ----------
        units : dict[str, Any] | str
            Either a string that can be converted to an ``MeasurementUnits``, or a dictionary mapping string keys to
            either ``MeasurementUnits`` values or further dictionaries.

        Returns
        -------
        dict[str, Any] | str
            The validated and stringified units.

        Raises
        ------
        TypeError
            If any unit or nested unit does not have the type ``MeasurementUnits``.
        """
        if isinstance(units, dict):
            return {key: self._stringify_units(unit) for key, unit in units.items()}

        if type(units) is not MeasurementUnits:
            logger.error(
                "The following unit does not have the type MeasurementUnits: %s (type %s).",
                units,
                type(units),
                extra={"rufas_log_name": "invalid_units_type"},
            )

            raise TypeError(
                f"The following unit does not have the type MeasurementUnits: {units} (type {type(units)})."
            )

        return str(units)

    def _generate_key(self, name: str, info_map: dict[str, Union[str, bool]]) -> str:
        """
        Generates a key for the pool by combining an optional prefix, the variable
        name, and an optional suffix.

        Parameters
        ----------
        name : str
            Base name of the variable.
        info_map : dict[str, str | bool]
            Dictionary controlling key construction.

        Returns
        -------
        str
            Constructed pool key in the form ``{prefix}{name}{suffix}``.

        Raises
        ------
        KeyError
            If ``info_map["class"]`` or ``info_map["function"]`` are not present.
        """
        if info_map.get("class") is None:
            raise KeyError("'class' was not found in info_map")
        if info_map.get("function") is None:
            raise KeyError("'function' was not found in info_map")

        prefix = ""
        prefix_value = info_map.get("prefix")
        if isinstance(prefix_value, str):
            prefix = prefix_value + "."
        elif not info_map.get("suppress_prefix", False):
            class_value = info_map.get("class")
            function_value = info_map.get("function")
            if isinstance(class_value, str) and isinstance(function_value, str):
                prefix = self._get_prefix(class_value, function_value) + "."

        suffix = f'.{info_map.get("suffix")}' if info_map.get("suffix") is not None else ""

        return f"{prefix}{name}{suffix}"

    def _get_prefix(self, caller_class: str, caller_function: str) -> str:
        """
        Returns the prefix for a key in the pool.

        Parameters
        ----------
        caller_class : str
            Name of the class in which the call to ``OutputManager`` is originated
        caller_function : str
            Name of the function which called the ``OutputManager`` originated

        Returns
        -------
        str
            ``{caller_class}.{caller_function}``
        """
        return f"{caller_class}.{caller_function}"

    def _sort_saved_chunk_files(self) -> list[Path]:
        """
        Get a list of all saved chunks of the output variable pool by retrieving all JSON files under
        the ``saved_pool_chunks_path``. Then sort the files according to their file name to preserve the order.
        """
        list_of_dumped_files: list[Path] = [
            file for file in self.saved_pool_chunks_path.iterdir() if file.is_file() and file.name.endswith(".json")
        ]
        list_of_dumped_files.sort(key=lambda file_name: int((str(file_name).split("saved_pool_")[1]).split("_")[0]))
        return list_of_dumped_files

    def load_saved_pools(self) -> None:
        """
        Loads saved pools of data from JSON files in the ``saved_pool_chunks_path`` directory and merges them into
        a single variables pool.
        """
        merged_pool: dict[str, POOL_ELEMENT_TYPE] = {}
        list_of_dumped_files = self._sort_saved_chunk_files()
        for file in list_of_dumped_files:
            self.load_variables_pool_from_file(file)
            for key, value in self.variables_pool.items():
                if key not in merged_pool:
                    merged_pool[key] = value
                else:
                    merged_pool[key]["info_maps"].extend(value["info_maps"])
                    merged_pool[key]["values"].extend(value["values"])
            self.current_pool_size = 0
            self._set_variables_pool({}, pool_size_override=0)

        self._set_variables_pool(merged_pool, pool_size_override=sys.getsizeof(merged_pool))

    def load_variables_pool_from_file(self, file_path: Path) -> None:
        """
        Loads the ``variables_pool`` from file path provided by user.

        Parameters
        ----------
        file_path : Path
            The path to the file to be loaded to the ``variables_pool``.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.load_variables_pool_from_file.__name__,
        }
        loaded_pool = self.file_manager._read_variables_pool_file(file_path, info_map)
        self._set_variables_pool(loaded_pool)

    def load_multiple_variables_pools_from_files(self, pools: Sequence[tuple[str, Path] | dict[str, Any]]) -> None:
        """
        Loads multiple previously saved ``variable_pools``, namespacing each pool's entries.

        Parameters
        ----------
        pools : Sequence[tuple[str, Path] | dict[str, Any]]
            An iterable of pool descriptors. Each descriptor must provide a pool name and the
            path to the JSON file containing the pool to load. When dicts are provided they
            must include ``"name"`` and ``"path"`` keys.

        """
        info_map_base = {
            "class": self.__class__.__name__,
            "function": self.load_multiple_variables_pools_from_files.__name__,
        }

        separated_pools: dict[str, POOL_ELEMENT_TYPE] = {}
        normalized_pools: list[tuple[str, Path]] = []
        for pool in pools:
            if isinstance(pool, tuple):
                pool_name, pool_path = pool
            else:
                pool_name = pool["name"]
                pool_path = pool["path"]
            if not isinstance(pool_path, Path):
                pool_path = Path(pool_path)
            normalized_pools.append((pool_name, pool_path))

        for pool_name, pool_path in normalized_pools:
            pool_info_map = {**info_map_base, "pool_name": pool_name}
            loaded_pool = self.file_manager._read_variables_pool_file(pool_path, pool_info_map)
            separated_pools[pool_name] = loaded_pool

        self._set_variables_pool(separated_pools)

    def report_variables_usage_counts(self, path: Path) -> None:
        """
        Reports variable filter usage and daily/non-daily reporting diagnostics to CSV files.

        The ``variables_usage_counts`` CSV contains counts of how often each variable was used by ``OutputManager``
        filters during post-processing. These counts do not represent how often a variable was reported to
        ``OutputManager`` during the simulation.

        The ``variables_reported_daily`` CSV lists variables treated as daily for reporting diagnostics.

        The ``variables_not_reported_daily`` CSV lists variables treated as non-daily for reporting diagnostics with
        columns ``variable_name`` and ``report_count``.

        Parameters
        ----------
        path : Path
            The path to the directory where the file will be saved.
        """
        # TODO this function may be best suited somewhere else as it's a reporting out function but it needs
        # _variables_usage_counter_data
        filename = self.file_manager.generate_file_name("variables_usage_counts", "csv")
        file_path_csv = path / filename
        sorted_variables_usage_counter_desc = self._variables_usage_counter.most_common()
        variable_name_col = {"values": [variable[0] for variable in sorted_variables_usage_counter_desc]}
        usage_count_col = {"values": [variable[1] for variable in sorted_variables_usage_counter_desc]}
        data_dict = {"variable_name": variable_name_col, "usage_count": usage_count_col}
        self.file_manager._dict_to_file_csv(data_dict, file_path_csv)

        daily_filename = self.file_manager.generate_file_name("variables_reported_daily", "csv")
        daily_file_path_csv = path / daily_filename
        daily_data_dict = self._get_variables_reported_daily()
        self.file_manager._dict_to_file_csv(daily_data_dict, daily_file_path_csv)

        non_daily_filename = self.file_manager.generate_file_name("variables_not_reported_daily", "csv")
        non_daily_file_path_csv = path / non_daily_filename
        non_daily_data_dict = self._get_variables_not_reported_daily()
        self.file_manager._dict_to_file_csv(non_daily_data_dict, non_daily_file_path_csv)

    def _get_variables_reported_daily(self) -> dict[str, dict[str, list[Any]]]:
        """Builds a CSV-ready dictionary listing variables treated as daily for reporting diagnostics."""

        variable_names: set[str] = set()
        for variable_name, variable_data in sorted(self._get_flat_variables_pool().items()):
            values = variable_data.get("values", [])
            if not isinstance(values, list):
                continue

            if not self._is_reported_daily(variable_data):
                continue

            variable_names.update(self._get_reported_variable_names(variable_name, values))

        return {"variable_name": {"values": sorted(variable_names)}}

    def _get_variables_not_reported_daily(self) -> dict[str, dict[str, list[Any]]]:
        """Builds a CSV-ready dictionary listing variables treated as non-daily for reporting diagnostics."""
        rows: set[tuple[str, int]] = set()

        for variable_name, variable_data in sorted(self._get_flat_variables_pool().items()):
            values = variable_data.get("values", [])
            if not isinstance(values, list):
                continue

            if self._is_reported_daily(variable_data):
                continue

            for reported_name in self._get_reported_variable_names(variable_name, values):
                rows.add((reported_name, len(values)))

        sorted_rows = sorted(rows)
        return {
            "variable_name": {"values": [name for name, _ in sorted_rows]},
            "report_count": {"values": [count for _, count in sorted_rows]},
        }

    def _is_reported_daily(self, variable_data: dict[str, Any]) -> bool:
        """Determines whether a variable should be treated as daily for reporting diagnostics."""

        is_daily_variable = variable_data.get("is_daily_variable", False)
        return is_daily_variable if isinstance(is_daily_variable, bool) else False

    def _get_reported_variable_names(self, variable_name: str, values: list[Any]) -> list[str]:
        """Returns nested variable names for dictionary-valued variables, otherwise the variable name."""

        if not values or not all(isinstance(value, dict) for value in values):
            return [variable_name]

        nested_variable_names = sorted({subkey for value in values for subkey in value.keys()})
        if not nested_variable_names:
            return [variable_name]

        return [f"{variable_name}.{nested_variable_name}" for nested_variable_name in nested_variable_names]

    def dump_variable_names_and_contexts(  # noqa: C901
        self,
        path: Path,
        exclude_info_maps: bool,
        format_option: str,
    ) -> None:
        """
        Dumps names of all variables added to ``variables_pool`` along with the caller class
        and function contextual information into a txt file in the given path to a directory.

        Parameters
        ----------
        path : Path
            The path to the file to be dumped to.

        exclude_info_maps : bool
            Flag to denote whether info_map data should be dumped with variable names.

        format_option : str
            The selection for the formatting option of the text written to the variable names text file.

        Examples
        --------
        For the different format options available:

        format_option: str = "basic" - Excludes information about whether data is from info_maps but has the same
                                       format as output CSV column headers.
        class_name.function_name.variable_name1.sub_variable1_name
        class_name.function_name.variable_name1.sub_variable2_name
        class_name.function_name.variable_name2.sub_variable1_name
        class_name.function_name.variable_name3

        format_option: str = "block"
        class_name.function_name.variable_name
                                            .values: variable1_name
                                            .values: variable2_name
                                            .info_maps: variable3_name
                                            .info_maps: variable4_name

        format_option: str = "inline"
        class_name.function_name.variable_name.values: [variable1_name, variable2_name]
        class_name.function_name.variable_name.info_maps: [variable3_name, variable4_name]

        format_option: str = "verbose"
        class_name.function_name.variable_name.values: variable1_name
        class_name.function_name.variable_name.values: variable2_name
        class_name.function_name.variable_name.info_maps: variable3_name
        class_name.function_name.variable_name.info_maps: variable4_name
        """
        var_list = [f"_{exclude_info_maps=}, expect info_maps accordingly.{os.linesep}"]
        for name, variable_data in self._get_flat_variables_pool().items():
            var_list.extend(self._format_variable_entry(name, variable_data, exclude_info_maps, format_option))
        file_path = path / self.file_manager.generate_file_name("variable_names", "txt")
        self.file_manager._list_to_file_txt(var_list, file_path)

    def _get_parsable_dicts(
        self,
        variable_data: dict[str, Any],
        exclude_info_maps: bool,
    ) -> tuple[list[str], list[Any]]:
        """Returns parsable dictionary keys and ``info_maps`` data for a variable entry."""
        parsable_dicts: list[str] = []
        var_data_info_maps: list[Any] = []
        if not exclude_info_maps and "info_maps" in variable_data:
            parsable_dicts.append("info_maps")
            var_data_info_maps = variable_data.get("info_maps", [])
        return parsable_dicts, var_data_info_maps

    def _format_variable_entry(
        self,
        name: str,
        variable_data: dict[str, Any],
        exclude_info_maps: bool,
        format_option: str,
    ) -> list[str]:
        """Returns formatted lines for a single variable in the variable names dump."""

        if "values" not in variable_data:
            return [f"{name}: **NO VARIABLES**{os.linesep}"]

        parsable_dicts, var_data_info_maps = self._get_parsable_dicts(variable_data, exclude_info_maps)
        units = var_data_info_maps[0]["units"] if var_data_info_maps else ""
        is_variable_nested = isinstance(variable_data["values"][0], dict)

        lines: list[str] = []
        if is_variable_nested:
            parsable_dicts.append("values")
        else:
            lines.append(f"{name} ({units}){os.linesep}" if units else f"{name}{os.linesep}")

        prefix = name
        if format_option == "block":
            if f"{name}{os.linesep}" not in lines:
                lines.append(f"{name}{os.linesep}")
            prefix = " " * len(name)

        for parsable_dict in parsable_dicts:
            keys = variable_data[parsable_dict][0].keys()
            lines.extend(self._format_parsable_dict_lines(name, prefix, parsable_dict, keys, units, format_option))

        return lines

    def _format_parsable_dict_lines(
        self,
        name: str,
        prefix: str,
        parsable_dict: str,
        keys: list[str],
        units: str | dict[str, str],
        format_option: str,
    ) -> list[str]:
        """Returns formatted lines for one parsable dictionary (values or info_maps) within a variable entry."""
        if format_option == "inline":
            return [
                (
                    f"{name}.{parsable_dict}: {list(keys)} ({units}){os.linesep}"
                    if not parsable_dict.endswith("info_maps") and units
                    else f"{name}.{parsable_dict}: {list(keys)}{os.linesep}"
                )
            ]

        lines: list[str] = []
        for key in keys:
            var_units = units.get(key, "") if isinstance(units, dict) else units
            show_units = key not in self._VARIABLE_DUMP_KEYS_TO_IGNORE and var_units
            if format_option == "basic":
                lines.append(f"{name}.{key} ({var_units}){os.linesep}" if show_units else f"{name}.{key}{os.linesep}")
            else:
                lines.append(
                    f"{prefix}.{parsable_dict}: {key} ({var_units}){os.linesep}"
                    if show_units
                    else f"{prefix}.{parsable_dict}: {key}{os.linesep}"
                )
        return lines

    def _set_variables_pool(
        self,
        new_pool: dict[str, POOL_ELEMENT_TYPE],
        *,
        pool_size_override: int | None = None,
    ) -> None:
        """
        Assigns the ``variables_pool`` and updates the cached size.

        Parameters
        ----------
        new_pool : dict[str, POOL_ELEMENT_TYPE]
            The new ``variables_pool`` to be assigned.
        pool_size_override : int | None, optional
            If provided, this value will be used to set the current pool size instead of calculating it.
        """
        self.variables_pool = new_pool
        if pool_size_override is not None:
            self.current_pool_size = pool_size_override
            return

        self.current_pool_size = sys.getsizeof(new_pool.__repr__())

    def _get_flat_variables_pool(self) -> dict[str, Any]:
        """Returns a flattened mapping of variable names to data when multiple pools are loaded."""

        if not self.variables_pool:
            return {}

        if all(
            isinstance(variable_data, dict) and "values" in variable_data
            for variable_data in self.variables_pool.values()
        ):
            return self.variables_pool

        flattened: dict[str, Any] = {}
        for pool_name, pool_data in self.variables_pool.items():
            if not isinstance(pool_data, dict):
                continue
            for variable_name, variable_data in pool_data.items():
                flattened[f"{pool_name}.{variable_name}"] = variable_data

        return flattened

    def flush_pools(self) -> None:
        """Sets the ``variables_pool`` to an empty dictionary."""
        self._set_variables_pool({})
