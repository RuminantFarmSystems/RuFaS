from collections import deque
from typing import Any

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.processor_enum import ProcessorType
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


PROCESSOR_CATEGORIES = ["anaerobic_digester", "separator", "storage", "handler"]


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
        manure_management_config: dict[str, list[dict[str, Any]]] = im.get_data("manure_management")
        processor_connections_input: dict[str, list[dict[str, Any]]] = im.get_data("manure_connections")

        processor_configs_by_name = self._get_processor_configs_by_name(manure_management_config)
        processor_connections_by_name = self._validate_and_parse_processor_connections(
            processor_connections_input, processor_configs_by_name
        )
        self._create_all_processors(processor_connections_by_name, processor_configs_by_name)
        self._populate_adjacency_matrix(processor_connections_by_name)

        self._validate_adjacency_matrix()

    def _validate_adjacency_matrix(self) -> None:
        """Validates the generated adjacency matrix."""
        for origin, destinations in self._adjacency_matrix.items():
            if destinations[origin] != 0:
                raise ValueError(f"The diagonal for origin {origin} is not 0.")
            column_sum = sum(destinations.values())
            if column_sum not in (0, 1):
                raise ValueError(f"Sum for {origin} column must be 0 or 1, but got {column_sum}")

    def _combine_adjacency_matrix_for_seperators(self) -> dict[str, dict[str, float]]:
        """Combines the seperator destinations for traversal."""

    def _traverse_adjacency_matrix(self) -> list[str]:
        """Finds the order of processing the processor."""
        all_nodes = set(self._adjacency_matrix.keys())

        in_degree = {node: 0 for node in all_nodes}

        for destinations in self._adjacency_matrix.values():
            for dest, weight in destinations.items():
                if weight != 0.0:
                    in_degree[dest] += 1

        queue = deque()
        for node in all_nodes:
            if in_degree[node] == 0:
                queue.append(node)

        sorted_order = []

        while queue:
            node = queue.popleft()
            sorted_order.append(node)
            for dest, weight in self._adjacency_matrix[node].items():
                if weight != 0.0:
                    in_degree[dest] -= 1
                    if in_degree[dest] == 0:
                        queue.append(dest)

        if len(sorted_order) != len(all_nodes):
            raise ValueError("Cycle detected — topological sort not possible.")

        return sorted_order


    def _get_processor_configs_by_name(
        self, manure_management_config: dict[str, list[dict[str, Any]]]
    ) -> dict[str, dict[str, Any]]:
        """
        Validates the uniqueness of processor names within the manure management configuration.

        Parameters
        ----------
        manure_management_config : dict[str, list[dict[str, Any]]]
            A dictionary containing lists of processor configurations grouped by categories such
            as 'anaerobic_digester', 'separator', 'storage', and 'handler'.

        Returns
        -------
        dict[str, dict[str, Any]]
            A dictionary mapping each unique processor name to its corresponding processor
            configuration dictionary.

        Notes
        -----
        The method internally combines all processor configurations from different categories,
        extracts all processor names, checks for duplicates, and creates a mapping of processor
        names to their respective configurations.
        """
        processor_configs_list: list[dict[str, Any]] = []
        for category in PROCESSOR_CATEGORIES:
            processor_configs_list.extend(manure_management_config[category])
        all_processor_names: list[str] = [processor_config["name"] for processor_config in processor_configs_list]
        self._check_for_duplicate_processor_names(all_processor_names)

        processor_configs_by_name: dict[str, dict[str, Any]] = {
            processor_config["name"]: processor_config for processor_config in processor_configs_list
        }
        return processor_configs_by_name

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
        duplicate_processor_names: set[str] = set()
        for processor_name in all_processor_names:
            if processor_name in unique_processor_names:
                duplicate_processor_names.add(processor_name)
            else:
                unique_processor_names.add(processor_name)
        if len(duplicate_processor_names) > 0:
            self._om.add_error(
                "Duplicate Processor Definitions.",
                f"Duplicate Processor Definitions found for {duplicate_processor_names}.",
                info_map,
            )
            raise ValueError(f"Duplicate Processor Definitions found for {duplicate_processor_names}.")

    def _validate_and_parse_processor_connections(
        self,
        processor_connections_input: dict[str, list[dict[str, Any]]],
        processor_configs_by_name: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, list[dict[str, Any]]]]:
        """
        Validates and parses the processor connections defined in the manure management configuration.

        Parameters
        ----------
        processor_connections_input : dict[str, list[dict[str, Any]]]
            The processor connection configuration, containing regular processor and separator connections.

        processor_configs_by_name : dict[str, dict[str, Any]]
            A dictionary mapping processor names to their respective configurations.

        Returns
        -------
        dict[str, dict[str, list[dict[str, Any]]]]
            A dictionary mapping processor names to their respective connection details.
        """
        all_processor_connections: list[dict[str, Any]] = (
            processor_connections_input["processor_connections"] + processor_connections_input["separator_connections"]
        )
        processor_names_in_connection_map: set[str] = self._find_all_processor_names_in_connection_map(
            all_processor_connections
        )
        processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]] = (
            self._build_processor_connection_map(all_processor_connections)
        )

        self._check_for_unknown_processor_names(processor_names_in_connection_map, processor_configs_by_name)
        self._check_for_processors_without_connection_definition(
            processor_names_in_connection_map, processor_connections_by_name
        )

        return processor_connections_by_name

    def _check_for_unknown_processor_names(
        self, processor_names_in_connection_map: set[str], processor_configs_by_name: dict[str, dict[str, Any]]
    ) -> None:
        """
        Validates if all processor names referenced in connection config are defined in the processor configurations.

        Parameters
        ----------
        processor_names_in_connection_map : set[str]
            Set of all processor names referenced in the connection configuration.
        processor_configs_by_name : dict[str, dict[str, Any]]
            Dictionary mapping processor names to their respective configurations.

        Raises
        ------
        ValueError
            If any referenced processor name does not exist in the processor configurations.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._check_for_unknown_processor_names.__name__,
        }
        unknown_processor_names: set[str] = set()
        for processor_name in processor_names_in_connection_map:
            if processor_name not in processor_configs_by_name:
                unknown_processor_names.add(processor_name)
                self._om.add_error("Unknown Processor Name.", f"No configuration found for {processor_name}.", info_map)
        if len(unknown_processor_names) > 0:
            raise ValueError(f"Unknown Processor: no processor config found for {unknown_processor_names}.")

    def _check_for_processors_without_connection_definition(
        self,
        processor_names_in_connection_map: set[str],
        processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]],
    ) -> None:
        """
        Checks for processors that are referenced but lack connection definitions.

        Parameters
        ----------
        processor_names_in_connection_map : set[str]
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
        for processor_name in processor_names_in_connection_map:
            if processor_name not in processor_connections_by_name:
                processors_without_connection_definition.add(processor_name)
                self._om.add_error(
                    "Undefined Processor Connection.",
                    f"No routing configurations found for {processor_name}.",
                    info_map,
                )
        if len(processors_without_connection_definition) > 0:
            raise ValueError(f"Undefined Routing Connections for {processors_without_connection_definition}.")

    def _find_all_processor_names_in_connection_map(self, processor_connections: list[dict[str, Any]]) -> set[str]:
        """
        Retrieves all referenced processor names from a list of processor connections.

        Parameters
        ----------
        processor_connections : list[dict[str, Any]]
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
            all_referenced_processor_names.add(origin_processor_name)
            is_separator: bool = "solid_output_destinations" in origin and "liquid_output_destinations" in origin
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

        Examples
        --------
        >>> connections = [
        ...     {
        ...         "processor_name": "Handler1",
        ...         "destinations": [{"name": "Separator1", "proportion": 1.0}],
        ...     },
        ...     {
        ...         "processor_name": "Storage1",
        ...         "destinations": [],
        ...     },
        ...     {
        ...         "processor_name": "Storage2",
        ...         "destinations": [],
        ...     },
        ...     {
        ...         "processor_name": "Separator1",
        ...         "solid_output_destinations": [{"name": "Storage1", "proportion": 1.0}],
        ...         "liquid_output_destinations": [{"name": "Storage2", "proportion": 1.0}],
        ...     },
        ... ]

        >>> self._build_processor_connection_map(connections)
        {
            "Handler1": {
                "destinations": [{"name": "Separator1", "proportion": 1.0}]
            },
            "Storage1": {
                "destinations": []
            },
            "Storage2": {
                "destinations": []
            },
            "Separator1": {
                "solid_output_destinations": [{"name": "Storage1", "proportion": 1.0}],
                "liquid_output_destinations": [{"name": "Storage2", "proportion": 1.0}],
            }
        }
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._build_processor_connection_map.__name__,
        }

        processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for origin in processor_connections:
            origin_processor_name = origin["processor_name"]

            if origin_processor_name in processor_connections_by_name:
                self._om.add_error(
                    "Duplicate processor connection definitions",
                    f"Duplicate connection definitions found for {origin_processor_name}.",
                    info_map,
                )
                raise ValueError(f"Duplicate connection definitions found for {origin_processor_name}.")

            is_separator: bool = "solid_output_destinations" in origin and "liquid_output_destinations" in origin
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
        processor_configs_by_name: dict[str, dict[str, Any]],
    ) -> None:
        """
        Creates and initializes all processors based on their definitions.

        Parameters
        ----------
        processor_connections_by_name : dict[str, dict[str, list[dict[str, Any]]]]
            A dictionary that maps processor names to their associated connection configurations.
        processor_configs_by_name : dict[str, dict[str, Any]]
            A dictionary that contains processor definitions, where each key is the processor name and
            the value is a dictionary with the processor's parameters and type.
        """
        for processor_name in processor_connections_by_name:
            processor_config = processor_configs_by_name[processor_name]
            processor_type = processor_config["type"]

            processor_initializer = ProcessorType.get_processor_class(processor_type)
            del processor_config["type"]
            processor = processor_initializer(**processor_config)
            self.all_processors[processor_name] = processor

            if isinstance(processor, Separator):
                self._all_separators[processor_name] = processor

    def _populate_adjacency_matrix(
        self, processor_connections_by_name: dict[str, dict[str, list[dict[str, Any]]]]
    ) -> None:
        """
        Builds the adjacency matrix using processor connection data.
        This method iterates over the provided connection mappings, identifying whether each processor is a separator or
        a standard processor. It then creates corresponding columns in the adjacency matrix and fills in output
        proportions based on the processor type:
        - For separators: handles both solid and liquid output destinations.
        - For other processors: handles general destinations.

        Parameters
        ----------
        processor_connections_by_name : dict[str, dict[str, list[dict[str, Any]]]]
            A dictionary where the keys are processor names, and the values contain information about their
            connections to other processors.
        """
        row_names: list[str] = self._generate_adjacency_matrix_keys()

        for origin_name, connections in processor_connections_by_name.items():
            is_separator: bool = origin_name in self._all_separators
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
        to each destination. If the receiving processor name corresponds to an separator, its name is modified to
        include the '_input' suffix before updating the matrix.

        Parameters
        ----------
        connections : list[dict[str, Any]]
            A list of connection dictionaries, where each dictionary contains information about the
            receiving processor name and the proportion of the connection.
        origin_name : str
            The name of the origin from which connections are originating.
        """
        for destination in connections:
            receiving_processor_name = destination["receiving_processor_name"]
            if receiving_processor_name in self._all_separators:
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
        original_row_names: list[str] = list(self.all_processors)
        result_row_names: list[str] = []
        for row_name in original_row_names:
            if row_name in self._all_separators:
                result_row_names += [f"{row_name}_input", f"{row_name}_solid_output", f"{row_name}_liquid_output"]
            else:
                result_row_names.append(row_name)
        return result_row_names
