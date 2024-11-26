tillage_schedule_schema = {
    "title": "Tillage Schedule Properties",
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
                "infoText": "List of years in which tillage will occur."
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
                "infoText": "List of days on which tilling will occur."
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
        "tillage_depths": {
            "title": "Tillage Depths",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of depths that the corresponding tillage applications reach.\nUnits: mm."
            },
            "items": {
                "title": "Tillage Depths Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0.1,
                "type": "number"
            }
        },
        "incorporation_fractions": {
            "title": "Incorporation Fractions",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of fractions of surface pools that get incorporated into the soil during applications."
            },
            "items": {
                "title": "Incorporation Fractions Element",
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
        "mixing_fractions": {
            "title": "Mixing Fractions",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of fractions of soil layer pools that are available to mix into other soil layers."
            },
            "items": {
                "title": "Mixing Fractions Element",
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
        "implements": {
            "title": "Implements",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "List of tillage implements which will be used to execute the tillage operations."
            },
            "items": {
                "title": "Implements Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "enum": [
                    "subsoiler",
                    "moldboard-plow",
                    "coulter-chisel-plow",
                    "disk-harrow",
                    "cultivator",
                    "seedbed-conditioner"
                ],
                "format": "select2",
                "type": "string"
            }
        },
        "pattern_repeat": {
            "title": "Pattern Repeat",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Number of times that this tillage schedule should be repeated."
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