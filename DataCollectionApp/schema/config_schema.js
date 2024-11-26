config_schema = {
    "title": "Config Properties",
    "format": "grid",
    "properties": {
        "start_date": {
            "title": "Start Date",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The year and Julian day on which the simulation will start."
            },
            "default": "2009:1",
            "pattern": "[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$",
            "type": "string"
        },
        "end_date": {
            "title": "End Date",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The year and Julian day on which the simulation will end."
            },
            "default": "2009:100",
            "pattern": "[12][019][0-9]{2}:(?:[1-9]|[1-9][0-9]|[12][0-9]{2}|3[0-5][0-9]|36[0-6])$",
            "type": "string"
        },
        "simulate_animals": {
            "title": "Simulate Animals",
            "type": "boolean",
            "format": "checkbox",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Whether or not to simulate animals during the simulation"
            },
            "default": true
        },
        "nutrient_standard": {
            "title": "Nutrient Standard",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The nutrient standard to use for feed."
            },
            "default": "NASEM",
            "enum": [
                "NASEM",
                "NRC"
            ],
            "format": "select2",
            "type": "string"
        },
        "FIPS_county_code": {
            "title": "Fips County Code",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Unique 5-digit code that represents a specific U.S. county."
            },
            "minimum": 1000,
            "maximum": 56045,
            "type": "number"
        },
        "include_detailed_values": {
            "title": "Include Detailed Values",
            "type": "boolean",
            "format": "checkbox",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Whether or not to add detailed_values property to the json output"
            },
            "default": false
        },
        "fileName": {
            "title": "File Name",
            "type": "string",
            "pattern": "^[a-zA-Z0-9_\\- ]{1,255}$",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Used to name the file that saves the data entered. This name will not be included in the saved file."
            }
        }
    },
    "type": "object"
}