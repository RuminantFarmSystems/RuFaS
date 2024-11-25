field_schema = {
    "title": "Field Properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "soil_specification": {
            "title": "Soil Specification",
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Name of the metadata blob that contains the data for this field's soil specification."
            }
        },
        "crop_specification": {
            "title": "Crop Specification",
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Name of the metadata blob that contains the data for this field's crop schedule specification."
            }
        },
        "fertilizer_management_specification": {
            "title": "Fertilizer Management Specification",
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Name of the metadata blob that contains the data for this field's fertilizer application schedule specification."
            }
        },
        "manure_management_specification": {
            "title": "Manure Management Specification",
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Name of the metadata blob that contains the data for this field's manure application schedule specification."
            }
        },
        "tillage_management_specification": {
            "title": "Tillage Management Specification",
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Name of the metadata blob that contains the data for this field's tillage application schedule specification."
            }
        },
        "field_size": {
            "title": "Field Size",
            "type": "number",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Size of the field."
            },
            "minimum": 0.0
        },
        "absolute_latitude": {
            "title": "Absolute Latitude",
            "type": "number",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The absolute latitude of the center of this field.\nUnits: degrees."
            },
            "minimum": 0.0,
            "maximum": 90.0,
            "default": 43.5
        },
        "longitude": {
            "title": "Longitude",
            "type": "number",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The longitude of the center of this field.\nUnits: degrees."
            },
            "minimum": -180.0,
            "maximum": 180.0,
            "default": -89.4
        },
        "minimum_daylength": {
            "title": "Minimum Daylength",
            "type": "number",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Length of the shortest day of the year for watershed the field is located in.\nUnits: hours."
            },
            "minimum": 0.0,
            "maximum": 24.0,
            "default": 9.0
        },
        "seasonal_high_water_table": {
            "title": "Seasonal High Water Table",
            "type": "boolean",
            "format": "checkbox",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "True if the HRU that contains the field has a high seasonal water table, false otherwise.\nUnitless.\nReference: SWAT Theoretical documentation section 2:3.2, SWAT Input .HRU - IWATABLE."
            },
            "default": false
        },
        "watering_amount_in_liters": {
            "title": "Watering Amount In Liters",
            "type": "number",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Amount of water to be applied as irrigation at the end of a specified interval.\nUnits: liters."
            },
            "minimum": 0.0,
            "default": 0.0
        },
        "watering_interval": {
            "title": "Watering Interval",
            "type": "number",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Number of days that make up the irrigation interval.\nUnits: days."
            },
            "minimum": 0,
            "default": 0
        },
        "supplement_manure_nutrient_deficiencies": {
            "title": "Supplement Manure Nutrient Deficiencies",
            "type": "boolean",
            "format": "checkbox",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Determines if nutrient deficient manure applications are supplemented with chemical fertilizer."
            },
            "default": false
        },
        "simulate_water_stress": {
            "title": "Simulate Water Stress",
            "type": "boolean",
            "format": "checkbox",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Whether water stress affects crops grown in this field."
            },
            "default": true
        },
        "simulate_temp_stress": {
            "title": "Simulate Temp Stress",
            "type": "boolean",
            "format": "checkbox",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Whether temperature stress affects crops grown in this field."
            },
            "default": true
        },
        "simulate_nitrogen_stress": {
            "title": "Simulate Nitrogen Stress",
            "type": "boolean",
            "format": "checkbox",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Whether nitrogen stress affects crops grown in this field."
            },
            "default": true
        },
        "simulate_phosphorus_stress": {
            "title": "Simulate Phosphorus Stress",
            "type": "boolean",
            "format": "checkbox",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Whether phosphrorus stress affects crops grown in this field."
            },
            "default": true
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
                "infoText": "Used to name the file that saves the data entered."
            }
        }
    }
}