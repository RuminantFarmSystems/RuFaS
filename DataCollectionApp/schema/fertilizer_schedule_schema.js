fertilizer_schedule_schema = {
    "title": "Fertilizer Schedule Properties",
    "format": "grid",
    "properties": {
        "available_fertilizer_mixes": {
            "title": "Available Fertilizer Mixes",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "All the available fertilizer mixes that are available besides the default ones."
            },
            "items": {
                "title": "Available Fertilizer Mixes Element",
                "format": "grid",
                "properties": {
                    "name": {
                        "title": "Name",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Name of the fertilizer mix."
                        },
                        "type": "string"
                    },
                    "N": {
                        "title": "N",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Fraction of nitrogen contained in the fertilizer mix by mass."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "type": "number"
                    },
                    "P": {
                        "title": "P",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Fraction of phosphorus contained in the fertilizer mix by mass."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "type": "number"
                    },
                    "K": {
                        "title": "K",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Fraction of potassium contained in the fertilizer mix by mass."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "type": "number"
                    }
                },
                "options": {
                    "infoText": "The name and nutrient breakdown of a single fertilizer mix."
                },
                "type": "object"
            }
        },
        "mix_names": {
            "title": "Mix Names",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of the mix names that will be used for the corresponding fertilizer application."
            },
            "items": {
                "title": "Mix Names Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "type": "string"
            }
        },
        "years": {
            "title": "Years",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of years in which fertilizer will be applied."
            },
            "items": {
                "title": "Years Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 1,
                "type": "number"
            }
        },
        "days": {
            "title": "Days",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of days on which fertilizer will be applied."
            },
            "items": {
                "title": "Days Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 1,
                "maximum": 366,
                "type": "number"
            }
        },
        "nitrogen_masses": {
            "title": "Nitrogen Masses",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of minimum nitrogen masses that the corresponding fertilizer applications should contain.\nUnits: kg."
            },
            "items": {
                "title": "Nitrogen Masses Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.0,
                "type": "number"
            }
        },
        "phosphorus_masses": {
            "title": "Phosphorus Masses",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of minimum phosphorus masses that the corresponding fertilizer applications should contain.\nUnits: kg."
            },
            "items": {
                "title": "Phosphorus Masses Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.0,
                "type": "number"
            }
        },
        "potassium_masses": {
            "title": "Potassium Masses",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of minimum potassium masses that the corresponding fertilizer applications should contain.\nUnits: kg."
            },
            "items": {
                "title": "Potassium Masses Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.0,
                "type": "number"
            }
        },
        "application_depths": {
            "title": "Application Depths",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of depths at which the fertilizer is injected into the soil.\nUnits: mm."
            },
            "items": {
                "title": "Application Depths Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.0,
                "type": "number"
            }
        },
        "surface_remainder_fractions": {
            "title": "Surface Remainder Fractions",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of fractions of fertilizer which remain on the soil surface when applied via injection."
            },
            "items": {
                "title": "Surface Remainder Fractions Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.0,
                "maximum": 1.0,
                "type": "number"
            }
        },
        "pattern_repeat": {
            "title": "Pattern Repeat",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Number of times that this fertilizer application schedule should be repeated."
            },
            "minimum": 0,
            "default": 0,
            "type": "number"
        },
        "pattern_skip": {
            "title": "Pattern Skip",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Number of years to be skipped between schedule repetitions."
            },
            "minimum": 0,
            "default": 0,
            "type": "number"
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