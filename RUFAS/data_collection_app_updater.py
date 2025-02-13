import copy
import json
from pathlib import Path
from typing import Any, Callable
import re

import pandas as pd

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility

"""Directory path for writing updated schema."""
SCHEMA_DIRECTORY_PATH: Path = Path("").joinpath("DataCollectionApp", "schema")

"""Path to the home page of the Data Collection App."""
INDEX_PATH: Path = Path("").joinpath("DataCollectionApp", "index.html")

"""Path to the template for regenerating the Data Collection App's home page."""
TEMPLATE_PATH: Path = Path("").joinpath("DataCollectionApp", "template")

"""Directory to the available user feed inputs."""
USER_FEED_PATH: Path = Path("").joinpath("input", "data", "feed", "user_feeds.csv")

"""Path to the feed_schema.js schema file."""
FEED_SCHEMA_PATH: Path = Path("").joinpath("DataCollectionApp", "schema", "feed_schema.js")

"""Placeholder for inserting schema import scripts in index.html."""
SCHEMA_SCRIPT_TAG_PLACEHOLDER: str = "    <!-- Schema imports go here-->"

"""Placeholder for listing newly available schemas in the rewritten index.html."""
AVAILABLE_SCHEMAS_LIST_PLACEHOLDER: str = "// List of available schema goes here"

"""Fallback placeholder in a DCA input field if no value has been entered into it."""
INPUT_PLACEHOLDER: str = "null"


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

    def update_data_collection_app(self, task_manager_metadata_properties: dict[str, Any]) -> None:
        """
        Updates schemas for collection of RuFaS inputs in the Data Collection App.

        Parameters
        ----------
        task_manager_metadata_properties : dict[str, Any]
            Properties Task Manager inputs.

        """
        schema_paths = self._rewrite_schemas(task_manager_metadata_properties)
        self._rewrite_index_page(schema_paths)
        self.update_feed_schema(self.gather_feed_data())

    def _rewrite_schemas(self, task_manager_metadata_properties: dict[str, Any]) -> list[Path]:
        """
        Rewrites schemas in the Data Collection App using the input properties found in the Input Manager.

        Parameters
        ----------
        task_manager_metadata_properties : dict[str, Any]
            Properties Task Manager inputs.

        Returns
        -------
        list[str]
            List of file names of the rewritten schema.

        """
        info_map = {"class": self.__class__.__name__, "function": self.update_data_collection_app.__name__}

        self._om.add_log("Schema generation starting", "Creating new schemas from metadata properties.", info_map)

        Utility.empty_dir(SCHEMA_DIRECTORY_PATH, [".keep"])

        properties: dict[str, Any] = self._im.meta_data["properties"]
        properties = properties | task_manager_metadata_properties

        schema_paths = []

        for key in properties.keys():
            data_collection_app_compatible = properties[key].get("data_collection_app_compatible", False)
            if not data_collection_app_compatible:
                continue
            schema_dict = {
                property_name: property_value
                for property_name, property_value in properties[key].items()
                if property_name != "data_collection_app_compatible"
            }
            new_schema = self._create_object_schema(key, schema_dict)
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
        list_of_schema = f'"oneOf": {schema_names}'.replace("'", "")
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
            "options": {"grid_columns": 12, "inputAttributes": {"class": "text-primary form-control"}},
        }
        minimum = input_properties.get("minimum")
        maximum = input_properties.get("maximum")
        default = input_properties.get("default")
        description = input_properties.get("description")
        nullable = input_properties.get("nullable")

        if minimum is not None:
            schema["minimum"] = minimum
        if maximum is not None:
            schema["maximum"] = maximum
        schema["default"] = default
        schema["options"]["inputAttributes"]["placeholder"] = default or minimum or maximum or INPUT_PLACEHOLDER
        schema["options"]["infoText"] = description
        schema["type"] = ["number", "null"] if nullable else "number"

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
            "format": "checkbox",
            "options": {"grid_columns": 12, "inputAttributes": {"class": "text-primary form-control"}},
        }
        default = input_properties.get("default")
        description = input_properties.get("description")
        nullable = input_properties.get("nullable")

        schema["default"] = default
        schema["options"]["infoText"] = description
        schema["options"]["inputAttributes"]["placeholder"] = default or INPUT_PLACEHOLDER
        schema["type"] = ["boolean", "null"] if nullable else "boolean"

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
            "options": {"grid_columns": 12, "inputAttributes": {"class": "text-primary form-control"}},
        }
        default = input_properties.get("default")
        pattern = input_properties.get("pattern")
        description = input_properties.get("description")
        nullable = input_properties.get("nullable")

        schema["default"] = default
        schema["options"]["infoText"] = description
        schema["options"]["inputAttributes"]["placeholder"] = default or INPUT_PLACEHOLDER
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
        schema["type"] = ["string", "null"] if nullable else "string"

        return schema

    def _get_list_of_options(self, input_pattern: str) -> list[str]:
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

        The Regex pattern used to check `input_pattern` ensures there no special characters in-between "^(" and ")$"
        unless they are a bar ("|"), hyphen ("-"), whitespace (" "), or slash ("/").

        Examples
        --------
        >>> DataCollectionAppUpdater._get_list_of_options("^(kg)$")
        ["kg"]
        >>> DataCollectionAppUpdater._get_list_of_options("^(default|no_kill)$")
        ["default", "no_kill"]
        >>> DataCollectionAppUpdater._get_list_of_options("^(TAI|ED|Synch-ED)$")
        ["TAI", "ED", "Synch-ED"]

        """
        pattern = r"\^\((?:(?![^\w|\/ \-']).)*\)\$"
        is_valid_pattern = bool(re.match(pattern, input_pattern))
        if not is_valid_pattern:
            raise ValueError(f"'{input_pattern}' is not a valid pattern. Cannot create list of valid options.")

        unsplit_list = input_pattern[2:-2]  # Removes "^(" and ")$" from the start and end of the string, respectively.
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

        schema["default"] = default
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

        schema["default"] = default
        schema["options"] = {"infoText": description}

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
                    "inputAttributes": {"class": "text-primary form-control", "placeholder": INPUT_PLACEHOLDER},
                    "infoText": "Used to name the file that saves the data entered. This name will not be included in "
                    "the saved file.",
                },
            }
        }
        schema["properties"].update(filename_field)
        return schema

    @staticmethod
    def gather_feed_data() -> dict[str, Any]:
        """Gather the user feed data to update."""
        df = pd.read_csv(USER_FEED_PATH)
        return {
            "id": df["rufas_id"].tolist(),
            "name": [
                f"{name} ({description}) - {rufas_id}"
                for name, description, rufas_id in zip(df["Name"], df["feed_description"], df["rufas_id"])
            ],
        }

    def update_feed_schema(self, user_feed: dict[str, list[Any]]) -> None:
        """
        Main routine to update the structure of feed schema.

        Parameters
        ----------
        user_feed : dict[str, list]
            The user feeds input data parsed so that it can be used to setup dropdowns.

        """
        js_path = FEED_SCHEMA_PATH

        with open(js_path, "r", encoding="utf-8") as file:
            js_content = file.read()
        json_str = js_content.split("=", 1)[1].strip()
        feed_schema = json.loads(json_str)

        feed_schema = self.modify_items_schema(feed_schema, user_feed)

        updated_js_content = f"feed_schema = {json.dumps(feed_schema, indent=4)};"

        with open(js_path, "w", encoding="utf-8") as file:
            file.write(updated_js_content)

    def modify_items_schema(
        self, data: dict[str, Any], dropdown_data: dict[str, list[Any]], skip_first: bool = True
    ) -> dict[str, Any]:
        """
        Modify the schema with dropdowns by updating the corresponding field with updated feed data.

        Parameters
        ----------
        data : dict[str, Any]
            The schema structure.
        dropdown_data : dict[str, list]
            The updated content in the dropdown.
        skip_first : bool, default=True
            Boolean indicators to help skip the first "properties" field

        Returns
        --------
        dict[str, Any]
            Input schema with updated dropdowns.

        """
        new_data = copy.deepcopy(data)
        if isinstance(new_data, dict):
            if "properties" in new_data:
                if skip_first:
                    skip_first = False
                else:
                    for key, value in new_data["properties"].items():
                        if isinstance(value, dict):
                            new_data["properties"][key] = self.modify_items_schema(value, dropdown_data, skip_first)

            if "items" in new_data and isinstance(new_data["items"], dict):
                items_data = new_data.get("items", {})

                if "properties" in items_data and isinstance(items_data["properties"], dict):
                    items_data["properties"] = self.update_first_property_with_enum(
                        items_data["properties"], dropdown_data
                    )

                else:
                    items_data["enum"] = dropdown_data["id"]
                    if "options" not in items_data:
                        items_data["options"] = {}
                    items_data["options"]["enum_titles"] = dropdown_data["name"]

            for key, value in new_data.items():
                new_data[key] = self.modify_items_schema(value, dropdown_data, skip_first)
            return new_data
        else:
            return new_data

    @staticmethod
    def update_first_property_with_enum(properties: dict[Any, Any], dropdown_data: dict[str, Any]) -> dict[Any, Any]:
        """
        Create a new properties dictionary with the first dictionary property.

        Parameters
        ----------
        properties : dict[Any, Any]
            The target properties to update with dropdown menu data.
        dropdown_data : dict[str, Any]
            The data containing the dropdown values to insert.

        Returns
        -------
        dict[Any, Any]
            A new dictionary with the update applied.

        """
        new_properties = copy.copy(properties)
        for key, prop_value in new_properties.items():
            if isinstance(prop_value, dict):
                prop_value["enum"] = dropdown_data["id"]
                prop_value["options"] = {**prop_value.get("options", {}), "enum_titles": dropdown_data["name"]}
                break

        return new_properties
