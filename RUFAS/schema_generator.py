import json
from pathlib import Path
from typing import Any, Callable
import re

from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility

DEFAULT_PROPERTIES_PATH: Path = Path("").joinpath("input", "metadata", "default_metadata.json")
DEFAULT_SCHEMA_OUTPUT_PATH: Path = Path("data_collection_app_schemas")

om = OutputManager()


class SchemaGenerator:
    """
    This class provides a suite of methods for automatically updating the JSON schemas for the Data Collection App based
    on the properties contained in the metadata.

    Methods
    -------
    generate_schemas(path_to_properties, path_to_schemas)
        Manages the I/0 and subroutines of creating new schemas.
    setup_number_schema(title, input_properties)
        Creates the JSON editor schema for a 'number' type.
    setup_bool_schema(title, input_properties)
        Creates the JSON editor schema for a 'bool' type.
    setup_string_schema(title, input_properties)
        Creates the JSON editor schema for a 'string' type.
    setup_array_schema(title, input_properties)
        Creates the JSON editor schema for an 'array' type.
    setup_object_schema(title, input_properties)
        Creates the JSON editor schema for an 'object' type.

    """

    def generate_schemas(self, path_to_properties: str | None, path_to_schema_outputs: str | None) -> None:
        """
        Produces updated schemas for the Data Collection App.

        Parameters
        ----------
        path_to_properties : str | None
            Path to the metadata properties from which the schemas will be generated. If None, then a default path will
            be used.
        path_to_schema_outputs : str | None
            Path to the location where the schemas should be written to. If None, then the schemas will be put in a
            default location.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.generate_schemas.__name__
        }

        path_to_properties = path_to_properties if path_to_properties else DEFAULT_PROPERTIES_PATH

        log_title = "Schema generation starting"
        log_message = f"Creating new schemas from metadata properties in '{path_to_properties}'"
        om.add_log(log_title, log_message, info_map)

        schema_output_path = path_to_schema_outputs if path_to_schema_outputs else DEFAULT_SCHEMA_OUTPUT_PATH
        keep_list = [".keep"]
        Utility.empty_dir(schema_output_path, keep_list)

        with open(path_to_properties) as metadata:
            metadata_dict = json.load(metadata)

        properties = metadata_dict["properties"]

        for key in properties.keys():
            try:
                new_schema = SchemaGenerator.setup_object_schema(key, properties[key])
            except Exception as e:
                error_title = "Schema generator raised exception"
                error_message = f"Key: '{key}' raised exception: {str(e)}"
                om.add_error(error_title, error_message, info_map)
                continue

            schema_name = key.replace("properties", "schema")
            new_schema_file_name = f"{schema_name}.json"
            new_schema_file_path = Path.joinpath(schema_output_path, new_schema_file_name)

            log_title = "Schema generator writing new schema"
            log_message = f"Writing new schema in {new_schema_file_path}"
            om.add_log(log_title, log_message, info_map)

            with open(new_schema_file_path, "w") as outfile:
                json.dump(new_schema, outfile, indent=2)

    @staticmethod
    def setup_number_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
        """
        Creates an input schema for a numerical input.

        Parameters
        ----------
        title : str
            The name of the variable for which this schema is being created.
        input_properties : dict[str, Any]
            The properties of the input variable.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the input schema for this variable.

        """
        schema = {
            "title": title,
            "type": "number",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            }
        }
        minimum = input_properties.get("minimum")
        maximum = input_properties.get("maximum")
        default = input_properties.get("default")
        description = input_properties.get("description")

        if minimum is not None:
            schema["minimum"] = minimum
        if maximum is not None:
            schema["maximum"] = maximum
        if default is not None:
            schema["default"] = default
        if description:
            schema["options"]["infoText"] = description

        return schema

    @staticmethod
    def setup_bool_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
        schema = {
            "title": title,
            "type": "boolean",
            "format": "checkbox",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            }
        }
        default = input_properties.get("default")
        description = input_properties.get("description")

        if default is not None:
            schema["default"] = default
        if description is not None:
            schema["options"]["infoText"] = description

        return schema

    @staticmethod
    def setup_string_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
        """
        Creates an input schema for a string input.

        Parameters
        ----------
        title : str
            The name of the variable for which this schema is being created.
        input_properties : dict[str, Any]
            The properties of the input variable.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the input schema for this variable.

        """
        schema = {
            "title": title,
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            }
        }
        default = input_properties.get("default")
        pattern = input_properties.get("pattern")
        description = input_properties.get("description")

        if default is not None:
            schema["default"] = default
        if description is not None:
            schema["options"]["infoText"] = description
        if pattern is not None:
            try:
                enum = SchemaGenerator._get_list_of_options(pattern)
            except ValueError as e:
                info_map = {
                    "class": SchemaGenerator.__name__,
                    "function": SchemaGenerator.setup_string_schema.__name__
                }
                om.add_error(
                    "Schema generation for string input encountered error",
                    f"Variable {title=} had error: {str(e)}",
                    info_map
                )
                return schema
            schema["enum"] = enum
            schema["format"] = "select2"

        return schema

    @staticmethod
    def _get_list_of_options(input_pattern: str) -> list[str]:
        """
        Gets a list of acceptable string inputs based on the Regex pattern that is used to validate the input.

        Parameters
        ----------
        input_pattern : str
            The Regex pattern that is used to determine if a string input is valid or not.

        Returns
        -------
        list[str]
            List of strings that would be valid when checked against the input pattern.

        Raises
        ------
        ValueError
            If the Regex pattern used for validation does not adhere to the format "^(<option 1>|<option 2>|...)$".

        Notes
        -----
        When a string input is taken, often it is to select from a preset group of options. This method is designed to
        derive those options from the Regex pattern that is used to validate it.

        """
        pattern = "\\^\\(.*\\)\\$"
        is_valid_pattern = bool(re.match(pattern, input_pattern))
        if not is_valid_pattern:
            raise ValueError(f"'{input_pattern}' is not a valid pattern. Cannot create list of valid options.")

        unsplit_list = input_pattern[2:-2]
        split_list = unsplit_list.split("|")
        return split_list

    @staticmethod
    def setup_array_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
        """
        Creates an input schema for an array input.

        Parameters
        ----------
        title : str
            The name of the variable for which this schema is being created.
        input_properties : dict[str, Any]
            The properties of the input variable.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the input schema for this variable.

        """
        schema = {
            "title": title,
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            }
        }
        default = input_properties.get("default")
        description = input_properties.get("description")

        if default is not None:
            schema["default"] = default
        if description is not None:
            schema["options"]["infoText"] = description

        element_properties = input_properties["properties"]
        element_schema_creator = SchemaGenerator.DATA_TYPE_TO_SCHEMA_SETUP_MAP[element_properties["type"]]
        element_title = title + "_element"
        element_property_dictionary = element_schema_creator(element_title, element_properties)
        schema["items"] = element_property_dictionary

        return schema

    @staticmethod
    def setup_object_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
        """
        Creates an input schema for an object input.

        Parameters
        ----------
        title : str
            The name of the variable for which this schema is being created.
        input_properties : dict[str, Any]
            The properties of the input variable.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the input schema for this variable.

        """
        schema = {
            "title": title,
            "type": "object",
            "format": "grid",
            "properties": {}
        }
        default = input_properties.get("default")
        description = input_properties.get("description")

        if default is not None:
            schema["default"] = default
        if description is not None:
            schema["options"] = {}
            schema["options"]["infoText"] = description

        ignored_keys = ["type", "description", "default"]
        keys = [key for key in input_properties.keys() if key not in ignored_keys]

        for key in keys:
            sub_property = input_properties[key]
            schema_setup_method = SchemaGenerator.DATA_TYPE_TO_SCHEMA_SETUP_MAP[sub_property["type"]]
            sub_property_schema = schema_setup_method(key, sub_property)
            schema["properties"][key] = sub_property_schema

        return schema

    DATA_TYPE_TO_SCHEMA_SETUP_MAP: dict[str, Callable[[str, dict[str, Any]], dict[str, Any]]] = {
        "number": setup_number_schema,
        "bool": setup_bool_schema,
        "string": setup_string_schema,
        "array": setup_array_schema,
        "object": setup_object_schema
    }
