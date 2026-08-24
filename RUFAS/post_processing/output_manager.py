from dataclasses import dataclass


@dataclass
class OutputManagerConfig:
    """
    Attributes
    ----------
    """


class OutputManager:
    """
    Output manager for RuFaS simulation results. Works by collecting variables,
    logs, warnings, and errors into separate pools, and populates requested
    output channels from the pools once the simulation is done.
    """
    __instance = None
    pool_element_type = dict[str, Any]
    JSON_OUTPUT_MAX_RECURSIVE_DEPTH = 4
    _VARIABLE_DUMP_KEYS_TO_IGNORE = frozenset(
        ["units", "timestep", "info_maps", "prefix", "suffix", "data_origin", "number_animals_in_pen", "simulation_day"]
    )

    def __new__(cls, config: OutputManagerConfig) -> OutputManager:
        if not hasattr(cls, "instance"):
            cls.instance = super(OutputManager, cls).__new__(cls)
        return cls.instance

    def __init__(self, config: OutputManagerConfig) -> None:
        pass
