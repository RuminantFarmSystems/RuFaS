manure_inputs_schema = {
    "title": "Manure Storage and Handling Data",
    "type": "object",
    "properties": {
        "manure_management_scenarios": {
            "type": "array",
            "title": "Manure Management Scenario Settings",
            "format": "grid",
            "options": {
                "infoText": "Add as many different manure management scenarios as needed"
            },
            "items": {
                "type": "object",
                "title": "Manure Management Scenario",
                "properties": {
                    "scenario_id": {
                        "title": "Scenario ID",
                        "type": "number",
                    },
                    "bedding_type": {
                        "title": "Bedding Type",
                        "type": "radio",
                        "enum": [
                            "sawdust",
                            "sand",
                            "manure_solids",
                            "straw"
                        ],
                    },
                    "manure_handler": {
                        "title": "Manure Handler",
                        "type": "radio",
                        "enum": [
                            "manual_scraping",
                            "flush_system",
                            "automatic_alley_scraping"
                        ]
                    },
                    "manure_separator": {
                        "title": "Manure Separator",
                        "type": "radio",
                        "enum": [
                            "none",
                            "screw press",
                            "sand lane manure separation",
                            "rotary screen"
                        ]
                    },
                    "manure_treatment": {
                        "title": "Primary Manure Treatment",
                        "type": "select2",
                        "required": true,
                        "enum": [
                            "slurry_storage_underfloor",
                            "slurry_storage_outdoor",
                            "composting",
                            "anaerobic_lagoon",
                            "anaerobic_digestion",
                            "other"
                        ],
                        "options": {
                            "grid_columns": 6,
                            "infoText": "The first manure treatment",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                }
            }
        },
        "bedding_configs": {
            "type": "array",
            "title": "Bedding Configs",
            "format": "grid",
            "options": {
                "infoText": "Add as many different bedding configs as needed"
            },
            "items": {
                "type": "object",
                "title": "Bedding Config",
                "format": "grid",
                "properties": {
                    "bedding_type": {
                        "title": "Bedding Type",
                        "type": "radio",
                        "enum": [
                            "sawdust",
                            "sand",
                            "manure_solids",
                            "straw"
                        ],
                        "options": {
                            "grid_columns": 6,
                        }
                    },
                    "bedding_mass_per_day": {
                        "title": "Bedding Mass Per Day",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                        }
                    },
                    "bedding_density": {
                        "title": "Bedding Density",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                        }
                    },
                    "bedding_dry_matter_content": {
                        "title": "Bedding Dry Matter Content",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                        }
                    },
                    "bedding_cleaned_fraction": {
                        "title": "Bedding Cleaned Fraction",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                        }
                    },
                    "bedding_carbon_fraction": {
                        "title": "Bedding Carbon Fraction",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                        }
                    },
                    "bedding_phosphorus_content": {
                        "title": "Bedding Phosphorus Content",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                        }
                    },
                    "sand_removal_efficiency": {
                        "title": "Sand Removal Efficiency",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                        }
                    },
                },
            }
        },
        "manure_handler_configs": {
            "type": "array",
            "title": "Manure Handler Configs",
            "format": "grid",
            "options": {
                "infoText": "Add as many different manure handler configs as needed"
            },
            "items": {
                "type": "object",
                "title": "Manure Handler Config",
                "format": "grid",
                "properties": {
                    "manure_handler_type": {
                        "title": "Manure Handler Type",
                        "type": "radio",
                        "enum": [
                            "flush_system",
                            "manual_scraping",
                            "alley_scraper",
                            "tillage"
                        ]
                    },
                    "cleaning_water_use_rate": {
                        "title": "Cleaning Water Use Rate",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "minutes_per_cleaning": {
                        "title": "Minutes Per Cleaning",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "cleanings_per_day": {
                        "title": "Cleanings Per Day",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "daily_tillage_frequency": {
                        "title": "Daily Tillage Frequency",
                        "type": "number",
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                },
            }
        },
        "manure_separator_configs": {
            "type": "array",
            "title": "Manure Separator Configs",
            "format": "grid",
            "options": {
                "infoText": "Add as many different manure separator configs as needed"
            },
            "items": {
                "type": "object",
                "title": "Manure Separator Config",
                "format": "grid",
                "properties": {
                    "manure_separator_type": {
                        "title": "Manure Separator Type",
                        "type": "radio",
                        "enum": [
                            "rotary_screen",
                            "screw_press"
                        ],
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "percent_dry_solids": {
                        "title": "Percent Dry Solids",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "total_solids_removal_efficiency_for_separator": {
                        "title": "Total Solids Removal Efficiency For Separator",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "volatile_solids_removal_efficiency_for_separator": {
                        "title": "Volatile Solids Removal Efficiency For Separator",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "nitrogen_removal_efficiency_for_separator": {
                        "title": "Nitrogen Removal Efficiency For Separator",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "total_ammoniacal_nitrogen_removal_efficiency_for_separator": {
                        "title": "Total Ammoniacal Nitrogen Removal Efficiency For Separator",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "phosphorus_removal_efficiency_for_separator": {
                        "title": "Phosphorus Removal Efficiency For Separator",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "potassium_removal_efficiency_for_separator": {
                        "title": "Potassium Removal Efficiency For Separator",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                },
            },
        },
        "manure_treatment_configs": {
            "type": "array",
            "title": "Manure Treatment Configs",
            "format": "grid",
            "options": {
                "infoText": "Add as many different manure treatment configs as needed"
            },
            "items": {
                "type": "object",
                "title": "Manure Treatment Config",
                "format": "grid",
                "properties": {
                    "manure_treatment_type": {
                        "title": "Manure Treatment Type",
                        "type": "radio",
                        "enum": [
                            "slurry_storage_underfloor",
                            "slurry_storage_outdoor",
                            "anaerobic_lagoon",
                            "anaerobic_digestion",
                            "composted_bedded_pack_barn"
                        ],
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "total_solids_removal_efficiency_for_treatment": {
                        "title": "Total Solids Removal Efficiency For Treatment",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "volatile_solids_removal_efficiency_for_treatment": {
                        "title": "Volatile Solids Removal Efficiency For Treatment",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "nitrogen_removal_efficiency_for_treatment": {
                        "title": "Nitrogen Removal Efficiency For Treatment",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": {
                        "title": "Total Ammoniacal Nitrogen Removal Efficiency For Treatment",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "phosphorus_removal_efficiency_for_treatment": {
                        "title": "Phosphorus Removal Efficiency For Treatment",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "potassium_removal_efficiency_for_treatment": {
                        "title": "Potassium Removal Efficiency For Treatment",
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "hydraulic_retention_time": {
                        "title": "Hydraulic Retention Time",
                        "type": "number",
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "sludge_accumulation_period": {
                        "title": "Sludge Accumulation Period",
                        "type": "number",
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "sludge_accumulation_volume_fraction": {
                        "title": "Sludge Accumulation Volume Fraction",
                        "type": "number",
                        "default": 0,
                        "minimum": 0,
                        "maximum": 1,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "storage_time_period": {
                        "title": "Storage Time Period",
                        "type": "number",
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "freeboard_input": {
                        "title": "Freeboard Input",
                        "type": "number",
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "top_cover_volume_fraction": {
                        "title": "Top Cover Volume Fraction",
                        "type": "number",
                        "default": 0,
                        "minimum": 0,
                        "maximum": 1,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "biogas_generation_ratio": {
                        "title": "Biogas Generation Ratio",
                        "type": "number",
                        "default": 0,
                        "minimum": 0,
                        "maximum": 1,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "methane_generation_ratio": {
                        "title": "Methane Generation Ratio",
                        "type": "number",
                        "default": 0,
                        "minimum": 0,
                        "maximum": 1,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "evaporation_fraction": {
                        "title": "Evaporation Fraction",
                        "type": "number",
                        "default": 0,
                        "minimum": 0,
                        "maximum": 1,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "anaerobic_digestion_temperature_set_point": {
                        "title": "Anaerobic Digestion Temperature Set Point",
                        "type": "number",
                        "default": 0,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "anaerobic_digestion_temperature_celsius": {
                        "title": "Anaerobic Digestion Temperature (Celsius)",
                        "type": "number",
                        "default": 37.5,
                        "options": {
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    }
                }
            }
        }

    }
}