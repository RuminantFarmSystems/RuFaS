tractor_dataset_schema = {
    "title": "Tractor Dataset Properties",
    "format": "grid",
    "properties": {
        "ID": {
            "title": "Id",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Unique integer identifier for the data entry"
            },
            "items": {
                "title": "Id Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "type": "number"
            }
        },
        "Crop Type or Tillage Implement": {
            "title": "Crop Type Or Tillage Implement",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "No description available"
            },
            "items": {
                "title": "Crop Type Or Tillage Implement Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": "untitled",
                "type": "string"
            }
        },
        "Tractor Size": {
            "title": "Tractor Size",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The categorical size of the tractor"
            },
            "items": {
                "title": "Tractor Size Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": "medium",
                "enum": [
                    "small",
                    "medium",
                    "large"
                ],
                "format": "select2",
                "type": "string"
            }
        },
        "Operation": {
            "title": "Operation",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "No description available"
            },
            "items": {
                "title": "Operation Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "type": "string"
            }
        },
        "Depth": {
            "title": "Depth",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "How deep in the soil the implement goes"
            },
            "items": {
                "title": "Depth Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0,
                "maximum": 10,
                "default": 0,
                "type": "number"
            }
        },
        "Tractor Implement": {
            "title": "Tractor Implement",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The implement that is attached to the tractor"
            },
            "items": {
                "title": "Tractor Implement Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "type": "string"
            }
        },
        "Tractor A (unitless)": {
            "title": "Tractor A (unitless)",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Parameter A as described in the scientific references"
            },
            "items": {
                "title": "Tractor A (unitless) Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0,
                "type": "number"
            }
        },
        "Tractor B (unitless)": {
            "title": "Tractor B (unitless)",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Parameter B as described in the scientific references"
            },
            "items": {
                "title": "Tractor B (unitless) Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0,
                "type": "number"
            }
        },
        "Tractor C (unitless)": {
            "title": "Tractor C (unitless)",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Parameter C as described in the scientific references"
            },
            "items": {
                "title": "Tractor C (unitless) Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0,
                "type": "number"
            }
        },
        "Tractor Implement Width (m)": {
            "title": "Tractor Implement Width (m)",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The width of the implement in meters"
            },
            "items": {
                "title": "Tractor Implement Width (m) Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0,
                "default": 0,
                "type": "number"
            }
        },
        "Tractor Implement Mass (kg)": {
            "title": "Tractor Implement Mass (kg)",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The mass of the implement in kg"
            },
            "items": {
                "title": "Tractor Implement Mass (kg) Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0,
                "default": 0,
                "type": "number"
            }
        },
        "Tractor E (unitless)": {
            "title": "Tractor E (unitless)",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Parameter E as described in the scientific references"
            },
            "items": {
                "title": "Tractor E (unitless) Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0,
                "type": "number"
            }
        },
        "Tractor F (unitless)": {
            "title": "Tractor F (unitless)",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Parameter F as described in the scientific references"
            },
            "items": {
                "title": "Tractor F (unitless) Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0,
                "type": "number"
            }
        },
        "Tractor G (unitless)": {
            "title": "Tractor G (unitless)",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Parameter G as described in the scientific references"
            },
            "items": {
                "title": "Tractor G (unitless) Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0,
                "type": "number"
            }
        },
        "is depth relevant": {
            "title": "Is Depth Relevant",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "true if depth is relevant for attachment operation, otherwise false"
            },
            "items": {
                "title": "Is Depth Relevant Element",
                "type": "boolean",
                "format": "checkbox",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                }
            }
        },
        "Max Throughput (tons dm/hour)": {
            "title": "Max Throughput (tons Dm/hour)",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The maximum throughput of the implement (tons dm/hour)"
            },
            "items": {
                "title": "Max Throughput (tons Dm/hour) Element",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0,
                "type": "number"
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
                "infoText": "Used to name the file that saves the data entered. This name will not be included in the saved file."
            }
        }
    },
    "type": "object"
}