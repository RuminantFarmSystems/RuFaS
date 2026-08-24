from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OutputManagerConfig:
    """
    Attributes
    ----------
    __metadata_prefix: str
        The prefix of the metadata used for the simulation.
    _exclude_info_maps_flag: bool
        A flag indicating whether ``info_maps`` should be exlcuded when adding variables to pool.
    time: RufasTime | None
        A ``RufasTime`` object used to track the simulation time.
    __supported_filter_types_prefixes: dict[str, str]
        A map of allowed filter type prefixes for output filters.
    __end_to_end_testing_filter_prefixes: dict[str, str]
        A map of allowed filter type prefixes for e2e testing filters.
    """
    __metadata_prefix: str = ""
    


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
        self.is_end_to_end_testing_run: bool = False
        self.is_first_post_processing: bool = True

    @property
    def config(self) -> OutputManagerConfig:
        return self._config
