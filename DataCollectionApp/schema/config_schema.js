config_schema = {
    "title": "config_properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "start_date": {
            "title": "start_date",
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
            "title": "end_date",
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
            "title": "simulate_animals",
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
            "title": "nutrient_standard",
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
            "title": "FIPS_county_code",
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
            "title": "include_detailed_values",
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
        }
    }
}