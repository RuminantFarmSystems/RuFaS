import json
# import pprint
from typing import Any

PROPERTIES_WITH_SCHEMA = {
    'crop_schedule': "Crop Specifications"
}


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
        schema["description"] = description

    return schema


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
