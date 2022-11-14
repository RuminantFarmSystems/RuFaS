# !/usr/bin/env python3


from typing import Any, Dict


class OutputManager (object):
    """
    Output manager for Rufas simulation results. Works by collecting variables into
    the pool, and populates requested output channels from the pool once the simulation
    is done. 

    Attributes:
        pool (Dict[str, Any]): Contains variables reported from simulation engine
    """

    def __init__(self) -> None:
        self.pool: Dict[str, Any] = {}

    def collect(self, name: str, value: Any, caller: Any) -> None:
        key = f"{self.__get_prefix(caller)}_{name}_{self.__get_suffix(name,caller)}"
        self.__add_to_pool(key, value)

    def __add_to_pool(self, key: str, value: Any) -> None:
        pass

    def __get_prefix(self, caller: Any) -> str:
        pass

    def __get_suffix(self, name: str, caller: Any) -> str:
        pass

    def __read_json_configs(self)->None:
        pass

    def save_to_file(self)->None:
        pass