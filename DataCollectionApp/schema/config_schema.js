config_schema = {
    "title": "Config Properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "start_date": {
            "title": "Start Date",
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The year and Julian day on which the simulation will start."
            },
            "default": "2009:1"
        },
        "end_date": {
            "title": "End Date",
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The year and Julian day on which the simulation will end."
            },
            "default": "2009:100"
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
            "type": "string",
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
            "format": "select2"
        },
        "FIPS_county_code": {
            "title": "Fips County Code",
            "type": "number",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Unique 5-digit code that represents a specific U.S. county."
            },
            "minimum": 1000,
            "maximum": 56045
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
        "filename": {
            "title": "File Name",
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Used to name the file that saves the data entered."
            }
        }
    }
}