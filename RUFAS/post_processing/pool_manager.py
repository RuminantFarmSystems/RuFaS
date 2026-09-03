import collections
from pathlib import Path

from numpy import inf
from shared_data_types import POOL_ELEMENT_TYPE
from typing import Any, Counter, Sequence, Union

from RUFAS.post_processing.file_manager import FileManager
from RUFAS.units import MeasurementUnits


class PoolManager:
    """
    Class overseeing the management of the variables pool including chunkification.
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
        pass

    def _pool_element_factory(self) -> POOL_ELEMENT_TYPE:
        """Factory for elements added to pools"""
        pass

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
        pass

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
        # TODO Determine if this should be here or in new OutputManager - needs time.
        pass

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
        pass

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
        pass

    def _save_current_variable_pool(self) -> None:
        """
        Save the current ``variables_pool`` into a JSON file. Flush the ``variables_pool`` and reset the pool size.
        """
        pass

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
        pass

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
        pass

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
        pass

    def _sort_saved_chunk_files(self) -> list[Path]:
        """
        Get a list of all saved chunks of the output variable pool by retrieving all JSON files under
        the ``saved_pool_chunks_path``. Then sort the files according to their file name to preserve the order.
        """
        pass

    def load_saved_pools(self) -> None:
        """
        Loads saved pools of data from JSON files in the ``saved_pool_chunks_path`` directory and merges them into
        a single variables pool.
        """
        pass

    def load_variables_pool_from_file(self, file_path: Path) -> None:
        """
        Loads the ``variables_pool`` from file path provided by user.

        Parameters
        ----------
        file_path : Path
            The path to the file to be loaded to the ``variables_pool``.
        """
        pass

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
        pass

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
        pass

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
        pass

    def _get_parsable_dicts(
        self,
        variable_data: dict[str, Any],
        exclude_info_maps: bool,
    ) -> tuple[list[str], list[Any]]:
        """Returns parsable dictionary keys and ``info_maps`` data for a variable entry."""
        pass

    def _format_variable_entry(
        self,
        name: str,
        variable_data: dict[str, Any],
        exclude_info_maps: bool,
        format_option: str,
    ) -> list[str]:
        """Returns formatted lines for a single variable in the variable names dump."""
        pass

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
        pass

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
        pass

    def _get_flat_variables_pool(self) -> dict[str, Any]:
        """Returns a flattened mapping of variable names to data when multiple pools are loaded."""
        pass

    def flush_pools(self) -> None:
        """Sets each pool to an empty dictionary."""
        pass
