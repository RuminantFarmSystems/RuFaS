feed_schema = {
    "title": "Feed Properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "calf_feeds": {
            "title": "Calf Feeds",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Calf Feeds (raised off farm - 24 hrs of age)."
            },
            "items": {
                "title": "Calf Feeds Element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 1,
                "maximum": 306,
                "default": 155
            }
        },
        "growing_feeds": {
            "title": "Growing Feeds",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Growing Feeds (HeiferI and HeiferII - return at 20 months) -- HeiferI is the number of youngstock post-weaning and before breeding. Heifer II is the number of heifers eligible for breeding and in early pregnancy."
            },
            "items": {
                "title": "Growing Feeds Element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 1,
                "maximum": 306
            }
        },
        "close_up_feeds": {
            "title": "Close Up Feeds",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Close Up Feeds (HeiferIII and Dry Cows) -- HeiferIII is the number of close-up heifers and Dry Cows are non-lactating cows."
            },
            "items": {
                "title": "Close Up Feeds Element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 1,
                "maximum": 306
            }
        },
        "lac_cow_feeds": {
            "title": "Lac Cow Feeds",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Lactating Cow Feeds"
            },
            "items": {
                "title": "Lac Cow Feeds Element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 1,
                "maximum": 306
            }
        },
        "purchased_feeds": {
            "title": "Purchased Feeds",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Purchased Feeds."
            },
            "items": {
                "title": "Purchased Feeds Element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "purchased_feed": {
                        "title": "Purchased Feed",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "No description available"
                        },
                        "minimum": 1,
                        "maximum": 306
                    },
                    "purchased_feed_cost": {
                        "title": "Purchased Feed Cost",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Cost of Feed (US dollars/kg DM)"
                        },
                        "minimum": 0
                    }
                }
            }
        },
        "farm_grown_feeds": {
            "title": "Farm Grown Feeds",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Farm-Grown Feeds"
            },
            "items": {
                "title": "Farm Grown Feeds Element",
                "type": "number",
                "options": {
                    "grid_columns": 12,
                    "inputAttributes": {
                        "class": "text-primary form-control"
                    }
                },
                "minimum": 1,
                "maximum": 306
            }
        },
        "storage_options": {
            "title": "Storage Options",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Storage Options."
            },
            "items": {
                "title": "Storage Options Element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "storage_type": {
                        "title": "Storage Type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Storage Type -- The type of storage unit used. This only applies to farm grown forage feeds"
                        },
                        "default": "Bunker Silo",
                        "enum": [
                            "8' Diameter Bag",
                            "10' Diameter Bag",
                            "12' Diameter Bag",
                            "14' Diameter Bag",
                            "Upright Silo - Traditional",
                            "Upright Silo - Oxygen-Excluding",
                            "Bunker Silo",
                            "Pile",
                            "Wrapped Bale",
                            "Bale - Covered",
                            "Bale - Uncovered",
                            "Bin"
                        ],
                        "format": "select2"
                    },
                    "moisture": {
                        "title": "Moisture",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Moisture -- The management practices used that determine the dry matter content of the preserved feed."
                        },
                        "default": "Wilted",
                        "enum": [
                            "Direct Cut",
                            "Wilted",
                            "Baleage",
                            "Haylage",
                            "Moist Hay",
                            "Dry Hay"
                        ],
                        "format": "select2"
                    },
                    "additive": {
                        "title": "Additive",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Additive -- Type of additive added to the forage material before ensiling."
                        },
                        "default": "preservative",
                        "enum": [
                            "preservative",
                            "nutrient additive",
                            "absorbant"
                        ],
                        "format": "select2"
                    },
                    "packing_density": {
                        "title": "Packing Density",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Packing Density -- The density of ensiled feed material, kg DM /m3"
                        },
                        "minimum": 200,
                        "maximum": 800,
                        "default": 200
                    },
                    "inoculation": {
                        "title": "Inoculation",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Inoculation"
                        },
                        "default": "None",
                        "enum": [
                            "None",
                            "heterofermentative",
                            "homofermentative"
                        ],
                        "format": "select2"
                    },
                    "bunk_type": {
                        "title": "Bunk Type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Bunk Type -- The type of bunk used to store the feed."
                        },
                        "default": "open_floor",
                        "enum": [
                            "open_floor"
                        ],
                        "format": "select2"
                    },
                    "ventilation": {
                        "title": "Ventilation",
                        "type": "boolean",
                        "format": "checkbox",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Ventilation -- True if the storage unit has appropriate ventilation."
                        },
                        "default": true
                    },
                    "removal_rate": {
                        "title": "Removal Rate",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Removal Rate -- Average rate of removal of material from the storage unit or silo described as the horizontal distance from the front of the storage. In units of meters."
                        },
                        "minimum": 0,
                        "maximum": 20,
                        "default": 0.5
                    },
                    "initial_dry_matter": {
                        "title": "Initial Dry Matter",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Initial Dry Matter -- The mass of feed dry matter in the storage unit at initiation of the simulation."
                        },
                        "minimum": 0,
                        "maximum": 500000,
                        "default": 1000
                    }
                }
            }
        },
        "user_defined_ration_percentages": {
            "title": "User Defined Ration Percentages",
            "type": "object",
            "format": "grid",
            "properties": {
                "calf": {
                    "title": "Calf",
                    "type": "array",
                    "format": "grid",
                    "options": {
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Calf Feeds."
                    },
                    "items": {
                        "title": "Calf Element",
                        "type": "object",
                        "format": "grid",
                        "properties": {
                            "feed_type": {
                                "title": "Feed Type",
                                "type": "number",
                                "options": {
                                    "grid_columns": 12,
                                    "inputAttributes": {
                                        "class": "text-primary form-control"
                                    },
                                    "infoText": "Calf Feed"
                                },
                                "minimum": 1,
                                "maximum": 306,
                                "default": 155
                            },
                            "ration_percentage": {
                                "title": "Ration Percentage",
                                "type": "number",
                                "options": {
                                    "grid_columns": 12,
                                    "inputAttributes": {
                                        "class": "text-primary form-control"
                                    },
                                    "infoText": "Calf Ration Percentage"
                                },
                                "minimum": 0,
                                "maximum": 100
                            }
                        }
                    }
                },
                "growing": {
                    "title": "Growing",
                    "type": "array",
                    "format": "grid",
                    "options": {
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Growing Heifers Feeds."
                    },
                    "items": {
                        "title": "Growing Element",
                        "type": "object",
                        "format": "grid",
                        "properties": {
                            "feed_type": {
                                "title": "Feed Type",
                                "type": "number",
                                "options": {
                                    "grid_columns": 12,
                                    "inputAttributes": {
                                        "class": "text-primary form-control"
                                    },
                                    "infoText": "Growing Heifers Feed"
                                },
                                "minimum": 1,
                                "maximum": 306,
                                "default": 1
                            },
                            "ration_percentage": {
                                "title": "Ration Percentage",
                                "type": "number",
                                "options": {
                                    "grid_columns": 12,
                                    "inputAttributes": {
                                        "class": "text-primary form-control"
                                    },
                                    "infoText": "Growing Heifers Ration Percentage"
                                },
                                "minimum": 0,
                                "maximum": 100
                            }
                        }
                    }
                },
                "close_up": {
                    "title": "Close Up",
                    "type": "array",
                    "format": "grid",
                    "options": {
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Close UP Feeds."
                    },
                    "items": {
                        "title": "Close Up Element",
                        "type": "object",
                        "format": "grid",
                        "properties": {
                            "feed_type": {
                                "title": "Feed Type",
                                "type": "number",
                                "options": {
                                    "grid_columns": 12,
                                    "inputAttributes": {
                                        "class": "text-primary form-control"
                                    },
                                    "infoText": "Close UP Feed"
                                },
                                "minimum": 1,
                                "maximum": 306,
                                "default": 1
                            },
                            "ration_percentage": {
                                "title": "Ration Percentage",
                                "type": "number",
                                "options": {
                                    "grid_columns": 12,
                                    "inputAttributes": {
                                        "class": "text-primary form-control"
                                    },
                                    "infoText": "Close UP Ration Percentage"
                                },
                                "minimum": 0,
                                "maximum": 100
                            }
                        }
                    }
                },
                "lac_cow": {
                    "title": "Lac Cow",
                    "type": "array",
                    "format": "grid",
                    "options": {
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Lactating Cow Feeds."
                    },
                    "items": {
                        "title": "Lac Cow Element",
                        "type": "object",
                        "format": "grid",
                        "properties": {
                            "feed_type": {
                                "title": "Feed Type",
                                "type": "number",
                                "options": {
                                    "grid_columns": 12,
                                    "inputAttributes": {
                                        "class": "text-primary form-control"
                                    },
                                    "infoText": "Lactating Cow Feed"
                                },
                                "minimum": 1,
                                "maximum": 306,
                                "default": 1
                            },
                            "ration_percentage": {
                                "title": "Ration Percentage",
                                "type": "number",
                                "options": {
                                    "grid_columns": 12,
                                    "inputAttributes": {
                                        "class": "text-primary form-control"
                                    },
                                    "infoText": "Lactating Cow Ration Percentage"
                                },
                                "minimum": 0,
                                "maximum": 100
                            }
                        }
                    }
                },
                "tolerance": {
                    "title": "Tolerance",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Tolerance -- Allowable +/- percentage variance in each of the defined ration inclusion percentage values"
                    },
                    "minimum": 0,
                    "maximum": 1
                },
                "milk_reduction_maximum": {
                    "title": "Milk Reduction Maximum",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Milk Reduction Maximum -- Allowable amount of milk reduction (kg) when dietary nutrient supply cannot meet animal requirements"
                    },
                    "minimum": 0,
                    "maximum": 50
                }
            },
            "options": {
                "infoText": "User Defined Ration Percentages"
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
                "infoText": "Used to name the file that saves the data entered."
            }
        }
    }
}