field_tillage_schema = {
    "title": "Field Tillage Management",
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
                "infoText": "List of years in which tillage will occur.",
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
                "infoText": "List of days on which tilling will occur.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "tillage_depths": {
            "title": "Tillage Depths",
            "type": "array",
            "items": {
                "type": "number",
                "title": "Tillage Depth",
                "minimum": 0.1,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of depths that the corresponding tillage applications reach.\nUnits: mm.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "incorporation_fractions": {
            "title": "Incorporation Fractions",
            "type": "array",
            "items": {
                "type": "number",
                "title": "Incorporation Fraction",
                "minimum": 0.0,
                "maximum": 1.0,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of fractions of surface pools that get incorporated into the soil during applications.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            }
        },
        "mixing_fractions": {
            "title": "Mixing Fractions",
            "type": "array",
            "items": {
                "type": "number",
                "title": "Mixing Fraction",
                "minimum": 0.0,
                "maximum": 1.0,
                "options": {
                    "inputAttributes": {
                        "class": "text-primary form-control",
                    }
                }
            },
            "options": {
                "infoText": "List of fractions of soil layer pools that are available to mix into other soil layers.",
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
                "infoText": "Number of times that this tillage schedule should be repeated.",
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