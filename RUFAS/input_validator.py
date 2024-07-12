import os
from enum import Enum
from typing import Dict, Any, Callable

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

    @staticmethod
    def _validate_metadata(metadata: Dict[str, Any]) -> None:
        """Checks that top-level metadata has valid and required keys and values."""
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
