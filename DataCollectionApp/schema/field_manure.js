field_manure_schema = {
    "title": "Field Manure Management",
    "type": "object",
    "format": "grid",
    "properties": {
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
                "infoText": "List of years in which manure will be applied.",
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
                "infoText": "List of days on which manure will be applied.",
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
                "infoText": "List of minimum nitrogen masses that the corresponding manure applications should contain.\nUnits: kg.",
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
                "infoText": "List of minimum phosphorus masses that the corresponding manure applications should contain.\nUnits: kg.",
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
                "infoText": "List of minimum potassium masses that the corresponding manure applications should contain.\nUnits: kg.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "coverage_fractions": {
            "title": "Coverage Fractions",
            "type": "array",
            "items": {
                "type": "number",
                "title": "Coverage Fraction",
                "minimum": 0.01,
                "maximum": 1.0,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of fractions of how much of the field is covered by the corresponding manure application.",
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
                "infoText": "List of depths at which the manure is injected into the soil.\nUnits: mm.",
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
                "infoText": "List of fractions of manure which remain on the soil surface when applied via injection.",
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
                "infoText": "Number of times that this manure application schedule should be repeated.",
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