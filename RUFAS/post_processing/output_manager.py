from __future__ import annotations

from typing import Any

from RUFAS.post_processing.file_manager import FileManager
from RUFAS.post_processing.output_config_validator import OutputConfigValidator
from RUFAS.post_processing.pool_manager import PoolManager
from RUFAS.rufas_time import RufasTime





class OutputManager:
    """
    Output manager for RuFaS simulation results. Works by collecting variables,
    logs, warnings, and errors into separate pools, and populates requested
    output channels from the pools once the simulation is done.
    """

    __instance: OutputManager | None = None

    def __new__(cls) -> OutputManager:
        if not hasattr(cls, "instance"):
            cls.instance = super(OutputManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if OutputManager.__instance is None:
            OutputManager.__instance = self
            self.__metadata_prefix: str = ""
            self.is_end_to_end_testing_run: bool = False
            self.is_first_post_processing: bool = True
            self._exclude_info_maps_flag: bool = False
            self.__supported_filter_types_prefixes: dict[str, str] = {
                "csv": "csv_",
                "graph": "graph_",
                "json": "json_",
                "report": "report_",
            }
            self.__end_to_end_testing_filter_prefixes: dict[str, str] = {
                "json": "e2e_json_",
                "comparison": "e2e_comparison_",
            }
            self.time: RufasTime | None = None
            self.file_manager = FileManager(self.__metadata_prefix, self._filter_prefixes)
            self.pool_manager = PoolManager(self.file_manager)
            self.output_config_validator = OutputConfigValidator()

    @property
    def _filter_prefixes(self) -> dict[str, str]:
        """Returns the appropriate set of acceptable filter prefixes."""
        if self.is_end_to_end_testing_run:
            return self.__end_to_end_testing_filter_prefixes
        else:
            return self.__supported_filter_types_prefixes

    def run_startup_sequence() -> None:
        pass

    def set_metadata_prefix(self, metadata_prefix: str) -> None:
        """Sets the metadata_prefix attribute."""
        self.__metadata_prefix = metadata_prefix
        self.file_manager.metadata_prefix = metadata_prefix

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
