tractor_dataset_schema = {
    "title": "tractor_dataset_properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "ID": {
            "title": "ID",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Unique integer identifier for the data entry"
            },
            "items": {
                "title": "ID_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                }
            }
        },
        "Crop Type or Tillage Implement": {
            "title": "Crop Type or Tillage Implement",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "No description available"
            },
            "items": {
                "title": "Crop Type or Tillage Implement_element",
                "type": "string",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": "untitled"
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
                "title": "Tractor Size_element",
                "type": "string",
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
                "format": "select2"
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
                "title": "Operation_element",
                "type": "string",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                }
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
                "title": "Depth_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0,
                "maximum": 10,
                "default": 0
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
                "title": "Tractor Implement_element",
                "type": "string",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                }
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
                "title": "Tractor A (unitless)_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0
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
                "title": "Tractor B (unitless)_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0
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
                "title": "Tractor C (unitless)_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0
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
                "title": "Tractor Implement Width (m)_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0,
                "default": 0
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
                "title": "Tractor Implement Mass (kg)_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 0,
                "default": 0
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
                "title": "Tractor E (unitless)_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0
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
                "title": "Tractor F (unitless)_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0
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
                "title": "Tractor G (unitless)_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0
            }
        },
        "is depth relevant": {
            "title": "is depth relevant",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "true if depth is relevant for attachment operation, otherwise false"
            },
            "items": {
                "title": "is depth relevant_element",
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
            "title": "Max Throughput (tons dm/hour)",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "The maximum throughput of the implement (tons dm/hour)"
            },
            "items": {
                "title": "Max Throughput (tons dm/hour)_element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "default": 0
            }
        }
    }
}