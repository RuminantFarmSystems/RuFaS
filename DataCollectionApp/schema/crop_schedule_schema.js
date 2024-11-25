crop_schedule_schema = {
    "title": "Crop Schedule Properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "crop_schedules": {
            "title": "Crop Schedules",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Array of all crop schedules to be executed over the run of the simulation."
            },
            "items": {
                "title": "Crop Schedules Element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "crop_species": {
                        "title": "Crop Species",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Name of the crop being grown."
                        },
                        "enum": [
                            "alfalfa_hay",
                            "alfalfa_silage",
                            "alfalfa_baleage",
                            "cereal_rye_hay",
                            "cereal_rye_grain",
                            "cereal_rye_silage",
                            "cereal_rye_baleage",
                            "corn_grain",
                            "corn_silage",
                            "soybean_hay",
                            "soybean_grain",
                            "tall_fescue_hay",
                            "tall_fescue_silage",
                            "tall_fescue_baleage",
                            "triticale_hay",
                            "triticale_grain",
                            "triticale_silage",
                            "triticale_baleage",
                            "winter_wheat_hay",
                            "winter_wheat_grain",
                            "winter_wheat_silage",
                            "winter_wheat_baleage"
                        ],
                        "format": "select2"
                    },
                    "harvest_days": {
                        "title": "Harvest Days",
                        "type": "array",
                        "format": "grid",
                        "options": {
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Julian day(s) of year to harvest"
                        },
                        "items": {
                            "title": "Harvest Days Element",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Julian day of year to harvest"
                            },
                            "minimum": 1,
                            "maximum": 366
                        }
                    },
                    "harvest_years": {
                        "title": "Harvest Years",
                        "type": "array",
                        "format": "grid",
                        "options": {
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Calendar years in which the harvesting occurs"
                        },
                        "items": {
                            "title": "Harvest Years Element",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                }
                            },
                            "minimum": 1
                        }
                    },
                    "harvest_operations": {
                        "title": "Harvest Operations",
                        "type": "array",
                        "format": "grid",
                        "options": {
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Operation(s) with which this crop will be harvested."
                        },
                        "items": {
                            "title": "Harvest Operations Element",
                            "type": "string",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                }
                            },
                            "default": "harvest_kill",
                            "enum": [
                                "harvest_kill",
                                "harvest_only",
                                "kill_only"
                            ],
                            "format": "select2"
                        }
                    },
                    "harvest_type": {
                        "title": "Harvest Type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Whether the crop uses scheduled harvests or optimal harvests"
                        },
                        "default": "scheduled",
                        "enum": [
                            "scheduled",
                            "optimal"
                        ],
                        "format": "select2"
                    },
                    "planting_days": {
                        "title": "Planting Days",
                        "type": "array",
                        "format": "grid",
                        "options": {
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Julian day(s) of year to plant"
                        },
                        "items": {
                            "title": "Planting Days Element",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                }
                            },
                            "minimum": 1,
                            "maximum": 366
                        }
                    },
                    "planting_years": {
                        "title": "Planting Years",
                        "type": "array",
                        "format": "grid",
                        "options": {
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Calendar years in which the planting occurs"
                        },
                        "items": {
                            "title": "Planting Years Element",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                }
                            },
                            "minimum": 1
                        }
                    },
                    "pattern_repeat": {
                        "title": "Pattern Repeat",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Number of times that this crop schedule should be repeated."
                        },
                        "minimum": 0,
                        "default": 0
                    },
                    "planting_skip": {
                        "title": "Planting Skip",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Number of years to be skipped between planting schedule repetitions."
                        },
                        "minimum": 0,
                        "default": 0
                    },
                    "harvesting_skip": {
                        "title": "Harvesting Skip",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Number of years to be skipped between harvest schedule repetitions."
                        },
                        "minimum": 0,
                        "default": 0
                    }
                },
                "options": {
                    "infoText": "Contains all the properties necessary to create a CropSchedule object."
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
                "infoText": "Used to name the file that saves the data entered."
            }
        }
    }
}