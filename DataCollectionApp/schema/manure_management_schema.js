manure_management_schema = {
    "title": "Manure Management Properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "manure_management_scenarios": {
            "title": "Manure Management Scenarios",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Manure Management Scenarios -- Add as many different manure scenarios as needed"
            },
            "items": {
                "title": "Manure Management Scenarios Element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "scenario_id": {
                        "title": "Scenario Id",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Scenario ID -- An identification number for livestock enclosures."
                        },
                        "minimum": 0
                    },
                    "bedding_type": {
                        "title": "Bedding Type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Name of the bedding configuration to be used in the scenario. Must match 'name' attribute of the Bedding Config to be used."
                        }
                    },
                    "manure_handler": {
                        "title": "Manure Handler",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Name of the Manure Handling Method -- Method for cleaning barn alleyways. Must match 'name' attribute of the Manure Handler Config to be used."
                        }
                    },
                    "manure_separator": {
                        "title": "Manure Separator",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Name of the manure separator used in a manure management scenario. Each named separator must have a Manure Separator Config defined, unless no separator ('none') is used."
                        }
                    },
                    "manure_separator_after_digestion": {
                        "title": "Manure Separator After Digestion",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Name of the manure separator used after digestion in a manure management scenario. Each named separator must have a Manure Separator Config defined, unless no separator ('none') is used."
                        }
                    },
                    "manure_treatment": {
                        "title": "Manure Treatment",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Name of the manure treatment and/or storage used in a manure management scenario. Each named treatment must have a Manure Treatment Config defined, unless the treatment is 'anaerobic digestion and lagoon' or 'anaerobic digestion and lagoon with separator'."
                        }
                    }
                }
            }
        },
        "bedding_configs": {
            "title": "Bedding Configs",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            },
            "items": {
                "title": "Bedding Configs Element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "name": {
                        "title": "Name",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Unique identifier for this bedding configuration."
                        }
                    },
                    "bedding_type": {
                        "title": "Bedding Type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Bedding Type -- The material used for bedding pack."
                        },
                        "enum": [
                            "sand",
                            "straw",
                            "sawdust",
                            "manure solids",
                            "CBPB sawdust",
                            "none"
                        ],
                        "format": "select2"
                    },
                    "bedding_mass_per_day": {
                        "title": "Bedding Mass Per Day",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "bedding_density": {
                        "title": "Bedding Density",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "bedding_dry_matter_content": {
                        "title": "Bedding Dry Matter Content",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "bedding_cleaned_fraction": {
                        "title": "Bedding Cleaned Fraction",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "bedding_carbon_fraction": {
                        "title": "Bedding Carbon Fraction",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "bedding_phosphorus_content": {
                        "title": "Bedding Phosphorus Content",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "sand_removal_efficiency": {
                        "title": "Sand Removal Efficiency",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    }
                }
            }
        },
        "manure_handler_configs": {
            "title": "Manure Handler Configs",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            },
            "items": {
                "title": "Manure Handler Configs Element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "name": {
                        "title": "Name",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Name of the unique manure handler config."
                        }
                    },
                    "manure_handler_type": {
                        "title": "Manure Handler Type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Manure Handling general type -- Method for cleaning barn alleyways."
                        },
                        "enum": [
                            "flush system",
                            "alley scraper",
                            "manual scraping",
                            "tillage",
                            "harrowing"
                        ],
                        "format": "select2"
                    },
                    "cleaning_water_use_rate": {
                        "title": "Cleaning Water Use Rate",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "minutes_per_cleaning": {
                        "title": "Minutes Per Cleaning",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        },
                        "minimum": 0
                    },
                    "cleanings_per_day": {
                        "title": "Cleanings Per Day",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        },
                        "minimum": 0
                    },
                    "daily_tillage_frequency": {
                        "title": "Daily Tillage Frequency",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Daily Tillage Frequency -- The number of times per day that tillage is performed."
                        },
                        "minimum": 0
                    },
                    "cleaning_water_recycle_fraction": {
                        "title": "Cleaning Water Recycle Fraction",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Fraction of cleaning water that is from recycled (not fresh) water sources."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                }
            }
        },
        "manure_separator_configs": {
            "title": "Manure Separator Configs",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            },
            "items": {
                "title": "Manure Separator Configs Element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "name": {
                        "title": "Name",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Name of the unique manure separator config. This can be any string besides 'none'."
                        },
                        "enum": [
                            "?!none$)(.*"
                        ],
                        "format": "select2"
                    },
                    "manure_separator_type": {
                        "title": "Manure Separator Type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Manure Separator Type -- The type of solid-liquid separator equipment to separate coarse fibrous solids/sand. "
                        },
                        "enum": [
                            "screw press",
                            "rotary screen"
                        ],
                        "format": "select2"
                    },
                    "percent_dry_solids": {
                        "title": "Percent Dry Solids",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "total_solids_removal_efficiency_for_separator": {
                        "title": "Total Solids Removal Efficiency For Separator",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "volatile_solids_removal_efficiency_for_separator": {
                        "title": "Volatile Solids Removal Efficiency For Separator",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "nitrogen_removal_efficiency_for_separator": {
                        "title": "Nitrogen Removal Efficiency For Separator",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "total_ammoniacal_nitrogen_removal_efficiency_for_separator": {
                        "title": "Total Ammoniacal Nitrogen Removal Efficiency For Separator",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "phosphorus_removal_efficiency_for_separator": {
                        "title": "Phosphorus Removal Efficiency For Separator",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    },
                    "potassium_removal_efficiency_for_separator": {
                        "title": "Potassium Removal Efficiency For Separator",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        }
                    }
                }
            }
        },
        "manure_treatment_configs": {
            "title": "Manure Treatment Configs",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            },
            "items": {
                "title": "Manure Treatment Configs Element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "name": {
                        "title": "Name",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "The unique identifier of the manure treatment configuration."
                        },
                        "enum": [
                            "?!anaerobic digestion and lagoon",
                            "anaerobic digestion and lagoon with separator$)(.*"
                        ],
                        "format": "select2"
                    },
                    "manure_treatment_type": {
                        "title": "Manure Treatment Type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Manure Treatment Methods -- Select the Manure Treatment Methods."
                        },
                        "enum": [
                            "slurry storage underfloor",
                            "slurry storage outdoor",
                            "open lots",
                            "compost bedded pack barn",
                            "anaerobic lagoon",
                            "composting",
                            "anaerobic digestion"
                        ],
                        "format": "select2"
                    },
                    "total_solids_removal_efficiency_for_treatment": {
                        "title": "Total Solids Removal Efficiency For Treatment",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Total solids removal efficiency for the manure storage and treatment system."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.0
                    },
                    "volatile_solids_removal_efficiency_for_treatment": {
                        "title": "Volatile Solids Removal Efficiency For Treatment",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Volatile solids removal efficiency for the manure storage and treatment system."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.0
                    },
                    "nitrogen_removal_efficiency_for_treatment": {
                        "title": "Nitrogen Removal Efficiency For Treatment",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Nitrogen removal efficiency for the manure storage and treatment system."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.0
                    },
                    "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": {
                        "title": "Total Ammoniacal Nitrogen Removal Efficiency For Treatment",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Total ammoniacal nitrogen removal efficiency for the manure storage and treatment system."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.0
                    },
                    "phosphorus_removal_efficiency_for_treatment": {
                        "title": "Phosphorus Removal Efficiency For Treatment",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Phosphorus removal efficiency for the manure storage and treatment system."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.0
                    },
                    "potassium_removal_efficiency_for_treatment": {
                        "title": "Potassium Removal Efficiency For Treatment",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Potassium removal efficiency for the manure storage and treatment system."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.0
                    },
                    "storage_time_period": {
                        "title": "Storage Time Period",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Storage Time Period -- The number of days that manure is stored before it is removed from the system (day)."
                        },
                        "minimum": 0,
                        "default": 120
                    },
                    "freeboard_input": {
                        "title": "Freeboard Input",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Freeboard -- Empty storage space above the manure in the treatment system."
                        },
                        "default": 0.0
                    },
                    "composting_type": {
                        "title": "Composting Type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Composting Type -- The type of composting."
                        },
                        "default": "intensive windrow",
                        "enum": [
                            "intensive windrow",
                            "passive windrow",
                            "static pile"
                        ],
                        "format": "select2"
                    },
                    "last_compost_turning_or_addition": {
                        "title": "Last Compost Turning Or Addition",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "The number of days since the last turning or addition event (day)"
                        },
                        "default": 1
                    },
                    "manure_cover": {
                        "title": "Manure Cover",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Indicates the presence or absence of a cover in the manure treatment or storage system. A cover referes to a human made cover where as a crust is naturally formed. A cover and flare refers to a storage system that is covered to capture and then destroy the methane produced with a flare. For the anaerobic diesgtion treatment, this property should be set to N/A."
                        },
                        "default": "no cover",
                        "enum": [
                            "cover",
                            "crust",
                            "no cover",
                            "cover and flare",
                            "N/A"
                        ],
                        "format": "select2"
                    },
                    "hydraulic_retention_time": {
                        "title": "Hydraulic Retention Time",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Hydraulic Retention Time -- The average time that manure is retained in the treatment system (day)."
                        },
                        "minimum": 0,
                        "default": 0
                    },
                    "sludge_accumulation_period": {
                        "title": "Sludge Accumulation Period",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Sludge Accumulation Period -- The number of days that sludge is accumulated in the treatment system (day)."
                        },
                        "minimum": 0,
                        "default": 0
                    },
                    "sludge_accumulation_volume_fraction": {
                        "title": "Sludge Accumulation Volume Fraction",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Sludge Accumulation Volume Fraction -- Based on the manure solids entering the treatment system."
                        },
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0
                    },
                    "top_cover_volume_fraction": {
                        "title": "Top Cover Volume Fraction",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Top Cover Volume Fraction -- Fraction of the total volume of the treatment system that is assumed to be the top cover volume."
                        },
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0
                    },
                    "evaporation_fraction": {
                        "title": "Evaporation Fraction",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Evaporation Fraction -- The fraction of the liquid portion evaporated from the treatment system."
                        },
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0
                    },
                    "anaerobic_digestion_temperature_set_point": {
                        "title": "Anaerobic Digestion Temperature Set Point",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Anaerobic Digestion Temperature Set Point -- The temperature set point for the anaerobic digestion treatment system (degrees Celsius)."
                        },
                        "minimum": 0,
                        "default": 0
                    },
                    "anaerobic_digestion_temperature_celsius": {
                        "title": "Anaerobic Digestion Temperature Celsius",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Anaerobic Digestion Temperature Celsius -- The temperature of the anaerobic digestion treatment system (degrees Celsius)."
                        },
                        "minimum": 0,
                        "default": 0
                    },
                    "digester_methane_leakage_fraction": {
                        "title": "Digester Methane Leakage Fraction",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "The fraction of methane generated in the digester that escapes to the atmosphere through unintended leakage and is not collected by the gas capture system."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.01
                    }
                }
            }
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
    }
}