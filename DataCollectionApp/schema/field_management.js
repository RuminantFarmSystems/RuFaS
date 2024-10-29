field_management_schema = {
    "title": "Overall Field Management",
    "type": "object",
    "format": "grid",
    "properties": {
        "soil_specification": {
            "title": "Soil Specification",
            "type": "string",
            "options": {
                "infoText": "Name of the metadata blob that contains the data for this field's soil specification.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                },
                "grid_columns": 6,
            }
        },
        "crop_specification": {
            "title": "Crop Specification",
            "type": "string",
            "options": {
                "infoText": "Name of the metadata blob that contains the data for this field's crop schedule specification.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                },
                "grid_columns": 6,
            }
        },
        "fertilizer_management_specification": {
            "title": "Fertilizer Management Specification",
            "type": "string",
            "options": {
                "infoText": "Name of the metadata blob that contains the data for this field's fertilizer application schedule specification.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                },
                "grid_columns": 6,
            }
        },
        "manure_management_specification": {
            "title": "Manure Management Specification",
            "type": "string",
            "options": {
                "infoText": "Name of the metadata blob that contains the data for this field's manure application schedule specification.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                },
                "grid_columns": 6,
            }
        },
        "tillage_management_specification": {
            "title": "Tillage Management Specification",
            "type": "string",
            "options": {
                "infoText": "Name of the metadata blob that contains the data for this field's tillage application schedule specification.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                },
                "grid_columns": 6,
            }
        },
        "field_size": {
            "title": "Field Size",
            "type": "number",
            "minimum": 0.0,
            "exclusiveMinimum": true,
            "default": null,
            "options": {
                "infoText": "Size of the field.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                },
                "grid_columns": 6,
            }
        },
        "absolute_latitude": {
            "title": "Absolute Latitude",
            "type": "number",
            "minimum": 0.0,
            "maximum": 90.0,
            "default": 43.5,
            "options": {
                "infoText": "The absolute latitude of the center of this field.\nUnits: degrees.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                },
                "grid_columns": 6,
            }
        },
        "longitude": {
            "title": "Longitude",
            "type": "number",
            "minimum": -180.0,
            "maximum": 180.0,
            "default": -89.4,
            "options": {
                "infoText": "The longitude of the center of this field.\nUnits: degrees.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                },
                "grid_columns": 6,
            }
        },
        "minimum_daylength": {
            "title": "Minimum Day Length",
            "type": "number",
            "minimum": 0.0,
            "maximum": 24.0,
            "default": 9.0,
            "options": {
                "infoText": "Length of the shortest day of the year for watershed the field is located in.\nUnits: hours.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                },
                "grid_columns": 6,
            }
        },
        "seasonal_high_water_table": {
            "title": "Seasonal High Water Table",
            "type": "boolean",
            "default": false,
            "options": {
                "infoText": "True if the HRU that contains the field has a high seasonal water table, false otherwise.\nUnitless.\nReference: SWAT Theoretical documentation section 2:3.2, SWAT Input .HRU - IWATABLE.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                },
                "grid_columns": 6,
            }
        },
        "watering_amount_in_liters": {
            "title": "Watering Amount in Liters",
            "type": "number",
            "minimum": 0.0,
            "default": 0.0,
            "options": {
                "infoText": "Amount of water to be applied as irrigation at the end of a specified interval.\nUnits: liters.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "watering_interval": {
            "title": "Watering Interval",
            "type": "number",
            "minimum": 0,
            "default": 0,
            "options": {
                "infoText": "Number of days that make up the irrigation interval.\nUnits: days.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
    }
}