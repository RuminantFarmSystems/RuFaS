soil_inputs_schema = {
    "title": "Field Soil Profiles",
    "type": "object",
    "format": "grid",
    "properties": {
        "second_moisture_condition_parameter": {
            "title": "Second Moisture Condition Parameter",
            "type": "number",
            "minimum": 30,
            "maximum": 100,
            "default": 85,
            "options": {
                "infoText": "Curve number parameter for average moisture condition equation.\nUnitless.\nReference: SWAT Input .MGT - CN2.",
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "grid_columns": 6,
            }
        },
        "average_subbasin_slope": {
            "title": "Average Subbasin Slope",
            "type": "number",
            "default": 0.05,
            "options": {
                "infoText": "Slope of the field, measured as rise over run.\nUnits: meters / meters or unitless.\nReference: SWAT Input .HRU - HRU_SLP.",
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "grid_columns": 6,
            }
        },
        "manning_roughness_coefficient": {
            "title": "Manning Roughness Coefficient",
            "type": "number",
            "minimum": 0.001,
            "default": 0.4,
            "options": {
                "infoText": "Manning's \"n\" value for overland flow.\nUnitless.\nReference: SWAT Input .HRU - OV_N.",
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "grid_columns": 6,
            }
        },
        "support_practice_factor": {
            "title": "Support Practice Factor",
            "type": "number",
            "default": 0.08,
            "options": {
                "infoText": "Ratio of soil loss with a specific support practice based on slope characteristics.This value adjusts for terracing, contouring, and stripcropping, and these features are not present in V1, so this value IS NOT used.\nUnitless.\nReference: SWAT Input .MGT - USLE_P.",
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "grid_columns": 6,
            }
        },
        "albedo": {
            "title": "Albedo",
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "default": 0.16,
            "options": {
                "infoText": "Ratio of solar radiation reflected by soil to amount of incident upon it.\nUnitless.\nReference: SWAT Input .SOL - SOL_ALB.",
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "grid_columns": 6,
            }
        },
        "initial_residue": {
            "title": "Initial Residue",
            "type": "number",
            "minimum": 0.0,
            "default": 0.0,
            "options": {
                "infoText": "Amount of residue present on the soil surface at the start of the simulation.\nUnits: kg / ha.",
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "grid_columns": 6,
            }
        },
        "soil_evaporation_compensation_coefficient": {
            "title": "Soil Evaporation Compensation Coefficient",
            "type": "number",
            "minimum": 0.01,
            "maximum": 1.0,
            "default": 0.95,
            "options": {
                "infoText": "Modifies depth distribution used to meet soil evaporative demand.\nUnitless.\nReference: SWAT Input .HRU, .BSN - ESCO.",
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "grid_columns": 6,
            }
        },
        "soil_layers": {
            "title": "Soil Layers",
            "type": "array",
            "options": {
                "infoText": "The soil layers that this profile contains. Each element of the array should be a `soil_layer` object.",
                "inputAttributes": {
                    "class": "text-primary form-control",
                }
            },
            "items": {
                "title": "Soil Layer",
                "type": "object",
                "description": "This represents a single soil layer.",
                "format": "grid",
                "properties": {
                    "bottom_depth": {
                        "title": "Bottom Depth",
                        "type": "number",
                        "minimum": 20,
                        "options": {
                            "infoText": "Bottom depth of this soil layer.\nUnits: mm.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "soil_water_concentration": {
                        "title": "Soil Water Concentration",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 0.95,
                        "default": 0.25,
                        "options": {
                            "infoText": "Concentration of water in this layer at the beginning of the simulation.\nUnits: mm water / mm soil.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "field_capacity_water_concentration": {
                        "title": "Field Capacity Water Concentration",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 0.95,
                        "default": 0.3,
                        "options": {
                            "infoText": "Concentration of water in this layer when at field capacity.\nUnits: mm water / mm soil.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "wilting_point_water_concentration": {
                        "title": "Wilting Point Water Concentration",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 0.95,
                        "default": 0.2,
                        "options": {
                            "infoText": "Concentration of water in this layer when at field capacity.\nUnits: mm water / mm soil.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "saturation_point_water_concentration": {
                        "title": "Saturation Point Water Concentration",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 0.95,
                        "default": 0.5,
                        "options": {
                            "infoText": "Concentration of water in a layer when it has become saturated.\nUnits: mm water / mm soil.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "temperature": {
                        "title": "Temperature",
                        "type": "number",
                        "default": 15.05,
                        "options": {
                            "infoText": "Temperature of the layer at the beginning of the simulation.\nUnits: degrees Celsius.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "saturated_hydraulic_conductivity": {
                        "title": "Saturated Hydraulic Conductivity",
                        "type": "number",
                        "minimum": 0.01,
                        "default": 9.5,
                        "options": {
                            "infoText": "Measure of ease of water movement through the soil.\nUnits: mm / hour.\nReference: SWAT Input .SOL - SOL_K.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "bulk_density": {
                        "title": "Bulk Density",
                        "type": "number",
                        "minimum": 1.1,
                        "maximum": 1.9,
                        "default": 1.4,
                        "options": {
                            "infoText": "Ratio of mass of solid particles to total volume of soil.\nUnits: Megagrams / cubic meter or grams / cubic centimeter.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "percent_organic_carbon_content": {
                        "title": "Percent Organic Carbon Content",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 100.0,
                        "default": 1.2,
                        "options": {
                            "infoText": "Percent of soil weight that is organic carbon.\nUnitless.\nReference: SWAT Input .SOL - SOL_CBN.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "percent_clay_content": {
                        "title": "Percent Clay Content",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 100.0,
                        "default": 22.5,
                        "options": {
                            "infoText": "Percent of soil weight that is clay.\nUnitless.\nReference: SWAT Input .SOL - SOL_CLAY.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "percent_silt_content": {
                        "title": "Percent Silt Content",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 100.0,
                        "default": 62.5,
                        "options": {
                            "infoText": "Percent of soil weight that is silt.\nUnitless.\nReference: SWAT Input .SOL - SOL_SILT.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "percent_sand_content": {
                        "title": "Percent Sand Content",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 100.0,
                        "default": 12.5,
                        "options": {
                            "infoText": "Percent of soil weight that is sand.\nUnitless.\nReference: SWAT Input .SOL - SOL_SILT.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "percent_rock_content": {
                        "title": "Percent Rock Content",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 100.0,
                        "default": 1.3,
                        "options": {
                            "infoText": "Percent of soil weight that is rock.\nUnitless.\nReference: SWAT Input .SOL - SOL_SILT.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "initial_labile_inorganic_phosphorus_concentration": {
                        "title": "Initial Labile Inorganic Phosphorus Concentration",
                        "type": "number",
                        "minimum": 0.0,
                        "default": null,
                        "options": {
                            "infoText": "Concentration of nitrate in the layer at the beginning of the simulation.\nUnits: milligrams / kilogram soil.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "initial_fresh_organic_phosphorus_concentration": {
                        "title": "Initial Fresh Organic Phosphorus Concentration",
                        "type": "number",
                        "minimum": 0.0,
                        "default": 0.0,
                        "options": {
                            "infoText": "Concentration of fresh organic phosphorus at the beginning of the simulation.\nUnits: milligrams / kilogram soil.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "initial_soil_nitrate_concentration": {
                        "title": "Initial Soil Nitrate Concentration",
                        "type": "number",
                        "minimum": 0.0,
                        "default": null,
                        "options": {
                            "infoText": "Concentration of nitrate in the layer at the beginning of the simulation.\nUnits: milligrams / kilogram soil.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "initial_soil_ammonium_concentration": {
                        "title": "Initial Soil Ammonium Concentration",
                        "type": "number",
                        "minimum": 0.0,
                        "default": null,
                        "options": {
                            "infoText": "Concentration of ammonium in the layer at the beginning of the simulation.\nUnits: milligrams / kilogram soil.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "humus_mineralization_rate_factor": {
                        "title": "Humus Mineralization Rate Factor",
                        "type": "number",
                        "minimum": 0.0,
                        "default": 0.0003,
                        "options": {
                            "infoText": "Rate factor for humus mineralization of active organic nutrients (N and P).\nUnitless.\nReference: SWAT Input .BSN - CMN.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "denitrification_rate_coefficient": {
                        "title": "Denitrification Rate Coefficient",
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 3.0,
                        "default": 1.4,
                        "options": {
                            "infoText": "Controls the rate of denitrification.\nUnitless.\nReference: SWAT Input .BSN - CDN.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "denitrification_threshold_water_content": {
                        "title": "Denitrification Threshold Water Content",
                        "type": "number",
                        "minimum": 0.0,
                        "default": 1.1,
                        "options": {
                            "infoText": "Fraction of field capacity water content above which denitrification takes place.\nUnitless.\nReference: SWAT Input .BSN - SDNCO.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    },
                    "residue_fresh_organic_mineralization_rate": {
                        "title": "Residue Fresh Organic Mineralization Rate",
                        "type": "number",
                        "minimum": 0.0,
                        "default": 0.05,
                        "options": {
                            "infoText": "Fraction of residue that will decompose in a day given optimal conditions.\nUnitless.\nReference SWAT Input: .BSN - RSDCO.",
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "grid_columns": 6,
                        }
                    }
                }
            }
        }
    }
}