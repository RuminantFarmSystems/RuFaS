import json
from pathlib import Path
from typing import Any, Callable
import re

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility

"""Directory path for writing updated schema."""
SCHEMA_DIRECTORY_PATH: Path = Path("").joinpath("DataCollectionApp", "schema")

"""Path to the home page of the Data Collection App."""
INDEX_PATH: Path = Path("").joinpath("DataCollectionApp", "index.html")

"""Path to the template for regenerating the Data Collection App's home page."""
TEMPLATE_PATH: Path = Path("").joinpath("DataCollectionApp", "template")

"""
Metadata properties for which the Data Collection App will generate schema.
If a property is not listed, its schema will not be generated.
"""
PROPERTIES_TO_CREATE_SCHEMA_FOR: list[str] = [
    "animal_properties",
    "config_properties",
    "crop_schedule_properties",
    "feed_properties",
    "fertilizer_schedule_properties",
    "field_properties",
    "manure_management_properties",
    "manure_schedule_properties",
    "tillage_schedule_properties",
    "tractor_dataset_properties",
]

"""Placeholder for inserting schema import scripts in index.html."""
SCHEMA_SCRIPT_TAG_PLACEHOLDER: str = "    <!-- Spot where schema import scripts go -->"

"""Placeholder for listing newly available schemas in the rewritten index.html."""
AVAILABLE_SCHEMAS_LIST_PLACEHOLDER: str = "// Spot where list of available schema go"


class DataCollectionAppUpdater:
    """
    This class provides a suite of methods for automatically updating the JSON schemas for the Data Collection App based
    on the properties contained in the metadata.

    Attributes
    ----------
    _im : InputManager
        Instance of the Input Manager.
    _om : OutputManager
        Instance of the Output Manager.
    _type_to_schema_map : dict[str, Callable[[str, dict[str, Any]], dict[str, Any]]]
        Maps types in the metadata properties to methods used to generate schema for those types.

    Methods
    -------
    update_data_collection_app
        Orchestrates updates to the schemas and index page of the Data Collection App.

    """

    def __init__(self) -> None:
        self._im = InputManager()
        self._om = OutputManager()
        self._type_to_schema_map: dict[str, Callable[[str, dict[str, Any]], dict[str, Any]]] = {
            "number": self._create_number_schema,
            "bool": self._create_bool_schema,
            "string": self._create_string_schema,
            "array": self._create_array_schema,
            "object": self._create_object_schema,
        }

    def update_data_collection_app(self) -> None:
        """
        Updates schemas for collection of RuFaS inputs in the Data Collection App.
        """
        schema_paths = self._rewrite_schemas()
        self._rewrite_index_page(schema_paths)

    def _rewrite_schemas(self) -> list[Path]:
        """
        Rewrites schemas in the Data Collection App using the input properties found in the Input Manager.

        Returns
        -------
        list[str]
            List of file names of the rewritten schema.

        """
        info_map = {"class": self.__class__.__name__, "function": self.update_data_collection_app.__name__}

        self._om.add_log("Schema generation starting", "Creating new schemas from metadata properties.", info_map)

        Utility.empty_dir(SCHEMA_DIRECTORY_PATH)

        properties: dict[str, Any] = self._im.meta_data["properties"]

        schema_paths = []
        for key in properties.keys():
            if key not in PROPERTIES_TO_CREATE_SCHEMA_FOR:
                continue

            new_schema = self._create_object_schema(key, properties[key])
            new_schema_with_filename = self._add_filename_input_field(new_schema)

            schema_name = key.replace("properties", "schema")
            new_schema_filename = f"{schema_name}.js"
            new_schema_file_path = Path.joinpath(SCHEMA_DIRECTORY_PATH, new_schema_filename)
            schema_paths.append(new_schema_file_path)

            self._om.add_log(
                "Schema generator writing new schema", f"Writing new schema in {new_schema_file_path}", info_map
            )

            schema_body = json.dumps(new_schema_with_filename, indent=4)
            with open(new_schema_file_path, "w") as outfile:
                outfile.write(f"{schema_name} = {schema_body}")

        return schema_paths

    def _rewrite_index_page(self, schema_paths: list[Path]) -> None:
        """
        Rewrites the index.html page of the Data Collection App to use the newly written schema.

        Parameters
        ----------
        schema_paths : list[Path]
            List of path instances which will be used to link the index page to the input schemas.

        """
        localized_schema_paths = [path.as_posix().replace("DataCollectionApp", ".") for path in schema_paths]

        schema_script_tags = "\n".join(
            [f'    <script src="{schema_path}"></script>' for schema_path in localized_schema_paths]
        )

        with open(TEMPLATE_PATH, "r", encoding="utf-8") as template_file:
            template = template_file.read()

        index_with_script_tags = template.replace(SCHEMA_SCRIPT_TAG_PLACEHOLDER, schema_script_tags)

        pattern_to_remove = r"\./schema/|\.js"
        schema_names = [re.sub(pattern_to_remove, "", name) for name in localized_schema_paths]
        list_of_schema = f'"anyOf": {schema_names}'.replace("'", "")
        rewritten_index = index_with_script_tags.replace(AVAILABLE_SCHEMAS_LIST_PLACEHOLDER, list_of_schema)

        with open(INDEX_PATH, "w", encoding="utf-8") as index:
            index.write(rewritten_index)

    def _create_number_schema(self, var_name: str, input_properties: dict[str, Any]) -> dict[str, Any]:
        """
        Creates an input schema for a numerical input.

        Parameters
        ----------
        var_name : str
            The name of the variable for which this schema is being created.
        input_properties : dict[str, Any]
            The properties of the input variable.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the input schema for this variable.

        """
        title = self._parse_variable_name_into_title(var_name)
        schema: dict[str, Any] = {
            "title": title,
            "type": "number",
            "options": {"grid_columns": 12, "inputAttributes": {"class": "text-primary form-control"}},
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
        if description is not None:
            schema["options"]["infoText"] = description

        return schema

    def _create_bool_schema(self, var_name: str, input_properties: dict[str, Any]) -> dict[str, Any]:
        """
        Creates an input schema for a boolean input.

        Parameters
        ----------
        var_name : str
            The name of the variable for which this schema is being created.
        input_properties : dict[str, Any]
            The properties of the input variable.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the input schema for this variable.

        """
        title = self._parse_variable_name_into_title(var_name)
        schema: dict[str, Any] = {
            "title": title,
            "type": "boolean",
            "format": "checkbox",
            "options": {"grid_columns": 12, "inputAttributes": {"class": "text-primary form-control"}},
        }
        default = input_properties.get("default")
        description = input_properties.get("description")

        if default is not None:
            schema["default"] = default
        if description is not None:
            schema["options"]["infoText"] = description

        return schema

    def _create_string_schema(self, var_name: str, input_properties: dict[str, Any]) -> dict[str, Any]:
        """
        Creates an input schema for a string input.

        Parameters
        ----------
        var_name : str
            The name of the variable for which this schema is being created.
        input_properties : dict[str, Any]
            The properties of the input variable.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the input schema for this variable.

        """
        title = self._parse_variable_name_into_title(var_name)
        schema: dict[str, Any] = {
            "title": title,
            "type": "string",
            "options": {"grid_columns": 12, "inputAttributes": {"class": "text-primary form-control"}},
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
                enum = self._get_list_of_options(pattern)
                schema["enum"] = enum
                schema["format"] = "select2"
            except ValueError:
                info_map = {"class": self.__class__.__name__, "function": self._create_string_schema.__name__}
                self._om.add_warning(
                    "Could not generate list of valid input options for a string input",
                    f"Variable {var_name} will not have drop-down options for Data Collection App users to pick from.",
                    info_map,
                )
                schema["pattern"] = pattern

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

    def _create_array_schema(self, var_name: str, input_properties: dict[str, Any]) -> dict[str, Any]:
        """
        Creates an input schema for an array input.

        Parameters
        ----------
        var_name : str
            The name of the variable for which this schema is being created.
        input_properties : dict[str, Any]
            The properties of the input variable.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the input schema for this variable.

        """
        title = self._parse_variable_name_into_title(var_name)
        schema: dict[str, Any] = {
            "title": title,
            "type": "array",
            "format": "grid",
            "options": {"inputAttributes": {"class": "text-primary form-control"}},
        }
        default = input_properties.get("default")
        description = input_properties.get("description")

        if default is not None:
            schema["default"] = default
        if description is not None:
            schema["options"]["infoText"] = description

        element_properties = input_properties["properties"]
        element_schema_creator = self._type_to_schema_map[element_properties["type"]]
        element_name = var_name + "_element"
        element_property_dictionary = element_schema_creator(element_name, element_properties)
        schema["items"] = element_property_dictionary

        return schema

    def _create_object_schema(self, var_name: str, input_properties: dict[str, Any]) -> dict[str, Any]:
        """
        Creates an input schema for an object input.

        Parameters
        ----------
        var_name : str
            The name of the variable for which this schema is being created.
        input_properties : dict[str, Any]
            The properties of the input variable.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the input schema for this variable.

        """
        title = self._parse_variable_name_into_title(var_name)
        schema: dict[str, Any] = {"title": title, "type": "object", "format": "grid", "properties": {}}
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
            schema_setup_method = self._type_to_schema_map[sub_property["type"]]
            sub_property_schema = schema_setup_method(key, sub_property)
            schema["properties"][key] = sub_property_schema

        return schema

    def _parse_variable_name_into_title(self, variable_name: str) -> str:
        """
        Converts a variable name written all or partially in snake case to a more readable name.

        Parameters
        ----------
        variable_name : str
            The variable name to be converted into a more readable title.

        Returns
        -------
        str
            The variable name with spaces between all words and the first letter of each word capitalized.

        """
        words = re.split(r"[_\s]+", variable_name)
        capitalized_words = [word.capitalize() for word in words]
        return " ".join(capitalized_words)

    def _add_filename_input_field(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Adds field to schema for collecting filename that data will be saved as."""
        filename_field = {
            "fileName": {
                "title": "File Name",
                "type": "string",
                "pattern": r"^[a-zA-Z0-9_\- ]{1,255}$",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {"class": "text-primary form-control"},
                    "infoText": "Used to name the file that saves the data entered. This name will not be included in "
                    "the saved file."
                },
            }
        }
        schema["properties"].update(filename_field)
        return schema
