fertilizer_schedule_schema = {
    "title": "Fertilizer Schedule Properties",
    "type": "object",
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
                            "infoText": "Name of the fertilizer mix."
                        }
                    },
                    "N": {
                        "title": "N",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Fraction of nitrogen contained in the fertilizer mix by mass."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "P": {
                        "title": "P",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Fraction of phosphorus contained in the fertilizer mix by mass."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "K": {
                        "title": "K",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Fraction of potassium contained in the fertilizer mix by mass."
                        },
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "options": {
                    "infoText": "The name and nutrient breakdown of a single fertilizer mix."
                }
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
                "type": "string",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                }
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
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.0
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
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.0
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
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.0
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
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.0
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
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.0,
                "maximum": 1.0
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
                "infoText": "Number of times that this fertilizer application schedule should be repeated."
            },
            "minimum": 0,
            "default": 0
        },
        "pattern_skip": {
            "title": "Pattern Skip",
            "type": "number",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Number of years to be skipped between schedule repetitions."
            },
            "minimum": 0,
            "default": 0
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