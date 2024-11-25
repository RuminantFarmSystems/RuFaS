animal_schema = {
    "title": "Animal Properties",
    "type": "object",
    "format": "grid",
    "properties": {
        "herd_information": {
            "title": "Herd Information",
            "type": "object",
            "format": "grid",
            "properties": {
                "calf_num": {
                    "title": "Calf Num",
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
                    "title": "Heiferi Num",
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
                    "title": "Heiferii Num",
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
                    "title": "Heiferiii Num Springers",
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
                    "title": "Cow Num",
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
                    "title": "Replace Num",
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
                    "title": "Herd Num",
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
                    "title": "Breed",
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
                    "title": "Parity Fractions",
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
                    "title": "Annual Milk Yield",
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
            "title": "Herd Initialization",
            "type": "object",
            "format": "grid",
            "properties": {
                "initial_animal_num": {
                    "title": "Initial Animal Num",
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
                    "title": "Simulation Days",
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
            "title": "Animal Config",
            "type": "object",
            "format": "grid",
            "properties": {
                "management_decisions": {
                    "title": "Management Decisions",
                    "type": "object",
                    "format": "grid",
                    "properties": {
                        "breeding_start_day_h": {
                            "title": "Breeding Start Day H",
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
                            "title": "Heifer Repro Method",
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
                            "title": "Cow Repro Method",
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
                            "title": "Semen Type",
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
                            "title": "Days In Preg When Dry",
                            "type": "number",
                            "options": {
                                "grid_columns": 12,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                },
                                "infoText": "Days In Pregnancy When Dry (days) -- The average days in pregnancy of cows at dry-off"
                            },
                            "minimum": 1,
                            "default": 218
                        },
                        "heifer_repro_cull_time": {
                            "title": "Heifer Repro Cull Time",
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
                            "title": "Do Not Breed Time",
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
                            "title": "Cull Milk Production",
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
                            "title": "Cow Times Milked Per Day",
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
                            "title": "Milk Fat Percent",
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
                            "title": "Milk Protein Percent",
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
                    "title": "Farm Level",
                    "type": "object",
                    "format": "grid",
                    "properties": {
                        "calf": {
                            "title": "Calf",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "male_calf_rate_sexed_semen": {
                                    "title": "Male Calf Rate Sexed Semen",
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
                                    "title": "Male Calf Rate Conventional Semen",
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
                                    "title": "Keep Female Calf Rate",
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
                                    "title": "Wean Day",
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
                                    "title": "Wean Length",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Wean Length (days) -- Length of the weaning process"
                                    },
                                    "minimum": 1,
                                    "default": 7
                                },
                                "milk_type": {
                                    "title": "Milk Type",
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
                            "title": "Repro",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "voluntary_waiting_period": {
                                    "title": "Voluntary Waiting Period",
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
                                    "title": "Conception Rate Decrease",
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
                                    "title": "Decrease Conception Rate In Rebreeding",
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
                                    "title": "Decrease Conception Rate By Parity",
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
                                    "title": "Avg Gestation Len",
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
                                    "title": "Std Gestation Len",
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
                                    "title": "Prefresh Day",
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
                                    "title": "Calving Interval",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Calving Interval (days) -- Current average calving interval, used for initial bodyweight adjustment and other calculations"
                                    },
                                    "minimum": 1,
                                    "default": 400
                                },
                                "heifers": {
                                    "title": "Heifers",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "estrus_detection_rate": {
                                            "title": "Estrus Detection Rate",
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
                                            "title": "Estrus Conception Rate",
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
                                            "title": "Repro Sub Protocol",
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
                                            "title": "Repro Sub Properties",
                                            "type": "object",
                                            "format": "grid",
                                            "properties": {
                                                "conception_rate": {
                                                    "title": "Conception Rate",
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
                                                    "title": "Estrus Detection Rate",
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
                                    "title": "Cows",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "estrus_detection_rate": {
                                            "title": "Estrus Detection Rate",
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
                                            "title": "Ed Conception Rate",
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
                                            "title": "Presynch Program",
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
                                            "title": "Presynch Program Start Day",
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
                                            "title": "Ovsynch Program",
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
                                            "title": "Ovsynch Program Start Day",
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
                                            "title": "Ovsynch Program Conception Rate",
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
                                            "title": "Resynch Program",
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
                            "title": "Bodyweight",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "birth_weight_avg_ho": {
                                    "title": "Birth Weight Avg Ho",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Average Holstein Birth Weight (kg/head)"
                                    },
                                    "minimum": 1,
                                    "default": 42.9
                                },
                                "birth_weight_std_ho": {
                                    "title": "Birth Weight Std Ho",
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
                                    "title": "Birth Weight Avg Je",
                                    "type": "number",
                                    "options": {
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Average Jersey Birth Weight (kg/head)"
                                    },
                                    "minimum": 1,
                                    "default": 25.2
                                },
                                "birth_weight_std_je": {
                                    "title": "Birth Weight Std Je",
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
                                    "title": "Target Heifer Preg Day",
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
                                    "title": "Mature Body Weight Avg",
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
                                    "title": "Mature Body Weight Std",
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
                    "title": "From Literature",
                    "type": "object",
                    "format": "grid",
                    "properties": {
                        "repro": {
                            "title": "Repro",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "preg_check_day_1": {
                                    "title": "Preg Check Day 1",
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
                                    "title": "Preg Loss Rate 1",
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
                                    "title": "Preg Check Day 2",
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
                                    "title": "Preg Loss Rate 2",
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
                                    "title": "Preg Check Day 3",
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
                                    "title": "Preg Loss Rate 3",
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
                                    "title": "Avg Estrus Cycle Return",
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
                                    "title": "Std Estrus Cycle Return",
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
                                    "title": "Avg Estrus Cycle Heifer",
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
                                    "title": "Std Estrus Cycle Heifer",
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
                                    "title": "Avg Estrus Cycle Cow",
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
                                    "title": "Std Estrus Cycle Cow",
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
                                    "title": "Avg Estrus Cycle After Pgf",
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
                                    "title": "Std Estrus Cycle After Pgf",
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
                            "title": "Culling",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "cull_day_count": {
                                    "title": "Cull Day Count",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Culling day count"
                                    },
                                    "items": {
                                        "title": "Cull Day Count Element",
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
                                    "title": "Feet Leg Cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "Probability",
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
                                            "title": "Cull Day Prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for feet-and-leg-related health issues."
                                            },
                                            "items": {
                                                "title": "Cull Day Prob Element",
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
                                    "title": "Injury Cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "Probability",
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
                                            "title": "Cull Day Prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for injury-related health issues."
                                            },
                                            "items": {
                                                "title": "Cull Day Prob Element",
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
                                    "title": "Mastitis Cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "Probability",
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
                                            "title": "Cull Day Prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for mastitis-related health issues."
                                            },
                                            "items": {
                                                "title": "Cull Day Prob Element",
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
                                    "title": "Disease Cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "Probability",
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
                                            "title": "Cull Day Prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for disease-related health issues."
                                            },
                                            "items": {
                                                "title": "Cull Day Prob Element",
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
                                    "title": "Udder Cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "Probability",
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
                                            "title": "Cull Day Prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for udder-related health issues."
                                            },
                                            "items": {
                                                "title": "Cull Day Prob Element",
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
                                    "title": "Unknown Cull",
                                    "type": "object",
                                    "format": "grid",
                                    "properties": {
                                        "probability": {
                                            "title": "Probability",
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
                                            "title": "Cull Day Prob",
                                            "type": "array",
                                            "format": "grid",
                                            "options": {
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                },
                                                "infoText": "Culling probability on the cull day for unknown health issues."
                                            },
                                            "items": {
                                                "title": "Cull Day Prob Element",
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
                                    "title": "Parity Death Prob",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Death Probability, by Parity"
                                    },
                                    "items": {
                                        "title": "Parity Death Prob Element",
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
                                    "title": "Parity Cull Prob",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Cull Probability, by Parity"
                                    },
                                    "items": {
                                        "title": "Parity Cull Prob Element",
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
                                    "title": "Death Day Prob",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        },
                                        "infoText": "Culling probability for death"
                                    },
                                    "items": {
                                        "title": "Death Day Prob Element",
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
                            "title": "Life Cycle",
                            "type": "object",
                            "format": "grid",
                            "properties": {
                                "still_birth_rate": {
                                    "title": "Still Birth Rate",
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
            "title": "Methane Mitigation",
            "type": "object",
            "format": "grid",
            "properties": {
                "methane_mitigation_method": {
                    "title": "Methane Mitigation Method",
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
                    "title": "Methane Mitigation Additive Amount",
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
                    "title": "3-nop Additive Amount",
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
                    "title": "Monensin Additive Amount",
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
                    "title": "Essential Oils Additive Amount",
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
                    "title": "Seaweed Additive Amount",
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
            "title": "Housing",
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
            "title": "Pasture Concentrate",
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
            "title": "Methane Model",
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
            "title": "Ration",
            "type": "object",
            "format": "grid",
            "properties": {
                "user_input": {
                    "title": "User Input",
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
                    "title": "Formulation Interval",
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
                    "title": "Phosphorus Requirement Buffer",
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
            "title": "Pen Information",
            "type": "array",
            "format": "grid",
            "options": {
                "inputAttributes": {
                    "class": "text-primary form-control"
                },
                "infoText": "Pen Information"
            },
            "items": {
                "title": "Pen Information Element",
                "type": "object",
                "format": "grid",
                "properties": {
                    "id": {
                        "title": "Id",
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
                        "title": "Pen Name",
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
                        "title": "Animal Combination",
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
                        "title": "Vertical Dist To Milking Parlor",
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
                        "title": "Horizontal Dist To Milking Parlor",
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
                        "title": "Number Of Stalls",
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
                        "title": "Housing Type",
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
                        "title": "Pen Type",
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
                        "title": "Max Stocking Density",
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
                        "title": "Manure Management Scenario Id",
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