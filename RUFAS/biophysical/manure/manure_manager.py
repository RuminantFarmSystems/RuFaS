from typing import Any

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.processor_enum import ProcessorType
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


class ManureManager:
    """
    Manages the manure processing system by handling processor definitions,
    connections, adjacency matrix, and processing order.

    Attributes
    ----------
    _om : OutputManager
        An instance of OutputManager for logging errors and information.
    all_processors : dict[str, Processor]
        A dictionary mapping processor names to their instances.
    _all_separators : dict[str, Separator]
        A dictionary mapping separator names to their instances.
    _adjacency_matrix : dict[str, dict[str, float]]
        A matrix defining the connections between processors, weighted by connection properties.
    _processing_order : list[Processor]
        A list defining the execution order of processors.
    """

    def __init__(self) -> None:
        self._om = OutputManager()

        self.all_processors: dict[str, Processor] = {}
        self._all_separators: dict[str, Separator] = {}

        self._adjacency_matrix: dict[str, dict[str, float]] = {}
        self._processing_order: list[str] = []

        im = InputManager()
        manure_management_config: dict[str, list[dict[str, Any]]] = im.get_data("manure")

        processor_definitions_by_name = self._validate_unique_processor_names(manure_management_config)
        processor_connections_by_name = self._validate_and_parse_processor_connections(
            manure_management_config, processor_definitions_by_name
        )
        self._create_all_processors(processor_connections_by_name, processor_definitions_by_name)
        self._populate_adjacency_matrix(processor_connections_by_name)

    def _validate_unique_processor_names(
        self, manure_management_config: dict[str, list[dict[str, Any]]]
    ) -> dict[str, dict[str, Any]]:
        """
        Validates the uniqueness of processor names within the manure management configuration.

        Parameters
        ----------
        manure_management_config : dict[str, list[dict[str, Any]]]
            A dictionary containing lists of processor definitions grouped by categories such
            as 'anaerobic_digester', 'separator', 'storage', and 'handler'. Each processor
            definition is expected to be a dictionary containing at least a 'name' key.

        Returns
        -------
        dict[str, dict[str, Any]]
            A dictionary mapping each unique processor name to its corresponding processor
            definition dictionary.

        Raises
        ------
        ValueError
            If duplicate processor names are found within the manure management configuration.

        Notes
        -----
        The method internally combines all processor definitions from different categories,
        extracts all processor names, checks for duplicates, and creates a mapping of processor
        names to their respective definitions.
        """
        processor_definition_list: list[dict[str, Any]] = (
            manure_management_config["anaerobic_digester"]
            + manure_management_config["separator"]
            + manure_management_config["storage"]
            + manure_management_config["handler"]
        )
        all_processor_names: list[str] = [processor_config["name"] for processor_config in processor_definition_list]
        self._check_for_duplicate_processor_names(all_processor_names)

        processor_definitions_by_name: dict[str, dict[str, Any]] = {
            processor_config["name"]: processor_config for processor_config in processor_definition_list
        }
        return processor_definitions_by_name

    def _check_for_duplicate_processor_names(self, all_processor_names: list[str]) -> None:
        """
        Checks for duplicate processor names in the provided list.

        If duplicate processor names are found, this method logs an error message
        and raises a ValueError indicating the duplicate names.

        Parameters
        ----------
        all_processor_names : list[str]
            A list of processor names to be checked for duplicates.

        Raises
        ------
        ValueError
            If duplicate processor names are found, a ValueError is raised with
            the details of the duplicates.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._check_for_duplicate_processor_names.__name__,
        }
        unique_processor_names: set[str] = set()
        duplicate_processor_names: set[str] = set(
            [
                processor_name
                for processor_name in all_processor_names
                if processor_name in unique_processor_names or unique_processor_names.add(processor_name)
            ]
        )
        if len(duplicate_processor_names) > 0:
            self._om.add_error(
                "Duplicate Processor Definitions.",
                f"Duplicate Processor Definitions found for {duplicate_processor_names}.",
                info_map,
            )
            raise ValueError(f"Duplicate Processor Definitions found for {duplicate_processor_names}.")

    def _validate_and_parse_processor_connections(
        self,
        manure_management_config: dict[str, list[dict[str, Any]]],
        processor_definitions_by_name: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, list[dict[str, Any]]]]:
        """
        Validates and parses the processor connections defined in the manure management configuration.

        Parameters
        ----------
        manure_management_config : dict[str, list[dict[str, Any]]]
            The configuration for manure management, containing regular processor and separator connections.

        processor_definitions_by_name : dict[str, dict[str, Any]]
            A dictionary mapping processor names to their respective definitions.

        Returns
        -------
        dict[str, dict[str, list[dict[str, Any]]]]
            A dictionary mapping processor names to their respective connection details.
        """
        processor_connections: list[dict[str, Any]] = (
            manure_management_config["processor_connections"] + manure_management_config["separator_connections"]
        )
        all_referenced_processor_names: set[str] = self._find_all_referenced_processor_names(processor_connections)
        processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]] = (
            self._build_processor_connection_map(processor_connections)
        )

        self._check_for_unknown_processor_names(all_referenced_processor_names, processor_definitions_by_name)
        self._check_for_processors_without_connection_definition(
            all_referenced_processor_names, processor_connections_by_name
        )

        return processor_connections_by_name

    def _check_for_unknown_processor_names(
        self, all_referenced_processor_names: set[str], processor_definitions_by_name: dict[str, dict[str, Any]]
    ) -> None:
        """
        Validates if all processor names referenced are defined in the processor definitions.

        Parameters
        ----------
        all_referenced_processor_names : set[str]
            Set of all processor names referenced in the connection configuration.
        processor_definitions_by_name : dict[str, dict[str, Any]]
            Dictionary mapping processor names to their respective configurations.

        Raises
        ------
        ValueError
            If any referenced processor name does not exist in the processor definitions.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._check_for_unknown_processor_names.__name__,
        }
        unknown_processor_names: set[str] = set()
        for processor_name in all_referenced_processor_names:
            if processor_name not in processor_definitions_by_name.keys():
                unknown_processor_names.add(processor_name)
                self._om.add_error("Unknown Processor Name.", f"No configuration found for {processor_name}.", info_map)
        if len(unknown_processor_names) > 0:
            raise ValueError(f"Unknown Processor Name found for {unknown_processor_names}.")

    def _check_for_processors_without_connection_definition(
        self,
        all_referenced_processor_names: set[str],
        processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    ) -> None:
        """
        Checks for processors that are referenced but lack connection definitions.

        Parameters
        ----------
        all_referenced_processor_names : set[str]
            A set of names of all processors that are referenced and expected to have routing configurations.
        processor_connections_by_name : dict[str, dict[str, list[dict[str, Any]]]]
            A mapping of processor names to their routing connections, defining the configuration details.

        Raises
        ------
        ValueError
            If any processors are found to be missing a routing configuration.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._check_for_processors_without_connection_definition.__name__,
        }
        processors_without_connection_definition: set[str] = set()
        for processor_name in all_referenced_processor_names:
            if processor_name not in processor_connections_by_name.keys():
                processors_without_connection_definition.add(processor_name)
                self._om.add_error(
                    "Undefined Processor Connection.",
                    f"No routing configurations found for {processor_name}.",
                    info_map,
                )
        if len(processors_without_connection_definition) > 0:
            raise ValueError(f"Undefined Routing Connections for {processors_without_connection_definition}.")

    def _find_all_referenced_processor_names(self, processor_connections: list[dict[str, Any]]) -> set[str]:
        """
        Retrieves all referenced processor names from a list of processor connections.

        Parameters
        ----------
        processor_connections : list of dict
            A list containing dictionaries that define connections between processors. Each dictionary is expected to
            have a "processor_name" key, and either "solid_output_destinations" and "liquid_output_destinations",
            or "destinations".

        Returns
        -------
        set[str]
            A set of all unique processor names (both as origin and as destination) referenced in the connections.
        """
        all_referenced_processor_names: set[str] = set()
        for origin in processor_connections:
            origin_processor_name = origin["processor_name"]

            is_separator: bool = (
                "solid_output_destinations" in origin.keys() and "liquid_output_destinations" in origin.keys()
            )
            all_referenced_processor_names.add(origin_processor_name)
            destinations: list[dict[str, Any]] = (
                (origin["solid_output_destinations"] + origin["liquid_output_destinations"])
                if is_separator
                else origin["destinations"]
            )

            for destination in destinations:
                all_referenced_processor_names.add(destination["receiving_processor_name"])
        return all_referenced_processor_names

    def _build_processor_connection_map(
        self, processor_connections: list[dict[str, Any]]
    ) -> dict[str, dict[str, list[dict[str, Any]]]]:
        """
        Adds a list of processor connections to a structured map.

        Parameters
        ----------
        processor_connections : list[dict[str, Any]]
            A list of dictionaries, where each dictionary represents a processor connection.
            Each dictionary should include information about the processor's name and its destinations.

        Returns
        -------
        dict[str, dict[str, list[dict[str, Any]]]]
            A dictionary mapping processor names to their connection details.
            If the processor acts as a separator, it contains keys including "solid_output_destinations"
            and "liquid_output_destinations". Otherwise, it contains a key "destinations".

        Raises
        ------
        ValueError
            If duplicate connection definitions are found for a processor name.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._build_processor_connection_map.__name__,
        }

        processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for origin in processor_connections:
            origin_processor_name = origin["processor_name"]

            if origin_processor_name in processor_connections_by_name.keys():
                self._om.add_error(
                    "Duplicate connection definitions",
                    f"Duplicate connection definitions found for {origin_processor_name}.",
                    info_map,
                )
                raise ValueError(f"Duplicate connection definitions found for {origin_processor_name}.")

            is_separator: bool = (
                "solid_output_destinations" in origin.keys() and "liquid_output_destinations" in origin.keys()
            )
            if is_separator:
                processor_connections_by_name[origin_processor_name] = {
                    "solid_output_destinations": origin["solid_output_destinations"],
                    "liquid_output_destinations": origin["liquid_output_destinations"],
                }
            else:
                processor_connections_by_name[origin_processor_name] = {"destinations": origin["destinations"]}
        return processor_connections_by_name

    def _create_all_processors(
        self,
        processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
        processor_definitions_by_name: dict[str, dict[str, Any]],
    ) -> None:
        """
        Creates and initializes all processors based on their definitions.

        Parameters
        ----------
        processor_connections_by_name : dict[str, dict[str, list[dict[str, Any]]]]
            A dictionary that maps processor names to their associated connection configurations.
        processor_definitions_by_name : dict[str, dict[str, Any]]
            A dictionary that contains processor definitions, where each key is the processor name and
            the value is a dictionary with the processor's parameters and type.

        Returns
        -------
        None
        """
        for processor_name in processor_connections_by_name.keys():
            processor_definition = processor_definitions_by_name[processor_name]
            processor_type = processor_definition["type"]

            processor_initializer = ProcessorType.get_processor_class(processor_type)
            del processor_definition["type"]
            processor = processor_initializer(**processor_definition)
            self.all_processors[processor_name] = processor

            if isinstance(processor, Separator):
                self._all_separators[processor_name] = processor

    def _populate_adjacency_matrix(
        self, processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]]
    ) -> None:
        """
        Populates the adjacency matrix by processing the provided dictionary of processor connections.

        This method iterates through the connection data, differentiating between separators and other processors.
        It builds out the adjacency matrix structure and calculates proportions for both solid and liquid outputs
        for separators, or general destinations for non-separators.

        Parameters
        ----------
        processor_connections_by_name : dict[str, dict[str, list[dict[str, Any]]]]
            A dictionary where the keys are processor names, and the values contain information about their
            connections to other processors.

        Returns
        -------
        None
        """
        row_names: list[str] = self._generate_adjacency_matrix_keys()

        for origin_name, connections in processor_connections_by_name.items():
            is_separator: bool = origin_name in self._all_separators.keys()
            if is_separator:
                self._create_column_in_adjacency_matrix(origin_name, row_names, is_separator)
                self._populate_destination_proportions(
                    connections["solid_output_destinations"], f"{origin_name}_solid_output"
                )
                self._populate_destination_proportions(
                    connections["liquid_output_destinations"], f"{origin_name}_liquid_output"
                )
            else:
                self._create_column_in_adjacency_matrix(origin_name, row_names, is_separator)
                self._populate_destination_proportions(connections["destinations"], origin_name)

    def _create_column_in_adjacency_matrix(self, origin_name: str, row_names: list[str], is_separator: bool) -> None:
        """
        Add a column to the adjacency matrix for a given origin node.

        This method modifies the adjacency matrix to include connections
        from the specified origin node to a list of destination nodes.
        For separators, it creates multiple columns representing distinct
        output types (input, solid output, liquid output). For non-separators,
        a single column is created.

        Parameters
        ----------
        origin_name : str
            The name of the origin node for which the column(s) will be created.
        row_names : list[str]
            The list of destination node names to initialize in the adjacency matrix.
        is_separator : bool
            A flag indicating whether the origin node is a separator

        Returns
        -------
        None
        """
        if is_separator:
            self._adjacency_matrix[f"{origin_name}_input"] = {destination_name: 0.0 for destination_name in row_names}
            self._adjacency_matrix[f"{origin_name}_solid_output"] = {
                destination_name: 0.0 for destination_name in row_names
            }
            self._adjacency_matrix[f"{origin_name}_liquid_output"] = {
                destination_name: 0.0 for destination_name in row_names
            }
        else:
            self._adjacency_matrix[origin_name] = {destination_name: 0.0 for destination_name in row_names}

    def _populate_destination_proportions(self, connections: list[dict[str, Any]], origin_name: str) -> None:
        """
        Populate the destination proportions for the given origin in the adjacency matrix.

        This method updates the adjacency matrix to store the proportion of connections from the specified origin
        to each destination. If the receiving processor name corresponds to an internal separator, its name is
        modified to include the '_input' suffix before updating the matrix.

        Parameters
        ----------
        connections : list[dict[str, Any]]
            A list of connection dictionaries, where each dictionary contains information about the
            receiving processor name and the proportion of the connection.
        origin_name : str
            The name of the origin from which connections are originating.

        Returns
        -------
        None
        """
        for destination in connections:
            receiving_processor_name = destination["receiving_processor_name"]
            if receiving_processor_name in self._all_separators.keys():
                receiving_processor_name = f"{receiving_processor_name}_input"
            self._adjacency_matrix[origin_name][receiving_processor_name] = destination["proportion"]

    def _generate_adjacency_matrix_keys(self) -> list[str]:
        """
        Generates a list of keys to be used in constructing an adjacency matrix.

        Returns
        -------
        list[str]
            A list of keys representing the rows/columns of the adjacency matrix.
        """
        row_names: list[str] = list(self.all_processors.keys())
        for row_name in row_names:
            if row_name in self._all_separators.keys():
                row_names.remove(row_name)
                row_names += [f"{row_name}_input", f"{row_name}_solid_output", f"{row_name}_liquid_output"]
        return row_names
