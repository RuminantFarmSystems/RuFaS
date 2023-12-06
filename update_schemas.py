import json
from pathlib import Path
from typing import Any, Callable
import re

from RUFAS.util import Utility

PROPERTIES_PATH: Path = Path("").joinpath("input", "metadata", "default_metadata.json")


class SchemaSetupMethods:

    @staticmethod
    def setup_number_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
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
            "options": {
                "grid_columns": 12,
                "format": "select2",
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
                enum = SchemaSetupMethods._get_list_of_options(pattern)
            except ValueError as e:
                print(e)
                return schema
            schema["enum"] = enum
            schema["format"] = "select2"

        return schema

    @staticmethod
    def _get_list_of_options(string: str) -> list[str]:
        pattern = "\\^\\(.*\\)\\$"
        is_valid_pattern = bool(re.match(pattern, string))
        if not is_valid_pattern:
            raise ValueError(f"'{string}' is not a valid pattern. Cannot create list of valid options.")

        unsplit_list = string[2:-2]
        split_list = unsplit_list.split("|")
        return split_list

    @staticmethod
    def setup_array_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
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
        element_schema_creator = SchemaSetupMethods.DATA_TYPE_TO_SCHEMA_SETUP_MAP[element_properties["type"]]
        element_title = title + "_element"
        element_property_dictionary = element_schema_creator(element_title, element_properties)
        schema["items"] = element_property_dictionary

        return schema

    @staticmethod
    def setup_object_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
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

        keys = [key for key in input_properties.keys() if key != "type" and key != "description" and key != "default"]
        for key in keys:
            sub_property = input_properties[key]
            schema_setup_method = SchemaSetupMethods.DATA_TYPE_TO_SCHEMA_SETUP_MAP[sub_property["type"]]
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


def main() -> None:
    schema_dir_path = Path('schemas/')
    Utility.empty_dir(schema_dir_path, None)

    with open(PROPERTIES_PATH) as metadata:
        metadata_dict = json.load(metadata)

    properties = metadata_dict["properties"]

    for key in properties.keys():
        try:
            new_schema = SchemaSetupMethods.setup_object_schema(key, properties[key])
        except Exception as e:
            print(f"Key: '{key}' raised exception: {str(e)}")
            continue

        schema_name = key.replace("properties", "schema")
        new_schema_file_name = f"{schema_name}.json"
        new_schema_file_path = Path.joinpath(schema_dir_path, new_schema_file_name)
        print(new_schema_file_path)

        with open(new_schema_file_path, "w") as outfile:
            json.dump(new_schema, outfile, indent=2)


if __name__ == "__main__":
    main()
