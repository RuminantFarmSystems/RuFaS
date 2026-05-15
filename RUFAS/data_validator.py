import os
from pathlib import Path
import re
from enum import Enum
from typing import Any, Callable, Sequence, cast

from RUFAS.util import Aggregator

AGGREGATION_FUNCTIONS: dict[
    str, Callable[[list[float]], float] | Callable[[list[float]], float | None] | Callable[[list[Any]], Any | None]
] = {
    "average": Aggregator.average,
    "division": Aggregator.division,
    "product": Aggregator.product,
    "standard_deviation": Aggregator.standard_deviation,
    "sum": Aggregator.sum,
    "difference": Aggregator.subtraction,
    "no_op": Aggregator.no_op,
}


class ElementState(Enum):
    """
    An enumeration of the states a data element can be in during validation. An element cannot
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
            raise ValueError(f"Input element has an invalid state: {state}")

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

    REQUIRED_LOCKED = "required locked"
    REQUIRED_UNLOCKED = "required unlocked"
    UNREQUIRED_UNLOCKED = "unrequired unlocked"

    @classmethod
    def values(cls) -> list[str]:
        """
        Provides a list of the string values of the enum members.

        Returns
        -------
        List[str]
            A list containing the string values of the enum members.
        """
        return list(map(lambda c: c.value, cls))

    @classmethod
    def get_required_during_initialization(cls) -> list["Modifiability"]:
        return [Modifiability.REQUIRED_LOCKED, Modifiability.REQUIRED_UNLOCKED]

    @classmethod
    def get_modifiable_at_runtime(cls) -> list["Modifiability"]:
        return [Modifiability.REQUIRED_UNLOCKED, Modifiability.UNREQUIRED_UNLOCKED]


class DataValidator:
    """This class is will be utilized to validate all types of data across RuFas codebase."""

    def __init__(self) -> None:
        self.event_logs: list[dict[str, str | dict[str, str]]] = []

    def validate_properties(self, metadata: dict[str, Any], metadata_depth_limit: int) -> tuple[bool, str]:
        """Iteratively traverses the metadata properties to check the max depth and routes
        properties to be validated by type.

        return
        ------
        Tuple[bool, str]
            boolean to indicate the validation status, error message in str if there's error that should be raised by
            the caller.
        """
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator.validate_properties.__name__,
        }

        stack: list[tuple[dict[str, Any], int, list[str]]] = [(metadata["properties"], 0, [])]
        current_max_depth: int = 0
        deepest_path: list[str] = []

        type_to_validator_map: dict[str, Callable[[list[str], dict[str, Any]], tuple[bool, str]]] = {
            "number": self._metadata_number_validator,
            "array": self._metadata_array_validator,
            "bool": self._metadata_bool_validator,
            "string": self._metadata_string_validator,
            "object": self._metadata_object_validator,
        }

        while stack:
            current_obj, depth, path = stack.pop()

            if depth > metadata_depth_limit:
                self.event_logs.append(
                    {
                        "error": "Max metadata depth exceeded.",
                        "message": f"Metadata depth exceeds maximum allowed depth"
                        f" of {metadata_depth_limit} at path {path}",
                        "info_map": info_map,
                    }
                )
                error_message = f"Metadata depth exceeds maximum allowed depth of {metadata_depth_limit} at path {path}"
                return False, error_message

            if depth > current_max_depth:
                current_max_depth = depth
                deepest_path = path

            if isinstance(current_obj, dict):
                for key, value in current_obj.items():
                    if isinstance(value, dict):
                        stack.append((value, depth + 1, path + [key]))
                        value_type = value.get("type")
                        if value_type in type_to_validator_map:
                            valid, error_message = type_to_validator_map[value_type](path + [key], value)
                            if not valid:
                                return valid, error_message
                        else:
                            if value_type is not None:
                                self.event_logs.append(
                                    {
                                        "error": "Properties value type error",
                                        "message": f"'type' value not" f" in {type_to_validator_map.keys()}",
                                        "info_map": info_map,
                                    }
                                )
                                error_message = f"Properties 'type' value not in {list(type_to_validator_map.keys())}"
                                return False, error_message
        self.event_logs.append(
            {
                "log": "Metadata properties depth",
                "message": f"Max depth of metadata properties is {current_max_depth}",
                "info_map": info_map,
            }
        )
        self.event_logs.append(
            {
                "log": "Metadata properties path",
                "message": f"Deepest path of metadata properties is {deepest_path}",
                "info_map": info_map,
            }
        )
        return True, ""

    def _validate_metadata_properties_keys(
        self,
        required_properties_keys: set[str],
        optional_properties_keys: set[str],
        properties: dict[str, Any],
        path: list[str],
    ) -> tuple[bool, str]:
        """Validates that keys in the metadata properties sections."""
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._validate_metadata_properties_keys.__name__,
        }
        if missing_required_keys := required_properties_keys - properties.keys():
            self.event_logs.append(
                {
                    "error": "Metadata Validation",
                    "message": f"Missing required keys {sorted(missing_required_keys)} for"
                    f" {path}. Required"
                    f" keys are {sorted(required_properties_keys)}.",
                    "info_map": info_map,
                }
            )
            error_message = (
                f"Missing required keys {sorted(missing_required_keys)} for {path}."
                f" Required keys are {sorted(required_properties_keys)}."
            )
            return False, error_message

        property_type = properties.get("type", "Unknown type")
        valid_properties_keys = required_properties_keys.union(optional_properties_keys)
        if property_type == "object":
            if not (set(properties.keys()) - valid_properties_keys):
                self.event_logs.append(
                    {
                        "error": "Metadata Validation",
                        "message": f"No unique keys for {path}. At least one unique key is" f" expected.",
                        "info_map": info_map,
                    }
                )
                error_message = f"No unique keys for {path}. At least one unique key is expected."
                return False, error_message
            return True, ""

        if invalid_keys := set(properties.keys()) - valid_properties_keys:
            self.event_logs.append(
                {
                    "error": "Metadata Validation",
                    "message": f"Invalid keys {sorted(invalid_keys)} in {property_type} for"
                    f" {path}. Valid"
                    f" keys are {sorted(valid_properties_keys)}.",
                    "info_map": info_map,
                }
            )
            error_message = (
                f"Invalid keys {sorted(invalid_keys)} in {property_type} for {path}. Valid"
                f" keys are {sorted(valid_properties_keys)}."
            )
            return False, error_message

        return True, ""

    def _metadata_number_validator(self, key_path: list[str], value: dict[str, Any]) -> tuple[bool, str]:
        """Validates number type properties in metadata."""
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._metadata_number_validator.__name__,
        }
        required_number_property_keys = {"type"}
        optional_number_property_keys = {"description", "minimum", "maximum", "default", "nullable"}
        valid, error_message = self._validate_metadata_properties_keys(
            required_number_property_keys, optional_number_property_keys, value, key_path
        )
        if not valid:
            return valid, error_message

        default = value.get("default", "No default")
        has_no_default = default == "No default"
        nullable = value.get("nullable", False)

        if default is None and not nullable:
            self.event_logs.append(
                {
                    "error": "Invalid metadata default number value.",
                    "message": f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'.",
                    "info_map": info_map,
                }
            )
            error_message = f"Invalid 'default' for '{key_path}': value is not nullable and default is 'None'."
            return False, error_message

        if default is not None and not isinstance(default, (int, float)) and not has_no_default:
            self.event_logs.append(
                {
                    "error": "Invalid metadata default number value.",
                    "message": f"Invalid 'default' for '{key_path}': Expected a number but got {type(default)}.",
                    "info_map": info_map,
                }
            )
            error_message = f"Invalid 'default' for '{key_path}': Expected a number but got {type(default)}."
            return False, error_message

        minimum = value.get("minimum")
        maximum = value.get("maximum")

        if minimum is not None and not isinstance(minimum, (int, float)):
            self.event_logs.append(
                {
                    "error": "Invalid metadata number properties minimum.",
                    "message": f"Invalid 'minimum' for '{key_path}': Expected a number but" f" got {type(minimum)}.",
                    "info_map": info_map,
                }
            )
            error_message = f"Invalid 'minimum' for '{key_path}': " f"Expected a number but got {type(minimum)}."
            return False, error_message

        if maximum is not None and not isinstance(maximum, (int, float)):
            self.event_logs.append(
                {
                    "error": "Invalid metadata number properties maximum.",
                    "message": f"Invalid 'maximum' for '{key_path}': Expected a number but got" f" {type(maximum)}.",
                    "info_map": info_map,
                }
            )
            error_message = f"Invalid 'maximum' for '{key_path}': Expected a number but got {type(maximum)}."
            return False, error_message

        if maximum is not None and minimum is not None and maximum < minimum:
            self.event_logs.append(
                {
                    "error": "Invalid range of acceptable numbers.",
                    "message": f"Invalid 'range' for key '{key_path}': 'minimum' value"
                    f" {minimum} is "
                    f"greater than 'maximum' value {maximum}",
                    "info_map": info_map,
                }
            )
            error_message = (
                f"Invalid 'range' for key '{key_path}': 'minimum' value {minimum} is "
                f"greater than 'maximum' value {maximum}"
            )
            return False, error_message
        if default is not None and not has_no_default:
            if minimum is not None and default < minimum:
                self.event_logs.append(
                    {
                        "error": "Invalid metadata default.",
                        "message": f"Invalid 'default' for '{key_path}': 'default' {default}"
                        f" is less than 'minimum' {minimum}",
                        "info_map": info_map,
                    }
                )
                error_message = (
                    f"Invalid 'default' for '{key_path}': 'default' {default} is " f"less than 'minimum' {minimum}"
                )
                return False, error_message
            if maximum is not None and default > maximum:
                self.event_logs.append(
                    {
                        "error": "Invalid metadata default.",
                        "message": f"Invalid 'default' for '{key_path}': 'default' {default} is"
                        f" greater than 'maximum' {maximum}",
                        "info_map": info_map,
                    }
                )
                error_message = (
                    f"Invalid 'default' for '{key_path}': 'default' {default} is " f"greater than 'maximum' {maximum}"
                )
                return False, error_message

        return True, ""

    def _metadata_string_validator(self, key_path: list[str], value: dict[str, Any]) -> tuple[bool, str]:
        """Validates string type properties in metadata."""
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._metadata_string_validator.__name__,
        }
        required_str_property_keys = {"type"}
        optional_str_property_keys = {"description", "pattern", "default", "nullable"}
        valid, message = self._validate_metadata_properties_keys(
            required_str_property_keys, optional_str_property_keys, value, key_path
        )
        if not valid:
            return valid, message
        default = value.get("default", "No default")
        has_no_default = default == "No default"
        nullable = value.get("nullable", False)
        if default is None and not nullable:
            self.event_logs.append(
                {
                    "error": "Invalid metadata default string value.",
                    "message": f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'",
                    "info_map": info_map,
                }
            )
            error_message = f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'"
            return False, error_message

        if default is not None and not has_no_default and not isinstance(default, str):
            self.event_logs.append(
                {
                    "error": "Invalid metadata default string value.",
                    "message": f"Invalid 'default' for '{key_path}': Expected a string but got {type(default)}",
                    "info_map": info_map,
                }
            )
            error_message = f"Invalid 'default' for '{key_path}': Expected a string but got {type(default)}"
            return False, error_message

        pattern = value.get("pattern")
        if pattern is not None and not isinstance(pattern, str):
            self.event_logs.append(
                {
                    "error": "Invalid metadata string properties pattern.",
                    "message": f"Invalid 'pattern' for '{key_path}': Expected a string but got {type(pattern)}",
                    "info_map": info_map,
                }
            )
            error_message = f"Invalid 'pattern' for '{key_path}': Expected a string but got {type(pattern)}"
            return False, error_message
        try:
            if pattern is not None:
                re.compile(pattern)
        except re.error:
            self.event_logs.append(
                {
                    "error": "Invalid metadata string properties pattern.",
                    "message": f"Invalid 'pattern' for '{key_path}': 'pattern' value '{pattern}'"
                    f" is not "
                    "a valid regex pattern.",
                    "info_map": info_map,
                }
            )
            error_message = (
                f"Invalid 'pattern' for '{key_path}': 'pattern' value '{pattern}' is not " "a valid regex pattern."
            )
            return False, error_message
        if default != "" and default is not None and not has_no_default:
            if pattern is not None and not re.match(pattern, default):
                self.event_logs.append(
                    {
                        "error": "Invalid metadata default string value.",
                        "message": f"Invalid 'default' for '{key_path}': 'default' value"
                        f" '{default}' does not "
                        f"match pattern {pattern}",
                        "info_map": info_map,
                    }
                )
                error_message = (
                    f"Invalid 'default' for '{key_path}': 'default' value '{default}' does not "
                    f"match pattern {pattern}"
                )
                return False, error_message

        return True, ""

    def _metadata_bool_validator(self, key_path: list[str], value: dict[str, Any]) -> tuple[bool, str]:
        """Validates bool type properties in metadata."""
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._metadata_bool_validator.__name__,
        }
        required_bool_property_keys = {"type"}
        optional_bool_property_keys = {"description", "default", "nullable"}
        valid, message = self._validate_metadata_properties_keys(
            required_bool_property_keys, optional_bool_property_keys, value, key_path
        )
        if not valid:
            return valid, message
        default = value.get("default", "No default")
        has_no_default = default == "No default"
        nullable = value.get("nullable", False)
        if default is None and not nullable:
            self.event_logs.append(
                {
                    "error": "Invalid metadata default bool value.",
                    "message": f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'",
                    "info_map": info_map,
                }
            )
            error_message = f"Invalid 'default' for '{key_path}': Value is not nullable and default is 'None'"
            return False, error_message
        if default is not None and not isinstance(default, bool) and not has_no_default:
            self.event_logs.append(
                {
                    "error": "Invalid metadata default bool value.",
                    "message": f"Invalid 'default' for '{key_path}': Expected a bool but got {type(default)}",
                    "info_map": info_map,
                }
            )
            error_message = f"Invalid 'default' for key {key_path}: Expected a bool but got {type(default)}"
            return False, error_message

        return True, ""

    def _metadata_array_validator(self, key_path: list[str], value: dict[str, Any]) -> tuple[bool, str]:
        """Validates array type properties in metadata."""
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._metadata_array_validator.__name__,
        }
        required_array_property_keys = {"type", "properties"}
        optional_array_property_keys = {"description", "minimum_length", "maximum_length", "nullable", "default"}
        valid, message = self._validate_metadata_properties_keys(
            required_array_property_keys, optional_array_property_keys, value, key_path
        )
        if not valid:
            return valid, message
        minimum_length = value.get("minimum_length")
        maximum_length = value.get("maximum_length")
        if minimum_length is not None and not isinstance(minimum_length, (int, float)):
            self.event_logs.append(
                {
                    "error": "Invalid metadata default array minimum length.",
                    "message": f"Invalid 'minimum_length' for '{key_path}': Expected a number but"
                    f" got {type(minimum_length)}",
                    "info_map": info_map,
                }
            )
            error_message = (
                f"Invalid 'minimum_length' for '{key_path}': " f"Expected a number but got {type(minimum_length)}"
            )
            return False, error_message
        if maximum_length is not None and not isinstance(maximum_length, (int, float)):
            self.event_logs.append(
                {
                    "error": "Invalid metadata default array maximum length.",
                    "message": f"Invalid 'maximum_length' for '{key_path}': Expected a number but"
                    f" got {type(maximum_length)}",
                    "info_map": info_map,
                }
            )
            error_message = (
                f"Invalid 'maximum_length' for '{key_path}': " f"Expected a number but got {type(maximum_length)}"
            )
            return False, error_message
        if maximum_length is not None and minimum_length is not None and maximum_length < minimum_length:
            self.event_logs.append(
                {
                    "error": "Invalid metadata array length range.",
                    "message": f"Invalid length 'range' for key '{key_path}': 'minimum_length' "
                    f"value {minimum_length} is "
                    f"greater than 'maximum_length' value {maximum_length}",
                    "info_map": info_map,
                }
            )
            error_message = (
                f"Invalid length 'range' for key '{key_path}': 'minimum_length' value {minimum_length} is "
                f"greater than 'maximum_length' value {maximum_length}"
            )
            return False, error_message

        return True, ""

    def _metadata_object_validator(self, key_path: list[str], value: dict[str, Any]) -> tuple[bool, str]:
        """Validates object type properties in metadata."""
        required_object_property_keys = {"type"}
        optional_object_property_keys = {"description"}
        valid, message = self._validate_metadata_properties_keys(
            required_object_property_keys, optional_object_property_keys, value, key_path
        )
        if not valid:
            return valid, message
        return True, ""

    def validate_metadata(
        self,
        metadata: dict[str, Any],
        valid_data_types: set[str],
        address_to_data: str,
        input_root: Path,
    ) -> tuple[bool, str]:
        """
        Checks that top-level metadata has valid and required keys and values.

        Parameters
        ----------
        metadata : dict[str, Any]
            The metadata to be validated.
        valid_data_types : set[str]
            The set of valid data types.
        address_to_data : str
            The key in the metadata dictionary that points to the data to be validated.
        input_root : Path
            The root directory for input files.
        """
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator.validate_metadata.__name__,
        }

        metadata_files = metadata[address_to_data]

        required_keys = {"type", "properties"}
        optional_keys = {"title", "description", "path", "paths"}
        valid_keys = required_keys | optional_keys

        for key, data in metadata_files.items():
            are_keys_valid, msg = self._validate_metadata_keys(key, data, required_keys, valid_keys, info_map)
            if not are_keys_valid:
                return False, msg

            has_path_or_paths, msg = self._validate_has_path_or_paths(key, data, info_map)
            if not has_path_or_paths:
                return False, msg

            is_type_valid, msg = self._validate_metadata_type(key, data, valid_data_types, info_map)
            if not is_type_valid:
                return False, msg

            paths, msg = self._get_paths_to_check(key, data, info_map)
            if paths is None:
                return False, msg

            are_paths_valid, msg = self._validate_paths_exist(key, paths, input_root, info_map)
            if not are_paths_valid:
                return False, msg

            are_properties_valid, msg = self._validate_metadata_properties(key, data, info_map)
            if not are_properties_valid:
                return False, msg

        self.event_logs.append(
            {"log": "Metadata Validation", "message": "Top level metadata is valid.", "info_map": info_map}
        )
        return True, ""

    def _generate_fail_message(self, message: str, info_map: dict[str, Any]) -> tuple[bool, str]:
        """Helper function to log failure messages and return a consistent response."""
        self.event_logs.append({"error": "Metadata Validation", "message": message, "info_map": info_map})
        return False, message

    def _validate_metadata_keys(
        self,
        key: str,
        data: dict[str, Any],
        required_keys: set[str],
        valid_keys: set[str],
        info_map: dict[str, Any],
    ) -> tuple[bool, str]:
        """Helper function to validate metadata keys."""
        if missing_keys := (required_keys - data.keys()):
            return self._generate_fail_message(f"Missing required keys '{list(missing_keys)}' in '{key}'", info_map)
        if invalid_keys := (data.keys() - valid_keys):
            return self._generate_fail_message(f"Invalid keys '{list(invalid_keys)}' in '{key}'", info_map)
        return True, ""

    def _validate_has_path_or_paths(self, key: str, data: dict[str, Any], info_map: dict[str, Any]) -> tuple[bool, str]:
        """Helper function to validate that at least one of 'path' or 'paths' is defined."""
        if "path" not in data and "paths" not in data:
            return self._generate_fail_message(
                f"'{key}' must define at least one of the keys 'path' or 'paths', but neither was found.",
                info_map,
            )
        return True, ""

    def _validate_metadata_type(
        self,
        key: str,
        data: dict[str, Any],
        valid_data_types: set[str],
        info_map: dict[str, Any],
    ) -> tuple[bool, str]:
        """Helper function to validate the 'type' value in metadata."""
        if data["type"] not in valid_data_types:
            return self._generate_fail_message(
                f"Invalid type '{data['type']}' in '{key}'. Expected one option from {valid_data_types}",
                info_map,
            )
        return True, ""

    def _get_paths_to_check(
        self, key: str, data: dict[str, Any], info_map: dict[str, Any]
    ) -> tuple[list[str] | None, str]:
        """Helper function to get the paths to check in metadata."""
        paths: list[str] = []

        if "path" in data:
            path_value = data.get("path")
            if not isinstance(path_value, str) or not path_value:
                _, msg = self._generate_fail_message(f"Invalid path value '{path_value}' in '{key}'", info_map)
                return None, msg
            paths.append(path_value)

        if "paths" in data:
            paths_value = data.get("paths")

            if not isinstance(paths_value, list) or not paths_value:
                _, msg = self._generate_fail_message(f"Invalid paths value '{paths_value}' in '{key}'", info_map)
                return None, msg

            invalid_entries = [p for p in paths_value if not isinstance(p, str) or not p]
            if invalid_entries:
                _, msg = self._generate_fail_message(f"Invalid paths value '{paths_value}' in '{key}'", info_map)
                return None, msg

            paths.extend(paths_value)

        return paths, ""

    def _validate_paths_exist(
        self,
        key: str,
        paths_to_check: list[str],
        input_root: Path,
        info_map: dict[str, Any],
    ) -> tuple[bool, str]:
        """Helper function to validate that the specified paths exist."""
        for rel_path in paths_to_check:
            full_path = os.path.join(input_root, rel_path)
            if not os.path.isfile(full_path):
                return self._generate_fail_message(f"Invalid path '{rel_path}' in '{key}'", info_map)
        return True, ""

    def _validate_metadata_properties(
        self, key: str, data: dict[str, Any], info_map: dict[str, Any]
    ) -> tuple[bool, str]:
        """Helper function to validate the 'properties' section in metadata."""
        if data["properties"] is None or data["properties"] == "":
            return self._generate_fail_message(f"Properties section empty or None in '{key}'", info_map)
        return True, ""

    def validate_data_by_type(
        self,
        variable_properties: dict[str, Any],
        variable_path: list[str | int],
        data: dict[str | int, Any] | list[Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
        fixable_data_types: set[str],
        input_path: Path,
    ) -> bool:
        """
        Validates the data based on its specified type.

        Parameters
        ----------
        variable_properties : dict[str, Any]
            A dictionary containing properties relevant to the validation.
        variable_path : list[str | int]
            The path to the variable being validated.
        data : dict[str | int, Any] | list[Any]
            The data to be validated.
        eager_termination : bool
            If True, the process will be terminated as soon as finding invalid data and failing to fix it.
        properties_blob_key : str
            The metadata properties for the data file being checked.
        elements_counter : ElementsCounter
            A counter to keep track of the number of valid, invalid, and fixed elements.
        called_during_initialization : bool
            Boolean variable indicating whether the function is being called during initialization.
        fixable_data_types : set[str]
            Set enumerating the data types that the caller will attempt to fix while validating data.
        input_path : Path
            Reference identifying the origin of the data currently being validated.

        Returns
        -------
        bool
            True if the data is valid, False otherwise.

        Raises
        ------
        KeyError
            If the variable's properties does not specify a "type".
        ValueError
            If the variable's properties specifies a "type" that is not supported.

        Notes
        -----
        Fixing invalid data will only be attempted if the data is a "simple" type (i.e. a string, bool or number).

        """
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator.validate_data_by_type.__name__,
        }
        if "type" not in variable_properties:
            raise KeyError(f"Input property missing 'type' key in {variable_properties}")

        data_type = variable_properties["type"]

        type_to_validator_map: dict[
            str,
            Callable[
                [
                    list[int | str],
                    dict[str, Any],
                    dict[str | int, Any] | list[Any],
                    bool,
                    str,
                    ElementsCounter,
                    bool,
                    set[str],
                    Path,
                ],
                bool,
            ],
        ] = {
            "array": self._array_type_validator,
            "object": self._object_type_validator,
            "string": self._string_type_validator,
            "number": self._number_type_validator,
            "bool": self._bool_type_validator,
        }
        path = self.convert_variable_path_to_str(variable_path)

        if data_type not in type_to_validator_map:
            raise ValueError(
                f"The metadata type of the element '{path}' in input '{input_path}' "
                f"is not valid. Supported types are: {type_to_validator_map.keys()}."
            )

        is_valid = type_to_validator_map[data_type](
            variable_path,
            variable_properties,
            data,
            eager_termination,
            properties_blob_key,
            elements_counter,
            called_during_initialization,
            fixable_data_types,
            input_path,
        )

        if data_type not in fixable_data_types:
            if not is_valid:
                error_message = (
                    f"Variable: '{path}' data type '{data_type}' from the '{input_path}' "
                    "is not fixable by Input Manager. Please check the inputs."
                )
                self.event_logs.append(
                    {
                        "error": "Validation: data type is not fixable by Input Manager",
                        "message": error_message,
                        "info_map": info_map,
                    }
                )
            return is_valid

        if is_valid:
            elements_counter.increment(ElementState.VALID)
            return True

        is_fixed = self._fix_data(variable_properties, variable_path, data, properties_blob_key, input_path)

        if is_fixed:
            elements_counter.increment(ElementState.FIXED)
            return True
        else:
            elements_counter.increment(ElementState.INVALID)
            return False

    def _validate_array_container_properties(
        self,
        variable_path: list[str | int],
        variable_properties: dict[str, Any],
        data: Any,
        properties_blob_key: str,
    ) -> bool:
        """
        Validates the container properties of an array data element.

        Parameters
        ----------
        variable_path : List[str | int]
            The path to the variable being validated.
        variable_properties : Dict[str, Any]
            The metadata properties for the variable being validated.
        data : Any
            The data to be validated.
        properties_blob_key : str
            The metadata properties for the data file being checked.

        Returns
        -------
        bool
            True if the array container properties are valid, False otherwise.
        """
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._validate_array_container_properties.__name__,
        }
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )
        variable_path_str = self.convert_variable_path_to_str(variable_path)
        if not isinstance(data, list):
            self.event_logs.append(
                {
                    "warning": "Validation: array container is not a list",
                    "message": f"Variable: '{variable_path_str}' is not"
                    f" an array but has type: {type(data)}. "
                    f"{properties_violation_message}",
                    "info_map": info_map,
                }
            )
            return False

        maximum_length = variable_properties.get("maximum_length")
        minimum_length = variable_properties.get("minimum_length")
        if minimum_length is not None:
            is_in_range = variable_properties["minimum_length"] <= len(data)
            if not is_in_range:
                self.event_logs.append(
                    {
                        "warning": "Validation: array length less than minimum",
                        "message": f"Variable: '{variable_path_str}' has length: {len(data)}, "
                        f"less than minimum length:"
                        f"{minimum_length}. {properties_violation_message}",
                        "info_map": info_map,
                    }
                )
                return False

        if maximum_length is not None:
            is_in_range = len(data) <= variable_properties["maximum_length"]
            if not is_in_range:
                self.event_logs.append(
                    {
                        "warning": "Validation: array length greater than maximum",
                        "message": f"Variable: '{variable_path_str}' has"
                        f" length: {len(data)}, greater than maximum length: "
                        f"{maximum_length}. {properties_violation_message}",
                        "info_map": info_map,
                    }
                )
                return False
        return True

    def _array_type_validator(
        self,
        variable_path: list[str | int],
        variable_properties: dict[str, Any],
        data: dict[str | int, Any] | list[Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
        fixable_data_types: set[str],
        input_path: Path,
    ) -> bool:
        """
        Validates a data element of type array.

        Parameters
        ----------
        variable_path : list[str | int]
            The path to the variable being validated.
        variable_properties : dict[str, Any]
            The metadata properties for the variable being validated.
        data : data: dict[str | Any] | list[Any]
            The data to be validated.
        eager_termination : bool
            If True, the process will be terminated upon finding invalid data.
        properties_blob_key : str
            The metadata properties for the data file being checked.
        elements_counter : ElementsCounter
            A counter to keep track of the number of valid, invalid, and fixed elements.
        called_during_initialization: bool
            Boolean variable indicating whether the function is being called during initialization.
        fixable_data_types: set[str]
            Set of data types that are fixable.
        input_path : Path
            Reference identifying the origin of the data currently being validated.

        Returns
        -------
        bool
            True if the data element is valid or fixable, False otherwise.
        """

        array_value = self._extract_data_by_key_list(
            data, variable_path, variable_properties, called_during_initialization, input_path
        )

        if variable_properties.get("nullable", False) and array_value is None:
            return True

        if not self._validate_array_container_properties(
            variable_path, variable_properties, array_value, properties_blob_key
        ):
            return False

        is_whole_array_acceptable = True
        for index, element in enumerate(array_value):
            is_element_acceptable = self.validate_data_by_type(
                variable_properties["properties"],
                variable_path + [index],
                data,
                eager_termination,
                properties_blob_key,
                elements_counter,
                called_during_initialization,
                fixable_data_types,
                input_path,
            )
            is_whole_array_acceptable = is_whole_array_acceptable and is_element_acceptable
            if not is_element_acceptable and eager_termination:
                return False
        return is_whole_array_acceptable

    def _object_type_validator(
        self,
        variable_path: list[str | int],
        variable_properties: dict[str, Any],
        data: dict[str | int, Any] | list[Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: ElementsCounter,
        called_during_initialization: bool,
        fixable_data_types: set[str],
        input_path: Path,
    ) -> bool:
        """
        Validates a data element of type object.

        Parameters
        ----------
        variable_path : list[str | int]
            The path to the variable being validated.
        variable_properties : dict[str, Any]
            The metadata properties for the variable being validated.
        data : dict[str | int, Any] | list[Any]
            The data to be validated.
        eager_termination : bool
            If True, the process will be terminated upon finding invalid data.
        properties_blob_key : str
            The metadata properties for the data file being checked.
        elements_counter : ElementsCounter
            A counter to keep track of the number of valid, invalid, and fixed elements.
        called_during_initialization: bool
            Boolean variable indicating whether the function is being called during initialization.
        input_path : Path
            Reference identifying the origin of the data currently being validated.

        Returns
        -------
        bool
            True if the data element is valid or fixable, False otherwise.

        Notes
        -----
        This method will look for and delete any keys in the data that do not have properties specified for them
        in the metadata properties.

        """
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._object_type_validator.__name__,
        }

        object_value = self._extract_data_by_key_list(
            data, variable_path, variable_properties, called_during_initialization, input_path
        )
        variable_path_str = self.convert_variable_path_to_str(variable_path)
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )
        if not isinstance(object_value, dict):
            self.event_logs.append(
                {
                    "warning": "Validation: object is not a dictionary",
                    "message": f"Variable: '{variable_path_str}' in '{input_path}' is"
                    f" not an object but has type: {type(object_value)}. "
                    f"{properties_violation_message}",
                    "info_map": info_map,
                }
            )
            return False

        is_whole_object_acceptable = True
        for key in variable_properties.keys():
            if key in ["type", "description", "default"]:
                continue
            is_element_acceptable = self.validate_data_by_type(
                variable_properties[key],
                variable_path + [key],
                data,
                eager_termination,
                properties_blob_key,
                elements_counter,
                called_during_initialization,
                fixable_data_types,
                input_path,
            )
            is_whole_object_acceptable = is_whole_object_acceptable and is_element_acceptable
            if not is_element_acceptable and eager_termination:
                return False

        extraneous_keys = [key for key in object_value.keys() if key not in variable_properties.keys()]
        for key in extraneous_keys:
            self.event_logs.append(
                {
                    "warning": "Validation: object contains extraneous data",
                    "message": f"Variable: '{variable_path_str}' in '{input_path}' contains "
                    f"data at key '{key}' that is not specified in "
                    f"the metadata"
                    f" properties. {properties_violation_message}",
                    "info_map": info_map,
                }
            )
            del object_value[key]

        return is_whole_object_acceptable

    def _number_type_validator(
        self,
        variable_path: list[str | int],
        variable_properties: dict[str, Any],
        data: dict[str | int, Any] | list[Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
        fixable_data_types: set[str],
        input_path: Path,
    ) -> bool:
        """Validates an data number element."""
        data_value = self._extract_data_by_key_list(
            data, variable_path, variable_properties, called_during_initialization, input_path
        )

        if variable_properties.get("nullable", False) and data_value is None:
            return True

        variable_path_str = self.convert_variable_path_to_str(variable_path)

        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._number_type_validator.__name__,
        }
        minimum_value = variable_properties.get("minimum")
        maximum_value = variable_properties.get("maximum")
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )

        if type(data_value) is not float and type(data_value) is not int:
            warning_string = "Validation: value is not a number"
            warning_message = (
                f"Variable: '{variable_path_str}' in '{input_path}' has value: {data_value}, is type: "
                f"{type(data_value)}. {properties_violation_message}"
            )
            self.event_logs.append({"warning": warning_string, "message": warning_message, "info_map": info_map})
            return False
        if minimum_value is not None:
            is_in_range = minimum_value <= data_value
            if not is_in_range:
                warning_name = "Validation: value less than minimum"
                warning_message = (
                    f"Variable: '{variable_path_str}' in '{input_path}' has value: {data_value}, "
                    f"less than minimum value: {minimum_value: .2f}. {properties_violation_message}"
                )
                self.event_logs.append({"warning": warning_name, "message": warning_message, "info_map": info_map})
                return False
        if maximum_value is not None:
            is_in_range = data_value <= maximum_value
            if not is_in_range:
                warning_name = "Validation: value greater than maximum"
                warning_message = (
                    f"Variable: '{variable_path_str}' in '{input_path}' has value: {data_value}, "
                    f"greater than maximum value: {maximum_value: .2f}. {properties_violation_message}"
                )
                self.event_logs.append({"warning": warning_name, "message": warning_message, "info_map": info_map})
                return False

        return True

    def _string_type_validator(
        self,
        variable_path: list[str | int],
        variable_properties: dict[str, Any],
        data: dict[str | int, Any] | list[Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
        fixable_data_types: set[str],
        input_path: Path,
    ) -> bool:
        """Validates a data string element."""
        data_value = self._extract_data_by_key_list(
            data, variable_path, variable_properties, called_during_initialization, input_path
        )

        if variable_properties.get("nullable", False) and data_value is None:
            return True

        variable_path_str = self.convert_variable_path_to_str(variable_path)
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._string_type_validator.__name__,
        }
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )

        if type(data_value) is not str:
            warning_name = "Validation: string variable is not a string"
            warning_message = (
                f"Variable: '{variable_path_str}' in '{input_path}' has value: {data_value}, is type: "
                f"{type(data_value)}. {properties_violation_message}"
            )
            self.event_logs.append({"warning": warning_name, "message": warning_message, "info_map": info_map})
            return False

        pattern_check = variable_properties.get("pattern")
        if pattern_check is not None:
            is_valid_string = bool(re.match(pattern_check, data_value))
            if not is_valid_string:
                warning_name = "Validation: string variable does not match pattern"
                warning_message = (
                    f"Variable: '{variable_path_str}' in '{input_path}' has value: '{data_value}', "
                    f"does not match pattern: {pattern_check}. {properties_violation_message}"
                )
                self.event_logs.append({"warning": warning_name, "message": warning_message, "info_map": info_map})
                return False

        minimum_length = variable_properties.get("minimum_length")
        maximum_length = variable_properties.get("maximum_length")
        if minimum_length is not None:
            is_valid_string = variable_properties["minimum_length"] <= len(data_value)
            if not is_valid_string:
                warning_name = "Validation: string length less than minimum"
                warning_message = (
                    f"Variable: '{variable_path_str}' in '{input_path}' has value: '{data_value}', length is less than "
                    f"minimum length: {minimum_length}. {properties_violation_message}"
                )
                self.event_logs.append({"warning": warning_name, "message": warning_message, "info_map": info_map})
                return False
        if maximum_length is not None:
            is_valid_string = len(data_value) <= variable_properties["maximum_length"]
            if not is_valid_string:
                warning_name = "Validation: string length greater than maximum"
                warning_message = (
                    f"Variable: '{variable_path_str}' in '{input_path}' has value: '{data_value}', "
                    f"length is greater than maximum length: {maximum_length}. {properties_violation_message}"
                )
                self.event_logs.append({"warning": warning_name, "message": warning_message, "info_map": info_map})
                return False

        return True

    def _bool_type_validator(
        self,
        variable_path: list[str | int],
        variable_properties: dict[str, Any],
        data: dict[str | int, Any] | list[Any],
        eager_termination: bool,
        properties_blob_key: str,
        elements_counter: "ElementsCounter",
        called_during_initialization: bool,
        fixable_data_types: set[str],
        input_path: Path,
    ) -> bool:
        """Validates a data bool element."""
        data_value = self._extract_data_by_key_list(
            data, variable_path, variable_properties, called_during_initialization, input_path
        )

        if variable_properties.get("nullable", False) and data_value is None:
            return True

        variable_path_str = self.convert_variable_path_to_str(variable_path)

        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._bool_type_validator.__name__,
        }
        properties_violation_message = (
            f"Violates properties defined in metadata properties section" f" '{properties_blob_key}'."
        )

        if type(data_value) is not bool:
            warning_name = "Validation: bool variable is not a bool"
            warning_message = (
                f"Variable: '{variable_path_str}' in '{input_path}' has value: '{data_value}', is type: "
                f"'{type(data_value)}'. {properties_violation_message}"
            )
            self.event_logs.append({"warning": warning_name, "message": warning_message, "info_map": info_map})

            return False

        return True

    def _fix_data(
        self,
        variable_properties: dict[str, Any],
        element_hierarchy: list[str | int],
        data: dict[str | int, Any] | list[Any],
        properties_blob_key: str,
        input_path: Path,
    ) -> bool:
        """
        Attempt to fix the invalid data.

        Parameters
        ----------
        variable_properties : dict[str, Any]
            The properties for the variable of interest.
        element_hierarchy: list[str | int]
            A list indicating the path to reach the variable of interest in self.__metadata and self.__pool.
        data: dict[str | int, Any] | list[Any]
            A buffer dictionary that holds the data for validation and fixing.
        properties_blob_key : str
            The metadata properties section keyword for the data file being checked.
        input_path : Path
            Reference identifying the origin of the data currently being validated.

        Returns
        -------
        bool
            True if the data is fixed, False otherwise.
        """
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._fix_data.__name__,
        }

        variable_parent: dict[str | int, Any] | list[Any] = data
        for key in element_hierarchy[:-1]:
            variable_parent = variable_parent[key] if isinstance(variable_parent, dict) else variable_parent[int(key)]

        element_path = ".".join([str(element) for element in element_hierarchy])
        properties_violation_message = (
            f"Violates properties defined in metadata properties section '{properties_blob_key}'."
        )
        if "default" not in variable_properties.keys():
            invalid_value = (
                variable_parent.get(element_hierarchy[-1], "missing required value")
                if isinstance(variable_parent, dict)
                else variable_parent[int(element_hierarchy[-1])]
            )
            error_message = (
                f"Variable: '{element_hierarchy[-1]}' in '{input_path}' has invalid value: '{invalid_value}'"
                f", and cannot be changed to a default value. {properties_violation_message}"
            )
            self.event_logs.append(
                {
                    "error": "Validation: invalid data not able to be fixed",
                    "message": error_message,
                    "info_map": info_map,
                }
            )
            return False

        if type(variable_parent) is list:
            original_invalid_value = variable_parent[int(element_hierarchy[-1])]
        else:
            assert type(variable_parent) is dict
            original_invalid_value = variable_parent.get(str(element_hierarchy[-1]))

        warning_message = (
            f"Variable: '{element_path}' in '{input_path}' has value: {original_invalid_value}."
            f" {properties_violation_message}"
        )
        self.event_logs.append(
            {"warning": "Validation: invalid data found", "message": warning_message, "info_map": info_map}
        )
        if type(variable_parent) is list:
            variable_parent[int(element_hierarchy[-1])] = variable_properties["default"]
        else:
            assert type(variable_parent) is dict
            variable_parent[str(element_hierarchy[-1])] = variable_properties["default"]

        warning_message = (
            f"Invalid data from '{input_path}' fixed: '{element_path}' value changed from "
            f"{original_invalid_value} to {variable_properties['default']}. Fix enabled by default value specified in "
            f"'{properties_blob_key}'."
        )
        self.event_logs.append({"warning": "Validation: data fixed", "message": warning_message, "info_map": info_map})
        return True

    def _extract_data_by_key_list(
        self,
        data: dict[str | int, Any] | list[Any],
        variable_path: Sequence[str | int],
        variable_properties: dict[str, Any],
        called_during_initialization: bool,
        input_path: Path,
    ) -> Any:
        """
        Extracts a value from the data based on a specified path and handles missing data by calling
        DataValidator._log_missing_data().

        Parameters
        ----------
        data : List[Any] | Dict[str, Any]
            The data containing the value to be extracted.
        variable_path : List[str | int]
            A list of keys to be used to extract the value from the data.
        variable_properties : Dict[str, Any]
            The metadata properties for the variable being validated.
        called_during_initialization: bool
            Boolean variable indicating whether the function is being called during initialization.
        input_path : Path
            Reference identifying the origin of the data currently being validated.

        Returns
        -------
        Any
            The value extracted from the data if found.
            None if not found.

        Notes
        -----
        This function navigates through the given data (which can be a list or a dictionary) following the path
        specified in `variable_path`. If the path leads to a value, it is returned.
        If a KeyError occurs during this process (i.e., a key or index is missing in the path), the function extracts
        the variable name by finding the last string element in the `variable_path` array and handles this missing data
        by calling DataValidator._log_missing_data().
        """
        result = None
        try:
            result = self.extract_value_by_key_list(data, variable_path, input_path)
        except KeyError:
            var_name: str = [name for name in reversed(variable_path) if type(name) is str][0]
            self._log_missing_data(
                variable_properties=variable_properties,
                var_name=var_name,
                called_during_initialization=called_during_initialization,
                input_path=input_path,
            )
        return result

    def _log_missing_data(
        self,
        variable_properties: dict[str, Any],
        var_name: str,
        called_during_initialization: bool,
        input_path: Path,
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
        input_path : Path
            Reference identifying the origin of the data currently being validated.

        Raises
        ------
        KeyError
            Raised if the missing data is deemed necessary, either during initialization or for a runtime update.

        Notes
        -----
        This function determines if it's being called during the initialization phase and checks if the missing variable
        data is required at this stage using '_is_data_required_upon_initialization'. If required, it logs an error and
        raises a KeyError. If not, it logs a warning.
        """
        info_map = {"class": DataValidator.__name__, "function": DataValidator._log_missing_data.__name__}
        if not called_during_initialization:
            error_msg = (
                f"Key {var_name} not found in data from '{input_path}'. "
                "A value is required to update variable during runtime."
            )
            self.event_logs.append({"error": "Missing required data", "message": error_msg, "info_map": info_map})
            raise KeyError(error_msg)

        if self._is_data_required_upon_initialization(variable_name=var_name, variable_properties=variable_properties):
            self.event_logs.append(
                {
                    "error": "Missing required data",
                    "message": f"Key {var_name} not found in data from source '{input_path}'. Data value is required "
                    "for this variable upon program initialization.",
                    "info_map": info_map,
                }
            )
            raise KeyError(
                f"Key {var_name} not found in input data source '{input_path}'. Data value is required for this "
                "variable upon program initialization."
            )
        self.event_logs.append(
            {
                "warning": "Validation: key not found in input data. Data not required upon initialization",
                "message": f"Key {var_name} not found in data source '{input_path}'. Data value is not required for "
                "this variable upon program initialization, setting the variable value to None.",
                "info_map": info_map,
            }
        )

    def _is_data_required_upon_initialization(self, variable_name: str, variable_properties: dict[str, Any]) -> bool:
        """
        Determines whether a variable requires a data value upon initialization based on its modifiability status.

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
            True if the variable's modifiability status necessitates a data value upon initialization,
            False otherwise.
        """
        variable_modifiability = self._get_variable_modifiability(
            variable_name=variable_name, variable_properties=variable_properties
        )
        return variable_modifiability in Modifiability.get_required_during_initialization()

    def _get_variable_modifiability(self, variable_name: str, variable_properties: dict[str, Any]) -> Modifiability:
        """
        Determines the modifiability status of a variable based on its properties and returns the corresponding enum
        value.

        Notes
        -----
        This function looks for a 'modifiability' key within `variable_properties`. If present and its value is not
        empty, the function attempts to map this value to an enum member in Modifiability. If the value does not
        correspond to any enum members, a KeyError is raised after logging the error downstream. If 'modifiability'
        is absent or its value is empty, the function defaults to Modifiability.NOT_REQUIRED_AND_UNLOCKED.

        Parameters
        ----------
        variable_name : str
            The name of the variable for which the modifiability status is being determined. Used for error logging.
        variable_properties : dict[str, Any]
            A dictionary containing the properties of the variable, containing the desired 'modifiability' property.

        Returns
        -------
        Modifiability
            An enum member representing the variable's modifiability status.

        """
        info_map = {
            "class": DataValidator.__name__,
            "function": DataValidator._get_variable_modifiability.__name__,
        }

        default = "UNREQUIRED UNLOCKED"
        modifiability = variable_properties.get("modifiability", default)

        try:
            return Modifiability.__getitem__("_".join(modifiability.strip().upper().split()))
        except KeyError:
            self.event_logs.append(
                {
                    "warning": "Unknown modifiability entry",
                    "message": f"Unknown modifiability value of {modifiability} for variable"
                    f" {variable_name}. Modifiability should be "
                    f"one of {Modifiability.values()}."
                    f" Using the default value: {default}",
                    "info_map": info_map,
                }
            )
            return Modifiability.__getitem__("_".join(default.strip().upper().split()))

    def convert_variable_path_to_str(self, variable_path: list[str | int]) -> str:
        """
        Converts a list of keys (int or str) into a string representation of the path to a variable.

        Parameters
        ----------
        variable_path : List[str | int]
            A list of keys to be used to extract the value from the data.

        Returns
        -------
        str
            A string representation of the path to a variable.

        Examples
        --------
        >>> input_manager = InputManager()
        >>> var_path = ["animal", "herd_information", "calf_num"]
        >>> DataValidator.convert_variable_path_to_str(var_path)
        'animal.herd_information.calf_num'

        >>> input_manager = InputManager()
        >>> var_path = ["manure_management_scenarios", 0, "bedding_type"]
        >>> DataValidator.convert_variable_path_to_str(var_path)
        'manure_management_scenarios.[0].bedding_type'
        """

        formatted_path_elems = []
        for raw_path_elem in variable_path:
            if isinstance(raw_path_elem, int) or (isinstance(raw_path_elem, str) and raw_path_elem.isdigit()):
                formatted_path_elems.append(f"[{raw_path_elem}]")
            else:
                formatted_path_elems.append(f"{raw_path_elem}")
        return ".".join(formatted_path_elems)

    def extract_value_by_key_list(
        self, data: list[Any] | dict[str | int, Any], variable_path: Sequence[str | int], input_path: Path | None = None
    ) -> Any:
        """
        Extracts a value from a nested list or dictionary using a list of keys (int or str).

        Parameters
        ----------
        data : list[Any] | dict[str, Any]
            The data containing the value to be extracted.
        variable_path : dist[str | int]
            A list of keys to be used to extract the value from the data.
        input_path : Path | str | None, default=None
            Reference identifying the origin of the data currently being extracted.
            None indicates that the extraction process is in-simulation data retrieval.

        Returns
        -------
        Any
            The value extracted from the data.

        Raises
        ------
        KeyError
            If the value cannot be extracted from the data using the provided variable path.

        Examples
        --------
        >>> data_validator = DataValidator()
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
        >>> DataValidator.extract_value_by_key_list(example_data, var_path)
        8

        >>> data_validator = DataValidator()
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
        >>> DataValidator.extract_value_by_key_list(example_data, var_path)
        'straw'
        """
        for key in variable_path:
            if isinstance(data, list) and 0 <= int(key) < len(data):
                data = data[int(key)]
            elif isinstance(data, dict) and isinstance(key, str) and key in data:
                data = data[key]
            else:
                if input_path is not None:
                    raise KeyError(
                        f"There is an error at key {key} in path {variable_path} "
                        f"from input source '{input_path}'. Data cannot be extracted."
                    )

                raise KeyError(f"There is an error at key {key} in the path {variable_path}. Data cannot be extracted.")

        return data


class CrossValidator:
    """
    This class is will be utilized for cross-validation.

    Attributes
    ----------
    _alias_pool : dict[str, Any]
        Alias pool storing data for cross validation.
    _event_logs : list[dict[str, str | dict[str, str]]]
        Logs for the events that will be handled by output manager.
    relation_mapping : dict[str, Any]
        A mapping for all the supported relationship evaluation functions.

    """

    def __init__(self) -> None:
        self._alias_pool: dict[str, Any] = {}
        self._event_logs: list[dict[str, str | dict[str, str]]] = []
        self.relation_mapping: dict[str, Callable[[object, object, bool], bool]] = {
            "equal": lambda left, right, eager_termination: self._evaluate_equal_condition(
                left, right, eager_termination
            ),
            "greater": lambda left, right, eager_termination: self._evaluate_greater_condition(
                left, right, eager_termination
            ),
            "greater_or_equal_to": lambda left, right, eager_termination: self._evaluate_greater_or_equal_condition(
                left, right, eager_termination
            ),
            "not_equal": lambda left, right, eager_termination: not self._evaluate_equal_condition(
                left, right, eager_termination
            ),
            "is_of_type": lambda left, right, eager_termination: self._evaluate_is_type(left, right, eager_termination),
            "is_null": lambda left, _right, eager_termination: self._evaluate_is_null(left),
            "regex": lambda left, right, eager_termination: self._evaluate_regex(left, right),
            "is_equal_length": lambda left, right, eager_termination: self._evaluate_equal_data_length(
                left, right, eager_termination
            ),
        }

    def cross_validate_data(
        self, target_and_save_result: dict[str, Any], cross_validation_block: dict[str, Any], eager_termination: bool
    ) -> bool:
        """
        Performs cross-validation on the provided data using the provided cross validation rules.

        Parameters
        ----------
        target_and_save_result : dict[str, Any]
            A dictionary containing the target and save result retrieved from IM to be validated.
        cross_validation_block : dict[str, Any]
            A dictionary containing the cross-validation rules to be applied.
        eager_termination : bool
            Whether to raise an error if the data does not pass cross-validation.

        Returns
        -------
        bool
            A boolean indicating whether the data passed cross-validation.
        """
        self._target_and_save(target_and_save_result)

        apply_when_rules = cross_validation_block.get("apply_when", [])
        apply_when_conditions_satisfied = self._evaluate_condition_clause_array(apply_when_rules, eager_termination)
        if not apply_when_conditions_satisfied:
            return True

        is_cross_validation_successful = True
        validation_rules = cross_validation_block.get("rules", [])
        for rule in validation_rules:
            is_cross_validation_successful = self._evaluate_condition(rule, eager_termination)
            if not is_cross_validation_successful and eager_termination:
                break
        return is_cross_validation_successful

    def _save_to_alias_pool(self, alias_name: str, value: Any) -> None:
        """
        Saves a value to the alias pool with the specified alias name.

        Parameters
        ----------
        alias_name : str
            The name of the alias to be saved.
        value : Any
            The value to be saved.
        """
        self._alias_pool[alias_name] = value

    def _get_alias_value(self, alias_name: str, eager_termination: bool, relationship: str) -> Any:
        """
        Retrieves the value associated with the specified alias name from the alias pool.

        Parameters
        ----------
        alias_name : str
            The alias of the value to retrieve.
        eager_termination : bool
            Whether to raise an error if the expression is not successfully evaluated.
        relationship : str
            The relationship being evaluated.

        Returns
        -------
        Any
            The value associated with the specified alias name from the alias pool.

        Raises
        ------
        KeyError
            Raises the error when the alias name provided does not have value in the alias pool.

        """
        value = self._alias_pool.get(alias_name, None)
        if value is None and relationship != "is_null":
            self._event_logs.append(
                {
                    "error": "Alias name not found.",
                    "message": f"{alias_name} does not exist in the alias pool of cross validator.",
                    "info_map": {
                        "class": self.__class__.__name__,
                        "function": self._get_alias_value.__name__,
                    },
                }
            )
            if eager_termination:
                raise ValueError(f"Cross-validation error: Unknown alias name: {alias_name}")

        return value

    def _target_and_save(self, target_and_save_result: dict[str, Any]) -> None:
        """
        This function handles the "target and save block" in the cross-validation rule.
        It retrieves the value of the target variable from the InputManager variable pool
        and saves it to the alias pool with the specified alias name. It also saves the
        constants defined in the "constants" block to the alias pool with the specified alias.

        Parameters
        ----------
        target_and_save_result : dict[str, dict[str, Any]]
            A dictionary containing the "target and save block" of the cross-validation rule.

        """
        for alias_key, value in target_and_save_result.items():
            self._save_to_alias_pool(alias_key, value)

    def check_target_and_save_block(
        self, target_and_save_block: dict[str, dict[str, Any]], eager_termination: bool
    ) -> None:
        """Check if the target and save block is valid."""
        for section in target_and_save_block.keys():
            if section not in ["variables", "constants"]:
                self._event_logs.append(
                    {
                        "error": "Unsupported Target and Save Block Content",
                        "message": "Only constants or variables keys' content will be processed for retrieving and"
                        f" saving values. Unsupported keys {section} provided.",
                        "info_map": {
                            "class": self.__class__.__name__,
                            "function": self.check_target_and_save_block.__name__,
                        },
                    }
                )
                if eager_termination:
                    raise ValueError(
                        f"Cross-validation error: Unknown target and save block: {section}. "
                        "target_and_save_block should only have variables and constants blocks."
                    )

    def _evaluate_expression(
        self, expression_block: dict[str, Any], eager_termination: bool, relationship: str
    ) -> tuple[Any, bool]:
        """
        Evaluates an expression based on the provided expression block, optionally
        saving the result to the alias pool if the ``save_as`` key is present.

        Parameters
        ----------
        expression_block : dict[str, Any]
            Dictionary containing the expression block to evaluate, with an
            optional ``save_as`` key.
        eager_termination : bool
            Whether to raise an error if the expression is not successfully evaluated.
        relationship : str
            The relationship being evaluated.

        Returns
        -------
        tuple[Any, bool]
            Result of the expression evaluation and a boolean indicating whether
            the expression was successfully evaluated.

        Raises
        ------
        ValueError
            If the expression block contains an unknown operation or missing
            ordered variables.

        Notes
        -----
        Two mutually exclusive sub-block forms are supported for the expression block:

        Aggregation form:
        ``{"aggregation": {"operation": "...", "operands": [...], "mode": "..."}, "save_as": "..."}``

        Array-of-dicts form:
        ``{"for_each": {"in": "...", "field": "...", "value_to_compare": "..." | "field_to_compare": "...",
        "relationship": "...", "mode": "filter" | "enforce"}, "save_as": "..."}``
        """
        if "for_each" in expression_block:
            result, evaluated = self._evaluate_for_each_block(
                expression_block["for_each"], eager_termination, relationship
            )

        elif "aggregation" in expression_block:
            result, evaluated = self._evaluate_aggregation_block(
                expression_block["aggregation"], eager_termination, relationship
            )
        else:
            self._log_cross_validation_error(
                "Unknown expression block",
                f"Unknown expression block: {expression_block}. Supported blocks are 'aggregation' and 'for_each'.",
                self._evaluate_expression.__name__,
            )
            if eager_termination:
                raise ValueError(
                    f"Cross-validation error: Unknown expression block: "
                    f"{expression_block}. Supported blocks are 'aggregation' and 'for_each'."
                )
            return None, False

        if evaluated and "save_as" in expression_block:
            save_as_alias_name: str = expression_block["save_as"]
            self._save_to_alias_pool(alias_name=save_as_alias_name, value=result)
        return result, evaluated

    def _evaluate_aggregation_block(
        self, aggregation_block: dict[str, Any], eager_termination: bool, relationship: str
    ) -> tuple[Any, bool]:
        """
        Evaluates an aggregation block, resolving ordered variables from the alias
        pool and applying the specified aggregation operation.

        Parameters
        ----------
        aggregation_block : dict[str, Any]
            Dictionary containing the aggregation block to evaluate.
        eager_termination : bool
            Whether to raise an error if evaluation fails.
        relationship : str
            The relationship being evaluated, forwarded to alias-pool lookups.

        Returns
        -------
        tuple[Any, bool]
            Aggregated result and ``True`` on success, or ``(None, False)`` on error.

        Raises
        ------
        ValueError
            If ``eager_termination`` is ``True`` and the operation is unknown or
            ``operands`` is empty or missing.

        Notes
        -----
        Expected keys in ``aggregation_block``:

        - ``operation``: aggregation function name (e.g. ``"sum"``, ``"no_op"``).
          Defaults to ``"no_op"`` when absent.
        - ``operands``: list of alias names to resolve and aggregate.
        - ``mode``: ``"element_wise"`` or ``"aggregate"`` — required when any
          resolved variable is a list or dict. Defaults to ``"aggregate"`` for
          scalar variables.

        Examples
        --------
        Sum two scalar aliases:

        .. code-block:: python

            {"operation": "sum", "operands": ["alias_a", "alias_b"]}

        Pass a single alias through without aggregation:

        .. code-block:: python

            {"operation": "no_op", "operands": ["alias_a"]}

        Element-wise operation on a list variable:

        .. code-block:: python

            {"operands": ["alias_list"], "mode": "element_wise"}
        """
        operation = aggregation_block.get("operation", "no_op")
        aggregator = AGGREGATION_FUNCTIONS[operation]
        ordered_variable_alias: list[str] = aggregation_block["operands"]
        ordered_values: list[Any] = []
        for alias_name in ordered_variable_alias:
            value = self._get_alias_value(alias_name, eager_termination, relationship)
            ordered_values.append(value)

        if any(isinstance(value, (list, dict)) for value in ordered_values):
            if not self._validate_expression_block_with_complex_variable_values(
                aggregation_block, ordered_values, eager_termination
            ):
                return None, False
            ordered_values = (
                ordered_values[0] if isinstance(ordered_values[0], list) else list(ordered_values[0].values())
            )
            mode = aggregation_block.get("mode", "aggregate")
            result = ordered_values if mode == "element_wise" else [aggregator(ordered_values)]
        else:
            result = ordered_values if operation == "no_op" else [aggregator(ordered_values)]
        return result, True

    def _resolve_for_each_source(
        self, source_alias: str, eager_termination: bool, outer_relationship: str
    ) -> list[dict[str, Any]] | None:
        """
        Resolves and validates the source array for a ``for_each`` block.

        Looks up ``source_alias`` in the alias pool and confirms the result is a
        ``list[dict]``. Logs an error and optionally raises if the value is absent or
        has the wrong type.

        Parameters
        ----------
        source_alias : str
            Alias name for the ``list[dict]`` value in the alias pool.
        eager_termination : bool
            Whether to raise on error.
        outer_relationship : str
            Operator of the enclosing condition clause, forwarded to alias-pool lookups.

        Returns
        -------
        list[dict[str, Any]] or None
            The resolved array on success, or ``None`` on error.
        """
        array = self._get_alias_value(source_alias, eager_termination, outer_relationship)
        if array is None or not (isinstance(array, list) and all(isinstance(entry, dict) for entry in array)):
            self._log_cross_validation_error(
                "Invalid data address",
                f"'{source_alias}' must resolve to a list of dicts in the alias pool.",
                self._resolve_for_each_source.__name__,
            )
            if eager_termination:
                raise ValueError(f"Cross-validation error: '{source_alias}' must resolve to a list of dicts.")
            return None
        return cast(list[dict[str, Any]], array)

    def _build_comparand_getter(
        self,
        value_to_compare_alias: str | None,
        field_to_compare: str | None,
        eager_termination: bool,
        outer_relationship: str,
    ) -> Callable[[dict[str, Any]], list[Any]] | None:
        """
        Builds a callable that produces the right-hand comparison value for each entry.

        When ``value_to_compare_alias`` is given, the alias is resolved once from the pool
        and the same value is reused for every entry. When ``field_to_compare`` is given,
        the value is read from that key within each entry at call time.

        Parameters
        ----------
        value_to_compare_alias : str or None
            Alias name for a scalar comparison value. Mutually exclusive with
            ``field_to_compare``.
        field_to_compare : str or None
            Key within each dict entry to use as the right-hand value. Mutually exclusive
            with ``value_to_compare_alias``.
        eager_termination : bool
            Whether to raise on alias-pool lookup error.
        outer_relationship : str
            Operator of the enclosing condition clause, forwarded to alias-pool lookups.

        Returns
        -------
        Callable[[dict[str, Any]], list[Any]] or None
            A callable ``(entry) -> list`` on success, or ``None`` if alias resolution
            fails.
        """
        if value_to_compare_alias is not None:
            comparison_value = self._get_alias_value(value_to_compare_alias, eager_termination, outer_relationship)
            if comparison_value is None:
                return None
            if not isinstance(comparison_value, list):
                comparison_value = [comparison_value]
            return lambda _entry: comparison_value
        assert field_to_compare is not None
        return lambda entry: [entry.get(field_to_compare)]

    def _evaluate_for_each_block(
        self, iter_block: dict[str, Any], eager_termination: bool, outer_relationship: str
    ) -> tuple[Any, bool]:
        """
        Evaluates a ``for_each`` block against a list of dicts in the alias pool.

        Parameters
        ----------
        iter_block : dict[str, Any]
            Dictionary describing how to iterate the array.
        eager_termination : bool
            Whether to raise on error.
        outer_relationship : str
            The operator of the enclosing condition clause, used for alias-pool
            error handling.

        Returns
        -------
        tuple[Any, bool]
            ``(result, True)`` on success or ``(None, False)`` on error.

        Notes
        -----
        Expected keys in ``iter_block``:

        - ``in``: alias for the ``list[dict]`` value in the alias pool.
        - ``field``: key within each dict entry to evaluate.
        - ``value_to_compare``: alias for a scalar comparison value. Mutually
          exclusive with ``field_to_compare``.
        - ``field_to_compare``: key within each dict entry used as the right-hand
          comparand. Mutually exclusive with ``value_to_compare``.
        - ``relationship``: one of the supported relationship strings (e.g. ``"equal"``).
        - ``mode``: ``"filter"`` to return the matching subset; ``"enforce"`` to
          return ``[True]`` when all entries satisfy, otherwise ``[False]``.

        Examples
        --------
        Filter entries where ``"status"`` equals a scalar alias:

        .. code-block:: python

            {
                "in": "alias_list",
                "field": "status",
                "value_to_compare": "alias_status",
                "relationship": "equal",
                "mode": "filter"
            }

        Enforce that all entries have ``"age"`` greater than a peer field:

        .. code-block:: python

            {
                "in": "alias_list",
                "field": "age",
                "field_to_compare": "min_age",
                "relationship": "greater_than",
                "mode": "enforce"
            }
        """
        source_alias: str = iter_block["in"]
        field: str = iter_block["field"]
        value_to_compare_alias: str | None = iter_block.get("value_to_compare", None)
        field_to_compare: str | None = iter_block.get("field_to_compare", None)
        relationship: str = iter_block["relationship"]
        mode: str = iter_block["mode"]

        compare_function = self.relation_mapping[relationship]

        array_of_dicts = self._resolve_for_each_source(source_alias, eager_termination, outer_relationship)
        if array_of_dicts is None:
            return None, False

        comparand_for = self._build_comparand_getter(
            value_to_compare_alias, field_to_compare, eager_termination, outer_relationship
        )
        if comparand_for is None:
            return None, False

        if mode == "filter":
            return [
                entry
                for entry in array_of_dicts
                if compare_function([entry.get(field)], comparand_for(entry), eager_termination)
            ], True
        else:
            return [
                all(
                    compare_function([entry.get(field)], comparand_for(entry), eager_termination)
                    for entry in array_of_dicts
                )
            ], True

    def _validate_expression_block_with_complex_variable_values(
        self, expression_block: dict[str, Any], ordered_values: list[Any], eager_termination: bool
    ) -> bool:
        """
        Validates an expression block when it contains complex variables.

        This method checks the validity of an expression block if it includes complex variables
        (such as lists or dictionaries) and ensures it adheres to predefined rules. Validation
        errors are logged, and eager termination behavior is enforced if specified.

        Parameters
        ----------
        expression_block : dict[str, Any]
            A dictionary representing the expression block to be validated.
        ordered_values : list[Any]
            A list of variables involved in the evaluation. Only one list or dictionary variable
            is permitted for cross-validation in a single block.
        eager_termination : bool
            Specifies whether to immediately terminate the process when a validation error is
            encountered.

        Raises
        ------
        ValueError
            -If multiple complex variables are selected for cross-validation in a single expression block.
            -If the 'mode' key is missing in the expression block when a complex variable is selected.
            -If the 'mode' value is not one of the expected options ('element_wise' or 'aggregate').

        Returns
        -------
        bool
            Returns True if the expression block is valid, otherwise False if eager termination
            is disabled.
        """
        if len(ordered_values) > 1:
            self._log_cross_validation_error(
                "Multiple Complex Variables Selected",
                "Only one list or dict variable can be selected for cross validation in a single expression block.",
                self._validate_expression_block_with_complex_variable_values.__name__,
            )
            if eager_termination:
                raise ValueError(
                    "Cross-validation error: Only one list or dict variable can be selected for cross validation in "
                    "a single expression block."
                )
            else:
                return False

        if "mode" not in expression_block:
            self._log_cross_validation_error(
                "Missing `mode` key",
                "The 'mode' key is required in aggregation block when a complex data structure is selected.",
                self._validate_expression_block_with_complex_variable_values.__name__,
            )
            if eager_termination:
                raise ValueError(
                    "Cross-validation error: Missing 'mode' key in aggregation block for "
                    "selected complex data structure."
                )
            else:
                return False
        return True

    def _validate_expression_block(self, expression_block: dict[str, Any], eager_termination: bool) -> bool:
        """
        Validates the structure of an expression block before evaluation.

        Dispatches to the appropriate sub-validator based on which top-level key
        is present.

        Parameters
        ----------
        expression_block : dict[str, Any]
            The expression block to validate.
        eager_termination : bool
            Whether to raise on the first error.

        Returns
        -------
        bool
            ``True`` if the block is structurally valid, ``False`` otherwise.

        Raises
        ------
        ValueError
            If ``eager_termination`` is ``True`` and a structural error is detected.

        Notes
        -----
        The following rules are enforced:

        - Exactly one of ``aggregation`` or ``for_each`` must be present:
            - A block containing both keys is invalid.
            - A block containing neither key is invalid.
        """
        if "aggregation" in expression_block and "for_each" not in expression_block:
            return self._validate_aggregation_block_structure(expression_block["aggregation"], eager_termination)
        if "for_each" in expression_block and "aggregation" not in expression_block:
            return self._validate_for_each_block_structure(expression_block["for_each"], eager_termination)
        self._log_cross_validation_error(
            "Missing expression block",
            "Expression block must contain either an 'aggregation' or a 'for_each' sub-block.",
            self._validate_expression_block.__name__,
        )
        if eager_termination:
            raise ValueError(
                "Cross-validation error: Expression block must contain either an 'aggregation' "
                "or a 'for_each' sub-block."
            )
        return False

    def _validate_aggregation_block_structure(self, aggregation_block: dict[str, Any], eager_termination: bool) -> bool:
        """
        Validates the structure of an aggregation block.

        Parameters
        ----------
        aggregation_block : dict[str, Any]
            The ``aggregation`` sub-dict to validate.
        eager_termination : bool
            Whether to raise on the first error.

        Returns
        -------
        bool
            ``True`` if the block is structurally valid, ``False`` otherwise.

        Raises
        ------
        ValueError
            If ``eager_termination`` is ``True`` and a structural error is detected.

        Notes
        -----
        The following rules are enforced:

        - ``operands`` must be a non-empty list.
        - When ``operands`` has more than one entry, ``operation`` must be provided
          and cannot be ``"no_op"``.
        - ``operation``, when provided, must be a known aggregation function.
        - ``mode``, when provided, must be ``"element_wise"`` or ``"aggregate"``.
        """
        function_name = self._validate_aggregation_block_structure.__name__

        operands = aggregation_block.get("operands")
        if not isinstance(operands, list) or len(operands) == 0:
            self._log_cross_validation_error(
                "Invalid operands",
                "'operands' must be a non-empty list in aggregation block.",
                function_name,
            )
            if eager_termination:
                raise ValueError("Cross-validation error: 'operands' must be a non-empty list in aggregation block.")
            return False

        operation = aggregation_block.get("operation")
        if len(operands) > 1:
            if not operation or operation == "no_op":
                self._log_cross_validation_error(
                    "Invalid operation for multi-operand aggregation",
                    "When 'operands' has more than one entry, 'operation' must be provided and " "cannot be 'no_op'.",
                    function_name,
                )
                if eager_termination:
                    raise ValueError(
                        "Cross-validation error: 'operation' must be provided and cannot be 'no_op' "
                        "when 'operands' has more than one entry."
                    )
                return False

        if operation is not None and operation not in AGGREGATION_FUNCTIONS:
            self._log_cross_validation_error(
                "Unknown aggregation operation",
                f"Unknown operation '{operation}' in aggregation block. "
                f"Expected one of {list(AGGREGATION_FUNCTIONS.keys())}.",
                function_name,
            )
            if eager_termination:
                raise ValueError(f"Cross-validation error: Unknown operation '{operation}' in aggregation block.")
            return False

        mode = aggregation_block.get("mode")
        if mode is not None and mode not in ("element_wise", "aggregate"):
            self._log_cross_validation_error(
                "Invalid mode in aggregation block",
                f"Invalid mode '{mode}' in aggregation block. " "Must be 'element_wise' or 'aggregate'.",
                function_name,
            )
            if eager_termination:
                raise ValueError(f"Cross-validation error: Invalid mode '{mode}' in aggregation block.")
            return False

        return True

    def _validate_for_each_block_structure(self, for_each_block: dict[str, Any], eager_termination: bool) -> bool:
        """
        Validates the structure of a ``for_each`` block.

        Parameters
        ----------
        for_each_block : dict[str, Any]
            The ``for_each`` sub-dict to validate.
        eager_termination : bool
            Whether to raise on the first error.

        Returns
        -------
        bool
            ``True`` if the block is structurally valid, ``False`` otherwise.

        Raises
        ------
        ValueError
            If ``eager_termination`` is ``True`` and a structural error is detected.

        Notes
        -----
        The following rules are enforced:

        - ``mode`` must be present and be either ``"enforce"`` or ``"filter"``.
        - ``in`` and ``field`` must both be present and non-empty.
        - Exactly one of ``value_to_compare`` or ``field_to_compare`` must be provided.
        - ``relationship`` must be present and be a known relation string.
        """
        function_name = self._validate_for_each_block_structure.__name__

        mode = for_each_block.get("mode")
        if mode not in ("enforce", "filter"):
            self._log_cross_validation_error(
                "Invalid or missing mode in for_each block",
                f"'mode' must be 'enforce' or 'filter' in for_each block. Got: {mode!r}.",
                function_name,
            )
            if eager_termination:
                raise ValueError("Cross-validation error: 'mode' must be 'enforce' or 'filter' in for_each block.")
            return False

        missing = [key for key in ("in", "field") if not for_each_block.get(key)]
        if missing:
            self._log_cross_validation_error(
                "Missing required keys in for_each block",
                f"Missing required key(s) {missing} in for_each block.",
                function_name,
            )
            if eager_termination:
                raise ValueError(f"Cross-validation error: Missing required key(s) {missing} in for_each block.")
            return False

        has_value_to_compare = "value_to_compare" in for_each_block
        has_field_to_compare = "field_to_compare" in for_each_block
        if has_value_to_compare == has_field_to_compare:
            self._log_cross_validation_error(
                "Invalid comparison target in for_each block",
                "Exactly one of 'value_to_compare' or 'field_to_compare' must be provided in " "for_each block.",
                function_name,
            )
            if eager_termination:
                raise ValueError(
                    "Cross-validation error: Exactly one of 'value_to_compare' or 'field_to_compare' "
                    "must be provided in for_each block."
                )
            return False

        relationship = for_each_block.get("relationship")
        if relationship not in self.relation_mapping:
            self._log_cross_validation_error(
                "Invalid or missing relationship in for_each block",
                f"'relationship' must be one of {list(self.relation_mapping.keys())}. " f"Got: {relationship!r}.",
                function_name,
            )
            if eager_termination:
                raise ValueError(f"Cross-validation error: Invalid relationship '{relationship}' in for_each block.")
            return False

        return True

    def _evaluate_condition(self, condition_clause: dict[str, Any], eager_termination: bool) -> bool:
        """
        Evaluates if a single condition is satisfied based on the provided condition clause.

        Parameters
        ----------
        condition_clause : dict[str, Any]
            The condition clause to be evaluated.
        eager_termination : bool
            Specifies whether to immediately terminate the process when a validation error is
            encountered.

        Returns
        -------
        bool
            A boolean indicating whether the condition is satisfied.

        """
        if not self._validate_condition_clause(condition_clause, eager_termination):
            return False
        relationship = condition_clause.get("relationship", "")
        left_hand, left_evaluated = self._evaluate_expression(
            condition_clause["left_hand"], eager_termination, relationship
        )
        right_hand, right_evaluated = self._evaluate_expression(
            condition_clause["right_hand"], eager_termination, relationship
        )

        if not (left_evaluated and right_evaluated):
            return False

        evaluation_function = self.relation_mapping[condition_clause["relationship"]]
        return evaluation_function(left_hand, right_hand, eager_termination)

    def _validate_condition_clause(self, condition_clause: dict[str, Any], eager_termination: bool) -> bool:
        """Validate the whole condition block."""
        left_expression = condition_clause.get("left_hand", False)
        right_expression = condition_clause.get("right_hand", False)
        relationship = condition_clause.get("relationship", False)
        fields = {
            "left hand": left_expression,
            "right hand": right_expression,
            "relationship": relationship,
        }
        valid = True
        if self._validate_relationship(relationship, eager_termination):
            missing = [name for name, val in fields.items() if val is False]
            for name in missing:
                self._log_missing_condition_clause_field(name)
            if missing and eager_termination:
                raise KeyError("Cross-validation error: Missing required field in conditional clause.")
            elif missing:
                valid = False

        else:
            valid = False

        if valid:
            for expression in (left_expression, right_expression):
                if not self._validate_expression_block(expression, eager_termination):
                    valid = False

        return valid

    def _log_missing_condition_clause_field(self, missing_field: str) -> None:
        """Helper method to log the missing essential field in conditional clause."""
        self._event_logs.append(
            {
                "error": "Missing required condition clause field",
                "message": f"Missing the {missing_field} field in condition clause.",
                "info_map": {
                    "class": self.__class__.__name__,
                    "function": self._log_missing_condition_clause_field.__name__,
                },
            }
        )

    def _log_cross_validation_error(self, error: str, message: str, function_name: str) -> None:
        """Append a standardized cross-validation error entry to the event log."""
        self._event_logs.append(
            {
                "error": error,
                "message": message,
                "info_map": {
                    "class": self.__class__.__name__,
                    "function": function_name,
                },
            }
        )

    def _validate_relationship(self, relationship: Any, eager_termination: bool) -> bool:
        """Validate if a valid relationship check is given."""
        available_relationship = self.relation_mapping.keys()
        if not isinstance(relationship, str):
            self._event_logs.append(
                {
                    "error": "Relationship must be a string.",
                    "message": f"Relationship block must be a string, got: {type(relationship)}.",
                    "info_map": {
                        "class": self.__class__.__name__,
                        "function": self._validate_relationship.__name__,
                    },
                }
            )
            if eager_termination:
                raise ValueError("Cross-validation error: Conditional clause relationship must be a string.")
            return False
        elif relationship not in available_relationship:
            self._event_logs.append(
                {
                    "error": "Invalid relationship.",
                    "message": f"Relationship block must be one of {available_relationship}," f" got: {relationship}.",
                    "info_map": {
                        "class": self.__class__.__name__,
                        "function": self._validate_relationship.__name__,
                    },
                }
            )
            if eager_termination:
                raise ValueError("Cross-validation error: Invalid conditional clause relationship provided.")
            return False
        else:
            return True

    def _evaluate_pairwise_condition(
        self,
        left_hand_value: Any,
        right_hand_value: Any,
        comparison_function: Callable[[Any, Any], bool],
        eager_termination: bool,
    ) -> bool:
        """Evaluate a comparison for two values.

        When both inputs are lists, compare their values pairwise and require every comparison to pass. Otherwise,
        compare the two input values directly.

        Parameters
        ----------
        left_hand_value : Any
            Value on the left side of the comparison.
        right_hand_value : Any
            Value on the right side of the comparison.
        comparison_function : Callable[[Any, Any], bool]
            Function that evaluates the relationship between two values.
        eager_termination : bool
            Whether to raise an error immediately when pairwise list lengths differ.

        Returns
        -------
        bool
            True when the direct comparison passes, or when all pairwise comparisons pass.
        """
        if isinstance(left_hand_value, list) and isinstance(right_hand_value, list):
            if len(left_hand_value) != len(right_hand_value):
                self._event_logs.append(
                    {
                        "error": "Unequal list lengths for pairwise comparison",
                        "message": "Both lists must have equal length for pairwise comparison.",
                        "info_map": {
                            "class": self.__class__.__name__,
                            "function": self._evaluate_pairwise_condition.__name__,
                        },
                    }
                )
                if eager_termination:
                    raise ValueError("Cross-validation error: Lists must have equal length for pairwise comparison.")
                return False
            return all(comparison_function(left, right) for left, right in zip(left_hand_value, right_hand_value))
        return comparison_function(left_hand_value, right_hand_value)

    def _evaluate_equal_data_length(self, left_hand_value: Any, right_hand_value: Any, eager_termination: bool) -> bool:
        """Evaluates if two lists have the same length."""
        if not (isinstance(left_hand_value, list) and isinstance(right_hand_value, list)):
            self._event_logs.append(
                {
                    "error": "Invalid data length validation",
                    "message": "Both data have to be list type to validate their length.",
                    "info_map": {
                        "class": self.__class__.__name__,
                        "function": self._evaluate_equal_data_length.__name__,
                    },
                }
            )
            if eager_termination:
                raise ValueError("Cross-validation error: Invalid type comparison.")
            return False
        return len(left_hand_value) == len(right_hand_value)

    def _evaluate_equal_condition(
        self, left_hand_value: Any, right_hand_value: Any, eager_termination: bool = False
    ) -> bool:
        """Evaluates equal condition."""
        return bool(
            self._evaluate_pairwise_condition(
                left_hand_value, right_hand_value, lambda left, right: left == right, eager_termination
            )
        )

    def _evaluate_greater_condition(
        self, left_hand_value: Any, right_hand_value: Any, eager_termination: bool = False
    ) -> bool:
        """Evaluates greater than condition"""
        return bool(
            self._evaluate_pairwise_condition(
                left_hand_value, right_hand_value, lambda left, right: left > right, eager_termination
            )
        )

    def _evaluate_greater_or_equal_condition(
        self, left_hand_value: Any, right_hand_value: Any, eager_termination: bool = False
    ) -> bool:
        """Evaluates greater than or equal to condition."""
        return bool(
            self._evaluate_pairwise_condition(
                left_hand_value, right_hand_value, lambda left, right: left >= right, eager_termination
            )
        )

    def _evaluate_is_null(self, left_hand_value: Any) -> bool:
        """Evaluates is null condition."""
        return bool(all(value is None for value in left_hand_value))

    def _evaluate_is_type(self, left_hand_value: Any, data_type: Any, eager_termination: bool) -> bool:
        """Evaluates the if_type condition"""
        if not isinstance(data_type[0], str):
            self._event_logs.append(
                {
                    "error": "Invalid type validation",
                    "message": f"Must indicate the type to compare in string data type, got: {type(data_type)}",
                    "info_map": {
                        "class": self.__class__.__name__,
                        "function": self._evaluate_is_type.__name__,
                    },
                }
            )
            if eager_termination:
                raise ValueError("Cross-validation error: Invalid type comparison.")
            return False
        data_type = data_type[0].strip().lower()
        checkers: dict[str, Callable[[Any], bool]] = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "float": lambda v: isinstance(v, float),
            "boolean": lambda v: isinstance(v, bool),
            "number": lambda v: (isinstance(v, (int, float)) and not isinstance(v, bool)),
        }
        checker = checkers.get(data_type)
        if checker is None:
            supported = ", ".join(sorted({k for k in checkers}))
            self._event_logs.append(
                {
                    "error": "Invalid data type expectation.",
                    "message": f"Unsupported data type {data_type}. Supported types: {supported}.",
                    "info_map": {
                        "class": self.__class__.__name__,
                        "function": self._evaluate_is_type.__name__,
                    },
                }
            )
            if eager_termination:
                raise ValueError(
                    f"Cross-validation error: Unsupported data type: {data_type}. " f"Supported types: {supported}."
                )
            return False

        return bool(all(checker(value) for value in left_hand_value))

    def _evaluate_regex(self, left_hand_value: Any, right_hand_value: Any) -> bool:
        """
        Check if a value matches a given regex pattern.

        Parameters
        ----------
        left_hand_value : str
            The string to check.
        right_hand_value : str
            The regex pattern to match.

        Returns
        -------
        bool
            True if the value fully matches the regex pattern, otherwise False.
        """
        return bool(re.fullmatch(right_hand_value, left_hand_value) is not None)

    def _evaluate_condition_clause_array(
        self, condition_clause_array: list[dict[str, Any]], eager_termination: bool
    ) -> bool:
        """
        Evaluates if all conditions in the provided condition clause array are satisfied.

        Parameters
        ----------
        condition_clause_array : list[dict[str, Any]]
            An array of condition clauses to be evaluated.
        eager_termination : bool
            Specifies whether to immediately terminate the process when a validation error is
            encountered.

        Returns
        -------
        bool
            A boolean indicating whether all conditions in the array are satisfied.
        """
        for clause in condition_clause_array:
            satisfied = self._evaluate_condition(clause, eager_termination)
            if not satisfied:
                self._event_logs.append(
                    {
                        "log": "Unsatisfied condition clause in conditional clause array.",
                        "message": f"Condition not satisfied for condition clause: {clause}",
                        "info_map": {
                            "class": self.__class__.__name__,
                            "function": self._evaluate_condition_clause_array.__name__,
                        },
                    }
                )
                return False
        return True
