from typing import Any

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.enums import AnimalCombination
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


class ManureManager:
    def __init__(self) -> None:
        im = InputManager()
        self._om = OutputManager()
        manure_management_config: dict[str, Any] = im.get_data("manure")

        self.all_processors: dict[str, Processor] = {}

        # TODO: Update the key for this map after confirming how to handle incoming manure from animal module.
        self._pen_manure_routing_map: dict[AnimalCombination, dict[Processor, float]] = {}
        self._adjacency_matrix: dict[Processor, dict[Processor, float]] = {}
        self._processing_order: list[Processor] = []

    def _create_all_processors(self, manure_management_config: dict[str, Any]) -> None:
        info_map = {
            "class": self.__class__.__name__,
            "function": self._create_all_processors.__name__,
        }
        processor_connections_config: list[dict[str, Any]] = manure_management_config["processor_connections"]
        all_processor_names: list[str] = [processor["processor_name"] for processor in processor_connections_config]
        all_configs: list[dict[str, Any]] = (
            manure_management_config["handler"]
            + manure_management_config["anaerobic_digester"]
            + manure_management_config["separator"]
            + manure_management_config["storage"]
        )
        try:
            all_processor_configs: dict[str, dict[str, Any]] = {
                processor_config["name"]: processor_config for processor_config in all_configs
            }
        except Exception as e:
            # duplicate processor names
            raise e

        for processor_name in all_processor_names:
            if processor_name not in all_processor_configs.keys():
                self._om.add_error("", "", info_map)
                raise ValueError(f"Processor {processor_name} not defined")
            processor_config = all_processor_configs[processor_name]
            self.all_processors[processor_name] = Processor(**processor_config)

    def _populate_pen_manure_routing_map(self, pen_manure_routing_config: dict[str, Any]) -> None:
        pass
