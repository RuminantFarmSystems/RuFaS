# import json
# import pprint
from typing import Any, Callable
import re

PROPERTIES_WITH_SCHEMA = {
    'crop_schedule': "Crop Specifications"
}


class SchemaSetupMethods:
    def __init__(self):
        pass

    @staticmethod
    def _setup_number_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
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
        if minimum is not None and maximum is not None:
            schema["format"] = "range"
        if default is not None:
            schema["default"] = default
        if description:
            schema["options"]["infoText"] = description

        return schema

    @staticmethod
    def _setup_bool_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
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
    def _setup_string_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
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
        if pattern is not None:
            enum = self._get_enum_of_options(pattern)
            schema["enum"] = enum
            schema["format"] = "select2"
        if description is not None:
            schema["options"]["infoText"] = description

        return schema

    @staticmethod
    def _get_enum_of_options(string: str) -> list[str]:
        pattern = "\\^\\(.*\\)\\$"
        is_valid_pattern = bool(re.match(pattern, string))
        if not is_valid_pattern:
            raise ValueError(f"'{string}' is not a valid pattern. Cannot create schema")

        unsplit_list = string[2:-2]
        split_list = unsplit_list.split("|")
        return split_list

    @staticmethod
    def _setup_array_schema(title: str, input_properties: dict[str, Any]) -> dict[str, Any]:
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

    DATA_TYPE_TO_SCHEMA_SETUP_MAP: dict[str, Callable[[str, dict[str, Any]], dict[str, Any]]] = {
        "number": _setup_number_schema,
        "bool": _setup_bool_schema,
        "string": _setup_bool_schema,
        "array": _setup_array_schema,
    }


# def _setup_schema(title: str, structure: dict[str, Any]) -> dict[str, Any]:
#     if
#     schema = {"title": title,
#               "type": "object",
#               "format": "grid",
#               "properties": {}
#               }
#     for key in structure.keys():
#
#     return schema

#
# with open("input/metadata/default_metadata.json") as metadata:
#     metadata_dict = json.load(metadata)
#
# properties = metadata_dict["properties"]
#
# for key in properties.keys():
#     if key in PROPERTIES_WITH_SCHEMA.keys():
#         new_schema = _setup_schema(PROPERTIES_WITH_SCHEMA[key], properties[key])
#     print(key)
# pprint.pprint(json.dumps(properties, indent=4))
