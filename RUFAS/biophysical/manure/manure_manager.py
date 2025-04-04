from typing import Any

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.processor_enum import ProcessorType
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


class ManureManager:
    def __init__(self) -> None:
        self._om = OutputManager()

        self.all_processors: dict[str, Processor] = {}
        self._all_separators: dict[str, Separator] = {}

        self._adjacency_matrix: dict[str, dict[str, float]] = {}
        self._processing_order: list[Processor] = []

        im = InputManager()
        manure_management_config: dict[str, list[dict[str, Any]]] = im.get_data("manure")
        processor_definitions_by_name = self._validate_unique_processor_names(manure_management_config)
        processor_connections_by_name = self._ensure_referenced_processors_defined(
            manure_management_config, processor_definitions_by_name)
        self._create_all_processors(processor_connections_by_name, processor_definitions_by_name)
        self._populate_adjacency_matrix(processor_connections_by_name)

    def _validate_unique_processor_names(
            self, manure_management_config: dict[str, list[dict[str, Any]]]
    ) -> dict[str, dict[str, Any]]:
        info_map = {
            "class": self.__class__.__name__,
            "function": self._validate_unique_processor_names.__name__,
        }

        processor_definition_list: list[dict[str, Any]] = (
            manure_management_config["anaerobic_digester"]
            + manure_management_config["separator"]
            + manure_management_config["storage"]
            + manure_management_config["handler"]
        )
        processor_definitions_by_name: dict[str, dict[str, Any]] = {
            processor_config["name"]: processor_config for processor_config in processor_definition_list
        }
        unique_processor_names: set[str] = set()
        duplicate_processor_names: set[str] = set(
            [processor_name for processor_name in processor_definitions_by_name.keys()
             if processor_name in unique_processor_names or unique_processor_names.add(processor_name)]
        )

        if len(duplicate_processor_names) > 0:
            self._om.add_error(
                "Duplicate Processor Definitions.",
                f"Duplicate Processor Definitions found for {duplicate_processor_names}.",
                info_map
            )
            raise ValueError(f"Duplicate Processor Definitions found for {duplicate_processor_names}.")
        return processor_definitions_by_name

    def _ensure_referenced_processors_defined(
            self,
            manure_management_config: dict[str, list[dict[str, Any]]],
            processor_definitions_by_name: dict[str, dict[str, Any]]
    ) -> dict[str, dict[str, list[dict[str, Any]]]]:
        info_map = {
            "class": self.__class__.__name__,
            "function": self._ensure_referenced_processors_defined.__name__,
        }

        processor_connections: list[dict[str, Any]] = (manure_management_config["processor_connections"]
                                                       + manure_management_config["separator_connections"])
        all_referenced_processor_names: set[str] = set()
        processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for origin in processor_connections:
            if (origin_processor_name := origin["processor_name"]) in processor_connections_by_name.keys():
                self._om.add_error(
                    "Duplicate connection definitions",
                    f"Duplicate connection definitions found for {origin_processor_name}.",
                    info_map
                )
                raise ValueError(f"Duplicate connection definitions found for {origin_processor_name}.")

            all_referenced_processor_names.add(origin_processor_name)
            destinations: list[dict[str, Any]] = []
            if "destinations" in origin.keys():
                destinations = origin["destinations"]
                processor_connections_by_name[origin_processor_name] = {"destinations": destinations}
            elif "solid_output_destinations" in origin.keys() and "liquid_output_destinations" in origin.keys():
                destinations = origin["solid_output_destinations"] + origin["liquid_output_destinations"]
                processor_connections_by_name[origin_processor_name] = {
                    "solid_output_destinations": origin["solid_output_destinations"],
                    "liquid_output_destinations": origin["liquid_output_destinations"],
                }
            for destination in destinations:
                all_referenced_processor_names.add(destination["receiving_processor_name"])

        unknown_processor_names: set[str] = set()
        undefined_processor_connections: set[str] = set()
        for processor_name in all_referenced_processor_names:
            if processor_name not in processor_definitions_by_name.keys():
                unknown_processor_names.add(processor_name)
                self._om.add_error(
                    "Unknown Processor Name.",
                    f"No configuration found for {processor_name}.",
                    info_map
                )
            if processor_name not in processor_connections_by_name.keys():
                undefined_processor_connections.add(processor_name)
                self._om.add_error(
                    "Undefined Processor Connection.",
                    f"No routing configurations found for {processor_name}.",
                    info_map
                )

        if len(unknown_processor_names) > 0:
            raise ValueError(f"Unknown Processor Name found for {unknown_processor_names}.")
        if len(undefined_processor_connections) > 0:
            raise ValueError(f"Undefined Routing Connections for {undefined_processor_connections}.")

        return processor_connections_by_name

    def _create_all_processors(
            self,
            processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
            processor_definitions_by_name: dict[str, dict[str, Any]]
    ) -> None:
        for processor_name in processor_connections_by_name.keys():
            processor_definition = processor_definitions_by_name[processor_name]
            processor = ProcessorType.get_processor_class(processor_definition["type"])(**processor_definition)
            self.all_processors[processor_name] = processor

    def _populate_adjacency_matrix(
            self, processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]]
    ) -> None:
        row_names: list[str] = list(self.all_processors.keys())
        for row_name in row_names:
            if row_name in self._all_separators.keys():
                row_names.remove(row_name)
                row_names += [f"{row_name}_input", f"{row_name}_solid_output", f"{row_name}_liquid_output"]

        for origin_name, connections in processor_connections_by_name.items():
            if origin_name in self._all_separators.keys():
                self._adjacency_matrix[f"{origin_name}_input"] = {
                    destination_name: 0.0 for destination_name in row_names
                }
                self._adjacency_matrix[f"{origin_name}_solid_output"] = {
                    destination_name: 0.0 for destination_name in row_names
                }
                self._adjacency_matrix[f"{origin_name}_liquid_output"] = {
                    destination_name: 0.0 for destination_name in row_names
                }
                for destination in connections["solid_output_destinations"]:
                    receiving_processor_name = destination["receiving_processor_name"]
                    if receiving_processor_name in self._all_separators.keys():
                        receiving_processor_name = f"{receiving_processor_name}_input"
                    self._adjacency_matrix[origin_name][receiving_processor_name] = destination["proportion"]
                for destination in connections["liquid_output_destinations"]:
                    receiving_processor_name = destination["receiving_processor_name"]
                    if receiving_processor_name in self._all_separators.keys():
                        receiving_processor_name = f"{receiving_processor_name}_input"
                    self._adjacency_matrix[origin_name][receiving_processor_name] = destination["proportion"]
            else:
                self._adjacency_matrix[origin_name] = {
                    destination_name: 0.0 for destination_name in row_names
                }
                for destination in connections["destinations"]:
                    receiving_processor_name = destination["receiving_processor_name"]
                    if receiving_processor_name in self._all_separators.keys():
                        receiving_processor_name = f"{receiving_processor_name}_input"
                    self._adjacency_matrix[origin_name][receiving_processor_name] = destination["proportion"]
