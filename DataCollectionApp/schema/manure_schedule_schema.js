manure_schedule_schema = {
    "title": "Manure Schedule Properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "years": {
            "title": "Years",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of years in which manure will be applied."
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
                "infoText": "List of days on which manure will be applied."
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
                "infoText": "List of minimum nitrogen masses that the corresponding manure applications should contain.\nUnits: kg."
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
                "infoText": "List of minimum phosphorus masses that the corresponding manure applications should contain.\nUnits: kg."
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
                "infoText": "List of minimum potassium masses that the corresponding manure applications should contain.\nUnits: kg."
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
        "coverage_fractions": {
            "title": "Coverage Fractions",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of fractions of how much of the field is covered by the corresponding manure application."
            },
            "items": {
                "title": "Coverage Fractions Element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.01,
                "maximum": 1.0
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
                "infoText": "List of depths at which the manure is injected into the soil.\nUnits: mm."
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
                "infoText": "List of fractions of manure which remain on the soil surface when applied via injection."
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
        "manure_types": {
            "title": "Manure Types",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The type of manure which will be requested for the application."
            },
            "items": {
                "title": "Manure Types Element",
                "type": "string",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "enum": [
                    "liquid",
                    "solid"
                ],
                "format": "select2"
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
                "infoText": "Number of times that this manure application schedule should be repeated."
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
        }
    }
}