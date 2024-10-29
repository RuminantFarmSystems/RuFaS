animal_schema = {
    "title": "animal_properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "herd_information": {
            "title": "herd_information",
            "type": "object",
            "format": "grid",
            "properties": {
                "calf_num": {
                    "title": "calf_num",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Number of Calves (head) -- The initial number of pre-weaned calves"
                    },
                    "minimum": 2,
                    "default": 8
                },
                "heiferI_num": {
                    "title": "heiferI_num",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Number of HeiferI's (head) -- The initial number of heifers that are weaned but not yet bred"
                    },
                    "minimum": 2,
                    "default": 44
                },
                "heiferII_num": {
                    "title": "heiferII_num",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Number of HeiferII's (head) -- The initial number of heifers that are either eligible for breeding (based on user-inputted Breeding Start Day for heifers), or in early pregnancy"
                    },
                    "minimum": 2,
                    "default": 38
                },
                "heiferIII_num_springers": {
                    "title": "heiferIII_num_springers",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Number of HeiferIII's (head) -- The initial number of close-up heifers (heifers within the user-defined close-up period, i.e. Prefresh Day)"
                    },
                    "minimum": 2,
                    "default": 5
                },
                "cow_num": {
                    "title": "cow_num",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Number of Cows (head) -- The initial number of dry and lactating cows."
                    },
                    "minimum": 6,
                    "default": 100
                },
                "replace_num": {
                    "title": "replace_num",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Replacements (head) -- Number of replacement animals available in the replacement market"
                    },
                    "minimum": 50,
                    "default": 5000
                },
                "herd_num": {
                    "title": "herd_num",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Herd Number (head) -- The target number of dry and lactating cows on the farm"
                    },
                    "minimum": 6,
                    "default": 100
                },
                "breed": {
                    "title": "breed",
                    "type": "string",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Breed (select one) -- The predominant breed of the herd (Holstein or Jersey)"
                    },
                    "default": "HO",
                    "enum": [
                        "HO",
                        "JE"
                    ],
                    "format": "select2"
                },
                "parity_fractions": {
                    "title": "parity_fractions",
                    "type": "object",
                    "format": "grid",
                    "properties": {
                        "1": {
                            "title": "1",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "No description available"
                            },
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "2": {
                            "title": "2",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "No description available"
                            },
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "3": {
                            "title": "3",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "No description available"
                            },
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    },
                    "options": {
                        "infoText": "Fractions of the milking animal population that are parity 1, 2, and 3 and beyond. The sum of these fractions must be 1.0"
                    }
                },
                "annual_milk_yield": {
                    "title": "annual_milk_yield",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "The total milk yield generated by the farm in one year (kg). If this information is not available, it can be input as null"
                    },
                    "minimum": 0
                }
            },
            "options": {
                "infoText": "Herd Demographics"
            }
        },
        "herd_initialization": {
            "title": "herd_initialization",
            "type": "object",
            "format": "grid",
            "properties": {
                "initial_animal_num": {
                    "title": "initial_animal_num",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "The initial number of animals for the simulation starting with to generate the herd"
                    },
                    "minimum": 0,
                    "default": 10000
                },
                "simulation_days": {
                    "title": "simulation_days",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "The number of days to simulate for generating the herd"
                    },
                    "minimum": 0,
                    "default": 5000
                }
            },
            "options": {
                "infoText": "Animal generation related inputs"
            }
        },
        "animal_config": {
            "title": "animal_config",
            "type": "object",
            "format": "grid",
            "properties": {
                "management_decisions": {
                    "title": "management_decisions",
                    "type": "object",
                    "format": "grid",
                    "properties": {
                        "breeding_start_day_h": {
                            "title": "breeding_start_day_h",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Heifer Breeding Start Day (days) -- Days old when RuFaS initiates estrus protocol (first cycle to occur ~21 days later)"
                            },
                            "minimum": 0,
                            "default": 380
                        },
                        "heifer_repro_method": {
                            "title": "heifer_repro_method",
                            "type": "string",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Heifer Reproductive Program (select one) -- TAI - Timed Artificial Insemination; ED - Estrus Detection; Synch-ED - Synchronized Estrus Detection"
                            },
                            "default": "TAI",
                            "enum": [
                                "TAI",
                                "ED",
                                "SynchED"
                            ],
                            "format": "select2"
                        },
                        "cow_repro_method": {
                            "title": "cow_repro_method",
                            "type": "string",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Cow Reproduction Protocol (select one) -- TAI - Timed Artificial Insemination; ED - Estrus Detection; ED-TAI - Combination of ED and TAI"
                            },
                            "default": "TAI",
                            "enum": [
                                "TAI",
                                "ED",
                                "ED-TAI"
                            ],
                            "format": "select2"
                        },
                        "semen_type": {
                            "title": "semen_type",
                            "type": "string",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Semen type (select one) -- The semen type (sexed or conventional) that makes up a majority of the farm's breedings"
                            },
                            "default": "conventional",
                            "enum": [
                                "sexed",
                                "conventional"
                            ],
                            "format": "select2"
                        },
                        "days_in_preg_when_dry": {
                            "title": "days_in_preg_when_dry",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Days In Pregnancy When Dry (days) -- The average days in pregnancy of cows at dry-off"
                            },
                            "minimum": 0,
                            "default": 218
                        },
                        "heifer_repro_cull_time": {
                            "title": "heifer_repro_cull_time",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Heifer Reproduction Cull Time (days) -- Days old when a heifer would be culled for failure to become pregnant"
                            },
                            "minimum": 0,
                            "default": 500
                        },
                        "do_not_breed_time": {
                            "title": "do_not_breed_time",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Cow Do Not Breed Time (days) -- The length of the breeding period after parturition for cows after which reproduction protocols stop if they fail to get pregnant"
                            },
                            "minimum": 0,
                            "default": 185
                        },
                        "cull_milk_production": {
                            "title": "cull_milk_production",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Cull Milk Production (kg/d) -- Milk production threshold at which 'do not breed' cows are culled if they fall below"
                            },
                            "minimum": 0,
                            "default": 30
                        },
                        "cow_times_milked_per_day": {
                            "title": "cow_times_milked_per_day",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Number of Milkings (per day) -- The average or most common number of times cows are milked per day (1, 2, or 3 times daily)"
                            },
                            "minimum": 0,
                            "default": 3
                        },
                        "milk_fat_percent": {
                            "title": "milk_fat_percent",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Milk Fat Percent (percent) -- The average or most common milk fat percentage in cow milk"
                            },
                            "minimum": 0,
                            "default": 3.5
                        },
                        "milk_protein_percent": {
                            "title": "milk_protein_percent",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Milk Protein Percent (percent) -- The average or most common milk protein percentage in cow milk"
                            },
                            "minimum": 0,
                            "default": 3.2
                        }
                    },
                    "options": {
                        "infoText": "General Management"
                    }
                },
                "farm_level": {
                    "title": "farm_level",
                    "type": "object",
                    "format": "grid",
                    "properties": {
                        "calf": {
                            "title": "calf",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "male_calf_rate_sexed_semen": {
                                    "title": "male_calf_rate_sexed_semen",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Male Calf Rate, Sexed Semen (percent) -- The rate of male calves when using sexed semen"
                                    },
                                    "minimum": 0,
                                    "maximum": 1,
                                    "default": 0.1
                                },
                                "male_calf_rate_conventional_semen": {
                                    "title": "male_calf_rate_conventional_semen",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Male Calf Rate, Conventional Semen (percent) -- The rate of male calves when using conventional semen"
                                    },
                                    "minimum": 0,
                                    "maximum": 1,
                                    "default": 0.53
                                },
                                "keep_female_calf_rate": {
                                    "title": "keep_female_calf_rate",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Female Calf Retention Rate (percent) -- The percentage of female calves kept and raised on-farm"
                                    },
                                    "minimum": 0,
                                    "maximum": 1,
                                    "default": 1
                                },
                                "wean_day": {
                                    "title": "wean_day",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Wean Day (days) -- The days of age at which calves are fully weaned from milk or milk replacer"
                                    },
                                    "minimum": 0,
                                    "default": 60
                                },
                                "wean_length": {
                                    "title": "wean_length",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Wean Length (days) -- Length of the weaning process"
                                    },
                                    "minimum": 0,
                                    "default": 7
                                },
                                "milk_type": {
                                    "title": "milk_type",
                                    "type": "string",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Milk Type (select one) -- The type of milk that is used to feed calves (Whole or Replacer)"
                                    },
                                    "default": "whole",
                                    "enum": [
                                        "whole",
                                        "replacer"
                                    ],
                                    "format": "select2"
                                }
                            },
                            "options": {
                                "infoText": "Calf Management"
                            }
                        },
                        "repro": {
                            "title": "repro",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "voluntary_waiting_period": {
                                    "title": "voluntary_waiting_period",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Voluntary Waiting Period (days) -- When the cow's days in milk has reached this day, monitoring for estrus and subsequent breeding, if found, will begin. Used only in the ED and ED-TAI protocols. When TAI protocol is used, this value will be ignored, and it is recommended to set it to 0."
                                    },
                                    "minimum": 0,
                                    "default": 50
                                },
                                "conception_rate_decrease": {
                                    "title": "conception_rate_decrease",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Conception Rate Decrease (percent) -- The percent decrease in conception rate of each breeding after the first breeding"
                                    },
                                    "minimum": 0,
                                    "maximum": 0.1,
                                    "default": 0.026
                                },
                                "decrease_conception_rate_in_rebreeding": {
                                    "title": "decrease_conception_rate_in_rebreeding",
                                    "type": "boolean",
                                    "format": "checkbox",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Decrease Conception Rate in Rebreeding -- whether or not to decrease the conception rate in rebreeding (default is false)"
                                    },
                                    "default": false
                                },
                                "decrease_conception_rate_by_parity": {
                                    "title": "decrease_conception_rate_by_parity",
                                    "type": "boolean",
                                    "format": "checkbox",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Decrease Conception Rate by Parity -- whether or not to decrease the conception rate by parity (default is false)"
                                    },
                                    "default": false
                                },
                                "avg_gestation_len": {
                                    "title": "avg_gestation_len",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Average Gestation Length (days) -- Average length of gestation"
                                    },
                                    "minimum": 0,
                                    "default": 278
                                },
                                "std_gestation_len": {
                                    "title": "std_gestation_len",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Gestation Length Standard Deviation (days) -- Standard deviation of gestation length"
                                    },
                                    "minimum": 0,
                                    "default": 6
                                },
                                "prefresh_day": {
                                    "title": "prefresh_day",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Prefresh Day -- days prior to calving at which pregnant animals enter the close-up period (i.e., the length of the close-up period)"
                                    },
                                    "minimum": 0,
                                    "default": 30
                                },
                                "calving_interval": {
                                    "title": "calving_interval",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Calving Interval (days) -- Current average calving interval, used for initial bodyweight adjustment and other calculations"
                                    },
                                    "minimum": 0,
                                    "default": 400
                                },
                                "heifers": {
                                    "title": "heifers",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "estrus_detection_rate": {
                                            "title": "estrus_detection_rate",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Estrus Detection Rate (percent) -- The percentage of total heifers in estrus that are detected in the ED (Estrus Detection) protocol"
                                            },
                                            "minimum": 0,
                                            "maximum": 1,
                                            "default": 0.6
                                        },
                                        "estrus_conception_rate": {
                                            "title": "estrus_conception_rate",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Estrus Conception Rate (percent) -- The percentage of inseminated heifers that become pregnant in the ED (Estrus Detection) and SynchED protocols"
                                            },
                                            "minimum": 0,
                                            "maximum": 1,
                                            "default": 0.9
                                        },
                                        "repro_sub_protocol": {
                                            "title": "repro_sub_protocol",
                                            "type": "string",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "No description available"
                                            },
                                            "default": "5dCG2P",
                                            "enum": [
                                                "5dCG2P",
                                                "5dCGP",
                                                "2P",
                                                "CP",
                                                "N/A"
                                            ],
                                            "format": "select2"
                                        },
                                        "repro_sub_properties": {
                                            "title": "repro_sub_properties",
                                            "type": "object",
                                            "format": "grid",
                                            "properties": {
                                                "conception_rate": {
                                                    "title": "conception_rate",
                                                    "type": "number",
                                                    "options": {
                                                        "grid_columns": 12,
                                                        "inputAttributes": {
                                                            "class": "text-primary form-control"
                                                        },
                                                        "infoText": "Conception Rate -- The conception rate for the heifer reproductive program (default is 0.6)"
                                                    },
                                                    "minimum": 0,
                                                    "maximum": 1,
                                                    "default": 0.6
                                                },
                                                "estrus_detection_rate": {
                                                    "title": "estrus_detection_rate",
                                                    "type": "number",
                                                    "options": {
                                                        "grid_columns": 12,
                                                        "inputAttributes": {
                                                            "class": "text-primary form-control"
                                                        },
                                                        "infoText": "Estrus Detection Rate -- The % of in-heat animals that would be detected in the ED (Estrus Detection) programs (default is 0.6)"
                                                    },
                                                    "minimum": 0,
                                                    "maximum": 1,
                                                    "default": 0.7
                                                }
                                            }
                                        }
                                    },
                                    "options": {
                                        "infoText": "Heifer Reproduction Protocols"
                                    }
                                },
                                "cows": {
                                    "title": "cows",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "estrus_detection_rate": {
                                            "title": "estrus_detection_rate",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The fraction of in-heat cows that would be detected in the ED (Estrus Detection) protocol, including during the estrus detection portion of ED-TAI protocols. When TAI protocol is used, this value will be ignored, and it is recommended to set it to 0."
                                            },
                                            "minimum": 0,
                                            "maximum": 1,
                                            "default": 0.6
                                        },
                                        "ED_conception_rate": {
                                            "title": "ED_conception_rate",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The fraction of cows with estrus detected that would conceive in the ED (Estrus Detection) protocol, including during the estrus detection portion of ED-TAI protocols. When TAI protocol is used, this value will be ignored, and it is recommended to set it to 0."
                                            },
                                            "minimum": 0,
                                            "maximum": 1,
                                            "default": 0.6
                                        },
                                        "presynch_program": {
                                            "title": "presynch_program",
                                            "type": "string",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The presynch program (1st breeding) for cow in the TAI protocol. Currently, this is only supported in TAI protocol. When other protocols such as ED or ED-TAI are used, this value will be ignored, and it is recommended to set it to None."
                                            },
                                            "default": "Double OvSynch",
                                            "enum": [
                                                "Double OvSynch",
                                                "PreSynch",
                                                "G6G",
                                                "None"
                                            ],
                                            "format": "select2"
                                        },
                                        "presynch_program_start_day": {
                                            "title": "presynch_program_start_day",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The presynch program start day is the day of the first hormone injection in a presynch program used in the TAI protocol. When a presynch program is followed by an OvSynch program, the start day of the OvSynch program should be on or after the last day of the presynch program. The durations of the 3 options - PreSynch, Double OvSynch, and G6G, are 25, 16, and 8 days, respectively. Because the presynch program is only supported in TAI protocol, this value will be ignored when other protocols such as ED or ED-TAI are used, and it is recommended to set it to 0."
                                            },
                                            "minimum": 0,
                                            "default": 50
                                        },
                                        "ovsynch_program": {
                                            "title": "ovsynch_program",
                                            "type": "string",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The OvSynch program to be used for cows in the TAI protocol and the TAI portion of the ED-TAI protocol. When the ED protocol is used, this value will be ignored, and it is recommended to set it to None"
                                            },
                                            "default": "OvSynch 56",
                                            "enum": [
                                                "OvSynch 48",
                                                "OvSynch 56",
                                                "CoSynch 72",
                                                "5d CoSynch",
                                                "None"
                                            ],
                                            "format": "select2"
                                        },
                                        "ovsynch_program_start_day": {
                                            "title": "ovsynch_program_start_day",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "When set properly in the TAI protocol, OvSynch program start day is the day of the first GnRH injection in an OvSynch program. When the OvSynch program follows a presynch program, the start day of the OvSynch program should be on or after the last day of the presynch program. Otherwise, the OvSynch program will be shifted to start on the last day of the presynch program. When ED-TAI protocol is used and no estrus detected between the end of the voluntary waiting period and this OvSynch program start day, then the OvSynch program will start on this day. When the ED protocol is used, this value will be ignored, and it is recommended to set it to 0."
                                            },
                                            "minimum": 0,
                                            "default": 70
                                        },
                                        "ovsynch_program_conception_rate": {
                                            "title": "ovsynch_program_conception_rate",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The conception rate for the OvSynch program used in the TAI protocol and the TAI portion of the ED-TAI protocol. When the ED protocol is used, this value will be ignored, and it is recommended to set it to 0."
                                            },
                                            "minimum": 0,
                                            "maximum": 1,
                                            "default": 0.6
                                        },
                                        "resynch_program": {
                                            "title": "resynch_program",
                                            "type": "string",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Resynch program for cow before/at/after first pregnancy check day in the TAI and ED-TAI repro protocols. When the ED protocol is used, this value will be ignored, and it is recommended to set it to None. If PGFatPD is chosen, the values for estrus detection rate and conception rate to that detected estrus following PGF are determined by estrus_detection_rate and ED_conception_rate. Anytime an insemination is performed after an ovsynch program, the conception rate will be changed to the ovsynch_program_conception_rate."
                                            },
                                            "default": "TAIafterPD",
                                            "enum": [
                                                "TAIafterPD",
                                                "TAIbeforePD",
                                                "PGFatPD",
                                                "None"
                                            ],
                                            "format": "select2"
                                        }
                                    }
                                }
                            },
                            "options": {
                                "infoText": "Repro Management"
                            }
                        },
                        "bodyweight": {
                            "title": "bodyweight",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "birth_weight_avg_ho": {
                                    "title": "birth_weight_avg_ho",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Average Holstein Birth Weight (kg/head)"
                                    },
                                    "minimum": 0,
                                    "default": 42.9
                                },
                                "birth_weight_std_ho": {
                                    "title": "birth_weight_std_ho",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Holstein Birth Weight Standard Deviation (kg/head)"
                                    },
                                    "minimum": 0,
                                    "default": 6
                                },
                                "birth_weight_avg_je": {
                                    "title": "birth_weight_avg_je",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Average Jersey Birth Weight (kg/head)"
                                    },
                                    "minimum": 0,
                                    "default": 25.2
                                },
                                "birth_weight_std_je": {
                                    "title": "birth_weight_std_je",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Jersey Birth Weight Standard Deviation (kg/head)"
                                    },
                                    "minimum": 0,
                                    "default": 4.4
                                },
                                "target_heifer_preg_day": {
                                    "title": "target_heifer_preg_day",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Target Heifer Pregnancy Day (days) -- The target age (in days) for heifers to become pregnant - for adjusting heifer body weight"
                                    },
                                    "minimum": 0,
                                    "default": 420
                                },
                                "mature_body_weight_avg": {
                                    "title": "mature_body_weight_avg",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Average Mature Body Weight (kg/head) -- The average mature body weight of cows"
                                    },
                                    "minimum": 0,
                                    "default": 740.1
                                },
                                "mature_body_weight_std": {
                                    "title": "mature_body_weight_std",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Mature Body Weight Standard Deviation (kg/head) -- The standard deviation of mature body weight of cows"
                                    },
                                    "minimum": 0,
                                    "default": 73.5
                                }
                            },
                            "options": {
                                "infoText": "Bodyweight"
                            }
                        }
                    },
                    "options": {
                        "infoText": "Farm Level Management"
                    }
                },
                "from_literature": {
                    "title": "from_literature",
                    "type": "object",
                    "format": "grid",
                    "properties": {
                        "repro": {
                            "title": "repro",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "preg_check_day_1": {
                                    "title": "preg_check_day_1",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Pregnancy Check Days, Check 1 (days) -- Days since last insemination at the 1st pregnancy check"
                                    },
                                    "minimum": 1,
                                    "default": 32
                                },
                                "preg_loss_rate_1": {
                                    "title": "preg_loss_rate_1",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Pregnancy Loss Rate 1 (percent) -- The percentage of cows that abort their pregnancy before the 1st pregnancy check"
                                    },
                                    "minimum": 0,
                                    "maximum": 1,
                                    "default": 0.02
                                },
                                "preg_check_day_2": {
                                    "title": "preg_check_day_2",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Pregnancy Check Days, Check 2 (days) --  Days since last insemination at the second pregnancy check, for cows confirmed pregnant at 1st pregnancy check"
                                    },
                                    "minimum": 0,
                                    "default": 60
                                },
                                "preg_loss_rate_2": {
                                    "title": "preg_loss_rate_2",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Pregnancy Loss Rate, Check 2 (percent) -- The percentage of cows that abort their pregnancy between the 1st and 2nd pregnancy checks"
                                    },
                                    "minimum": 0,
                                    "maximum": 0.1,
                                    "default": 0.096
                                },
                                "preg_check_day_3": {
                                    "title": "preg_check_day_3",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Pregnancy Check Day, Check 3 (days) -- Days since last insemination at the third pregnancy check, for cows confirmed pregnant at 2nd pregnancy check"
                                    },
                                    "minimum": 0,
                                    "default": 200
                                },
                                "preg_loss_rate_3": {
                                    "title": "preg_loss_rate_3",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Pregnancy Loss Rate, Check 3 (percent) -- The percentage of cows that abort their pregnancy between the 2nd and 3rd pregnancy checks"
                                    },
                                    "minimum": 0,
                                    "maximum": 0.1,
                                    "default": 0.017
                                },
                                "avg_estrus_cycle_return": {
                                    "title": "avg_estrus_cycle_return",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Average Estrous Cycle Return (days) -- Average days between calving and first estrous cycle after calving"
                                    },
                                    "minimum": 1,
                                    "default": 23
                                },
                                "std_estrus_cycle_return": {
                                    "title": "std_estrus_cycle_return",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Estrous Cycle Return Standard Deviation (days)"
                                    },
                                    "minimum": 1,
                                    "default": 6
                                },
                                "avg_estrus_cycle_heifer": {
                                    "title": "avg_estrus_cycle_heifer",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Heifer Estrous Cycle Length (days) -- Average length of estrous cycle for heifers"
                                    },
                                    "minimum": 1,
                                    "default": 21
                                },
                                "std_estrus_cycle_heifer": {
                                    "title": "std_estrus_cycle_heifer",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Heifer Estrous Cycle Length Standard Deviation (days)"
                                    },
                                    "minimum": 1,
                                    "default": 2.5
                                },
                                "avg_estrus_cycle_cow": {
                                    "title": "avg_estrus_cycle_cow",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Cow Estrous Cycle Length (days) -- Average length of estrous cycle for cows"
                                    },
                                    "minimum": 1,
                                    "default": 21
                                },
                                "std_estrus_cycle_cow": {
                                    "title": "std_estrus_cycle_cow",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Cow Estrous Cycle Length Standard Deviation (days)"
                                    },
                                    "minimum": 1,
                                    "default": 4
                                },
                                "avg_estrus_cycle_after_pgf": {
                                    "title": "avg_estrus_cycle_after_pgf",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Average Estrous Cycle days after PGF (days) -- Average days between the injection of PGF and the occurrence of estrus in the PGFatPD resynch protocol"
                                    },
                                    "minimum": 1,
                                    "default": 5
                                },
                                "std_estrus_cycle_after_pgf": {
                                    "title": "std_estrus_cycle_after_pgf",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Estrous Cycle days after PGF Standard Deviation (days) -- Standard deviation of days between the injection of PGF and the occurrence of estrus in the PGFatPD resynch protocol"
                                    },
                                    "minimum": 1,
                                    "default": 2
                                }
                            },
                            "options": {
                                "infoText": "Literature Repro Values"
                            }
                        },
                        "culling": {
                            "title": "culling",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "cull_day_count": {
                                    "title": "cull_day_count",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Culling day count"
                                    },
                                    "items": {
                                        "title": "cull_day_count_element",
                                        "type": "number",
                                        "options": {
                                            "grid_columns": 12,
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            }
                                        },
                                        "minimum": 0
                                    }
                                },
                                "feet_leg_cull": {
                                    "title": "feet_leg_cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "probability",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The probability of culling due to feet-and-leg-related health issues."
                                            },
                                            "minimum": 0,
                                            "maximum": 1
                                        },
                                        "cull_day_prob": {
                                            "title": "cull_day_prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for feet-and-leg-related health issues."
                                            },
                                            "items": {
                                                "title": "cull_day_prob_element",
                                                "type": "number",
                                                "options": {
                                                    "grid_columns": 12,
                                                    "inputAttributes": {
                                                        "class": "text-primary form-control"
                                                    }
                                                },
                                                "minimum": 0,
                                                "maximum": 1
                                            }
                                        }
                                    },
                                    "options": {
                                        "infoText": "Cull probabilities due to feet-and-leg-related health issues."
                                    }
                                },
                                "injury_cull": {
                                    "title": "injury_cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "probability",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The probability of culling due to injury-related health issues."
                                            },
                                            "minimum": 0,
                                            "maximum": 1
                                        },
                                        "cull_day_prob": {
                                            "title": "cull_day_prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for injury-related health issues."
                                            },
                                            "items": {
                                                "title": "cull_day_prob_element",
                                                "type": "number",
                                                "options": {
                                                    "grid_columns": 12,
                                                    "inputAttributes": {
                                                        "class": "text-primary form-control"
                                                    }
                                                },
                                                "minimum": 0,
                                                "maximum": 1
                                            }
                                        }
                                    },
                                    "options": {
                                        "infoText": "Cull probabilities due to injury-related health issues."
                                    }
                                },
                                "mastitis_cull": {
                                    "title": "mastitis_cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "probability",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The probability of culling due to mastitis-related health issues."
                                            },
                                            "minimum": 0,
                                            "maximum": 1
                                        },
                                        "cull_day_prob": {
                                            "title": "cull_day_prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for mastitis-related health issues."
                                            },
                                            "items": {
                                                "title": "cull_day_prob_element",
                                                "type": "number",
                                                "options": {
                                                    "grid_columns": 12,
                                                    "inputAttributes": {
                                                        "class": "text-primary form-control"
                                                    }
                                                },
                                                "minimum": 0,
                                                "maximum": 1
                                            }
                                        }
                                    },
                                    "options": {
                                        "infoText": "Cull probabilities due to mastitis-related health issues."
                                    }
                                },
                                "disease_cull": {
                                    "title": "disease_cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "probability",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The probability of culling due to disease-related health issues."
                                            },
                                            "minimum": 0,
                                            "maximum": 1
                                        },
                                        "cull_day_prob": {
                                            "title": "cull_day_prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for disease-related health issues."
                                            },
                                            "items": {
                                                "title": "cull_day_prob_element",
                                                "type": "number",
                                                "options": {
                                                    "grid_columns": 12,
                                                    "inputAttributes": {
                                                        "class": "text-primary form-control"
                                                    }
                                                },
                                                "minimum": 0,
                                                "maximum": 1
                                            }
                                        }
                                    },
                                    "options": {
                                        "infoText": "Cull probabilities due to disease-related health issues."
                                    }
                                },
                                "udder_cull": {
                                    "title": "udder_cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "probability",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The probability of culling due to udder-related health issues."
                                            },
                                            "minimum": 0,
                                            "maximum": 1
                                        },
                                        "cull_day_prob": {
                                            "title": "cull_day_prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for udder-related health issues."
                                            },
                                            "items": {
                                                "title": "cull_day_prob_element",
                                                "type": "number",
                                                "options": {
                                                    "grid_columns": 12,
                                                    "inputAttributes": {
                                                        "class": "text-primary form-control"
                                                    }
                                                },
                                                "minimum": 0,
                                                "maximum": 1
                                            }
                                        }
                                    },
                                    "options": {
                                        "infoText": "Cull probabilities due to udder-related health issues."
                                    }
                                },
                                "unknown_cull": {
                                    "title": "unknown_cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "probability",
                                            "type": "number",
                                            "options": {
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "The probability of culling due to other health issues."
                                            },
                                            "minimum": 0,
                                            "maximum": 1
                                        },
                                        "cull_day_prob": {
                                            "title": "cull_day_prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for unknown health issues."
                                            },
                                            "items": {
                                                "title": "cull_day_prob_element",
                                                "type": "number",
                                                "options": {
                                                    "grid_columns": 12,
                                                    "inputAttributes": {
                                                        "class": "text-primary form-control"
                                                    }
                                                },
                                                "minimum": 0,
                                                "maximum": 1
                                            }
                                        }
                                    },
                                    "options": {
                                        "infoText": "Cull probabilities due to other health issues."
                                    }
                                },
                                "parity_death_prob": {
                                    "title": "parity_death_prob",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Death Probability, by Parity"
                                    },
                                    "items": {
                                        "title": "parity_death_prob_element",
                                        "type": "number",
                                        "options": {
                                            "grid_columns": 12,
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            },
                                            "infoText": "Death Probability, by Parity Group -- The probability of death for cows of a single parity group (first lactation, second lactation, etc.); a separate entry should be included for 1st, 2nd, 3rd, and 4th+ parities (4 entries total)"
                                        },
                                        "minimum": 0,
                                        "maximum": 1
                                    }
                                },
                                "parity_cull_prob": {
                                    "title": "parity_cull_prob",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Cull Probability, by Parity"
                                    },
                                    "items": {
                                        "title": "parity_cull_prob_element",
                                        "type": "number",
                                        "options": {
                                            "grid_columns": 12,
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            },
                                            "infoText": "Cull Probability, by Parity -- The probability of culling for cows of a single parity (first lactation, second lactation, etc.); a separate entry should be included for 1st, 2nd, 3rd, and 4th+ parities (4 entries total)"
                                        },
                                        "minimum": 0,
                                        "maximum": 1
                                    }
                                },
                                "death_day_prob": {
                                    "title": "death_day_prob",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Culling probability for death"
                                    },
                                    "items": {
                                        "title": "death_day_prob_element",
                                        "type": "number",
                                        "options": {
                                            "grid_columns": 12,
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            }
                                        },
                                        "minimum": 0,
                                        "maximum": 1
                                    }
                                }
                            },
                            "options": {
                                "infoText": "Probabilities for removal from the herd for specific reason"
                            }
                        },
                        "life_cycle": {
                            "title": "life_cycle",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "still_birth_rate": {
                                    "title": "still_birth_rate",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Rate of stillbirths (percent)"
                                    },
                                    "minimum": 0,
                                    "maximum": 1,
                                    "default": 0.065
                                }
                            },
                            "options": {
                                "infoText": ""
                            }
                        }
                    },
                    "options": {
                        "infoText": "From Literature"
                    }
                }
            },
            "options": {
                "infoText": "Animal Configuration"
            }
        },
        "methane_mitigation": {
            "title": "methane_mitigation",
            "type": "object",
            "format": "grid",
            "properties": {
                "methane_mitigation_method": {
                    "title": "methane_mitigation_method",
                    "type": "string",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Methane Mitigation Method (select one) -- The type of enteric methane mitigation supplement that is fed to the lactating cows. Note that default values given are not implemented unless the specific supplement is selected here"
                    },
                    "default": "None",
                    "enum": [
                        "None",
                        "3-NOP",
                        "Monensin",
                        "Essential Oils",
                        "Seaweed"
                    ],
                    "format": "select2"
                },
                "methane_mitigation_additive_amount": {
                    "title": "methane_mitigation_additive_amount",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        }
                    },
                    "default": 0
                },
                "3-NOP_additive_amount": {
                    "title": "3-NOP_additive_amount",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "3-NOP Additive Amount (mg/kg DMI) -- The dosage of the 3-NOP mitigation additive"
                    },
                    "minimum": 40,
                    "maximum": 100,
                    "default": 70
                },
                "monensin_additive_amount": {
                    "title": "monensin_additive_amount",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Monensin Additive Amount (mg/kg DMI) -- The dosage of the monensin mitigation additive"
                    },
                    "minimum": 20,
                    "maximum": 36,
                    "default": 24
                },
                "essential_oils_additive_amount": {
                    "title": "essential_oils_additive_amount",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Essential Oils Additive Amount (mg/kg DMI) -- The dosage of the essential oils mitigation additive"
                    },
                    "minimum": 0,
                    "maximum": 100,
                    "default": 0
                },
                "seaweed_additive_amount": {
                    "title": "seaweed_additive_amount",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Seaweed Additive Amount (mg/kg DMI) -- The dosage of seaweed mitigation additive"
                    },
                    "minimum": 0,
                    "maximum": 100,
                    "default": 0
                }
            },
            "options": {
                "infoText": "Methane Mitigation"
            }
        },
        "housing": {
            "title": "housing",
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Housing Type (select one) -- The type of housing management for the herd"
            },
            "default": "barn",
            "enum": [
                "barn",
                "pasture",
                "drylot"
            ],
            "format": "select2"
        },
        "pasture_concentrate": {
            "title": "pasture_concentrate",
            "type": "number",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Pasture Concentrate Fed (kg/head/day) -- Amount of concentrate provided to lactating cows each day if animals are housed on pasture"
            },
            "minimum": 0,
            "default": 0
        },
        "methane_model": {
            "title": "methane_model",
            "type": "string",
            "options": {
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Methane Model (select one) -- The method used to estimate enteric methane emissions for lactating cows"
            },
            "default": "IPCC",
            "enum": [
                "Mills",
                "Mutian",
                "IPCC"
            ],
            "format": "select2"
        },
        "ration": {
            "title": "ration",
            "type": "object",
            "format": "grid",
            "properties": {
                "user_input": {
                    "title": "user_input",
                    "type": "boolean",
                    "format": "checkbox",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "User Input -- A bool value indicating if the user will provide the ration or diet formulation they would like to feed to the cattle (true) or not (false)."
                    },
                    "default": false
                },
                "formulation_interval": {
                    "title": "formulation_interval",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Formulation Interval (days) -- The length of time in days between when the diets are reformulated"
                    },
                    "minimum": 1,
                    "default": 30
                },
                "phosphorus_requirement_buffer": {
                    "title": "phosphorus_requirement_buffer",
                    "type": "number",
                    "options": {
                        "grid_columns": 12,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        },
                        "infoText": "Percentage increase in phosphorus nutrient requirement in calculation of animal requirements. The default value is highly recommended as the starting value (e.g. some testing may be required to find a reasonable buffer value). For example, if you wanted to supply 150% of the calculated requirement, you would use a value of 50."
                    },
                    "minimum": 0,
                    "default": 75
                }
            },
            "options": {
                "infoText": "Ration"
            }
        },
        "pen_information": {
            "title": "pen_information",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Pen Information"
            },
            "items": {
                "title": "pen_information_element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "id": {
                        "title": "id",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Pen ID -- The index of the pen"
                        }
                    },
                    "pen_name": {
                        "title": "pen_name",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Pen Name -- The name or identifier of a given pen"
                        }
                    },
                    "animal_combination": {
                        "title": "animal_combination",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Animal Combination (select one) -- The valid combinations of animal types that can be in a pen. CALF = Calves; GROWING = HeiferI's and HeiferII's; CLOSE_UP = HeiferIII's and Dry Cows; LAC_COWS = Lactating Cows"
                        },
                        "enum": [
                            "CALF",
                            "GROWING",
                            "CLOSE_UP",
                            "LAC_COW"
                        ],
                        "format": "select2"
                    },
                    "vertical_dist_to_milking_parlor": {
                        "title": "vertical_dist_to_milking_parlor",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Vertical Distance to Milking Parlor (m) -- The elevation gain (in meters) between the pen and the milking parlor"
                        },
                        "minimum": 0,
                        "default": 0.1
                    },
                    "horizontal_dist_to_milking_parlor": {
                        "title": "horizontal_dist_to_milking_parlor",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Horizontal Distance to Milking Parlor (m) -- The distance (in meters) between the pen and the milking parlor"
                        },
                        "minimum": 0,
                        "default": 10
                    },
                    "number_of_stalls": {
                        "title": "number_of_stalls",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Number of Stalls -- The number of stalls in the pen"
                        },
                        "minimum": 0,
                        "default": 1000
                    },
                    "housing_type": {
                        "title": "housing_type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Housing Type (select one) -- The type of barn the pen is in"
                        },
                        "default": "open air barn",
                        "enum": [
                            "open air barn"
                        ],
                        "format": "select2"
                    },
                    "pen_type": {
                        "title": "pen_type",
                        "type": "string",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Pen Type -- The type of pen (freestall, tiestall, open lot, compost bedded pack barn)"
                        },
                        "default": "freestall",
                        "enum": [
                            "freestall",
                            "tiestall",
                            "open lot",
                            "compost bedded pack barn"
                        ],
                        "format": "select2"
                    },
                    "max_stocking_density": {
                        "title": "max_stocking_density",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Maximum Stocking Density -- The maximum ratio of the number of animals in the pen to the number of stalls in the pen"
                        },
                        "minimum": 0.5,
                        "maximum": 5,
                        "default": 1.2
                    },
                    "manure_management_scenario_id": {
                        "title": "manure_management_scenario_id",
                        "type": "number",
                        "options": {
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            },
                            "infoText": "Manure Management Scenario ID (number) -- The ID number of the manure management practices that are used for this pen (scenarios are defined in manure management schema)"
                        },
                        "minimum": 0,
                        "default": 0
                    }
                }
            }
        }
    }
}