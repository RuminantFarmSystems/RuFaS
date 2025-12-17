import json
import os
from copy import deepcopy
from functools import reduce
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd
from deepdiff import DeepDiff

from RUFAS.data_validator import DataValidator, ElementsCounter, Modifiability, CrossValidator
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility

"""
Set enumerating the input data types that the Input Manager will attempt to fix while validating input data.
"""
FIXABLE_INPUT_DATA_TYPES: set[str] = {"string", "number", "bool"}

"""
Set enumerating the input data formats the Input Manager can accept.
"""
VALID_INPUT_TYPES: set[str] = {"json", "csv"}

ADDRESS_TO_INPUTS = "files"

VARIABLE_PROPERTIES_TO_IGNORE = ["type", "description", "modifiability", "data_collection_app_compatible"]


class InputManager:
    """
    Input Manager class responsible for loading, validating, and providing access to input data.
    """

    __instance = None

    def __new__(cls, metadata_depth_limit: int | None = None) -> "InputManager":
        if not hasattr(cls, "instance"):
            cls.instance = super(InputManager, cls).__new__(cls)
        return cls.instance

    def __init__(self, metadata_depth_limit: int | None = None) -> None:
        self.om = OutputManager()
        if InputManager.__instance is None:
            InputManager.__instance = self
            self.__metadata: dict[str, Any] = {}
            self.__pool: dict[str, Any] = {}
            self.__get_data_logs_pool: dict[str, str] = {}
            self.__delete_data_logs_pool: dict[str, str] = {}
            self.elements_counter = ElementsCounter()
            self.csv_report_generation_list: list[str] = []
            self.data_validator = DataValidator()
            self.cross_validator = CrossValidator()
        self.metadata_depth_limit = 7 if metadata_depth_limit is None else metadata_depth_limit

    @property
    def meta_data(self) -> Dict[str, Any]:
        """The getter method for __metadata"""
        return self.__metadata

    @meta_data.setter
    def meta_data(self, incoming_metadata: Dict[str, Any]) -> None:
        """The setter method for __metadata"""
        self.__metadata = incoming_metadata

    @property
    def pool(self) -> Dict[str, Any]:
        """The getter method for __pool"""
        return self.__pool

    @pool.setter
    def pool(self, incoming_pool: Dict[str, Any]) -> None:
        """The setter method for __pool"""
        self.__pool = incoming_pool

    def start_data_processing(self, metadata_path: Path, input_root: Path, eager_termination: bool = True) -> bool:
        """
        Starts the pipeline for organizing metadata and input data processing.

        Parameters
        ----------
        metadata_path : Path
            File path to the metadata.
        input_root : Path
            Root directory for all input files.
        eager_termination : bool, default=True
            If True, the process will be terminated as soon as finding invalid data and failing to fix it.
            If False, the process will be terminated after going through and validating the entire data.

        Returns
        -------
        bool
            True if data is valid, otherwise False.
        """
        full_metadata_path = Path(input_root) / metadata_path
        self._load_metadata(full_metadata_path)
        valid, message = self.data_validator.validate_metadata(
            self.__metadata, VALID_INPUT_TYPES, ADDRESS_TO_INPUTS, input_root
        )
        if not valid:
            raise ValueError(message)
        self._load_properties()
        valid, message = self.data_validator.validate_properties(self.__metadata, self.metadata_depth_limit)
        if not valid:
            self.om.route_logs(self.data_validator.event_logs)
            raise ValueError(message)
        is_input_data_valid = self._populate_pool(input_root, eager_termination)
        failing_cross_validation_blocks: list[str] = []
        cross_validation_blocks = self.__metadata.get("cross-validation", [])
        if cross_validation_blocks:
            for block in cross_validation_blocks:
                target_and_save_block = block.get("target_and_save", {})
                target_and_save_result = self._extract_target_and_save_block(target_and_save_block, eager_termination)
                is_cross_validation_successful = self.cross_validator.cross_validate_data(
                    target_and_save_result,
                    block,
                    eager_termination,
                )
                if not is_cross_validation_successful:
                    failing_cross_validation_blocks.append(block.get("description", "unnamed block"))
                    if eager_termination:
                        break
        if len(failing_cross_validation_blocks) > 0:
            self.om.add_error(
                "Cross Validation Failure",
                "One or more cross-validation rules failed: " f"{', '.join(failing_cross_validation_blocks)}",
                {
                    "class": self.__class__.__name__,
                    "function": self.start_data_processing.__name__,
                },
            )
            is_input_data_valid = False
        self.om.route_logs(self.data_validator.event_logs)
        return is_input_data_valid

    def load_runtime_metadata(self, metadata_key: str, eager_termination: bool) -> bool:
        """Load and validate a runtime metadata document before ingesting the referenced data.

        Parameters
        ----------
        metadata_key : str
            Identifier declared in the primary metadata document's ``runtime_metadata`` section.
        eager_termination : bool
            Flag forwarded to :py:meth:`add_runtime_variable_to_pool` determining whether validation
            failures should prevent additional fixes before continuing execution.

        Returns
        -------
        bool
            ``True`` when all referenced datasets are validated and added to the pool, otherwise
            ``False`` when any failure is encountered.
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self.load_runtime_metadata.__name__,
        }

        if not self._is_metadata_loaded(info_map):
            return self._runtime_metadata_guard_failure(
                "Active metadata must be loaded before runtime metadata can be processed.",
                info_map,
            )

        runtime_metadata_map = self._get_runtime_metadata_map(info_map)
        if runtime_metadata_map is None:
            return self._runtime_metadata_guard_failure(
                "Runtime metadata configuration could not be resolved from the active metadata document.",
                info_map,
            )

        runtime_files = self._resolve_runtime_metadata_files(runtime_metadata_map, metadata_key, info_map)
        if runtime_files is None:
            return False

        data_type_to_loader_map = self._runtime_data_loader_map()

        results: list[bool] = []
        for variable_name, file_details in runtime_files.items():
            result = self._process_runtime_file(
                variable_name,
                file_details,
                data_type_to_loader_map,
                eager_termination,
                info_map,
            )
            results.append(result)
            if eager_termination and not result:
                break

        self.om.route_logs(self.data_validator.event_logs)
        if results == []:
            self.om.add_warning(
                "No runtime metadata files processed",
                f"No runtime metadata files were processed for key '{metadata_key}'. "
                "Check if the configuration is correct or if this key is expected to have no runtime files.",
                info_map,
            )

        return all(results) if results else True

    def _runtime_metadata_guard_failure(self, reason: str, info_map: Dict[str, Any]) -> bool:
        self.om.add_error("Runtime metadata load failure", reason, info_map)
        return False

    def _resolve_runtime_metadata_files(
        self, runtime_metadata_map: Dict[str, Any], metadata_key: str, info_map: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        metadata_reference = self._get_runtime_metadata_reference(runtime_metadata_map, metadata_key, info_map)
        if metadata_reference is None:
            self._runtime_metadata_guard_failure(
                f"Runtime metadata entry '{metadata_key}' is unavailable for loading.",
                info_map,
            )
            return None

        metadata_path = self._get_runtime_metadata_path(metadata_reference, metadata_key, info_map)
        if metadata_path is None:
            self._runtime_metadata_guard_failure(
                f"Runtime metadata entry '{metadata_key}' does not define a loadable path.",
                info_map,
            )
            return None

        runtime_metadata = self._load_runtime_metadata_contents(metadata_path, info_map)
        if runtime_metadata is None:
            self._runtime_metadata_guard_failure(
                f"Runtime metadata document at '{metadata_path}' could not be loaded.",
                info_map,
            )
            return None

        if not self._validate_runtime_metadata(runtime_metadata, info_map):
            self._runtime_metadata_guard_failure(
                f"Runtime metadata document at '{metadata_path}' failed validation.",
                info_map,
            )
            return None

        runtime_files = self._extract_runtime_files(runtime_metadata, metadata_path, info_map)
        if runtime_files is None:
            self._runtime_metadata_guard_failure(
                f"Runtime metadata document at '{metadata_path}' is missing a valid '{ADDRESS_TO_INPUTS}' section.",
                info_map,
            )
            return None

        return runtime_files

    def _is_metadata_loaded(self, info_map: Dict[str, Any]) -> bool:
        if self.__metadata:
            return True
        self.om.add_error(
            "Runtime metadata load failure",
            "No metadata is currently loaded into the InputManager.",
            info_map,
        )
        return False

    def _get_runtime_metadata_map(self, info_map: Dict[str, Any]) -> Dict[str, Any] | None:
        try:
            return self.get_metadata("runtime_metadata")
        except KeyError:
            self.om.add_error(
                "Runtime metadata not configured",
                "No runtime metadata configuration found in the active metadata document.",
                info_map,
            )
            return None

    def _get_runtime_metadata_reference(
        self, runtime_metadata_map: Dict[str, Any], metadata_key: str, info_map: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        metadata_reference = runtime_metadata_map.get(metadata_key)
        if metadata_reference is None:
            self.om.add_error(
                "Runtime metadata key missing",
                f"Runtime metadata key '{metadata_key}' not found in configuration.",
                info_map,
            )
            return None
        return metadata_reference

    def _get_runtime_metadata_path(
        self, metadata_reference: Dict[str, Any], metadata_key: str, info_map: Dict[str, Any]
    ) -> Path | None:
        metadata_path_value = metadata_reference.get("path")
        if metadata_path_value is None:
            self.om.add_error(
                "Runtime metadata path missing",
                f"Runtime metadata entry '{metadata_key}' is missing a path attribute.",
                info_map,
            )
            return None
        return Path(metadata_path_value)

    def _load_runtime_metadata_contents(self, metadata_path: Path, info_map: Dict[str, Any]) -> Dict[str, Any] | None:
        try:
            return self._load_runtime_metadata_document(metadata_path)
        except Exception as exc:
            self.om.add_error(
                "Runtime metadata load failure",
                f"Failed to load runtime metadata from {metadata_path}: {exc}",
                info_map,
            )
            return None

    def _validate_runtime_metadata(self, runtime_metadata: Dict[str, Any], info_map: Dict[str, Any]) -> bool:
        is_valid, message = self.data_validator.validate_metadata(
            runtime_metadata, VALID_INPUT_TYPES, ADDRESS_TO_INPUTS, self.input_root
        )
        if is_valid:
            return True
        self.om.add_error("Runtime metadata validation failed", message, info_map)
        self.om.route_logs(self.data_validator.event_logs)
        return False

    def _extract_runtime_files(
        self, runtime_metadata: Dict[str, Any], metadata_path: Path, info_map: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        runtime_files = runtime_metadata.get(ADDRESS_TO_INPUTS, {})
        if isinstance(runtime_files, dict):
            return runtime_files
        self.om.add_error(
            "Runtime metadata files invalid",
            f"Runtime metadata document {metadata_path} does not contain a valid '{ADDRESS_TO_INPUTS}' section.",
            info_map,
        )
        self.om.route_logs(self.data_validator.event_logs)
        return None

    def _runtime_data_loader_map(self) -> Dict[str, Callable[[Path], Dict[str, Any]]]:
        return {
            "json": self._load_data_from_json,
            "csv": self._load_data_from_csv,
        }

    def _process_runtime_file(
        self,
        variable_name: str,
        file_details: Dict[str, Any],
        data_type_to_loader_map: Dict[str, Callable[[Path], Dict[str, Any]]],
        eager_termination: bool,
        info_map: Dict[str, Any],
    ) -> bool:
        properties_blob_key = file_details.get("properties")
        if not properties_blob_key:
            self.om.add_error(
                "Runtime metadata properties missing",
                f"Runtime metadata for '{variable_name}' is missing a properties reference.",
                info_map,
            )
            return False

        try:
            self._metadata_properties_exist(variable_name, properties_blob_key)
        except (ValueError, KeyError):
            return False

        data_type = file_details.get("type")
        data_loader = data_type_to_loader_map.get(data_type)
        if data_loader is None:
            supported_types = ", ".join(sorted(data_type_to_loader_map.keys()))
            self.om.add_error(
                "Unsupported runtime metadata type",
                f"Faulty data type in {variable_name}, supported types are: {supported_types}",
                info_map,
            )
            return False

        file_path_value = file_details.get("path")
        if not file_path_value:
            self.om.add_error(
                "Runtime metadata path missing",
                f"Runtime metadata for '{variable_name}' is missing a path attribute.",
                info_map,
            )
            return False
        try:
            input_data = data_loader(Path(file_path_value))
        except Exception as exc:
            self.om.add_error(
                "Runtime metadata load failure",
                f"Failed to load data for '{variable_name}' from {file_details.get('path')}: {exc}",
                info_map,
            )
            return False

        try:
            is_runtime_data_added = self.add_runtime_variable_to_pool(
                variable_name=variable_name,
                data=input_data,
                properties_blob_key=properties_blob_key,
                eager_termination=eager_termination,
            )
        except (TypeError, ValueError, PermissionError) as exc:
            self.om.add_error(
                "Runtime metadata variable addition failed",
                f"Failed to add runtime metadata variable '{variable_name}' to pool: {exc}",
                info_map,
            )
            return False

        return is_runtime_data_added

    def _load_runtime_metadata_document(self, metadata_path: Path) -> Dict[str, Any]:
        """Load a runtime metadata document without disturbing the active metadata state.

        Parameters
        ----------
        metadata_path : Path
            Location of the metadata document that should be loaded for runtime processing.

        Returns
        -------
        Dict[str, Any]
            Parsed metadata content from ``metadata_path``.

        Notes
        -----
        The active metadata is restored after loading so callers retain their previously parsed
        metadata tree.
        """

        original_metadata = deepcopy(self.__metadata)
        try:
            self._load_metadata(metadata_path)
            runtime_metadata = deepcopy(self.__metadata)
        finally:
            self.__metadata = original_metadata

        return runtime_metadata

    def _load_metadata(self, metadata_path: Path) -> None:
        """
        Loads metadata from json file to IM metadata dict.

        Parameters
        ----------
        metadata_path : Path
            The path to the metadata file.

        Raises
        ------
        Exception
            If an error occurs while opening or reading the metadata_path file.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._load_metadata.__name__,
        }
        self.om.add_log(
            "load_metadata_attempt",
            f"Attempting to load metadata from {metadata_path}.",
            info_map,
        )
        try:
            with open(metadata_path) as metadata_file:
                self.__metadata = json.load(metadata_file)
                self.om.add_log(
                    "load_metadata_success",
                    f"Successfully loaded metadata from {metadata_path}",
                    info_map,
                )
        except Exception as e:
            raise e

    def _load_properties(self) -> None:
        """
        Loads properties data from a specified JSON file and updates the metadata.

        This method reads the properties file path from the metadata, checks if the file exists, and then loads the
        properties into the metadata. The original properties data in the metadata is first copied to a separate
        attribute for future reference and then removed from the metadata files section.

        Raises
        ------
        FileNotFoundError
            If the properties file does not exist at the specified path.
        json.JSONDecodeError
            If there is an error in decoding the JSON file.
        Exception
            For any other unexpected errors during properties loading.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._load_properties.__name__,
        }
        try:
            properties_metadata = self.__metadata["files"]["properties"]
            properties_paths = properties_metadata.get("paths") or properties_metadata.get("path")

            if isinstance(properties_paths, str):
                properties_paths = [properties_paths]
            if not isinstance(properties_paths, list) or len(properties_paths) == 0:
                raise ValueError("Properties paths must be a non-empty string or list of strings")

            if not all(isinstance(path, str) and path for path in properties_paths):
                raise ValueError("Each properties path must be a non-empty string")

            self.om.add_log(
                "load_properties_attempt",
                f"Attempting to load properties from {properties_paths}",
                info_map,
            )

            combined_properties: dict[str, Any] = {}
            for properties_path_str in properties_paths:
                properties_path = Path(properties_path_str)
                if not properties_path.exists():
                    raise FileNotFoundError(f"Properties file not found at {properties_path}")
                loaded_properties = self._load_data_from_json(properties_path)
                combined_properties.update(loaded_properties)

            del self.__metadata["files"]["properties"]

            self.__metadata["properties"] = combined_properties
            self.om.add_log(
                "load_properties_success",
                f"Successfully loaded properties from {properties_paths}",
                info_map,
            )

        except FileNotFoundError as fnfe:
            self.om.add_error("load_properties_file_not_found", str(fnfe), info_map)
            raise
        except json.JSONDecodeError as jde:
            self.om.add_error("load_properties_json_error", str(jde), info_map)
            raise
        except Exception as e:
            self.om.add_error("load_properties_error", f"Unexpected error: {e}", info_map)
            raise

    def _load_data_from_json(self, file_path: Path) -> Dict[str, Any]:
        """
        Loads data from input json file.

        Parameters
        ----------
        file_path : Path
            Path to the input file to load.

        Returns
        -------
        Dict[str, Any]
            The data dictionary loaded from the json file.

        Raises
        ------
        Exception
            For any other unexpected errors during JSON file loading.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._load_data_from_json.__name__,
        }
        self.om.add_log("open_json_file", f"Attempting to open {file_path}.", info_map)
        try:
            with open(file_path) as json_file:
                data: Dict[str, Any] = json.load(json_file)
                self.om.add_log(
                    "load_data_successful",
                    f"Successfully loaded data from {file_path}.",
                    info_map,
                )
                return data
        except Exception as e:
            raise e

    def _load_data_from_csv(self, file_path: Path) -> Dict[str, Any]:
        """
        Loads data from input csv file.

        Parameters
        ----------
        file_path : Path
            Path to the input file to load.

        Returns
        -------
        Dict[str, Any]
            The data dictionary loaded from the json file.

        Raises
        ------
        FileNotFoundError
            If the CSV file does not exist at the specified path.
        Exception
            For any other unexpected errors during CSV file loading.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._load_data_from_csv.__name__,
        }
        self.om.add_log("open_csv_file", f"Attempting to open {file_path}.", info_map)
        try:
            with open(file_path, "r", encoding="utf-8") as csv_file:
                data_frame = pd.read_csv(csv_file)
                data_dict = {column: data_frame[column].tolist() for column in data_frame.columns}
                if not data_frame.empty:
                    self.om.add_log(
                        "load_data_successful",
                        f"Successfully loaded data from {file_path}.",
                        info_map,
                    )
                return data_dict
        except Exception as e:
            raise e

    def _populate_pool(self, input_root: Path, eager_termination: bool) -> bool:
        """
        Loads input files, runs validations on the data from the input files, attempts to fix invalid data,
        then adds data to the pool.

        Parameters
        ----------
        input_root : Path
            The root directory for all input files.
        eager_termination : bool
            If True, the process will be terminated as soon as finding invalid data and failing to fix it.
            If False, the process will be terminated after going through and validating the entire data
            if invalid data is found.

        Returns
        -------
        bool
            True if data is valid, otherwise False.

        Raises
        ------
        KeyError
            If faulty data type found in data blob key.

        """
        self.input_root = input_root
        data_type_to_loader_map: dict[str, Callable[[Path], dict[str, Any]]] = {
            "json": self._load_data_from_json,
            "csv": self._load_data_from_csv,
        }
        valid_data = True
        for file_blob_key, file_details in self.__metadata["files"].items():
            file_path = Path(self.input_root) / file_details["path"]
            if file_details["type"] == "json":
                self.csv_report_generation_list.append(file_blob_key)

            try:
                data_loader = data_type_to_loader_map[file_details["type"]]
                input_data = data_loader(file_path)
            except KeyError:
                raise KeyError(
                    f"Faulty data type in {file_blob_key}," f"supported types are: {data_type_to_loader_map.keys()}"
                )

            properties_blob_key = file_details["properties"]
            metadata_properties = self.__metadata["properties"][properties_blob_key]

            validated_data = {}
            for metadata_property in metadata_properties.keys():
                if metadata_property == "data_collection_app_compatible":
                    continue
                variable_properties = metadata_properties[metadata_property]
                is_element_acceptable = self.data_validator.validate_data_by_type(
                    variable_path=[metadata_property],
                    variable_properties=variable_properties,
                    data=input_data,
                    eager_termination=eager_termination,
                    properties_blob_key=properties_blob_key,
                    elements_counter=self.elements_counter,
                    called_during_initialization=True,
                    fixable_data_types=FIXABLE_INPUT_DATA_TYPES,
                )

                valid_data = valid_data and is_element_acceptable

                if is_element_acceptable:
                    validated_data[metadata_property] = input_data[metadata_property]
                elif eager_termination:
                    return False

            if validated_data:
                self.__pool[file_blob_key] = validated_data

        return valid_data

    def _get_variable_modifiability(self, variable_name: str, variable_properties: Dict[str, Any]) -> Modifiability:
        """
        Determines the modifiability status of a variable based on its properties and returns the corresponding enum
        value.

        Notes
        -----
        This function looks for a 'modifiability' key within `variable_properties`. If present and its value is not
        empty, the function attempts to map this value to an enum member in Modifiability. If the value does not
        correspond to any enum members, a KeyError is raised after logging the error. If 'modifiability' is absent or
        its value is empty, the function defaults to Modifiability.NOT_REQUIRED_AND_UNLOCKED.

        Parameters
        ----------
        variable_name : str
            The name of the variable for which the modifiability status is being determined. Used for error logging.
        variable_properties : Dict[str, Any]
            A dictionary containing the properties of the variable, containing the desired 'modifiability' property.

        Returns
        -------
        Modifiability
            An enum member representing the variable's modifiability status.

        Raises
        ------
        KeyError
            If 'modifiability' in `variable_properties` does not match any enum member in Modifiability. The error
            message includes the invalid modifiability value and suggests valid values.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._get_variable_modifiability.__name__,
        }

        default = "UNREQUIRED UNLOCKED"
        modifiability = variable_properties.get("modifiability", default)

        try:
            return Modifiability.__getitem__("_".join(modifiability.strip().upper().split()))
        except KeyError:
            self.om.add_warning(
                "Unknown modifiability entry",
                f"Unknown modifiability value of {modifiability} for variable {variable_name}. Modifiability should be "
                f"one of {Modifiability.values()}. Using the default value: {default}",
                info_map,
            )
            return Modifiability.__getitem__("_".join(default.strip().upper().split()))

    def _is_input_required_upon_initialization(self, variable_name: str, variable_properties: Dict[str, Any]) -> bool:
        """
        Determines whether a variable requires an input value upon initialization based on its modifiability status.

        This function utilizes the '_get_variable_modifiability' method to ascertain the modifiability status of the
        variable identified by 'variable_name' and described by 'variable_properties'. It then checks if the
        modifiability status is either 'REQUIRED_AND_LOCKED' or 'REQUIRED_AND_UNLOCKED', indicating that the variable
        must be initialized with a value.

        Parameters
        ----------
        variable_name : str
            The name of the variable being evaluated for its initialization requirements.
        variable_properties : Dict[str, Any]
            A dictionary containing the properties of the variable, which should include its modifiability status among
            others.

        Returns
        -------
        bool
            True if the variable's modifiability status necessitates an input value upon initialization,
            False otherwise.
        """
        variable_modifiability = self._get_variable_modifiability(
            variable_name=variable_name, variable_properties=variable_properties
        )
        return variable_modifiability in Modifiability.get_required_during_initialization()

    def _is_modifiable_during_runtime(self, variable_name: str, variable_properties: Dict[str, Any]) -> bool:
        """
        Checks if a variable can be modified during runtime based on its modifiability status.

        This function determines the modifiability status of a variable using the '_get_variable_modifiability' method.
        It assesses whether the variable, identified by 'variable_name' and described by 'variable_properties', is
        allowed to be modified after initialization. A variable is considered modifiable during runtime if its
        modifiability status is either 'REQUIRED_AND_UNLOCKED' or 'NOT_REQUIRED_AND_UNLOCKED'.

        Parameters
        ----------
        variable_name : str
            The name of the variable to check for runtime modifiability.
        variable_properties : Dict[str, Any]
            A dictionary containing the properties of the variable, including details that determine its modifiability.

        Returns
        -------
        bool
            True if the variable is allowed to be modified during runtime, False otherwise.
        """
        variable_modifiability = self._get_variable_modifiability(
            variable_name=variable_name, variable_properties=variable_properties
        )
        return variable_modifiability in Modifiability.get_modifiable_at_runtime()

    def _log_missing_data(
        self, variable_properties: Dict[str, Any], var_name: str, called_during_initialization: bool
    ) -> None:
        """
        Handles logging for missing data for a variable, logging errors or warnings based on the context of
        initialization or runtime updates.

        Parameters
        ----------
        variable_properties : Dict[str, Any]
            Properties of the variable, potentially including its modifiability status.
        var_name : str
            The name of the variable with missing data.
        called_during_initialization: bool
            Boolean variable indicating whether the function is being called during initialization

        Raises
        ------
        KeyError
            Raised if the missing data is deemed necessary, either during initialization or for a runtime update.

        Notes
        -----
        This function determines if it's being called during the initialization phase and checks if the missing variable
        data is required at this stage using '_is_input_required_upon_initialization'. If required, it logs an error and
        raises a KeyError. If not, it logs a warning.
        """
        info_map = {"class": self.__class__.__name__, "function": self._log_missing_data.__name__}
        if not called_during_initialization:
            error_msg = f"Key {var_name} not found in data. A value is required to update variable during runtime."
            self.om.add_error("Missing required data", error_msg, info_map)
            raise KeyError(error_msg)

        if self._is_input_required_upon_initialization(variable_name=var_name, variable_properties=variable_properties):
            self.om.add_error(
                "Missing required data",
                f"Key {var_name} not found in input data. Input value is required for this "
                "variable upon program initialization.",
                info_map,
            )
            raise KeyError(
                f"Key {var_name} not found in input data. Input value is required for this "
                "variable upon program initialization."
            )
        self.om.add_warning(
            "Validation: key not found in input data -- input not required upon initialization",
            f"Key {var_name} not found in input data. Input value is not required for this "
            "variable upon program initialization, setting the variable value to None.",
            info_map,
        )

    def get_data(self, data_address: str) -> Any:
        """
        Get the requested data from the pool if it exists. If not, None is returned.

        Parameters
        ----------
        data_address : str
            The address of the requested data.

        Returns
        -------
        Any
            The requested data if found. None otherwise.

        Examples
        -------
        The user can request as broad or narrow a selection of the input data pool as is needed.

        Input Manager must first be instantiated:
        >>> input_manager = InputManager()

        This will return the value of `calf_num` of the `herd_information` section in the `animal` blob
        (in this example, the value for `calf_num` is 8):
        >>> input_manager.get_data('animal.herd_information.calf_num')
        8

        If a broader range of data is needed, the user can expand the query to get_data
        by shortening the data_address. This will return the full herd_information object:
        >>> input_manager.get_data('animal.herd_information')
        {
        calf_num: 8,
        heiferI_num: 44,
        heiferII_num: 38,
        heiferIII_num_springers: 5,
        cow_num: 100,
        herd_num: 187,
        herd_init: False,
        breed: HO
        }

        If the requested data does not exist, the method will return None:
        >>> input_manager.get_data('animal.herd_information.nonexistent_property')
        None
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self.get_data.__name__,
        }
        element_hierarchy = data_address.split(".")
        try:
            data_value = self.data_validator.extract_value_by_key_list(self.__pool, element_hierarchy)
            timestamp = Utility.get_timestamp(include_millis=True)
            self.__get_data_logs_pool[timestamp] = f"InputManager.get_data() called for {element_hierarchy}."
            return deepcopy(data_value)
        except KeyError as key_error:
            self.om.add_error("Validation: data not found", str(key_error), info_map)

        return None

    def check_property_exists_in_pool(self, data_address: str) -> bool:
        """
        Check if the requested property exists in the pool.

        Parameters
        ----------
        data_address : str
            The address of the requested property.

        Returns
        -------
        bool
            True if the property exists in the pool, False otherwise.

        Examples
        --------
        The user can check if a property exists in the pool.

        Input Manager must first be instantiated:
        >>> input_manager = InputManager()

        This will return True if the property `calf_num` exists in the `herd_information` section of the `animal` blob:
        >>> input_manager.check_property_exists_in_pool('animal.herd_information.calf_num')
        True

        If the property does not exist, the method will return False:
        >>> input_manager.check_property_exists_in_pool('animal.herd_information.nonexistent_property')
        False
        """
        variable_path = data_address.split(".")
        try:
            self.data_validator.extract_value_by_key_list(self.__pool, variable_path)
            self.om.route_logs(self.data_validator.event_logs)
            return True
        except KeyError:
            return False

    def get_metadata(self, metadata_address: str) -> Any:
        """
        Get the requested metadata from the IM metadata dictionary.

        Parameters
        ----------
        metadata_address : str
            The address of the requested metadata.

        Returns
        -------
        Any
            The requested metadata if found.

        Raises
        -------
        KeyError
            If the requested metadata is not found.

        Examples
        -------
        The user can request as broad or narrow a selection of the metadata as is needed.

        Input Manager must first be instantiated:
        >>> input_manager = InputManager()

        This will return the 'type' for `albedo` in the `soil_profile_properties` section of the metadata's properties
        (the type for `albedo` is `number`):
        >>> input_manager.get_metadata('properties.soil_profile_properties.albedo.type')
        "number"

        If a broader range of the metadata is needed, the user can expand the query to get_metadata
        by shortening the metadata_address. This will return the full 'albedo' object containing its type,
        description, minimum, maximum, and default:
        >>> input_manager.get_metadata('properties.soil_profile_properties.albedo')
        {
        "type": "number",
        "description": "Ratio of solar radiation reflected by soil to amount of incident upon it.
        \nUnitless.\nReference: SWAT Input .SOL - SOL_ALB",
        "minimum": 0.0,
        "maximum": 1.0,
        "default": 0.16
        }
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.get_metadata.__name__,
        }

        element_hierarchy = metadata_address.split(".")

        try:
            metadata_value = reduce(lambda d, key: d[key], element_hierarchy, self.__metadata)
            return deepcopy(metadata_value)

        except KeyError:
            invalid_key = element_hierarchy[-1]
            parent_address = ".".join(element_hierarchy[:-1])

            self.om.add_error(
                "Validation: data not found:",
                f'Cannot find "{metadata_address}", '
                f'"{parent_address}" does not have attribute '
                f'"{invalid_key}".',
                info_map,
            )

            raise KeyError(
                f'Data not found: Cannot find "{metadata_address}", '
                f'"{parent_address}" does not have attribute "{invalid_key}".'
            )

    def get_data_keys_by_properties(self, target_properties: str) -> list[str]:
        """
        Retrieves the list of metadata keys that point to data which have the target_properties.

        Parameters
        ----------
        target_properties : str
            The name of the metadata properties group that is being searched for.

        Returns
        -------
        list[str]
            List of keys which point to data within the Input Manager's data pool that adhere to the target metadata
            properties.

        Examples
        --------
        If the metadata looked like the following:
        ```
        {
            "files": {
                "field_1": {
                    "properties": "field_properties",
                    ...
                },
                "soil_1": {
                    "properties": "soil_profile_properties",
                    ...
                },
                "field_2": {
                    "properties": "field_properties",
                    ...
                },
                ...
            },
            "properties": {...},
            ...
        }
        ```
        The the call `get_data_keys_by_properties("field_properties")` would be expected to return the list
        `["field_1", "field_2"]`.

        Notes
        -----
        If no keys have the specified property, the method returns an empty list.

        """
        data_keys: List[str] = []

        info_map = {
            "class": self.__class__.__name__,
            "function": self.get_data_keys_by_properties.__name__,
        }

        try:
            input_data = self.get_metadata(ADDRESS_TO_INPUTS)
        except KeyError:
            error_name = "Cannot find data"
            error_message = "Could not find input metadata."
            self.om.add_error(error_name, error_message, info_map)
            return data_keys

        data_keys = [key for key, data in input_data.items() if data.get("properties") == target_properties]

        return data_keys

    def __delete_input_and_metadata(self, data_address: str) -> tuple[bool, bool]:
        """
        NOTE: **Please use extreme caution using this function as it will delete data and metadata from the pool.**

        When given a valid address, this function removes the input data and its associated metadata.

        Parameters
        ----------
        data_address : str
            The address of the input data to remove.

        Returns
        -------
        tuple[bool, bool]
            First value for indication of data removal, second value for indication of metadata removal.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.__delete_input_and_metadata.__name__,
        }
        keys = data_address.split(".")
        timestamp = Utility.get_timestamp(include_millis=True)

        try:
            self.data_validator.extract_value_by_key_list(self.__pool, keys[:-1]).pop(keys[-1])
            removed_data = True
            self.__delete_data_logs_pool[timestamp] = (
                f"InputManager.__delete_input_and_metadata() called for {keys}, data deleted from {data_address}"
            )
        except KeyError as keyerror:
            self.om.add_error("Validation: data not found", str(keyerror), info_map)
            removed_data = False

        try:
            file_key = keys[0]
            props_blob_key = self.__metadata["files"][file_key]["properties"]
            metadata_keys = ["properties", props_blob_key] + keys[1:]
            metadata_path = ".".join(metadata_keys)
            metadata_parent = reduce(lambda d, k: d[k], metadata_keys[:-1], self.__metadata)
            metadata_parent.pop(metadata_keys[-1], None)
            removed_metadata = True
            self.__delete_data_logs_pool[timestamp] = (
                f"Deleted metadata for {data_address} and removed it from {metadata_path}."
            )
        except KeyError as keyerror:
            self.om.add_error("Validation: metadata not found", str(keyerror), info_map)
            removed_metadata = False

        return removed_data, removed_metadata

    def flush_pool(self) -> None:
        """
        Clear the variable pool.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.flush_pool.__name__,
        }
        self.__pool = {}
        self.om.add_log("Clear variable pool", "The pool is emptied.", info_map)

    def _metadata_properties_exist(self, variable_name: str, properties_blob_key: str) -> bool:
        """
        Checks if specific properties exist in the metadata for a given variable.

        Notes
        -----
        This function is designed to verify the existence of specified properties
        within the metadata of a particular variable. It returns a boolean indicating
        the existence of the properties, and a KeyError in case of missing metadata
        or properties.

        Parameters
        ----------
        variable_name : str
            The name of the variable for which the metadata is to be checked.
        properties_blob_key : str
            The key representing the specific properties blob in the metadata to check.

        Returns
        -------
        bool
            True if the properties exist, False otherwise.

        Raises
        -------
        ValueError
            If no metadata is loaded in InputManager.__metadata.
        KeyError
            If no metadata properties can be found with the given `properties_blob_key`.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._metadata_properties_exist.__name__,
        }
        if not self.__metadata:
            self.om.add_error(
                "No metadata loaded",
                "No metadata is loaded to the InputManager.",
                info_map,
            )
            raise ValueError("No metadata loaded.")
        if properties_blob_key not in self.__metadata["properties"]:
            self.om.add_error(
                "No metadata found",
                f"No metadata is found for variable '{variable_name}' with given "
                f"properties_blob_key {properties_blob_key}. Consider adding variable "
                f"information and properties to the metadata.",
                info_map,
            )
            raise KeyError(
                f"No metadata is found for variable '{variable_name}' with given properties_blob_key"
                f" {properties_blob_key}. Consider adding variable information and properties to the "
                f"metadata."
            )
        return True

    def _add_variable_to_pool(
        self,
        variable_name: str,
        input_data: Dict[str, Any],
        properties_blob_key: str,
        eager_termination: bool,
    ) -> bool:
        """
        Adds a variable to the pool after validating its data against specified metadata properties.

        Notes
        -----
        This function processes and validates the input data for a variable based on its metadata properties,
        attempting to fix any invalid elements. If all elements are valid or successfully fixed, the data is added
        to a pool. The function supports eager termination, which can halt the process early if invalid data is
        encountered or if a non-modifiable variable is attempted to be modified during runtime.


        Parameters
        ----------
        variable_name : str
            The name of the variable to be added to the pool.
        input_data : Dict[str, Any]
            The data associated with the variable that needs validation and addition to the pool.
        properties_blob_key : str
            The key in the metadata properties against which the data is validated.
        eager_termination : bool
            Flag indicating whether the function should return early in case of invalid data.

        Returns
        -------
        bool
             True if the variable is successfully added, False otherwise.

        Raises
        -------
        ValueError
            If eager_termination is True and the variable failed validation.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._add_variable_to_pool.__name__,
        }
        validated_data = {}
        elements_counter = ElementsCounter()

        data, metadata_properties = self._prepare_data(variable_name, input_data, properties_blob_key)

        modifiable = self._check_modifiability(variable_name, metadata_properties, eager_termination)

        if not modifiable:
            return modifiable

        validated_data = self._validate_data(
            data, metadata_properties, eager_termination, properties_blob_key, elements_counter
        )

        if validated_data:
            self._add_to_pool(variable_name, validated_data)
            elements_counter += elements_counter

        if elements_counter.invalid_elements > 0:
            self.om.add_error(
                "Invalid variable",
                f"Variable {variable_name} has invalid components. Only successfully validated components are "
                f"added to InputManager pool during runtime.",
                info_map,
            )
            if eager_termination:
                raise ValueError(
                    f"Variable {variable_name} has invalid components. Only successfully validated components are added"
                    f" to InputManager pool during runtime."
                )
            return False

        return True

    def _prepare_data(
        self, variable_name: str, input_data: dict[str, Any], properties_blob_key: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Prepare data and metadata properties for validation.

        Parameters
        ----------
        variable_name : str
            The name of the variable to be added to the pool.
        input_data : Dict[str, Any]
            The data associated with the variable that needs validation and addition to the pool.
        properties_blob_key : str
            The key in the metadata properties against which the data is validated.

        Returns
        -------
        Tuple[List[str], Dict[str, Any], Dict[str, Any]]
            Prepared element hierarchy, data, and metadata properties.

        """
        element_hierarchy = variable_name.split(".")
        metadata_root = self.__metadata["properties"][properties_blob_key]
        if len(element_hierarchy) > 1:
            flat_key_data = {variable_name.split(".", 1)[1]: input_data}
            metadata_hierarchy = element_hierarchy if isinstance(input_data, Dict) else element_hierarchy[:-1]
            nested_data = Utility.flatten_keys_to_nested_structure(flat_key_data)

            metadata_properties = metadata_root
            data = input_data
            current_metadata = metadata_root
            current_nested_data = nested_data
            consumed_all_keys = True
            for key in metadata_hierarchy[1:]:
                if isinstance(current_metadata, dict) and key in current_metadata:
                    current_metadata = current_metadata[key]
                    metadata_properties = current_metadata
                else:
                    consumed_all_keys = False
                    break

                if isinstance(current_nested_data, dict) and key in current_nested_data:
                    current_nested_data = current_nested_data[key]
                    data = current_nested_data

            if consumed_all_keys and metadata_hierarchy[1:]:
                data = nested_data
        else:
            data = input_data
            metadata_properties = metadata_root

        return data, metadata_properties

    def _check_modifiability(
        self, variable_name: str, metadata_properties: dict[str, Any], eager_termination: bool
    ) -> bool:
        """
        Checks whether a variable is allowed to be modified at runtime.

        Parameters
        ----------
        variable_name : str
            The name of the variable to be added to the pool.
        metadata_properties : dict[str, Any]
            Metadata for each property of a variable, including details like type, description, modifiability,
            and validation constraints.
        eager_termination : bool
            Indicator for the need of eager termination.

        Returns
        -------
        bool
            Indicator for whether the data is modifiable.

        Raises
        ------
        PermissionError
            If eager_termination is True and the variable is not modifiable during runtime.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._check_modifiability.__name__,
        }
        is_modifiable_during_runtime = self._is_modifiable_during_runtime(
            variable_name=variable_name, variable_properties=metadata_properties
        )
        if not is_modifiable_during_runtime and eager_termination:
            self.om.add_error("IM Runtime Modification", f"{variable_name} is not modifiable during runtime.", info_map)
            raise PermissionError(f"IM Runtime Modification Error: {variable_name} is not modifiable during runtime.")
        elif not is_modifiable_during_runtime:
            self.om.add_warning(
                "IM Runtime Modification", f"{variable_name} is not modifiable during runtime.", info_map
            )
            return False
        return True

    def _validate_data(
        self,
        data: dict[str, Any],
        metadata_properties: dict[str, Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
    ) -> dict[str, Any]:
        """
        Validate input data based on metadata properties.

        Parameters
        ----------
        data : dict[str, Any]
            Data to be validated.
        metadata_properties : dict[str, Any]
            Metadata for each property of a variable, including details like type, description, modifiability,
            and validation constraints.
        eager_termination : bool
            Indicator for the need of eager termination.
        properties_blob_key : str
            The key in the metadata properties against which the data is validated.
        elements_counter : ElementsCounter
            An ElementsCounter object to keep track of status of variables.

        Returns
        -------
        dict[str, Any]
            A dictionary of validated data.

        """
        validated_data = {}
        for metadata_property in metadata_properties.keys():
            if metadata_property in VARIABLE_PROPERTIES_TO_IGNORE:
                continue
            variable_properties = metadata_properties[metadata_property]
            is_element_acceptable = self.data_validator.validate_data_by_type(
                variable_path=[metadata_property],
                variable_properties=variable_properties,
                data=data,
                eager_termination=eager_termination,
                properties_blob_key=properties_blob_key,
                elements_counter=elements_counter,
                called_during_initialization=False,
                fixable_data_types=FIXABLE_INPUT_DATA_TYPES,
            )

            if is_element_acceptable:
                validated_data[metadata_property] = data[metadata_property]

        return validated_data

    def _add_to_pool(self, variable_name: str, validated_data: dict[str, Any]) -> None:
        """
        Add validated data to the pool.

        Parameters
        ----------
        variable_name : str
            The name of the variable to be added to the pool.
        validated_data : dict[str, Any]
            A dictionary of validated data.

        """
        if variable_name in self.__pool.keys():
            info_map = {
                "class": self.__class__.__name__,
                "function": self._add_to_pool.__name__,
            }
            self.om.add_warning(
                "Overwriting existing variable",
                f"Variable {variable_name} already exists in InputManager pool, overwriting the old value.",
                info_map,
            )
        self.__pool[variable_name] = validated_data

    def add_runtime_variable_to_pool(
        self,
        variable_name: str,
        data: Dict[str, Any],
        properties_blob_key: str,
        eager_termination: bool,
    ) -> bool:
        """
        Adds a variable to the InputManager's pool after validating it against metadata.

        Notes
        -----
        This function takes in a variable along with its name and a key to access its validation metadata.
        It validates the data against the provided metadata and adds the data to the InputManager pool if it is valid.

        Parameters
        ----------
        variable_name: str
            The name of the dictionary variable to be added.
        data : Dict[str, Any]
            The data of the variable, structured as a dictionary.
        properties_blob_key : str
            A key used to locate the metadata for validation of the variable.
        eager_termination : bool
            If True, a ValueError will be raised from _add_variable_to_pool() when the variable is invalid.
            If False, the function returns False.

        Returns
        -------
        bool
            True if the variable is successfully validated and added to the pool.
            False if the variable is invalid and not added to the pool.

        Raises
        ------
        TypeError
            If `data` is not the expected type of Dict[str, Any].
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.add_runtime_variable_to_pool.__name__,
        }
        if not (isinstance(data, Dict)):
            self.om.add_error(
                "Incorrect variable type",
                f"Variable {variable_name} has type {type(data)}, does not match "
                f"the expected type of `Dict[str, Any]`.",
                info_map,
            )
            raise TypeError("Incorrect variable type. Expected types: `data: Dict[str, Any]`.")

        metadata_properties_exist = self._metadata_properties_exist(
            variable_name=variable_name, properties_blob_key=properties_blob_key
        )

        if metadata_properties_exist:
            add_variable_success = self._add_variable_to_pool(
                variable_name=variable_name,
                input_data=data,
                properties_blob_key=properties_blob_key,
                eager_termination=eager_termination,
            )
            return add_variable_success
        else:
            return False

    def dump_get_data_logs(self, path: Path) -> None:
        """
        Dumps the stored get data logs to a JSON file at the specified path.

        Parameters
        ----------
        path : Path
            The directory path where the JSON file will be saved.

        """
        file_name = self.om.generate_file_name(base_name="InputManager_get_data_log", extension="json")
        file_path = path / file_name
        self.om.create_directory(path)
        self.om.dict_to_file_json(self.__get_data_logs_pool, file_path)

    def dump_delete_data_logs(self, path: Path) -> None:
        """
        Dumps the stored get data logs to a JSON file at the specified path.

        Parameters
        ----------
        path : Path
            The directory path where the JSON file will be saved.

        """
        file_name = self.om.generate_file_name(base_name="InputManager_delete_data_log", extension="json")
        file_path = path / file_name
        self.om.create_directory(path)
        self.om.dict_to_file_json(self.__delete_data_logs_pool, file_path)

    def save_metadata_properties(self, output_dir: Path) -> None:
        """
        Saves metadata properties in CSV format.

        Parameters
        ----------
        output_dir : Path
            The path to the output directory where the metadata properties CSV will be saved.

        Raises
        ------
        FileNotFoundError
            If the file cannot be saved at the specified path.
        PermissionError
            If the user does not have permission to save the file at the specified path.
        OSError
            For any other unexpected error that occurs while trying to save the CSV.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.save_metadata_properties.__name__,
        }
        records = self._parse_metadata_properties(self.__metadata["properties"])
        df = pd.DataFrame(records)
        path_to_save = output_dir / self.om.generate_file_name("InputManager_metadata_properties", extension="csv")
        self.om.add_log(
            "CSV save attempt.", f"Attempting to save metadata properties as CSV to {path_to_save}", info_map
        )
        try:
            self.om.create_directory(output_dir)
            df.to_csv(path_to_save, index=False)
            self.om.add_log("Save CSV success.", f"Successfully saved to {path_to_save}.", info_map)
        except FileNotFoundError as fnfe:
            self.om.add_error("Save CSV failure.", f"Unable to save to {path_to_save} because of {fnfe}.", info_map)
            raise fnfe
        except PermissionError as pe:
            self.om.add_error("Save CSV failure.", f"Unable to save to {path_to_save} because of {pe}.", info_map)
            raise pe
        except OSError as e:
            self.om.add_error("Save CSV failure.", f"Unable to save to {path_to_save} because of {e}.", info_map)
            raise e

    def _parse_metadata_properties(
        self, data: Dict[str, Any], prefix: str = "", sep: str = "_"
    ) -> List[Dict[str, Any]]:
        """
        Recursively traverse through the metadata properties dictionary
        to flatten it by creating a record for each entry.

        Parameters
        ----------
        data : Dict[str, Any]
            The metadata properties data to be parsed.
        prefix : str, optional
            The data record prefix, by default ''.
        sep : str, optional
            The separator used between parts of the data entry names, by default '_'.

        Returns
        -------
        List[Dict[str, Any]]
            A list of flattened data entries from the json file.
        """
        records = []
        for property_key, property_value in data.items():
            if isinstance(property_value, dict):
                for nested_key, nested_value in property_value.items():
                    if isinstance(nested_value, dict):
                        if self._check_property_type_primitive(nested_value):
                            name = (
                                prefix + sep + property_key + sep + nested_key
                                if prefix
                                else property_key + sep + nested_key
                            )
                            nested_value["description"] = nested_value.get(
                                "description",
                                property_value.get("properties", {}).get("description", "No description available"),
                            )
                            record = self._create_record(nested_value, name)
                            records.append(record)
                        else:
                            records.extend(
                                self._parse_metadata_properties(
                                    nested_value,
                                    prefix + sep + property_key if prefix else property_key + sep + nested_key,
                                    sep,
                                )
                            )
                    elif self._check_property_type_primitive(property_value):
                        name = prefix + sep + property_key
                        record = self._create_record(property_value, name)
                        records.append(record)
                        break
                    elif property_value.get("type") == "object":
                        self._parse_metadata_properties(property_value, prefix + sep + property_key, sep)

        return records

    def _check_property_type_primitive(self, property: Dict[str, Any]) -> bool:
        """Checks whether the property's "type" is primitive or an array of primitive types."""
        if property.get("type") in ["bool", "string", "number"]:
            return True
        elif property.get("type") == "array":
            if property.get("properties", {}).get("type") in ["bool", "string", "number"]:
                return True
        return False

    def _create_record(self, data_entry: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Assembles a record to a specific format to match the columns of the CSV to which it will eventually be added.

        Parameters
        ----------
        data_entry : Dict[str, Any]
            The data entry from the json file to be converted into the record format.
        name : str
            The name to be used for the record.

        Returns
        -------
        Dict[str, Any]
            A dictionary of the data entry converted to the record format.
        """
        properties_index = name.find("_properties") + len("_properties")
        properties_group = name[:properties_index]
        name = name[properties_index + 1 :]
        return {
            "properties_group": properties_group,
            "name": name,
            "type": data_entry.get("type", ""),
            "description": data_entry.get("description", ""),
            "pattern": data_entry.get("pattern", ""),
            "default": data_entry.get("default", ""),
            "maximum": data_entry.get("maximum", ""),
            "minimum": data_entry.get("minimum", ""),
        }

    def compare_metadata_properties(
        self, properties_file_path: Path, comparison_properties_file_path: Path, output_directory: Path
    ) -> None:
        """
        Compares two metadata properties json files using the DeepDiff package and saves the results in a text file.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.compare_metadata_properties.__name__,
        }
        self.om.create_directory(output_directory)
        self._load_metadata(properties_file_path)
        properties1 = deepcopy(self.meta_data)
        self.meta_data = {}
        self._load_metadata(comparison_properties_file_path)
        properties2 = self.meta_data

        diff = DeepDiff(properties1, properties2, ignore_order=True, verbose_level=2)

        first_file_path = os.path.basename(str(properties_file_path))
        second_file_path = os.path.basename(str(comparison_properties_file_path))
        file_name = f"diff_results_{first_file_path}_vs_{second_file_path}"

        try:
            self.om.add_log("Save metadata diff try", f"Attempting to save to {file_name}", info_map)
            with open(f"{str(output_directory)}/{file_name}.txt", "w") as file:
                file.write(
                    f"Comparing changes going from '{properties_file_path}'"
                    f" to '{comparison_properties_file_path}'\n\n"
                )

                if diff == {}:
                    file.write("There were no differences found between these two properties files.")

                else:
                    sections = {
                        "dictionary_item_added": "Items added:\n",
                        "dictionary_item_removed": "Items removed:\n",
                        "values_changed": "Values changed:\n",
                    }
                    for key, heading in sections.items():
                        if key in diff:
                            file.write(heading)
                            for sub_key, value in diff[key].items():
                                file.write(f"{sub_key}: {value}\n")
                            file.write("\n")

            self.om.add_log("Save metadata diff successful", f"Successfully saved to {file_name}", info_map)

        except PermissionError:
            self.om.add_error(
                "Permission error in saving file",
                f"Permission denied when trying to write to {file_name}.txt.",
                info_map,
            )
            raise
        except OSError as e:
            self.om.add_error(
                "Unexpected error in saving file",
                f"An unexpected OS error occurred: {e}",
                info_map,
            )
            raise

    def export_pool_to_csv(self, output_prefix: str, output_path: Path) -> None:
        """
        Flatten the interested input data and export the variables with their values into a CSV.

        Parameters
        ----------
        output_prefix: str
            The output prefix for the current task.
        output_path: Path
            The folder to save the output CSV.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.export_pool_to_csv.__name__,
        }

        result_df = pd.DataFrame(columns=["property_group", "variable_name", f"{output_prefix}_value"])
        for property_group in self.csv_report_generation_list:
            if property_group == "animal_population":
                continue
            result = Utility.flatten_dictionary(self.pool[property_group])
            for key, value in result.items():
                result_df.loc[len(result_df)] = [property_group, key, value]

        try:
            self.om.create_directory(output_path)
            output_file = output_path / f"{output_prefix}.csv"
            result_df.to_csv(output_file, index=False)
            self.om.add_log("Save input data CSV success.", f"Successfully saved to {output_path}.", info_map)

        except FileNotFoundError as fnfe:
            self.om.add_error("Save CSV failure.", f"Unable to save to {output_path} because of {fnfe}.", info_map)
            raise fnfe
        except PermissionError as pe:
            self.om.add_error("Save CSV failure.", f"Unable to save to {output_path} because of {pe}.", info_map)
            raise pe
        except OSError as e:
            self.om.add_error("Save CSV failure.", f"Unable to save to {output_path} because of {e}.", info_map)
            raise e

    def _extract_target_and_save_block(
        self, target_and_save_block: dict[str, dict[str, Any]], eager_termination: bool
    ) -> dict[str, Any]:
        """
        Retrieves the alias value to pass to the CrossValidator for processing.

        Parameters
        ----------
        target_and_save_block : dict[str, dict[str, Any]]
            A dictionary containing the "target and save block" of the cross-validation rule.
        eager_termination : bool
            Specifies whether to immediately terminate the process when a validation error is
            encountered.

        Returns
        -------
        dict[str, Any]
            A dictionary mapping variable names to their values.

        """
        target_and_save_results = {}
        self.cross_validator.check_target_and_save_block(target_and_save_block, eager_termination)
        sections = ["variables", "constants"]
        for section in sections:
            if section == "variables" and target_and_save_block.get(section) is not None:
                for key, address in target_and_save_block[section].items():
                    target_and_save_results[key] = self.get_data(address)
            elif section == "constants" and target_and_save_block.get(section) is not None:
                for constant_name, value in target_and_save_block[section].items():
                    target_and_save_results[constant_name] = value
        return target_and_save_results
