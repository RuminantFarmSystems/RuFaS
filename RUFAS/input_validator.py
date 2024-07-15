import os
from enum import Enum
import re
from functools import reduce
from typing import Dict, Any, Callable, List, Union, Sequence

from RUFAS.input_manager import InputManager, Modifiability
from RUFAS.output_manager import OutputManager

"""
Set enumerating the input data types that the Input Manager will attempt to fix while validating input data.
"""
FIXABLE_INPUT_DATA_TYPES: set[str] = {"string", "number", "bool"}

"""
Set enumerating the input data formats the Input Manager can accept.
"""
VALID_INPUT_TYPES: set[str] = {"json", "csv"}

ADDRESS_TO_INPUTS = "files"


class InputValidator:

    @staticmethod
    def _validate_properties(metadata: Dict[str, Any], metadata_depth_limit: int) -> None:
        """Iteratively traverses the metadata properties to check the max depth and routes
        properties to be validated by type.

        Raises
        ------
        ValueError
            - If the depth of the metadata exceeds the metadata_depth_limit.
            - If the properties' 'type' value is neither in the type_to_validator_map keys,
            nor is None.
        """
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._validate_properties.__name__,
        }

        stack: list[tuple[dict[str, Any], int, list[str]]] = [(metadata["properties"], 0, [])]
        current_max_depth: int = 0
        deepest_path: list[str] = []

        type_to_validator_map: Dict[str, Callable[[list[str], dict[str, Any]], None]] = {
            "number": InputValidator._metadata_number_validator,
            "array": InputValidator._metadata_array_validator,
            "bool": InputValidator._metadata_bool_validator,
            "string": InputValidator._metadata_string_validator,
            "object": InputValidator._metadata_object_validator,
        }
        while stack:
            current_obj, depth, path = stack.pop()

            if depth > metadata_depth_limit:
                om.add_error(
                    "Max metadata depth exceeded.",
                    f"Metadata depth exceeds maximum allowed depth of {metadata_depth_limit} at path {path}",
                    info_map,
                )
                raise ValueError(
                    f"Metadata depth exceeds maximum allowed depth of {metadata_depth_limit} at path {path}"
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

    @staticmethod
    def _validate_metadata_properties_keys(
        required_properties_keys: set[str],
        optional_properties_keys: set[str],
        properties: dict[str, Any],
        path: list[str],
    ) -> None:
        """Validates that keys in the metadata properties sections."""
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._validate_metadata_properties_keys.__name__,
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

    @staticmethod
    def _metadata_number_validator(key_path: list[str], value: dict[str, Any]) -> None:
        """Validates number type properties in metadata."""
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._metadata_number_validator.__name__,
        }
        required_number_property_keys = {"type"}
        optional_number_property_keys = {"description", "minimum", "maximum", "default", "nullable"}
        InputValidator._validate_metadata_properties_keys(
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

    @staticmethod
    def _metadata_string_validator(key_path: list[str], value: dict[str, Any]) -> None:
        """Validates string type properties in metadata."""
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._metadata_string_validator.__name__,
        }
        required_str_property_keys = {"type"}
        optional_str_property_keys = {"description", "pattern", "default", "nullable"}
        InputValidator._validate_metadata_properties_keys(
            required_str_property_keys, optional_str_property_keys, value, key_path
        )
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

    @staticmethod
    def _metadata_bool_validator(key_path: list[str], value: dict[str, Any]) -> None:
        """Validates bool type properties in metadata."""
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._metadata_bool_validator.__name__,
        }
        required_bool_property_keys = {"type"}
        optional_bool_property_keys = {"description", "default", "nullable"}
        InputValidator._validate_metadata_properties_keys(
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

    @staticmethod
    def _metadata_array_validator(key_path: list[str], value: dict[str, Any]) -> None:
        """Validates array type properties in metadata."""
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._metadata_array_validator.__name__,
        }
        required_array_property_keys = {"type", "properties"}
        optional_array_property_keys = {"description", "minimum_length", "maximum_length", "nullable"}
        InputValidator._validate_metadata_properties_keys(
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

    @staticmethod
    def _metadata_object_validator(key_path: list[str], value: dict[str, Any]) -> None:
        """Validates object type properties in metadata."""
        required_object_property_keys = {"type"}
        optional_object_property_keys = {"description"}
        InputValidator._validate_metadata_properties_keys(
            required_object_property_keys, optional_object_property_keys, value, key_path
        )

    @staticmethod
    def _validate_metadata(metadata: Dict[str, Any]) -> None:
        """Checks that top-level metadata has valid and required keys and values."""
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._validate_metadata.__name__,
        }
        metadata_files = metadata[ADDRESS_TO_INPUTS]
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

    # Validate input by type related
    @staticmethod
    def _validate_input_by_type(
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
            "array": InputValidator._array_type_validator,
            "object": InputValidator._object_type_validator,
            "string": InputValidator._string_type_validator,
            "number": InputValidator._number_type_validator,
            "bool": InputValidator._bool_type_validator,
        }

        if data_type not in type_to_validator_map:
            raise ValueError(
                f"The metadata type of the element '{InputManager.convert_variable_path_to_str(variable_path)}' "
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
        is_fixed = InputValidator._fix_data(variable_properties, variable_path, input_data, properties_blob_key)
        if is_fixed:
            elements_counter.increment(ElementState.FIXED)
            return True
        elements_counter.increment(ElementState.INVALID)
        return False

    @staticmethod
    def _validate_array_container_properties(
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
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._validate_array_container_properties.__name__,
        }
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )
        variable_path_str = InputManager.convert_variable_path_to_str(variable_path)
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

    @staticmethod
    def _object_type_validator(
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
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._object_type_validator.__name__,
        }

        object_value = InputValidator._extract_input_data_by_key_list(
            input_data, variable_path, variable_properties, called_during_initialization
        )
        variable_path_str = InputManager.convert_variable_path_to_str(variable_path)
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
            is_element_acceptable = InputValidator._validate_input_by_type(
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

    @staticmethod
    def _number_type_validator(
        variable_path: List[str | int],
        variable_properties: Dict[str, Any],
        input_data: Dict[str, Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
    ) -> bool:
        """Validates an input data number element."""
        om = OutputManager()
        input_data_value = InputValidator._extract_input_data_by_key_list(
            input_data, variable_path, variable_properties, called_during_initialization
        )

        if variable_properties.get("nullable", False) and input_data_value is None:
            return True

        variable_path_str = InputManager.convert_variable_path_to_str(variable_path)

        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._number_type_validator.__name__,
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

    @staticmethod
    def _string_type_validator(
        variable_path: List[str | int],
        variable_properties: Dict[str, Any],
        input_data: Dict[str, Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
    ) -> bool:
        """Validates an input data string element."""
        om = OutputManager()
        input_data_value = InputValidator._extract_input_data_by_key_list(
            input_data, variable_path, variable_properties, called_during_initialization
        )

        if variable_properties.get("nullable", False) and input_data_value is None:
            return True

        variable_path_str = InputManager.convert_variable_path_to_str(variable_path)
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._string_type_validator.__name__,
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

    @staticmethod
    def _bool_type_validator(
        variable_path: List[str | int],
        variable_properties: Dict[str, Any],
        input_data: Dict[str, Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
    ) -> bool:
        """Validates an input data bool element."""
        om = OutputManager()
        input_data_value = InputValidator._extract_input_data_by_key_list(
            input_data, variable_path, variable_properties, called_during_initialization
        )

        if variable_properties.get("nullable", False) and input_data_value is None:
            return True

        variable_path_str = InputManager.convert_variable_path_to_str(variable_path)

        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._bool_type_validator.__name__,
        }
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

    @staticmethod
    def _fix_data(
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
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._fix_data.__name__,
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

    @staticmethod
    def _extract_value_by_key_list(input_data: List[Any] | Dict[str, Any], variable_path: Sequence[str | int]) -> Any:
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
        >>> InputValidator._extract_value_by_key_list(example_data, var_path)
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
        >>> InputValidator._extract_value_by_key_list(example_data, var_path)
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

    @staticmethod
    def _extract_input_data_by_key_list(
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
            result = InputValidator._extract_value_by_key_list(input_data, variable_path)
        except KeyError:
            var_name: str = [name for name in reversed(variable_path) if type(name) is str][0]
            InputValidator._log_missing_data(
                variable_properties=variable_properties,
                var_name=var_name,
                called_during_initialization=called_during_initialization,
            )
        return result

    @staticmethod
    def _log_missing_data(
        variable_properties: Dict[str, Any], var_name: str, called_during_initialization: bool
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
        om = OutputManager()
        info_map = {"class": InputValidator.__class__.__name__, "function": InputValidator._log_missing_data.__name__}
        if not called_during_initialization:
            error_msg = (f"Key {var_name} not found in data. A value is required to update variable during runtime.",)
            om.add_error("Missing required data", error_msg, info_map)
            raise KeyError(error_msg)

        if InputValidator._is_input_required_upon_initialization(
            variable_name=var_name, variable_properties=variable_properties
        ):
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

    @staticmethod
    def _is_input_required_upon_initialization(variable_name: str, variable_properties: Dict[str, Any]) -> bool:
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
        variable_modifiability = InputValidator._get_variable_modifiability(
            variable_name=variable_name, variable_properties=variable_properties
        )
        return variable_modifiability in Modifiability.get_required_during_initialization()

    @staticmethod
    def _get_variable_modifiability(variable_name: str, variable_properties: Dict[str, Any]) -> Modifiability:
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
        om = OutputManager()
        info_map = {
            "class": InputValidator.__class__.__name__,
            "function": InputValidator._get_variable_modifiability.__name__,
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
