from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from RUFAS.rufas_time import RufasTime


@dataclass
class OutputManagerConfig:
    """
    Attributes
    ----------
    __supported_filter_types_prefixes: dict[str, str]
        A map of allowed filter type prefixes for output filters.
    __end_to_end_testing_filter_prefixes: dict[str, str]
        A map of allowed filter type prefixes for e2e testing filters.
    """
    __supported_filter_types_prefixes: dict[str, str] = {
        "csv": "csv_",
        "graph": "graph_",
        "json": "json_",
        "report": "report_",
    }
    __end_to_end_testing_filter_prefixes: dict[str, str] = {
        "json": "e2e_json_",
        "comparison": "e2e_comparison_",
    }
    time: RufasTime | None = None


class OutputManager:
    """
    Output manager for RuFaS simulation results. Works by collecting variables,
    logs, warnings, and errors into separate pools, and populates requested
    output channels from the pools once the simulation is done.
    """
    __instance: OutputManager | None = None
    pool_element_type = dict[str, Any]
    JSON_OUTPUT_MAX_RECURSIVE_DEPTH = 4
    _VARIABLE_DUMP_KEYS_TO_IGNORE = frozenset(
        ["units", "timestep", "info_maps", "prefix", "suffix", "data_origin", "number_animals_in_pen", "simulation_day"]
    )

    def __new__(cls, config: OutputManagerConfig | None = None) -> OutputManager:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, config: OutputManagerConfig | None = None) -> None:
        if hasattr(self, "_config"):
            return

        if config is None:
            raise RuntimeError(
                "OutputManager must be configured when it is first instantiated."
            )

        self._config = config
        self.__metadata_prefix: str = ""
        self.is_end_to_end_testing_run: bool = False
        self.is_first_post_processing: bool = True
        self._exclude_info_maps_flag: bool = False

    @property
    def config(self) -> OutputManagerConfig:
        return self._config

    @property
    def _filter_prefixes(self) -> dict[str, str]:
        """Returns the appropriate set of acceptable filter prefixes."""
        if self.is_end_to_end_testing_run:
            return self.config.__end_to_end_testing_filter_prefixes
        else:
            return self.config.__supported_filter_types_prefixes

    def run_startup_sequence() -> None:
        pass

    def set_metadata_prefix(self, metadata_prefix: str) -> None:
        """Sets the metadata_prefix attribute."""
        self.__metadata_prefix = metadata_prefix
        pass

    def set_exclude_info_maps_flag(self, exclude_info_maps: bool) -> None:
        """
        Sets the ``exclude_info_maps`` flag to the given value.
        Parameters
        ----------
        exclude_info_maps : bool
            The value to set the ``exclude_info_maps`` flag to.
        """

        self._exclude_info_maps_flag = exclude_info_maps

    def save_results() -> None:
        pass

    def _route_save_functions() -> None:
        pass

    def dump_all_nondata_pools() -> None:
        pass

    def summarize_e2e_test_results() -> None:
        pass

    def _exclude_info_maps() -> None:
        pass

    def filter_variables_pool() -> None:
        pass

    def _parse_filtered_variables() -> None:
        pass

    def _list_filter_files_in_dir() -> None:
        pass
