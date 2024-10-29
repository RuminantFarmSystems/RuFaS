general_simulation_inputs_schema = {
    "title": "General Simulation Settings",
    "type": "object",
    "properties": {
        "simulation_config": {
            "title": "Simulation Configuration",
            "type": "object",
            "format": "grid",
            "options": {
                "collapsed": "true"
            },
            "properties": {
                "weather": {
                    "title": "Weather Configuration File",
                    "type": "string",
                    "readonly": true,
                    "default": "barnyard_weather.csv",
                    "options": {
                        "inputAttributes": {
                            "placeholder": "deafault_weather.csv",
                            "class": "text-primary form-control"
                        }
                    }
                },
                "output": {
                    "title": "Output Configuration File",
                    "type": "string",
                    "readonly": true,
                    "default": "all_reports.json",
                    "options": {
                        "inputAttributes": {
                            "placeholder": "all_reports.json",
                            "class": "text-primary form-control"
                        }
                    }
                },
                "csv_dir": {
                    "title": "CSV Directory Location",
                    "type": "string",
                    "readonly": true,
                    "default": "output/CSVs/",
                    "options": {
                        "inputAttributes": {
                            "placeholder": "output/CSVs/",
                            "class": "text-primary form-control"
                        }
                    }
                },
                "graphic_dir": {
                    "title": "Graphics Directory Location",
                    "type": "string",
                    "readonly": true,
                    "default": "output/graphics/",
                    "options": {
                        "inputAttributes": {
                            "placeholder": "output/graphics/",
                            "class": "text-primary form-control"
                        }
                    }
                },
                "set_seed": {
                    "title": "Set Seed?",
                    "type": "radio",
                    "readonly": true,
                    "enum": [
                        "False"
                    ]
                },
                "seed": {
                    "title": "Seed",
                    "type": "number",
                    "readonly": true,
                    "default": 0,
                    "options": {
                        "inputAttributes": {
                            "placeholder": 0,
                            "class": "text-primary form-control"
                        }
                    }
                }
            },
        },
        "start_date": {
            "title": "Simulation Start Date",
            "type": "string",
            "format": "date",
            "options": {
                "grid_columns": 6,
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            }
        },
        "end_date": {
            "title": "Simulation End Date",
            "type": "string",
            "format": "date",
            "options": {
                "grid_columns": 6,
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            }
        }
    }
}