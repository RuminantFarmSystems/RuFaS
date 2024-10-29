manure_management_schema = {
    "title": "manure_management_properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "manure_management_scenarios": {
            "title": "manure_management_scenarios",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Manure Management Scenarios -- Add as many different manure scenarios as needed"
            },
            "items": {
                "title": "manure_management_scenarios_element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "scenario_id": {
                        "title": "scenario_id",
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
                        "title": "bedding_type",
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
                        "title": "manure_handler",
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
                        "title": "manure_separator",
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
                        "title": "manure_separator_after_digestion",
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
                        "title": "manure_treatment",
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
            "title": "bedding_configs",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            },
            "items": {
                "title": "bedding_configs_element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "name": {
                        "title": "name",
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
                        "title": "bedding_type",
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
                        "title": "bedding_mass_per_day",
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
                        "title": "bedding_density",
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
                        "title": "bedding_dry_matter_content",
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
                        "title": "bedding_cleaned_fraction",
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
                        "title": "bedding_carbon_fraction",
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
                        "title": "bedding_phosphorus_content",
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
                        "title": "sand_removal_efficiency",
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
            "title": "manure_handler_configs",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            },
            "items": {
                "title": "manure_handler_configs_element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "name": {
                        "title": "name",
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
                        "title": "manure_handler_type",
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
                        "title": "cleaning_water_use_rate",
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
                        "title": "minutes_per_cleaning",
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
                        "title": "cleanings_per_day",
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
                        "title": "daily_tillage_frequency",
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
                        "title": "cleaning_water_recycle_fraction",
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
            "title": "manure_separator_configs",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            },
            "items": {
                "title": "manure_separator_configs_element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "name": {
                        "title": "name",
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
                        "title": "manure_separator_type",
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
                        "title": "percent_dry_solids",
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
                        "title": "total_solids_removal_efficiency_for_separator",
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
                        "title": "volatile_solids_removal_efficiency_for_separator",
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
                        "title": "nitrogen_removal_efficiency_for_separator",
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
                        "title": "total_ammoniacal_nitrogen_removal_efficiency_for_separator",
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
                        "title": "phosphorus_removal_efficiency_for_separator",
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
                        "title": "potassium_removal_efficiency_for_separator",
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
            "title": "manure_treatment_configs",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            },
            "items": {
                "title": "manure_treatment_configs_element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "name": {
                        "title": "name",
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
                        "title": "manure_treatment_type",
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
                        "title": "total_solids_removal_efficiency_for_treatment",
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
                        "title": "volatile_solids_removal_efficiency_for_treatment",
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
                        "title": "nitrogen_removal_efficiency_for_treatment",
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
                        "title": "total_ammoniacal_nitrogen_removal_efficiency_for_treatment",
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
                        "title": "phosphorus_removal_efficiency_for_treatment",
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
                        "title": "potassium_removal_efficiency_for_treatment",
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
                        "title": "storage_time_period",
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
                        "title": "freeboard_input",
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
                        "title": "composting_type",
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
                        "title": "last_compost_turning_or_addition",
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
                        "title": "manure_cover",
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
                        "title": "hydraulic_retention_time",
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
                        "title": "sludge_accumulation_period",
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
                        "title": "sludge_accumulation_volume_fraction",
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
                        "title": "top_cover_volume_fraction",
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
                        "title": "evaporation_fraction",
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
                        "title": "anaerobic_digestion_temperature_set_point",
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
                        "title": "anaerobic_digestion_temperature_celsius",
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
                        "title": "digester_methane_leakage_fraction",
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
        }
    }
}