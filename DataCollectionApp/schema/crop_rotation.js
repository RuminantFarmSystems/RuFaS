crop_rotation_schema = {
    "title": "Crop Specifications",
    "type": "object",
    "properties": {
        "crop_rotation": {
            "title": "Crop Specification",
            "type": "array",
            "description": "A Crop Specification is a pattern of planting and harvesting for a species. Add one Crop Specification per species unless they are planted or harvested at different timees/patterns",
            "items": {
                "title": "Crop Spec",
                "type": "object",
                "properties": {
                    "crop_species": {
                        "title": "Species",
                        "type": "select2",
                        "required": true,
                        "enum": [
                            "generic",
                            "corn",
                            "silage_corn",
                            "spring_wheat",
                            "winter_wheat",
                            "cereal_rye",
                            "spring_barley",
                            "fall_oats",
                            "tall_fescue",
                            "alfalfa",
                            "soybean",
                            "sugar_beet",
                            "potato",
                            "triticale"],
                        "options": {
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "harvest_days": {
                        "title": "Harvest Days",
                        "type": "array",
                        "description": "Only necessary to fill this out if previous field 'Harvest Scheduling' is set to 'scheduled'",
                        "items": {
                            "type": "number",
                            "format": "range",
                            "title": "Harvest Day",
                            "minimum": 1,
                            "maximum": 366
                        },
                        "options": {
                            "infoText": "Julian day(s) of year to harvest",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                    "harvest_years": {
                        "title": "Harvest Year",
                        "type": "array",
                        "items": {
                            "type": "number",
                            "format": "range",
                            "title": "Year",
                            "minimum": 1950,
                            "maximum": 2050,
                            "default": 2023,
                        },
                        "options": {
                            "infoText": "Years in which the harvesting occurs",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "harvest_operations": {
                        "title": "Harvest Operations",
                        "type": "array",
                        "items": {
                            "title": "Harvest Operation",
                            "type": "string",
                            "format": "radio",
                            "enum": [
                                "default",
                                "no_kill",
                            ],
                            "default": "default",
                        },
                        "options": {
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "harvest_type": {
                        "title": "Harvest Types",
                        "type": "array",
                        "items": {
                            "title": "Harvest Type",
                            "type": "string",
                            "format": "radio",
                            "enum": [
                                "scheduled",
                                "optimal",
                            ],
                            "default": "scheduled",
                        },
                        "options": {
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        }
                    },
                    "planting_days": {
                        "title": "Planting Days",
                        "type": "array",
                        "options": {
                            "infoText": "Julian day(s) of year to plant",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                        "items": {
                            "type": "string",
                            "format": "range",
                            "title": "Planting Day",
                            "minimum": 1,
                            "maximum": 366
                        }
                    },
                    "planting_years": {
                        "title": "Planting Years",
                        "type": "array",
                        "options": {
                            "infoText": "Years in which the planting occurs",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                        "items": {
                            "type": "string",
                            "format": "range",
                            "title": "Year",
                            "minimum": 1950,
                            "maximum": 2050,
                            "default": 2023
                        }
                    },
                    "pattern_repeat": {
                        "title": "Pattern Repeat",
                        "type": "number",
                        "minimum": 0,
                        "default": 0,
                        "options": {
                            "infoText": "Number of times that this crop schedule should be repeated.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
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
                            }
                        }
                    },
                },
            }
        }
    }
}