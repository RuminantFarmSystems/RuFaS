import math
from copy import deepcopy
from dataclasses import replace
from typing import Any

from RUFAS.biophysical.manure.field_manure_supplier import FieldManureSupplier
from RUFAS.biophysical.manure.handler.handler import Handler
from RUFAS.biophysical.manure.manure_nutrient_manager import ManureNutrientManager
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.processor_enum import ProcessorType
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.biophysical.manure.storage.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.biophysical.manure.storage.bedded_pack import BeddedPack
from RUFAS.biophysical.manure.storage.composting import Composting
from RUFAS.biophysical.manure.storage.daily_spread import DailySpread
from RUFAS.biophysical.manure.storage.open_lot import OpenLot
from RUFAS.biophysical.manure.storage.slurry_storage_outdoor import SlurryStorageOutdoor
from RUFAS.biophysical.manure.storage.slurry_storage_underfloor import SlurryStorageUnderfloor
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.manure_nutrients import ManureNutrients
from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequest, NutrientRequestResults
from RUFAS.data_structures.manure_types import ManureType
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits

PROCESSOR_CATEGORIES = ["anaerobic_digester", "separator", "storage", "handler"]

STORAGE_CLASS_TO_TYPE: dict[type[Storage], ManureType] = {
    AnaerobicLagoon: ManureType.LIQUID,
    SlurryStorageOutdoor: ManureType.LIQUID,
    SlurryStorageUnderfloor: ManureType.LIQUID,
    BeddedPack: ManureType.SOLID,
    Composting: ManureType.SOLID,
    OpenLot: ManureType.SOLID,
    DailySpread: ManureType.SOLID,
}


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

    def __init__(self, intercept_mean_temp: float, phase_shift: float, amplitude: float) -> None:
        self._om = OutputManager()
        self._manure_nutrient_manager = ManureNutrientManager()

        self.all_processors: dict[str, Processor] = {}
        self._all_separators: dict[str, Separator] = {}

        self._adjacency_matrix: dict[str, dict[str, float]] = {}
        self._processing_order: list[str] = []

        im = InputManager()
        manure_management_config: dict[str, list[dict[str, Any]]] = im.get_data("manure_management")
        processor_connections_input: dict[str, list[dict[str, Any]]] = im.get_data("manure_processor_connection")

        processor_configs_by_name = self._get_processor_configs_by_name(manure_management_config)
        processor_connections_by_name = self._validate_and_parse_processor_connections(
            processor_connections_input, processor_configs_by_name
        )
        self._create_all_processors(
            processor_connections_by_name, processor_configs_by_name, intercept_mean_temp, phase_shift, amplitude
        )
        self._populate_adjacency_matrix(processor_connections_by_name)

        self._validate_adjacency_matrix()
        self._processing_order = self._traverse_adjacency_matrix()  # noqa

    def run_daily_update(
        self, manure_streams: dict[str, ManureStream], time: RufasTime, current_day_conditions: CurrentDayConditions
    ) -> None:
        """
        Executes the daily update for all processors in the defined processing order.

        Parameters
        ----------
        manure_streams : dict[str, ManureStream]
            A dictionary of all the daily manure streams from the animal module.
        time : RufasTime
            The current time in the simulation.
        current_day_conditions : CurrentDayConditions
            The current day conditions.

        Raises
        ------
        ValueError
            If a first-processor name is not found in the list of all processors.
        """
        for stream in manure_streams.values():
            assert stream.pen_manure_data is not None
            first_processor_name = stream.pen_manure_data.first_processor
            try:
                assert first_processor_name is not None
                first_processor = self.all_processors[first_processor_name]
            except KeyError:
                self._om.add_error(
                    "Unknown First-Processor Name",
                    f"Processor '{first_processor_name}' not found in the system. "
                    f"Here are currently defined processors: {self.all_processors.keys()}",
                    {"class": self.__class__.__name__, "function": self.run_daily_update.__name__},
                )
                raise KeyError(f"Processor '{first_processor_name}' not found in the system.")
            first_processor.receive_manure(stream)

        for processor_name in self._processing_order:
            processor = self.all_processors[processor_name]
            processed_streams = processor.process_manure(current_day_conditions, time)

            for manure_classification, stream in processed_streams.items():
                origin_key = self._generate_origin_key(processor_name, manure_classification)
                destinations = self._adjacency_matrix.get(origin_key, {})

                for destination_name, proportion in destinations.items():
                    if proportion > 0.0:
                        destination_name = self._normalize_destination_name(destination_name)
                        destination_processor = self.all_processors[destination_name]
                        if math.isclose(proportion, 1.0):
                            destination_processor.receive_manure(stream)
                        else:
                            split_stream = stream.split_stream(proportion)
                            destination_processor.receive_manure(split_stream)

        self._manure_nutrient_manager.reset_nutrient_pools()
        self._build_nutrient_pools()

    def _build_nutrient_pools(self) -> None:
        """
        Build the pool for aggregated storage type.
        """
        for name, processor in self.all_processors.items():
            if isinstance(processor, Storage):
                manure_type = STORAGE_CLASS_TO_TYPE.get(type(processor))
                nutrients = ManureNutrients(
                    manure_type=manure_type,
                    nitrogen=processor.stored_manure.nitrogen,
                    phosphorus=processor.stored_manure.phosphorus,
                    potassium=processor.stored_manure.potassium,
                    total_manure_mass=processor.stored_manure.mass,
                    dry_matter=processor.stored_manure.total_solids,
                )

                self._manure_nutrient_manager.add_nutrients(nutrients)

    def _normalize_destination_name(self, destination_name: str) -> str:
        """
        Normalizes the destination name by removing suffixes for solid and liquid outputs.

        Parameters
        ----------
        destination_name : str
            The non-normalized name of the destination processor.

        Returns
        -------
        str
            The normalized name of the destination processor.
        """
        if destination_name.endswith("_input"):
            base_name = destination_name[:-6]
            if base_name in self._all_separators:
                destination_name = base_name
        return destination_name

    def _generate_origin_key(self, processor_name: str, output_key: str) -> str:
        """
        Generates the origin key for the adjacency matrix based on the processor name and output key.

        Parameters
        ----------
        processor_name : str
            The name of the processor.
        output_key : str
            The output key, which can be "manure", "solid", or "liquid".

        Returns
        -------
        str
            The generated origin key for the adjacency matrix.

        Raises
        ------
        ValueError
            If the output key is not recognized or if it does not match the expected format.
        """
        if output_key == "manure":
            origin_key = processor_name
        elif output_key in {"solid", "liquid"}:
            origin_key = f"{processor_name}_{output_key}_output"
        else:
            self._om.add_error(
                "Invalid Output Key",
                f"Unexpected output key '{output_key}' from processor '{processor_name}'.",
                {"class": self.__class__.__name__, "function": "run_daily_update"},
            )
            raise ValueError(f"Unexpected output key '{output_key}' from processor '{processor_name}'.")
        return origin_key

    def _validate_adjacency_matrix(self) -> None:
        """
        Validates the structure and content of the generated adjacency matrix.

        This method enforces two key invariants for the manure processor graph:

        1. Self-loops are not allowed — a processor cannot send output to itself. This is validated by ensuring that the
           diagonal entry (i.e., origin -> origin) in each adjacency matrix column is zero.

        2. Outgoing proportions must be normalized — for each origin processor, the total sum of outgoing connection
           proportions (i.e., the values across that column) must be either 0 (no connections) or 1 (fully distributed
           output).

        These checks ensure the integrity of the processor network: no unintended feedback loops exist, and all flow
        proportions are either well-defined or explicitly zeroed.

        Raises
        ------
        ValueError
            If a self-loop is found or if an origin has outgoing proportions that do not sum to 0 or 1.
        """
        for origin, destinations in self._adjacency_matrix.items():
            if destinations[origin] != 0:
                raise ValueError(f"The diagonal for origin {origin} is not 0.")
            column_sum = sum(destinations.values())
            if not math.isclose(column_sum, 0, abs_tol=1e-8) and not math.isclose(column_sum, 1, abs_tol=1e-8):
                raise ValueError(f"Sum for {origin} column must be 0 or 1, but got {column_sum}")

    def _traverse_adjacency_matrix(self) -> list[str]:
        """
        Determines a valid processing order of manure processors via topological sorting.

        This method merges separator-related rows in the adjacency matrix, computes in-degrees for all processors,
        and performs a topological sort to ensure upstream processors are handled before downstream ones.

        Returns
        -------
        list[str]
            A list of processor names in the order they should be processed.

        Raises
        ------
        ValueError
            If a cycle exists in the processor graph, making topological sort impossible.
        """
        matrix_to_traverse = self._merge_separator_rows()

        all_nodes = set(matrix_to_traverse.keys())

        in_degree = {node: 0 for node in all_nodes}

        for destinations in matrix_to_traverse.values():
            for dest, weight in destinations.items():
                if weight != 0.0:
                    in_degree[dest] += 1

        start_nodes: list[str] = [node for node in all_nodes if in_degree[node] == 0]

        sorted_order = self._perform_topological_sort(in_degree, start_nodes, matrix_to_traverse)

        if len(sorted_order) != len(all_nodes):
            raise ValueError("Cycle detected — topological sort not possible.")

        return sorted_order

    def _merge_separator_rows(self) -> dict[str, dict[str, float]]:
        """
        Creates a version of the adjacency matrix with merged separator rows for graph traversal.

        Each separator is originally represented by three separate rows:
        - {separator}_input
        - {separator}_solid_output
        - {separator}_liquid_output

        This function merges them into a single row keyed by the base separator name (e.g., 'separator1').
        It also removes internal separator suffixes from destination references to simplify traversal.

        Returns
        -------
        dict[str, dict[str, float]]
            A modified adjacency matrix where separator rows are merged and internal suffixes removed.
        Raises
        ------
        ValueError
            If a destination receives output from both solid and liquid separator streams.

        """
        matrix_to_return = deepcopy(self._adjacency_matrix)
        for separator_name in self._all_separators.keys():
            combined_row = {}
            input_row = matrix_to_return.pop(f"{separator_name}_input", {})
            solid_row = matrix_to_return.pop(f"{separator_name}_solid_output", {})
            liquid_row = matrix_to_return.pop(f"{separator_name}_liquid_output", {})

            all_destinations = set(input_row.keys()) | set(solid_row.keys()) | set(liquid_row.keys())

            for destination in all_destinations:
                solid_value = solid_row.get(destination, 0.0)
                liquid_value = liquid_row.get(destination, 0.0)

                if solid_value > 0.0 and liquid_value > 0.0:
                    raise ValueError(
                        f"Invalid output split in '{separator_name}': destination '{destination}' "
                        f"receives from both solid and liquid outputs (solid={solid_value}, liquid={liquid_value})"
                    )
                combined_row[destination] = (
                    input_row.get(destination, 0.0) + solid_row.get(destination, 0.0) + liquid_row.get(destination, 0.0)
                )

            matrix_to_return[separator_name] = combined_row

        for column, row in matrix_to_return.items():
            for key in list(row.keys()):
                if key.endswith("_solid_output") or key.endswith("_liquid_output"):
                    del row[key]
                elif key.endswith("_input"):
                    new_key = key[:-6]
                    row[new_key] = row.pop(key)
        return matrix_to_return

    @staticmethod
    def _perform_topological_sort(
        in_degree: dict[str, int], heap: list[str], matrix_to_traverse: dict[str, dict[str, float]]
    ) -> list[str]:
        """
        Performs topological sorting of the processors using Kahn's algorithm.

        This method processes nodes in order of zero in-degree, removing each from the graph and
        reducing the in-degree of its downstream neighbors. When a neighbor's in-degree becomes zero,
        it is added to the processing queue.

        Parameters
        ----------
        in_degree : dict[str, int]
            Mapping of each processor to the number of upstream dependencies it has.
        heap : list[str]
            Initial list of processors with in-degree zero (i.e., ready to be processed).
        matrix_to_traverse : dict[str, dict[str, float]]
            The adjacency matrix representing directed connections between processors.
            Edges with weight 0.0 are ignored.

        Returns
        -------
        list[str]
            A list of processor names in a valid topological order.

        """
        sorted_order = []
        while heap:
            node = heap.pop(0)
            sorted_order.append(node)
            for dest, weight in matrix_to_traverse[node].items():
                if weight != 0.0:
                    in_degree[dest] -= 1
                    if in_degree[dest] == 0:
                        heap.append(dest)
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
        intercept_mean_temp: float,
        phase_shift: float,
        amplitude: float,
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
        intercept_mean_temp : float
            The intercept mean temperature calculate from linest function.
        phase_shift : float
            Temperature phase shift of the weather data.
        amplitude : float
            The temperature amplitude of the weather data.
        """
        for processor_name in processor_connections_by_name:
            processor_config = processor_configs_by_name[processor_name]
            processor_type = processor_config["processor_type"]

            processor_initializer = ProcessorType.get_processor_class(processor_type)
            if not (issubclass(processor_initializer, Handler) or issubclass(processor_initializer, Separator)):
                del processor_config["processor_type"]
            processor = processor_initializer(**processor_config)
            if isinstance(processor, (AnaerobicLagoon, SlurryStorageOutdoor)):
                processor.intercept_mean_temp = intercept_mean_temp
                processor.phase_shift = phase_shift
                processor.amplitude = amplitude
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

    def request_nutrients(
        self, request: NutrientRequest, simulate_animals: bool, time: RufasTime
    ) -> NutrientRequestResults:
        """
        Handle the request for specific nutrients from the crop and soil module.
        This method evaluates the nutrient request made by considering both nitrogen and phosphorus
        quantities desired. It calculates the projected manure mass that would satisfy the request
        and checks against the nutrients available in the manager.

        If the request can be fulfilled either partially or wholly, the corresponding amount of nutrients
        is subtracted from the manager's internal bookkeeping. The method then returns the results of
        the nutrient request, which detail the amounts of nutrients that can be provided to fulfill the request.
        If the request cannot be fulfilled at all, the method will return None.

        Notes
        -----
        This is a wrapper method that calls the request_nutrients method of the manure nutrient manager.

        Parameters
        ----------
        request : NutrientRequest
            The specific nutrient request, including quantities of nitrogen and phosphorus.
        simulate_animals : bool
            Indicates whether animals are being simulated.
        time : RufasTime
            The current time in the simulation.

        Returns
        -------
        NutrientRequestResults | None
            The results of the nutrient request, detailed in a `NutrientRequestResults` object, which includes
            the amount of nitrogen, phosphorus, total manure mass, dry matter, and others that
            can be provided to fulfill the request.
            Returns None if the request cannot be fulfilled.

        """
        if simulate_animals:
            request_result, is_nutrient_request_fulfilled = self._manure_nutrient_manager.handle_nutrient_request(
                request
            )
            self._record_manure_request_results(request_result, "on_farm_manure", time)
            if request_result is not None:
                self._remove_nutrients_from_storage(request_result, request.manure_type)

            if not is_nutrient_request_fulfilled and request.use_supplemental_manure:
                self._om.add_log(
                    "Supplemental manure needed",
                    "Attempting to fulfill manure nutrient request shortfall with supplemental manure.",
                    {"class": self.__class__.__name__, "function": self.request_nutrients.__name__},
                )
                amount_supplemental_manure_needed = self._calculate_supplemental_manure_needed(request_result, request)
                supplemental_manure = FieldManureSupplier.request_nutrients(amount_supplemental_manure_needed)
                self._record_manure_request_results(supplemental_manure, "off_farm_manure", time)
                if request_result is None:
                    return supplemental_manure
                return request_result + supplemental_manure
            return request_result
        else:
            return FieldManureSupplier.request_nutrients(request)

    def _remove_nutrients_from_storage(self, results: NutrientRequestResults, manure_type: ManureType) -> None:
        """
        Remove nutrients from the storage based on the results of a nutrient request by manure type.

        Parameters
        ----------
        results : NutrientRequestResults
            The results of a nutrient request. See :class:`NutrientsRequestResults` for details.

        """
        nutrient_pool = self._manure_nutrient_manager.nutrients_by_manure_category[manure_type]
        is_nitrogen_limiting_nutrient = self._determine_limiting_nutrient(
            results.nitrogen,
            nutrient_pool.nitrogen_composition,
            results.phosphorus,
            nutrient_pool.phosphorus_composition,
        )

        if is_nitrogen_limiting_nutrient:
            limiting_nutrient_requested_amount = results.nitrogen
            available_amount_in_pool = nutrient_pool.nitrogen
        else:
            limiting_nutrient_requested_amount = results.phosphorus
            available_amount_in_pool = nutrient_pool.phosphorus

        proportion_of_limiting_nutrient_to_remove = self._determine_nutrient_proportion_to_be_removed(
            limiting_nutrient_requested_amount, available_amount_in_pool
        )
        non_limiting_fields = [
            "water",
            "ammoniacal_nitrogen",
            "potassium",
            "ash",
            "non_degradable_volatile_solids",
            "degradable_volatile_solids",
            "total_solids",
            "bedding_non_degradable_volatile_solids",
        ]

        for name, processor in self.all_processors.items():
            if isinstance(processor, Storage):
                processor.stored_manure, removal_details = self._compute_stream_after_removal(
                    stored_manure=processor.stored_manure,
                    nutrient_removal_proportion=proportion_of_limiting_nutrient_to_remove,
                    is_nitrogen_limiting_nutrient=is_nitrogen_limiting_nutrient,
                    non_limiting_fields=non_limiting_fields.copy(),
                )
                removal_details["manure_type"] = STORAGE_CLASS_TO_TYPE.get(type(processor))
                self._manure_nutrient_manager.remove_nutrients(removal_details)

    @staticmethod
    def _compute_stream_after_removal(
        stored_manure: ManureStream,
        nutrient_removal_proportion: float,
        is_nitrogen_limiting_nutrient: bool,
        non_limiting_fields: list[str],
    ) -> tuple[ManureStream, dict[str, Any]]:
        """
        Returns a new ManureStream with removals applied,
        plus a dict of how much was removed for each attribute.

        Parameters
        ----------
        stored_manure : ManureStream
            The stored manure in storage.
        nutrient_removal_proportion : float
            The proportion of nutrient to remove (unitless).
        is_nitrogen_limiting_nutrient : bool
            Determine if nitrogen is limiting nutrient.
        non_limiting_fields : list[str]
            A list containing the attribute names of nutrient fields to handle.

        Returns
        -------
        tuple[Manure Stream, dict[str, Any]]
            The stream after removal.
            The detail of the amount of nutrients removed.

        """
        if is_nitrogen_limiting_nutrient:
            limiting = "nitrogen"
            non_limiting_fields.append("phosphorus")
        else:
            limiting = "phosphorus"
            non_limiting_fields.append("nitrogen")

        removed: dict[str, Any] = {}

        original_limiting_nutrients_in_storage = getattr(stored_manure, limiting)
        if math.isclose(nutrient_removal_proportion, 1.0, abs_tol=1e-5):
            limiting_nutrients_to_remove = original_limiting_nutrients_in_storage
        else:
            limiting_nutrients_to_remove = original_limiting_nutrients_in_storage * nutrient_removal_proportion
        removed[limiting] = limiting_nutrients_to_remove

        updates: dict[str, float] = {limiting: original_limiting_nutrients_in_storage - limiting_nutrients_to_remove}

        for field in non_limiting_fields:
            original_amount = getattr(stored_manure, field)
            removal_amount = ManureManager._determine_non_limiting_nutrient_removal_amount(
                nutrient_removal_proportion, original_amount
            )
            removed[field] = removal_amount
            updates[field] = round(original_amount - removal_amount, 5)

        new_stream = replace(stored_manure, **updates)
        return new_stream, removed

    @staticmethod
    def _determine_non_limiting_nutrient_removal_amount(
        limiting_nutrient_proportion_to_be_removed: float,
        non_limiting_nutrients_amount: float,
    ) -> float:
        """
        Calculates the amount of non-limiting nutrients to remove in each storage.

        Parameters
        ----------
        limiting_nutrient_proportion_to_be_removed : float
            The proportion of limiting nutrient to remove from each storage.
        non_limiting_nutrients_amount : float
            The amount of non-limiting nutrient in the storage (kg).

        Returns
        -------
        float
            The amount of non-limiting nutrients to remove in each storage (kg).

        """
        return round(limiting_nutrient_proportion_to_be_removed * non_limiting_nutrients_amount, 5)

    @staticmethod
    def _determine_limiting_nutrient(
        requested_nitrogen_mass: float,
        nitrogen_fraction: float,
        requested_phosphorus_mass: float,
        phosphorus_fraction: float,
    ) -> bool:
        """
        Determines the limiting nutrient to remove.

        Parameters
        ----------
        requested_nitrogen_mass : float
            The mass of nitrogen requested (kg).
        nitrogen_fraction : float
            The fraction of nitrogen in the combined pool (unitless).
        requested_phosphorus_mass : float
            The mass of phosphorus requested (kg).
        phosphorus_fraction : float
            The fraction of phosphorus in the combined pool (unitless).

        Returns
        -------
        bool
            If true, nitrogen is the limiting nutrients.
            If false, phosphorus is the limiting nutrients.

        """
        nitrogen_maure_mass = ManureNutrientManager.calculate_projected_manure_mass(
            requested_nitrogen_mass, nitrogen_fraction
        )
        phosphorus_manure_mass = ManureNutrientManager.calculate_projected_manure_mass(
            requested_phosphorus_mass, phosphorus_fraction
        )
        if nitrogen_maure_mass < phosphorus_manure_mass:
            return True
        else:
            return False

    @staticmethod
    def _determine_nutrient_proportion_to_be_removed(
        limiting_nutrient_requested_mass: float, limited_nutrient_available: float
    ) -> float:
        """
        Calculates the proportion of limiting nutrients to remove.

        Parameters
        ----------
        limiting_nutrient_requested_mass : float
            The requested mass of limited nutrient (kg).
        limited_nutrient_available : float
            The amount of limited nutrient available in the total pool(kg).

        Returns
        -------
        float
            The proportion of limiting nutrient to remove from each storage.

        """
        if math.isclose(limited_nutrient_available, 0.0, abs_tol=1e-5):
            return 0.0
        else:
            return min(limiting_nutrient_requested_mass / limited_nutrient_available, 1)

    def _record_manure_request_results(
        self, manure_request_results: NutrientRequestResults | None, manure_source: str, time: RufasTime
    ) -> None:
        """
        Record the results of a manure request in the Output Manager.

        Parameters
        ----------
        manure_request_results : NutrientRequestResults | None
            The results of a manure request. If None, it means that there was no available on-farm manure.
        manure_source : str
            The source of the manure.
        time : RufasTime
            The current time in the simulation.

        """
        info_maps = {
            "class": ManureManager.__name__,
            "function": ManureManager._record_manure_request_results.__name__,
            "units": {
                "dry_matter_mass": MeasurementUnits.DRY_KILOGRAMS,
                "dry_matter_fraction": MeasurementUnits.FRACTION,
                "total_manure_mass": MeasurementUnits.KILOGRAMS,
                "organic_nitrogen_fraction": MeasurementUnits.FRACTION,
                "inorganic_nitrogen_fraction": MeasurementUnits.FRACTION,
                "ammonium_nitrogen_fraction": MeasurementUnits.FRACTION,
                "organic_phosphorus_fraction": MeasurementUnits.FRACTION,
                "inorganic_phosphorus_fraction": MeasurementUnits.FRACTION,
                "nitrogen": MeasurementUnits.KILOGRAMS,
                "phosphorus": MeasurementUnits.KILOGRAMS,
                "request_julian_day": MeasurementUnits.ORDINAL_DAY,
                "request_calendar_year": MeasurementUnits.CALENDAR_YEAR,
            },
        }
        if not manure_request_results:
            request_result_values = {
                "dry_matter_mass": 0.0,
                "dry_matter_fraction": 0.0,
                "total_manure_mass": 0.0,
                "organic_nitrogen_fraction": 0.0,
                "inorganic_nitrogen_fraction": 0.0,
                "ammonium_nitrogen_fraction": 0.0,
                "organic_phosphorus_fraction": 0.0,
                "inorganic_phosphorus_fraction": 0.0,
                "nitrogen": 0.0,
                "phosphorus": 0.0,
                "request_julian_day": time.current_julian_day,
                "request_calendar_year": time.current_calendar_year,
            }
            self._om.add_log(
                "Recording empty manure request result", "No manure available on farm to fulfill request.", info_maps
            )
        else:
            request_result_values = {
                "dry_matter_mass": manure_request_results.dry_matter,
                "dry_matter_fraction": manure_request_results.dry_matter_fraction,
                "total_manure_mass": manure_request_results.total_manure_mass,
                "organic_nitrogen_fraction": manure_request_results.organic_nitrogen_fraction,
                "inorganic_nitrogen_fraction": manure_request_results.inorganic_nitrogen_fraction,
                "ammonium_nitrogen_fraction": manure_request_results.ammonium_nitrogen_fraction,
                "organic_phosphorus_fraction": manure_request_results.organic_phosphorus_fraction,
                "inorganic_phosphorus_fraction": manure_request_results.inorganic_phosphorus_fraction,
                "nitrogen": manure_request_results.nitrogen,
                "phosphorus": manure_request_results.phosphorus,
                "request_julian_day": time.current_julian_day,
                "request_calendar_year": time.current_calendar_year,
            }
        self._om.add_variable(manure_source, request_result_values, info_maps)

    @staticmethod
    def _calculate_supplemental_manure_needed(
        on_farm_manure: NutrientRequestResults | None, nutrient_request: NutrientRequest
    ) -> NutrientRequest:
        """
        Calculate the amount of supplemental manure needed to fulfill the nutrient request.

        Parameters
        ----------
        on_farm_manure : NutrientRequestResults | None
            The results of the nutrient request for manure available from the farm. If None, it means that
            there was no available on-farm manure.
        nutrient_request : NutrientRequest
            The nutrient request.

        Returns
        -------
        NutrientRequest
            The request for supplemental manure needed to fulfill the original nutrient request.
        """
        remaining_nitrogen = max(0, nutrient_request.nitrogen - (on_farm_manure.nitrogen if on_farm_manure else 0))
        remaining_phosphorus = max(
            0, nutrient_request.phosphorus - (on_farm_manure.phosphorus if on_farm_manure else 0)
        )

        if math.isclose(remaining_nitrogen, 0.0, abs_tol=1e-5) and math.isclose(
            remaining_phosphorus, 0.0, abs_tol=1e-5
        ):
            return NutrientRequest(
                nitrogen=0.0,
                phosphorus=0.0,
                manure_type=nutrient_request.manure_type,
                use_supplemental_manure=True,
            )

        return NutrientRequest(
            nitrogen=remaining_nitrogen,
            phosphorus=remaining_phosphorus,
            manure_type=nutrient_request.manure_type,
            use_supplemental_manure=True,
        )
