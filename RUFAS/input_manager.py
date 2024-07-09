import json
import os
import re
from copy import deepcopy
from deepdiff import DeepDiff
from enum import Enum
from functools import reduce
from pathlib import Path
from typing import Any, Dict, List, Union, Callable, Sequence, Tuple

import pandas as pd

from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility

om = OutputManager()

"""
Set enumerating the input data types that the Input Manager will attempt to fix while validating input data.
"""
FIXABLE_INPUT_DATA_TYPES: set[str] = {"string", "number", "bool"}

"""
Set enumerating the input data formats the Input Manager can accept.
"""
VALID_INPUT_TYPES: set[str] = {"json", "csv"}

ADDRESS_TO_INPUTS = "files"


class Modifiability(Enum):
    """
    Enum class representing the modifiability status of a variable.

    This Enum defines various levels of modifiability for a variable, indicating whether a variable is required at
    initialization and if it can be modified during runtime.

    Attributes
    ----------
    REQUIRED_LOCKED : str
        Indicates the variable must be initialized with a value and cannot be modified thereafter.
    REQUIRED_UNLOCKED : str
        Indicates the variable must be initialized with a value but can be modified during runtime.
    UNREQUIRED_UNLOCKED : str
        Indicates the variable does not need to be initialized with a value and can be modified during runtime.
    """

    REQUIRED_LOCKED: str = "required locked"
    REQUIRED_UNLOCKED: str = "required unlocked"
    UNREQUIRED_UNLOCKED: str = "unrequired unlocked"

    @classmethod
    def values(cls) -> List[str]:
        """
        Provides a list of the string values of the enum members.

        Returns
        -------
        List[str]
            A list containing the string values of the enum members.
        """
        return list(map(lambda c: c.value, cls))

    @classmethod
    def get_required_during_initialization(cls) -> List["Modifiability"]:
        return [Modifiability.REQUIRED_LOCKED, Modifiability.REQUIRED_UNLOCKED]

    @classmethod
    def get_modifiable_at_runtime(cls) -> List["Modifiability"]:
        return [Modifiability.REQUIRED_UNLOCKED, Modifiability.UNREQUIRED_UNLOCKED]


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
        if InputManager.__instance is None:
            InputManager.__instance = self
            self.__metadata: Dict[str, Any] = {}
            self.__pool: Dict[str, Any] = {}
            self.__get_data_logs_pool: Dict[str, str] = {}
            self.elements_counter = ElementsCounter()
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

    def start_data_processing(self, metadata_path: Path, eager_termination: bool = True) -> bool:
        """
        Starts the pipeline for organizing metadata and input data processing.

        Parameters
        ----------
        metadata_path : Path
            File path to the metadata.
        eager_termination : bool, default=True
            If True, the process will be terminated as soon as finding invalid data and failing to fix it.
            If False, the process will be terminated after going through and validating the entire data.

        Returns
        -------
        bool
            True if data is valid, otherwise False.
        """
        self._load_metadata(metadata_path)
        self._validate_metadata()
        self._load_properties()
        self._validate_properties()
        is_input_data_valid = self._populate_pool(eager_termination)
        return is_input_data_valid

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
        om.add_log(
            "load_metadata_attempt",
            f"Attempting to load metadata from {metadata_path}.",
            info_map,
        )
        try:
            with open(metadata_path) as metadata_file:
                self.__metadata = json.load(metadata_file)
                om.add_log(
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
            properties_path = Path(self.__metadata["files"]["properties"]["path"])
            om.add_log(
                "load_properties_attempt",
                f"Attempting to load properties from {properties_path}",
                info_map,
            )
            if not properties_path.exists():
                raise FileNotFoundError(f"Properties file not found at {properties_path}")

            del self.__metadata["files"]["properties"]

            self.__metadata["properties"] = self._load_data_from_json(properties_path)
            om.add_log(
                "load_properties_success",
                f"Successfully loaded properties from {properties_path}",
                info_map,
            )

        except FileNotFoundError as fnfe:
            om.add_error("load_properties_file_not_found", str(fnfe), info_map)
            raise
        except json.JSONDecodeError as jde:
            om.add_error("load_properties_json_error", str(jde), info_map)
            raise
        except Exception as e:
            om.add_error("load_properties_error", f"Unexpected error: {e}", info_map)
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
        om.add_log("open_json_file", f"Attempting to open {file_path}.", info_map)
        try:
            with open(file_path) as json_file:
                data: Dict[str, Any] = json.load(json_file)
                om.add_log(
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
        om.add_log("open_csv_file", f"Attempting to open {file_path}.", info_map)
        try:
            with open(file_path, "r", encoding="utf-8") as csv_file:
                data_frame = pd.read_csv(csv_file)
                data_dict = {column: data_frame[column].tolist() for column in data_frame.columns}
                if not data_frame.empty:
                    om.add_log(
                        "load_data_successful",
                        f"Successfully loaded data from {file_path}.",
                        info_map,
                    )
                return data_dict
        except Exception as e:
            raise e

    def _populate_pool(self, eager_termination: bool) -> bool:
        """
        Loads input files, runs validations on the data from the input files, attempts to fix invalid data,
        then adds data to the pool.

        Parameters
        ----------
        eager_termination : bool
            If True, the process will be terminated as soon as finding invalid data and failing to fix it.
            If False, the process will be terminated after going through and validating the entire data,
            If invalid data is found.

        Returns
        -------
        bool
            True if data is valid, otherwise False.

        Raises
        ------
        KeyError
            If faulty data type found in data blob key.

        """

        data_type_to_loader_map: Dict[str, Callable[[Path], Dict[str, Any]]] = {
            "json": self._load_data_from_json,
            "csv": self._load_data_from_csv,
        }
        valid_data = True
        for file_blob_key, file_details in self.__metadata["files"].items():
            file_path = file_details["path"]

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
                variable_properties = metadata_properties[metadata_property]
                is_element_acceptable = self._validate_input_by_type(
                    variable_path=[metadata_property],
                    variable_properties=variable_properties,
                    input_data=input_data,
                    eager_termination=eager_termination,
                    properties_blob_key=properties_blob_key,
                    elements_counter=self.elements_counter,
                    called_during_initialization=True,
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
            om.add_warning(
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
            error_msg = (f"Key {var_name} not found in data. A value is required to update variable during runtime.",)
            om.add_error("Missing required data", error_msg, info_map)
            raise KeyError(error_msg)

        if self._is_input_required_upon_initialization(variable_name=var_name, variable_properties=variable_properties):
            om.add_error(
                "Missing required data",
                f"Key {var_name} not found in input data. Input value is required for this "
                "variable upon program initialization.",
                info_map,
            )
            raise KeyError(
                f"Key {var_name} not found in input data. Input value is required for this "
                "variable upon program initialization."
            )
        om.add_warning(
            "Validation: key not found in input data -- input not required upon initialization",
            f"Key {var_name} not found in input data. Input value is not required for this "
            "variable upon program initialization, setting the variable value to None.",
            info_map,
        )

    def _validate_input_by_type(
        self,
        variable_properties: Dict[str, Any],
        variable_path: List[str | int],
        input_data: Dict[str, Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
    ) -> bool:
        """
        Validates the input data based on its specified type.

        Parameters
        ----------
        variable_properties : Dict[str, Any]
            A dictionary containing properties relevant to the validation.
        variable_path : List[str | int]
            The path to the variable being validated.
        input_data : Dict[str, Any]
            The input data to be validated.
        eager_termination : bool
            If True, the process will be terminated as soon as finding invalid data and failing to fix it.
        properties_blob_key : str
            The metadata properties for the data input file being checked.
        elements_counter : ElementsCounter
            A counter to keep track of the number of valid, invalid, and fixed elements.
        called_during_initialization: bool
            Boolean variable indicating whether the function is being called during initialization.

        Returns
        -------
        bool
            True if the input data is valid, False otherwise.

        Raises
        ------
        KeyError
            If the variable's properties does not specify a "type".

        Notes
        -----
        Fixing invalid data will only be attempted if the data is a "simple" type (i.e. a string, bool or number).

        """

        if "type" not in variable_properties:
            raise KeyError(f"Missing 'type' key in {variable_properties}")
        data_type = variable_properties["type"]

        type_to_validator_map: Dict[
            str, Callable[[List[int | str], Dict[str, Any], Dict[str, Any], bool, str, "ElementsCounter", bool], bool]
        ] = {
            "array": self._array_type_validator,
            "object": self._object_type_validator,
            "string": self._string_type_validator,
            "number": self._number_type_validator,
            "bool": self._bool_type_validator,
        }

        if data_type not in type_to_validator_map:
            raise ValueError(
                f"The metadata type of the element '{self._convert_variable_path_to_str(variable_path)}' "
                f"is not valid. Supported types are: {type_to_validator_map.keys()}."
            )

        is_valid = type_to_validator_map[data_type](
            variable_path,
            variable_properties,
            input_data,
            eager_termination,
            properties_blob_key,
            elements_counter,
            called_during_initialization,
        )

        if data_type not in FIXABLE_INPUT_DATA_TYPES:
            return is_valid

        if is_valid:
            elements_counter.increment(ElementState.VALID)
            return True
        is_fixed = self._fix_data(variable_properties, variable_path, input_data, properties_blob_key)
        if is_fixed:
            elements_counter.increment(ElementState.FIXED)
            return True
        elements_counter.increment(ElementState.INVALID)
        return False

    def _validate_array_container_properties(
        self,
        variable_path: List[str | int],
        variable_properties: Dict[str, Any],
        input_data: Any,
        properties_blob_key: str,
    ) -> bool:
        """
        Validates the container properties of an array input data element.

        Parameters
        ----------
        variable_path : List[str | int]
            The path to the variable being validated.
        variable_properties : Dict[str, Any]
            The metadata properties for the variable being validated.
        input_data : Any
            The input data to be validated.
        properties_blob_key : str
            The metadata properties for the data input file being checked.

        Returns
        -------
        bool
            True if the array container properties are valid, False otherwise.
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self._validate_array_container_properties.__name__,
        }
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )
        variable_path_str = self._convert_variable_path_to_str(variable_path)
        if not isinstance(input_data, list):
            om.add_warning(
                "Validation: array container is not a list",
                f"Variable: '{variable_path_str}' is not an array but has type: {type(input_data)}. "
                f"{properties_violation_message}",
                info_map,
            )
            return False

        maximum_length = variable_properties.get("maximum_length")
        minimum_length = variable_properties.get("minimum_length")
        if minimum_length is not None:
            is_in_range = variable_properties["minimum_length"] <= len(input_data)
            if not is_in_range:
                om.add_warning(
                    "Validation: array length less than minimum",
                    f"Variable: '{variable_path_str}' has length: {len(input_data)}, less than minimum length: "
                    f"{minimum_length}. {properties_violation_message}",
                    info_map,
                )
                return False

        if maximum_length is not None:
            is_in_range = len(input_data) <= variable_properties["maximum_length"]
            if not is_in_range:
                om.add_warning(
                    "Validation: array length greater than maximum",
                    f"Variable: '{variable_path_str}' has length: {len(input_data)}, greater than maximum length: "
                    f"{maximum_length}. {properties_violation_message}",
                    info_map,
                )
                return False
        return True

    def _array_type_validator(
        self,
        variable_path: List[str | int],
        variable_properties: Dict[str, Any],
        input_data: Dict[str, Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
    ) -> bool:
        """
        Validates an input data element of type array.

        Parameters
        ----------
        variable_path : List[str | int]
            The path to the variable being validated.
        variable_properties : Dict[str, Any]
            The metadata properties for the variable being validated.
        input_data : Dict[str, Any]
            The input data to be validated.
        eager_termination : bool
            If True, the process will be terminated upon finding invalid data.
        properties_blob_key : str
            The metadata properties for the data input file being checked.
        elements_counter : ElementsCounter
            A counter to keep track of the number of valid, invalid, and fixed elements.
        called_during_initialization: bool
            Boolean variable indicating whether the function is being called during initialization.

        Returns
        -------
        bool
            True if the input data element is valid or fixable, False otherwise.
        """

        array_value = self._extract_input_data_by_key_list(
            input_data, variable_path, variable_properties, called_during_initialization
        )

        if variable_properties.get("nullable", False) and array_value is None:
            return True

        if not self._validate_array_container_properties(
            variable_path, variable_properties, array_value, properties_blob_key
        ):
            return False

        is_whole_array_acceptable = True
        for index, element in enumerate(array_value):
            is_element_acceptable = self._validate_input_by_type(
                variable_properties["properties"],
                variable_path + [index],
                input_data,
                eager_termination,
                properties_blob_key,
                elements_counter,
                called_during_initialization,
            )
            is_whole_array_acceptable = is_whole_array_acceptable and is_element_acceptable
            if not is_element_acceptable and eager_termination:
                return False
        return is_whole_array_acceptable

    def _object_type_validator(
        self,
        variable_path: List[str | int],
        variable_properties: Dict[str, Any],
        input_data: Dict[str, Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
    ) -> bool:
        """
        Validates an input data element of type object.

        Parameters
        ----------
        variable_path : List[str | int]
            The path to the variable being validated.
        variable_properties : Dict[str, Any]
            The metadata properties for the variable being validated.
        input_data : Dict[str, Any]
            The input data to be validated.
        eager_termination : bool
            If True, the process will be terminated upon finding invalid data.
        properties_blob_key : str
            The metadata properties for the data input file being checked.
        elements_counter : ElementsCounter
            A counter to keep track of the number of valid, invalid, and fixed elements.
        called_during_initialization: bool
            Boolean variable indicating whether the function is being called during initialization.

        Returns
        -------
        bool
            True if the input data element is valid or fixable, False otherwise.

        Notes
        -----
        This method will look for and delete any keys in the input data that do not have properties specified for them
        in the metadata properties.

        """
        info_map = {"class": self.__class__.__name__, "function": self._object_type_validator.__name__}

        object_value = self._extract_input_data_by_key_list(
            input_data, variable_path, variable_properties, called_during_initialization
        )
        variable_path_str = self._convert_variable_path_to_str(variable_path)
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )
        if not isinstance(object_value, dict):
            om.add_warning(
                "Validation: object is not a dictionary",
                f"Variable: '{variable_path_str}' is not an object but has type: {type(object_value)}. "
                f"{properties_violation_message}",
            )
            return False

        is_whole_object_acceptable = True
        for key in variable_properties.keys():
            if key in ["type", "description", "default"]:
                continue
            is_element_acceptable = self._validate_input_by_type(
                variable_properties[key],
                variable_path + [key],
                input_data,
                eager_termination,
                properties_blob_key,
                elements_counter,
                called_during_initialization,
            )
            is_whole_object_acceptable = is_whole_object_acceptable and is_element_acceptable
            if not is_element_acceptable and eager_termination:
                return False

        extraneous_keys = [key for key in object_value.keys() if key not in variable_properties.keys()]
        for key in extraneous_keys:
            om.add_warning(
                "Validation: object contains extraneous data",
                f"Variable: '{variable_path_str}' contains data at key '{key}' that is not specified in the metadata "
                f"properties. {properties_violation_message}",
                info_map,
            )
            del object_value[key]

        return is_whole_object_acceptable

    def _number_type_validator(
        self,
        variable_path: List[str | int],
        variable_properties: Dict[str, Any],
        input_data: Dict[str, Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
    ) -> bool:
        """Validates an input data number element."""
        input_data_value = self._extract_input_data_by_key_list(
            input_data, variable_path, variable_properties, called_during_initialization
        )

        if variable_properties.get("nullable", False) and input_data_value is None:
            return True

        variable_path_str = self._convert_variable_path_to_str(variable_path)

        info_map = {
            "class": self.__class__.__name__,
            "function": self._number_type_validator.__name__,
        }
        minimum_value = variable_properties.get("minimum")
        maximum_value = variable_properties.get("maximum")
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )

        if type(input_data_value) is not float and type(input_data_value) is not int:
            warning_string = "Validation: value is not a number"
            warning_message = (
                f"Variable: '{variable_path_str}' has value: {input_data_value}, is type: "
                f"{type(input_data_value)}. {properties_violation_message}"
            )
            om.add_warning(warning_string, warning_message, info_map)
            return False
        if minimum_value is not None:
            is_in_range = minimum_value <= input_data_value
            if not is_in_range:
                warning_name = "Validation: value less than minimum"
                warning_message = (
                    f"Variable: '{variable_path_str}' has value: {input_data_value}, less than minimum value: "
                    f"{minimum_value: .2f}. {properties_violation_message}"
                )
                om.add_warning(warning_name, warning_message, info_map)
                return False
        if maximum_value is not None:
            is_in_range = input_data_value <= maximum_value
            if not is_in_range:
                warning_name = "Validation: value greater than maximum"
                warning_string = (
                    f"Variable: '{variable_path_str}' has value: {input_data_value}, greater than maximum value: "
                    f"{maximum_value: .2f}. {properties_violation_message}"
                )
                om.add_warning(warning_name, warning_string, info_map)
                return False

        return True

    def _string_type_validator(
        self,
        variable_path: List[str | int],
        variable_properties: Dict[str, Any],
        input_data: Dict[str, Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
    ) -> bool:
        """Validates an input data string element."""
        input_data_value = self._extract_input_data_by_key_list(
            input_data, variable_path, variable_properties, called_during_initialization
        )

        if variable_properties.get("nullable", False) and input_data_value is None:
            return True

        variable_path_str = self._convert_variable_path_to_str(variable_path)
        info_map = {
            "class": self.__class__.__name__,
            "function": self._string_type_validator.__name__,
        }
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )

        if type(input_data_value) is not str:
            warning_name = "Validation: string variable is not a string"
            warning_message = (
                f"Variable: '{variable_path_str}' has value: {input_data_value}, is type: "
                f"{type(input_data_value)}. {properties_violation_message}"
            )
            om.add_warning(warning_name, warning_message, info_map)
            return False

        pattern_check = variable_properties.get("pattern")
        if pattern_check is not None:
            is_valid_string = bool(re.match(pattern_check, input_data_value))
            if not is_valid_string:
                warning_name = "Validation: string variable does not match pattern"
                warning_message = (
                    f"Variable: '{variable_path_str}' has value: '{input_data_value}', does not match pattern: "
                    f"{pattern_check}. {properties_violation_message}"
                )
                om.add_warning(warning_name, warning_message, info_map)
                return False

        minimum_length = variable_properties.get("minimum_length")
        maximum_length = variable_properties.get("maximum_length")
        if minimum_length is not None:
            is_valid_string = variable_properties["minimum_length"] <= len(input_data_value)
            if not is_valid_string:
                warning_name = "Validation: string length less than minimum"
                warning_message = (
                    f"Variable: '{variable_path_str}' has value: '{input_data_value}', length is less than "
                    f"minimum length: {minimum_length}. {properties_violation_message}"
                )
                om.add_warning(warning_name, warning_message, info_map)
                return False
        if maximum_length is not None:
            is_valid_string = len(input_data_value) <= variable_properties["maximum_length"]
            if not is_valid_string:
                warning_name = "Validation: string length greater than maximum"
                warning_message = (
                    f"Variable: '{variable_path_str}' has value: '{input_data_value}', length is greater than "
                    f"maximum length: {maximum_length}. {properties_violation_message}"
                )
                om.add_warning(warning_name, warning_message, info_map)
                return False

        return True

    def _bool_type_validator(
        self,
        variable_path: List[str | int],
        variable_properties: Dict[str, Any],
        input_data: Dict[str, Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
    ) -> bool:
        """Validates an input data bool element."""
        input_data_value = self._extract_input_data_by_key_list(
            input_data, variable_path, variable_properties, called_during_initialization
        )

        if variable_properties.get("nullable", False) and input_data_value is None:
            return True

        variable_path_str = self._convert_variable_path_to_str(variable_path)

        info_map = {"class": self.__class__.__name__, "function": self._bool_type_validator.__name__}
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )

        if type(input_data_value) is not bool:
            warning_name = "Validation: bool variable is not a bool"
            warning_message = (
                f"Variable: '{variable_path_str}' has value: '{input_data_value}', is type: "
                f"'{type(input_data_value)}'. {properties_violation_message}"
            )
            om.add_warning(warning_name, warning_message, info_map)
            return False

        return True

    def _extract_value_by_key_list(
        self, input_data: List[Any] | Dict[str, Any], variable_path: Sequence[str | int]
    ) -> Any:
        """
        Extracts a value from a nested list or dictionary using a list of keys (int or str).

        Parameters
        ----------
        input_data : List[Any] | Dict[str, Any]
            The input data containing the value to be extracted.
        variable_path : List[str | int]
            A list of keys to be used to extract the value from the input data.

        Returns
        -------
        Any
            The value extracted from the input data.

        Raises
        ------
        KeyError
            If the value cannot be extracted from the input data using the provided variable path.

        Examples
        --------
        >>> input_manager = InputManager()
        >>> example_data = {
        ...     "animal": {
        ...         "herd_information": {
        ...             "calf_num": 8,
        ...             "heiferI_num": 44,
        ...             "heiferII_num": 38,
        ...             "heiferIII_num_springers": 12
        ...         }
        ...     }
        ... }
        >>> var_path = ["animal", "herd_information", "calf_num"]
        >>> input_manager._extract_value_by_key_list(example_data, var_path)
        8

        >>> input_manager = InputManager()
        >>> example_data = {
        ...     "manure_management_scenarios": [
        ...         {
        ...             "bedding_type": "straw",
        ...             "manure_handler": "manual scraping"
        ...         },
        ...         {
        ...             "bedding_type": "sawdust",
        ...             "manure_handler": "flush system"
        ...         }
        ...     ]
        ... }
        >>> var_path = ["manure_management_scenarios", 0, "bedding_type"]
        >>> input_manager._extract_value_by_key_list(example_data, var_path)
        'straw'
        """

        for key in variable_path:
            if isinstance(input_data, list) and 0 <= int(key) < len(input_data):
                input_data = input_data[int(key)]
            elif isinstance(input_data, dict) and isinstance(key, str) and key in input_data:
                input_data = input_data[key]
            else:
                raise KeyError(f"There is an error at key {key} in the path {variable_path}")
        return input_data

    def _extract_input_data_by_key_list(
        self,
        input_data: List[Any] | Dict[str, Any],
        variable_path: Sequence[str | int],
        variable_properties: Dict[str, Any],
        called_during_initialization: bool,
    ) -> Any:
        """
        Extracts a value from the input data based on a specified path and handles missing data by calling
        InputManager._log_missing_data().

        Parameters
        ----------
        input_data : List[Any] | Dict[str, Any]
            The input data containing the value to be extracted.
        variable_path : List[str | int]
            A list of keys to be used to extract the value from the input data.
        variable_properties : Dict[str, Any]
            The metadata properties for the variable being validated.
        called_during_initialization: bool
            Boolean variable indicating whether the function is being called during initialization.

        Returns
        -------
        Any
            The value extracted from the input data if found.
            None if not found.

        Notes
        -----
        This function navigates through the given input data (which can be a list or a dictionary) following the path
        specified in `variable_path`. If the path leads to a value, it is returned.
        If a KeyError occurs during this process (i.e., a key or index is missing in the path), the function extracts
        the variable name by finding the last string element in the `variable_path` array and handles this missing data
        by calling InputManager._log_missing_data().
        """
        result = None
        try:
            result = self._extract_value_by_key_list(input_data, variable_path)
        except KeyError:
            var_name: str = [name for name in reversed(variable_path) if type(name) is str][0]
            self._log_missing_data(
                variable_properties=variable_properties,
                var_name=var_name,
                called_during_initialization=called_during_initialization,
            )
        return result

    def _convert_variable_path_to_str(self, variable_path: List[str | int]) -> str:
        """
        Converts a list of keys (int or str) into a string representation of the path to a variable.

        Parameters
        ----------
        variable_path : List[str | int]
            A list of keys to be used to extract the value from the input data.

        Returns
        -------
        str
            A string representation of the path to a variable.

        Examples
        --------
        >>> input_manager = InputManager()
        >>> var_path = ["animal", "herd_information", "calf_num"]
        >>> input_manager._convert_variable_path_to_str(var_path)
        'animal.herd_information.calf_num'

        >>> input_manager = InputManager()
        >>> var_path = ["manure_management_scenarios", 0, "bedding_type"]
        >>> input_manager._convert_variable_path_to_str(var_path)
        'manure_management_scenarios.[0].bedding_type'
        """

        formatted_path_elems = []
        for raw_path_elem in variable_path:
            if isinstance(raw_path_elem, int) or (isinstance(raw_path_elem, str) and raw_path_elem.isdigit()):
                formatted_path_elems.append(f"[{raw_path_elem}]")
            else:
                formatted_path_elems.append(f"{raw_path_elem}")
        return ".".join(formatted_path_elems)

    def _fix_data(
        self,
        variable_properties: Dict[str, Any],
        element_hierarchy: List[Union[str, int]],
        input_data: Dict[str, Any],
        properties_blob_key: str,
    ) -> bool:
        """
        Attempt to fix the invalid data.

        Parameters
        ----------
        variable_properties : dict[str, Any]
            The properties for the variable of interest.

        element_hierarchy: list
            A list indicating the path to reach the variable of interest in self.__metadata and self.__pool.

        input_data: dict[str, Any]
            A buffer dictionary that holds the input data for validation and fixing.

        properties_blob_key : str
            The metadata properties section keyword for the data input file being checked.

        Returns
        -------
        bool
            True if the data is fixed, False otherwise.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._fix_data.__name__,
        }

        variable_parent = reduce(lambda d, key: d[key], element_hierarchy[:-1], input_data)

        element_path = ".".join([str(element) for element in element_hierarchy])
        properties_violation_message = (
            f"Violates properties defined in metadata properties section '{properties_blob_key}'."
        )
        if "default" not in variable_properties.keys():
            error_message = (
                f"Variable: '{element_path}' has invalid value: {variable_parent[element_hierarchy[-1]]}"
                f", and cannot be changed to a default value. {properties_violation_message}"
            )
            om.add_error("Validation: invalid data not able to be fixed", error_message, info_map)
            return False

        if type(variable_parent) is list:
            original_invalid_value = variable_parent[element_hierarchy[-1]]
        else:
            original_invalid_value = variable_parent.get(element_hierarchy[-1])

        warning_message = (
            f"Variable: '{element_path}' has value: {original_invalid_value}. {properties_violation_message}"
        )
        om.add_warning("Validation: invalid data found", warning_message, info_map)

        variable_parent[element_hierarchy[-1]] = variable_properties["default"]

        warning_message = (
            f"Invalid data fixed: '{element_path}' value changed from {original_invalid_value} to "
            f"{variable_properties['default']}. Fix enabled by default value specified in "
            f"'{properties_blob_key}'."
        )
        om.add_warning("Validation: data fixed", warning_message, info_map)
        return True

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
            data_value = self._extract_value_by_key_list(self.__pool, element_hierarchy)
            timestamp = Utility.get_timestamp(include_millis=True)
            self.__get_data_logs_pool[timestamp] = f"InputManager.get_data() called for {element_hierarchy}."
            return deepcopy(data_value)
        except KeyError as key_error:
            om.add_error("Validation: data not found", str(key_error), info_map)

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
            self._extract_value_by_key_list(self.__pool, variable_path)
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

            om.add_error(
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
            om.add_error(error_name, error_message, info_map)
            return data_keys

        data_keys = [key for key, data in input_data.items() if data.get("properties") == target_properties]

        return data_keys

    def flush_pool(self) -> None:
        """
        Clear the variable pool.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.flush_pool.__name__,
        }
        self.__pool = {}
        om.add_log("Clear variable pool", "The pool is emptied.", info_map)

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
            om.add_error(
                "No metadata loaded",
                "No metadata is loaded to the InputManager.",
                info_map,
            )
            raise ValueError("No metadata loaded.")
        if properties_blob_key not in self.__metadata["properties"]:
            om.add_error(
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

    def _set_nested_value(
        self, nested_dict: Dict[str, Any], element_hierarchy: List[str], value: Any
    ) -> Dict[str, Any]:
        """
        Sets a given value within a nested dictionary structure at a specified hierarchical level and returns the
        updated dictionary.

        Notes
        -----
        This function iteratively traverses through the levels of a nested dictionary, guided by a list of keys
        (element_hierarchy). At each level, it checks for the existence of the key. If a key is missing, a new nested
        dictionary is created at that key. The function sets the given value at the final key in the hierarchy.

        While this function modifies the input dictionary in place, it also returns the modified dictionary for
        convenience and chaining operations.

        Be cautious of the in-place modification of the input dictionary, which may lead to unintended side effects.

        In other words, this function operates through the side effect of altering the state of `nested_dict` outside
        its local scope. This behavior of in-place modification of the input dictionary introduces potential unintended
        changes.

        Parameters
        ----------
        nested_dict : Dict[str, Any]
            The nested dictionary to be updated. This should be the top-level dictionary if the hierarchy spans multiple
            levels.
        element_hierarchy : List[str]
            A list of strings representing the keys that define the path through the nested dictionary to the location
            where the value should be set. Each element in the list corresponds to one level in the nested structure.
        value : Any
            The value to be set at the specified location within the nested dictionary structure.

        Returns
        -------
        Dict[str, Any]
            The updated nested dictionary after setting the specified value.

        Examples
        --------
        >>> nested_dictionary = {'a': {'b': {'c': 1}}}
        >>> updated_dict = self._set_nested_value(nested_dictionary, ['a', 'b', 'd'], 2)
        >>> print(updated_dict)
        {'a': {'b': {'c': 1, 'd': 2}}}

        >>> nested_dictionary = {'a': {'b': {'c': 1}}}
        >>> updated_dict = self._set_nested_value(nested_dictionary, ['a', 'b', 'c'], 2)
        >>> print(updated_dict)
        {'a': {'b': {'c': 2}}}
        """
        current_dict_level = nested_dict
        for key in element_hierarchy[:-1]:
            if key not in current_dict_level.keys():
                current_dict_level[key] = {}
            current_dict_level = current_dict_level[key]

        current_dict_level[element_hierarchy[-1]] = value
        return nested_dict

    def _add_variable_to_pool(  # noqa: C901
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
        PermissionError
            If eager_termination is True and the variable is not modifiable during runtime.
        ValueError
            If eager_termination is True and the variable failed validation.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._add_variable_to_pool.__name__,
        }
        validated_data = {}
        elements_counter = ElementsCounter()

        element_hierarchy, data, metadata_properties = self._prepare_data(
            variable_name, input_data, properties_blob_key
        )

        self._check_modifiability(variable_name, metadata_properties, eager_termination, info_map)

        validated_data = self._validate_data(
            data, metadata_properties, eager_termination, properties_blob_key, elements_counter
        )

        if validated_data:
            self._add_to_pool(variable_name, validated_data, info_map)
            elements_counter += elements_counter

        if elements_counter.invalid_elements > 0:
            om.add_error(
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
        self, variable_name: str, input_data: dict, properties_blob_key: str
    ) -> Tuple[List[str], Dict[str, Any], Dict[str, Any]]:
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
        if len(element_hierarchy) > 1:
            data = self._set_nested_value({}, element_hierarchy[1:], input_data)
            element_hierarchy = element_hierarchy if isinstance(input_data, Dict) else element_hierarchy[:-1]
            metadata_properties = reduce(
                lambda d, k: d[k], element_hierarchy[1:], self.__metadata["properties"][properties_blob_key]
            )
        else:
            data = input_data
            metadata_properties = self.__metadata["properties"][properties_blob_key]

        return element_hierarchy, data, metadata_properties

    def _check_modifiability(
        self, variable_name: str, metadata_properties: dict, eager_termination: bool, info_map: dict
    ) -> None:
        """
        Check if the variable is modifiable during runtime.
        """
        is_modifiable_during_runtime = self._is_modifiable_during_runtime(
            variable_name=variable_name, variable_properties=metadata_properties
        )
        if not is_modifiable_during_runtime and eager_termination:
            om.add_error("IM Runtime Modification", f"{variable_name} is not modifiable during runtime.", info_map)
            raise PermissionError(f"IM Runtime Modification Error: {variable_name} is not modifiable during runtime.")
        elif not is_modifiable_during_runtime:
            om.add_warning("IM Runtime Modification", f"{variable_name} is not modifiable during runtime.", info_map)

    def _validate_data(
        self,
        data: dict,
        metadata_properties: dict,
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
    ) -> dict:
        """
        Validate input data based on metadata properties.
        """
        validated_data = {}
        variable_properties_to_ignore = ["type", "description", "modifiability"]

        for metadata_property in metadata_properties.keys():
            if metadata_property in variable_properties_to_ignore:
                continue
            variable_properties = metadata_properties[metadata_property]
            is_element_acceptable = self._validate_input_by_type(
                variable_path=[metadata_property],
                variable_properties=variable_properties,
                input_data=data,
                eager_termination=eager_termination,
                properties_blob_key=properties_blob_key,
                elements_counter=elements_counter,
                called_during_initialization=False,
            )

            if is_element_acceptable:
                validated_data[metadata_property] = data[metadata_property]

        return validated_data

    def _add_to_pool(self, variable_name: str, validated_data: dict, info_map: dict) -> None:
        """
        Add validated data to the pool.
        """
        if variable_name in self.__pool.keys():
            om.add_warning(
                "Overwriting existing variable",
                f"Variable {variable_name} already exists in InputManager pool, overwriting the old value.",
                info_map,
            )
        self.__pool[variable_name] = validated_data

    def add_dict_variable_to_pool(
        self,
        variable_name: str,
        data: Dict[str, Any],
        properties_blob_key: str,
        eager_termination: bool,
    ) -> bool:
        """
        Adds a dictionary variable to the InputManager's pool after validating it against metadata.

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
            "function": self.add_dict_variable_to_pool.__name__,
        }
        if not (isinstance(data, Dict)):
            om.add_error(
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

    def add_tabular_variable_to_pool(
        self,
        variable_name: str,
        data: Dict[str, List[Any]] | List[Any],
        properties_blob_key: str,
        eager_termination: bool,
    ) -> bool:
        """
        Adds a tabular variable to the InputManager's pool after validating it against metadata.

        Notes
        -----
        This function takes in a variable along with its name and a key to access its validation metadata.
        It validates the data against the provided metadata and adds the data to the InputManager pool if it is valid.

        Parameters
        ----------
        variable_name: str
            The name of the variable to be added.
        data : Dict[str, List[Any]] | List[Any]
            The data of the tabular variable, structured as a dictionary of lists or a list.
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
        -------
        TypeError
            If `data` is not the expected type of Dict[str, List[Any]] | List[Any].

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.add_tabular_variable_to_pool.__name__,
        }
        if not (isinstance(data, Dict) or isinstance(data, List)):
            om.add_error(
                "Incorrect variable type",
                f"Variable {variable_name} has type {type(data)}, does not match "
                f"the expected type of `Dict[str, List[Any]] | List[Any]`.",
                info_map,
            )
            raise TypeError("Incorrect variable type. Expected types: `data: Dict[str, List[Any]] | List[Any]`.")

        data = {variable_name: data} if isinstance(data, List) else data

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
        file_name = om.generate_file_name(base_name="InputManager_get_data_log", extension="json")
        file_path = path / file_name
        om.create_directory(path)
        om.dict_to_file_json(self.__get_data_logs_pool, file_path)

    def _validate_metadata(self) -> None:
        """Checks that top-level metadata has valid and required keys and values."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self._validate_metadata.__name__,
        }
        metadata_files = self.__metadata[ADDRESS_TO_INPUTS]
        required_keys = {"path", "type", "properties"}
        optional_keys = {"title", "description"}
        valid_keys = required_keys | optional_keys
        for key, data in metadata_files.items():
            if missing_keys := (required_keys - data.keys()):
                om.add_error(
                    "Metadata Validation", f"Missing required keys '{list(missing_keys)}' in '{key}'", info_map
                )
                raise ValueError
            if invalid_keys := (data.keys() - valid_keys):
                om.add_error("Metadata Validation", f"Invalid keys '{list(invalid_keys)}' in '{key}'", info_map)
                raise ValueError

            if data["type"] not in VALID_INPUT_TYPES:
                om.add_error(
                    "Metadata Validation",
                    f"Invalid type '{data['type']}' in '{key}'. Expected one option from {VALID_INPUT_TYPES}",
                    info_map,
                )
                raise ValueError

            if not os.path.isfile(data["path"]):
                om.add_error("Metadata Validation", f"Invalid path '{data['path']}' in '{key}'", info_map)
                raise ValueError

            if data["properties"] is None or data["properties"] == "":
                om.add_error("Metadata Validation", f"Properties section empty or None in '{key}'", info_map)
                raise ValueError

        om.add_log("Metadata Validation", "Top level metadata is valid.", info_map)

    def _validate_properties(self) -> None:
        """Iteratively traverses the metadata properties to check the max depth and routes
        properties to be validated by type.

        Raises
        ------
        ValueError
            - If the depth of the metadata exceeds the metadata_depth_limit.
            - If the properties' 'type' value is neither in the type_to_validator_map keys,
            nor is None.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._validate_properties.__name__,
        }

        stack: list[tuple[dict[str, Any], int, list[str]]] = [(self.__metadata["properties"], 0, [])]
        current_max_depth: int = 0
        deepest_path: list[str] = []

        type_to_validator_map: Dict[str, Callable[[list[str], dict[str, Any]], None]] = {
            "number": self._metadata_number_validator,
            "array": self._metadata_array_validator,
            "bool": self._metadata_bool_validator,
            "string": self._metadata_string_validator,
            "object": self._metadata_object_validator,
        }
        while stack:
            current_obj, depth, path = stack.pop()

            if depth > self.metadata_depth_limit:
                om.add_error(
                    "Max metadata depth exceeded.",
                    f"Metadata depth exceeds maximum allowed depth of {self.metadata_depth_limit} at path {path}",
                    info_map,
                )
                raise ValueError(
                    f"Metadata depth exceeds maximum allowed depth of {self.metadata_depth_limit} at path {path}"
                )

            if depth > current_max_depth:
                current_max_depth = depth
                deepest_path = path

            if isinstance(current_obj, dict):
                for key, value in current_obj.items():
                    if isinstance(value, dict):
                        stack.append((value, depth + 1, path + [key]))
                        value_type = value.get("type")
                        if value_type in type_to_validator_map:
                            type_to_validator_map[value_type](path + [key], value)
                        else:
                            if value_type is not None:
                                om.add_error(
                                    "Properties value type error",
                                    f"'type' value not in {type_to_validator_map.keys()}",
                                    info_map,
                                )
                                raise ValueError(f"Properties 'type' value not in {list(type_to_validator_map.keys())}")

        om.add_log("Metadata properties depth", f"Max depth of metadata properties is {current_max_depth}", info_map)
        om.add_log("Metadata properties path", f"Deepest path of metadata properties is {deepest_path}", info_map)

    def _metadata_number_validator(self, key_path: list[str], value: dict[str, Any]) -> None:
        """Validates number type properties in metadata."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self._metadata_number_validator.__name__,
        }
        required_number_property_keys = {"type"}
        optional_number_property_keys = {"description", "minimum", "maximum", "default", "nullable"}
        self._validate_metadata_properties_keys(
            required_number_property_keys, optional_number_property_keys, value, key_path
        )
        default = value.get("default", "No default")
        has_no_default = default == "No default"
        nullable = value.get("nullable", False)
        if default is None and not nullable:
            om.add_error(
                "Invalid metadata default number value.",
                f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'.",
                info_map,
            )
            raise ValueError(f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'.")
        if default is not None:
            if not isinstance(default, (int, float)) and not has_no_default:
                om.add_error(
                    "Invalid metadata default number value.",
                    f"Invalid 'default' for '{key_path}': Expected a number but got {type(default)}.",
                    info_map,
                )
                raise ValueError(f"Invalid 'default' for '{key_path}': Expected a number but got {type(default)}.")
        minimum = value.get("minimum")
        maximum = value.get("maximum")
        if minimum is not None and not isinstance(minimum, (int, float)):
            om.add_error(
                "Invalid metadata number properties minimum.",
                f"Invalid 'minimum' for '{key_path}': Expected a number but got {type(minimum)}.",
                info_map,
            )
            raise ValueError(f"Invalid 'minimum' for '{key_path}': " f"Expected a number but got {type(minimum)}.")
        if maximum is not None and not isinstance(maximum, (int, float)):
            om.add_error(
                "Invalid metadata number properties maximum.",
                f"Invalid 'maximum' for '{key_path}': Expected a number but got {type(maximum)}.",
                info_map,
            )
            raise ValueError(f"Invalid 'maximum' for '{key_path}': Expected a number but got {type(maximum)}.")
        if maximum is not None and minimum is not None and maximum < minimum:
            om.add_error(
                "Invalid range of acceptable numbers.",
                f"Invalid 'range' for key '{key_path}': 'minimum' value {minimum} is "
                f"greater than 'maximum' value {maximum}",
                info_map,
            )
            raise ValueError(
                f"Invalid 'range' for key '{key_path}': 'minimum' value {minimum} is "
                f"greater than 'maximum' value {maximum}"
            )
        if default is not None and not has_no_default:
            if minimum is not None and default < minimum:
                om.add_error(
                    "Invalid metadata default.",
                    f"Invalid 'default' for '{key_path}': 'default' {default} is less than 'minimum' {minimum}",
                    info_map,
                )
                raise ValueError(
                    f"Invalid 'default' for '{key_path}': 'default' {default} is " f"less than 'minimum' {minimum}"
                )
            if maximum is not None and default > maximum:
                om.add_error(
                    "Invalid metadata default.",
                    f"Invalid 'default' for '{key_path}': 'default' {default} is greater than 'maximum' {maximum}",
                    info_map,
                )
                raise ValueError(
                    f"Invalid 'default' for '{key_path}': 'default' {default} is " f"greater than 'maximum' {maximum}"
                )

    def _metadata_string_validator(self, key_path: list[str], value: dict[str, Any]) -> None:
        """Validates string type properties in metadata."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self._metadata_string_validator.__name__,
        }
        required_str_property_keys = {"type"}
        optional_str_property_keys = {"description", "pattern", "default", "nullable"}
        self._validate_metadata_properties_keys(required_str_property_keys, optional_str_property_keys, value, key_path)
        default = value.get("default", "No default")
        has_no_default = default == "No default"
        nullable = value.get("nullable", False)
        if default is None and not nullable:
            om.add_error(
                "Invalid metadata default string value.",
                f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'",
                info_map,
            )
            raise ValueError(f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'")
        if default is not None and not has_no_default:
            if not isinstance(default, str):
                om.add_error(
                    "Invalid metadata default string value.",
                    f"Invalid 'default' for '{key_path}': Expected a string but got {type(default)}",
                    info_map,
                )
                raise ValueError(f"Invalid 'default' for '{key_path}': Expected a string but got {type(default)}")
        pattern = value.get("pattern")
        if pattern is not None and not isinstance(pattern, str):
            om.add_error(
                "Invalid metadata string properties pattern.",
                f"Invalid 'pattern' for '{key_path}': Expected a string but got {type(pattern)}",
                info_map,
            )
            raise ValueError(f"Invalid 'pattern' for '{key_path}': Expected a string but got {type(pattern)}")
        try:
            if pattern is not None:
                re.compile(pattern)
        except re.error:
            om.add_error(
                "Invalid metadata string properties pattern.",
                f"Invalid 'pattern' for '{key_path}': 'pattern' value '{pattern}' is not " "a valid regex pattern.",
                info_map,
            )
            raise ValueError(
                f"Invalid 'pattern' for '{key_path}': 'pattern' value '{pattern}' is not " "a valid regex pattern."
            )
        if default != "" and default is not None and not has_no_default:
            if pattern is not None and not re.match(pattern, default):
                om.add_error(
                    "Invalid metadata default string value.",
                    f"Invalid 'default' for '{key_path}': 'default' value '{default}' does not "
                    f"match pattern {pattern}",
                    info_map,
                )
                raise ValueError(
                    f"Invalid 'default' for '{key_path}': 'default' value '{default}' does not "
                    f"match pattern {pattern}"
                )

    def _metadata_bool_validator(self, key_path: list[str], value: dict[str, Any]) -> None:
        """Validates bool type properties in metadata."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self._metadata_bool_validator.__name__,
        }
        required_bool_property_keys = {"type"}
        optional_bool_property_keys = {"description", "default", "nullable"}
        self._validate_metadata_properties_keys(
            required_bool_property_keys, optional_bool_property_keys, value, key_path
        )
        default = value.get("default", "No default")
        has_no_default = default == "No default"
        nullable = value.get("nullable", False)
        if default is None and not nullable:
            om.add_error(
                "Invalid metadata default bool value.",
                f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'",
                info_map,
            )
            raise ValueError(f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'")
        if default is not None and not isinstance(default, bool) and not has_no_default:
            om.add_error(
                "Invalid metadata default bool value.",
                f"Invalid 'default' for '{key_path}': Expected a bool but got {type(default)}",
                info_map,
            )
            raise ValueError(f"Invalid 'default' for key {key_path}: Expected a bool but got {type(default)}")

    def _metadata_array_validator(self, key_path: list[str], value: dict[str, Any]) -> None:
        """Validates array type properties in metadata."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self._metadata_array_validator.__name__,
        }
        required_array_property_keys = {"type", "properties"}
        optional_array_property_keys = {"description", "minimum_length", "maximum_length", "nullable"}
        self._validate_metadata_properties_keys(
            required_array_property_keys, optional_array_property_keys, value, key_path
        )
        minimum_length = value.get("minimum_length")
        maximum_length = value.get("maximum_length")
        if minimum_length is not None and not isinstance(minimum_length, (int, float)):
            om.add_error(
                "Invalid metadata default array minimum length.",
                f"Invalid 'minimum_length' for '{key_path}': Expected a number but got {type(minimum_length)}",
                info_map,
            )
            raise ValueError(
                f"Invalid 'minimum_length' for '{key_path}': " f"Expected a number but got {type(minimum_length)}"
            )
        if maximum_length is not None and not isinstance(maximum_length, (int, float)):
            om.add_error(
                "Invalid metadata default array maximum length.",
                f"Invalid 'maximum_length' for '{key_path}': Expected a number but got {type(maximum_length)}",
                info_map,
            )
            raise ValueError(
                f"Invalid 'maximum_length' for '{key_path}': " f"Expected a number but got {type(maximum_length)}"
            )
        if maximum_length is not None and minimum_length is not None and maximum_length < minimum_length:
            om.add_error(
                "Invalid metadata array length range.",
                f"Invalid length 'range' for key '{key_path}': 'minimum_length' value {minimum_length} is "
                f"greater than 'maximum_length' value {maximum_length}",
                info_map,
            )
            raise ValueError(
                f"Invalid length 'range' for key '{key_path}': 'minimum_length' value {minimum_length} is "
                f"greater than 'maximum_length' value {maximum_length}"
            )

    def _metadata_object_validator(self, key_path: list[str], value: dict[str, Any]) -> None:
        """Validates object type properties in metadata."""
        required_object_property_keys = {"type"}
        optional_object_property_keys = {"description"}
        self._validate_metadata_properties_keys(
            required_object_property_keys, optional_object_property_keys, value, key_path
        )

    def _validate_metadata_properties_keys(
        self,
        required_properties_keys: set[str],
        optional_properties_keys: set[str],
        properties: dict[str, Any],
        path: list[str],
    ) -> None:
        """Validates that keys in the metadata properties sections."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self._validate_metadata_properties_keys.__name__,
        }
        if missing_required_keys := required_properties_keys - properties.keys():
            om.add_error(
                "Metadata Validation",
                f"Missing required keys {sorted(missing_required_keys)} for {path}. Required"
                f" keys are {sorted(required_properties_keys)}.",
                info_map,
            )
            raise ValueError(
                f"Missing required keys {sorted(missing_required_keys)} for {path}. Required"
                f" keys are {sorted(required_properties_keys)}."
            )
        property_type = properties.get("type", "Unknown type")
        valid_properties_keys = required_properties_keys.union(optional_properties_keys)
        if property_type == "object":
            if not (set(properties.keys()) - valid_properties_keys):
                om.add_error(
                    "Metadata Validation",
                    f"No unique keys for {path}. At least one unique key is expected.",
                    info_map,
                )
                raise ValueError(f"No unique keys for {path}. At least one unique key is expected.")
            return
        if invalid_keys := set(properties.keys()) - valid_properties_keys:
            om.add_error(
                "Metadata Validation",
                f"Invalid keys {sorted(invalid_keys)} in {property_type} for {path}. Valid"
                f" keys are {sorted(valid_properties_keys)}.",
                info_map,
            )
            raise ValueError(
                f"Invalid keys {sorted(invalid_keys)} in {property_type} for {path}. Valid"
                f" keys are {sorted(valid_properties_keys)}."
            )

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
        path_to_save = output_dir / om.generate_file_name("InputManager_metadata_properties", extension="csv")
        om.add_log("CSV save attempt.", f"Attempting to save metadata properties as CSV to {path_to_save}", info_map)
        try:
            om.create_directory(output_dir)
            df.to_csv(path_to_save, index=False)
            om.add_log("Save CSV success.", f"Successfully saved to {path_to_save}.", info_map)
        except FileNotFoundError as fnfe:
            om.add_error("Save CSV failure.", f"Unable to save to {path_to_save} because of {fnfe}.", info_map)
            raise fnfe
        except PermissionError as pe:
            om.add_error("Save CSV failure.", f"Unable to save to {path_to_save} because of {pe}.", info_map)
            raise pe
        except OSError as e:
            om.add_error("Save CSV failure.", f"Unable to save to {path_to_save} because of {e}.", info_map)
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
        om.create_directory(output_directory)
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
            om.add_log("Save metadata diff try", f"Attempting to save to {file_name}", info_map)
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

            om.add_log("Save metadata diff successful", f"Successfully saved to {file_name}", info_map)

        except PermissionError:
            om.add_error(
                "Permission error in saving file",
                f"Permission denied when trying to write to {file_name}.txt.",
                info_map,
            )
            raise
        except OSError as e:
            om.add_error(
                "Unexpected error in saving file",
                f"An unexpected OS error occurred: {e}",
                info_map,
            )
            raise


class ElementState(Enum):
    """
    An enumeration of the states an input data element can be in during validation. An element cannot
    be in more than one state at a time.

    Attributes
    ----------
    VALID : int
        The element is valid.
    INVALID : int
        The element is invalid and cannot be fixed.
    FIXED : int
        The element is invalid initially but has been fixed.
    """

    VALID = "valid"
    INVALID = "invalid"
    FIXED = "fixed"


class ElementsCounter:
    """
    A class to keep track of the number of elements in each state during validation.

    Attributes
    ----------
    valid_elements : int
        The number of valid elements.
    invalid_elements : int
        The number of invalid elements.
    fixed_elements : int
        The number of fixed elements.
    """

    def __init__(self) -> None:
        self.valid_elements = 0
        self.invalid_elements = 0
        self.fixed_elements = 0

    def update(self, state: ElementState, value: int) -> None:
        """
        Updates the count of elements in a given state.

        Parameters
        ----------
        state : ElementState
            The state of the element.
        value : int
            The value by which the count should be updated.

        Raises
        ------
        ValueError
            If the state is not one of the valid states.
        """
        if state == ElementState.VALID:
            self.valid_elements += value
        elif state == ElementState.INVALID:
            self.invalid_elements += value
        elif state == ElementState.FIXED:
            self.fixed_elements += value
        else:
            raise ValueError(f"Invalid state: {state}")

    def increment(self, state: ElementState) -> None:
        """
        Increments the count of elements in a given state by one.

        Parameters
        ----------
        state : ElementState
            The state of the element.
        """

        self.update(state, 1)

    def reset(self) -> None:
        """
        Resets the counts of all element states to zero.
        """

        self.valid_elements = 0
        self.invalid_elements = 0
        self.fixed_elements = 0

    def total_elements(self) -> int:
        """
        Returns the total number of elements by adding the counts of valid, invalid, and fixed elements.
        """
        return self.valid_elements + self.invalid_elements + self.fixed_elements

    def __str__(self) -> str:
        """
        Returns a string representation of the ElementsCounter object.
        """

        return str(
            {
                "valid_elements": self.valid_elements,
                "invalid_elements": self.invalid_elements,
                "fixed_elements": self.fixed_elements,
                "total_elements": self.total_elements(),
            }
        )

    def __add__(self, other: "ElementsCounter") -> "ElementsCounter":
        """
        Adds the counts of two ElementsCounter objects together.

        Parameters
        ----------
        other : ElementsCounter
            The other ElementsCounter object to be added.

        Returns
        -------
        ElementsCounter
            A new ElementsCounter object with the counts of the two objects added together.
        """

        new_counter = ElementsCounter()
        new_counter.valid_elements = self.valid_elements + other.valid_elements
        new_counter.invalid_elements = self.invalid_elements + other.invalid_elements
        new_counter.fixed_elements = self.fixed_elements + other.fixed_elements
        return new_counter
