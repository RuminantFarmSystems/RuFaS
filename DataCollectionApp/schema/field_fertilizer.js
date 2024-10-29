fertilizer_schema = {
    "title": "Field Fertilizer Management",
    "type": "object",
    "format": "grid",
    "properties": {
        "available_fertilizer_mixes": {
            "title": "Available Fertilizer Mixes",
            "type": "array",
            "options": {
                "infoText": "All the available fertilizer mixes that are available besides the default ones.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            },
            "items": {
                "type": "object",
                "title": "Available Fertilizer Mix",
                "format": "grid",
                "properties": {
                    "name": {
                        "title": "Fertilizer Mix Name",
                        "type": "string",
                        "options": {
                            "infoText": "Name of the fertilizer mix.",
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control",
                            }
                        },
                    },
                    "N": {
                        "title": "N",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "options": {
                            "infoText": "Fraction of nitrogen contained in the fertilizer mix by mass.",
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control",
                            }
                        },
                    },
                    "P": {
                        "title": "P",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "options": {
                            "infoText": "Fraction of phosphorus contained in the fertilizer mix by mass.",
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control",
                            }
                        },
                    },
                    "K": {
                        "title": "K",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "options": {
                            "infoText": "Fraction of potassium contained in the fertilizer mix by mass.",
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control",
                            }
                        },
                    },
                }
            }
        },
        "mix_names": {
            "title": "Mix Names",
            "type": "array",
            "options": {
                "infoText": "List of the mix names that will be used for the corresponding fertilizer application.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            },
            "items": {
                "type": "string",
                "title": "Mix Name"
            }
        },
        "years": {
            "title": "Years",
            "type": "array",
            "items": {
                "type": "number",
                "format": "range",
                "title": "Year",
                "minimum": 1950,
                "maximum": 2050,
                "default": 2023,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of years in which fertilizer will be applied.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "days": {
            "title": "Days",
            "type": "array",
            "items": {
                "type": "number",
                "format": "range",
                "title": "Day",
                "minimum": 1,
                "maximum": 366,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of days on which fertilizer will be applied.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "nitrogen_masses": {
            "title": "Nitrogen Masses",
            "type": "array",
            "items": {
                "type": "number",
                "title": "Nitrogen Mass",
                "minimum": 0.0,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of minimum nitrogen masses that the corresponding fertilizer applications should contain.\nUnits: kg.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "phosphorus_masses": {
            "title": "Phosphorus Masses",
            "type": "array",
            "items": {
                "type": "number",
                "title": "Phosphorus Mass",
                "minimum": 0.0,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of minimum phosphorus masses that the corresponding fertilizer applications should contain.\nUnits: kg.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "potassium_masses": {
            "title": "Potassium Masses",
            "type": "array",
            "items": {
                "type": "number",
                "title": "Potassium Mass",
                "minimum": 0.0,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of minimum potassium masses that the corresponding fertilizer applications should contain.\nUnits: kg.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "application_depths": {
            "title": "Application Depths",
            "type": "array",
            "items": {
                "type": "number",
                "title": "Application Depth",
                "minimum": 0.0,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of depths at which the fertilizer is injected into the soil.\nUnits: mm.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "surface_remainder_fractions": {
            "title": "Surface Remainder Fractions",
            "type": "array",
            "items": {
                "type": "number",
                "title": "Surface Remainder Fraction",
                "minimum": 0.0,
                "maximum": 1.0,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of fractions of fertilizer which remain on the soil surface when applied via injection.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "pattern_repeat": {
            "title": "Pattern Repeat",
            "type": "number",
            "minimum": 0,
            "default": 0,
            "options": {
                "infoText": "Number of times that this fertilizer application schedule should be repeated.",
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "grid_columns": 6,
            }
        },
        "pattern_skip": {
            "title": "Pattern Skip",
            "type": "number",
            "minimum": 0,
            "default": 0,
            "options": {
                "infoText": "Number of years to be skipped between schedule repetitions.",
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "grid_columns": 6,
            }
        },
    }
}