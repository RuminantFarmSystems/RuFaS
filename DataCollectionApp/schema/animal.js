animal_schema = {
    "title": "Animal Data",
    "type": "object",
    "format": "grid",
    "properties": {
        "herd_information": {
            "title": "Herd Demographics",
            "type": "object",
            "description": "An overview of the counts of different animal groups on the farm",
            "format": "grid",
            "properties": {
                "calf_num": {
                    "title": "Number of Calves (head)",
                    "type": "number",
                    "default": 8,
                    "minimum": 0,
                    "options": {
                        "infoText": "The average number of pre-weaned calves (default is ~4% of herd number)",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "placeholder": 8,
                            "class": "text-primary form-control"
                        }
                    },
                },
                "heiferI_num": {
                    "title": "Number of HeiferIs (head)",
                    "type": "number",
                    "default": 44,
                    "minimum": 0,
                    "options": {
                        "infoText": "HeiferI is the number of youngstock post-weaning and before breeding (default is ~23% of herd number)",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "placeholder": 44,
                            "class": "text-primary form-control"
                        }
                    }
                },
                "heiferII_num": {
                    "title": "Number of HeiferIIs (head)",
                    "type": "number",
                    "default": 38,
                    "minimum": 0,
                    "options": {
                        "infoText": "HeiferII is the number of heifers eligible for breeding and in early pregnancy (default is ~20% of herd number)",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "placeholder": 38,
                            "class": "text-primary form-control"
                        }
                    }
                },
                "heiferIII_num_springers": {
                    "title": "Number of HeiferIIIs (head)",
                    "type": "number",
                    "default": 5,
                    "minimum": 0,
                    "options": {
                        "infoText": "HeiferIII is the number of close-up heifers (default is ~3% of herd number)",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "placeholder": 5,
                            "class": "text-primary form-control"
                        }
                    }
                },
                "cow_num": {
                    "title": "Number of Cows (head)",
                    "type": "number",
                    "default": 100,
                    "minimum": 0,
                    "options": {
                        "infoText": "The initial number of dry and lactating cows (all parities, default is ~51% of herd number).",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "placeholder": 100,
                            "class": "text-primary form-control"
                        }
                    }
                },
                "herd_num": {
                    "title": "Herd Number (head)",
                    "type": "number",
                    "default": 100,
                    "minimum": 0,
                    "options": {
                        "infoText": "The target number of dry and lactating cows on farm.",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "placeholder": 100,
                            "class": "text-primary form-control"
                        }
                    }
                },
                "herd_init": {
                    "title": "Initialize Herd?",
                    "type": "boolean",
                    "format": "checkbox",
                    "options": {
                        "infoText": "Only check box if cow body weight and milk production exceedingly abnormal",
                        "grid_columns": 6,
                    }
                },
                "breed": {
                    "title": "Breed (select one Holstein/Jersey)",
                    "type": "radio",
                    "default": "HO",
                    "enum": [
                        "HO",
                        "JE"
                    ],
                    "options": {
                        "infoText": "The predominant breed of the herd (Holstein or Jersey)",
                        "grid_columns": 6,
                    }
                }
            }
        },
        "animal_config": {
            "type": "object",
            "title": "Animal Configuration",
            "format": "grid",
            "properties": {
                "management_decisions": {
                    "type": "object",
                    "format": "grid",
                    "title": "General Management",
                    "properties": {
                        "breeding_start_day_h": {
                            "title": "Breeding Start Day - Heifers (days)",
                            "type": "number",
                            "default": 380,
                            "minimum": 0,
                            "options": {
                                "infoText": "Days old when a heifer would be eligible for breeding (days)",
                                "grid_columns": 6,
                                "inputAttributes": {
                                    "placeholder": 380,
                                    "class": "text-primary form-control"
                                }
                            }
                        },
                        "heifer_repro_method": {
                            "title": "Heifer Reproductive Program (select one)",
                            "type": "string",
                            "default": "TAI",
                            "format": "select2",
                            "required": true,
                            "enum": [
                                "TAI",
                                "ED",
                                "Synch-ED"
                            ],
                            "options": {
                                "infoText": "TAI - Timed Artificial Insemination; ED - Estrus Detection; Synch-ED - Combination of ED and TAI",
                                "grid_columns": 6,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                }
                            }
                        },
                        "cow_repro_method": {
                            "title": "Cow Reproductive Program (select one)",
                            "type": "string",
                            "default": "TAI",
                            "format": "select2",
                            "required": true,
                            "enum": [
                                "TAI",
                                "ED",
                                "ED-TAI"
                            ],
                            "options": {
                                "infoText": "TAI - Timed Artificial Insemination; ED - Estrus Detection; ED-TAI -Combination of ED and TAI",
                                "grid_columns": 6,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                }
                            }
                        },
                        "semen_type": {
                            "title": "Semen Type (select one)",
                            "type": "radio",
                            "default": "conventional",
                            "enum": [
                                "sexed",
                                "conventional"
                            ],
                            "options": {
                                "infoText": "Please choose whichever semen selection type makes up a majority of your breedings",
                                "grid_columns": 6,
                            }
                        },
                        "days_in_preg_when_dry": {
                            "title": "Days In Pregnancy When Dry (days)",
                            "type": "number",
                            "default": 218,
                            "minimum": 0,
                            "options": {
                                "infoText": "The average day in pregnancy when a cow is dried off (default is 218)",
                                "grid_columns": 6,
                                "inputAttributes": {
                                    "placeholder": 218,
                                    "class": "text-primary form-control"
                                }
                            }
                        },
                        "heifer_repro_cull_time": {
                            "title": "Heifer Reproductive Cull Time (days)",
                            "type": "number",
                            "default": 500,
                            "minimum": 0,
                            "options": {
                                "infoText": "Days old when a heifer would be culled for unsuccessful in breeding (default is 500)",
                                "grid_columns": 6,
                                "inputAttributes": {
                                    "placeholder": 500,
                                    "class": "text-primary form-control"
                                }

                            }
                        },
                        "do_not_breed_time": {
                            "title": "Do Not Breed Time (days)",
                            "type": "number",
                            "default": 185,
                            "minimum": 0,
                            "options": {
                                "infoText": "The breeding period (days) for cows before reproductive programs stop if they fail to get pregnant (days)",
                                "grid_columns": 6,
                                "inputAttributes": {
                                    "placeholder": 185,
                                    "class": "text-primary form-control"
                                }

                            }
                        },
                        "cull_milk_production": {
                            "title": "Cull Milk Production (kg/d)",
                            "type": "number",
                            "default": 30,
                            "minimum": 0,
                            "options": {
                                "infoText": "Minimum daily milk production for do-not breed cow to be culled (default is 30 kg/d)",
                                "grid_columns": 6,
                                "inputAttributes": {
                                    "placeholder": 30,
                                    "class": "text-primary form-control"
                                }

                            }
                        },
                        "cow_times_milked_per_day": {
                            "title": "Number of Times Cows Milked (per day)",
                            "type": "number",
                            "default": 3,
                            "minimum": 0,
                            "options": {
                                "infoText": "The average or most common number of times the cows are milked, whole numbers 1-3",
                                "grid_columns": 6,
                                "inputAttributes": {
                                    "placeholder": 3,
                                    "class": "text-primary form-control"
                                }
                            }
                        },
                        "energy_and_nutrient_calculation_method": {
                            "title": "Energy and Nutrient Calculation Method",
                            "type": "string",
                            "default": "NASEM",
                            "enum": [
                                "NASEM",
                                "NRC",
                            ],
                            "options": {
                                "infoText": "The method used to calculate the animal nutrient requirements.",
                                "grid_columns": 6,
                                "inputAttributes": {
                                    "class": "text-primary form-control"
                                }
                            }
                        },
                    },
                },
                "farm_level": {
                    "type": "object",
                    "title": "Farm Level Management",
                    "properties": {
                        "calf": {
                            "type": "object",
                            "format": "grid",
                            "title": "Calf Management",
                            "properties": {
                                "male_calf_rate_sexed_semen": {
                                    "title": "Male Calf Rate - Sexed Semen",
                                    "type": "number",
                                    "default": 0.1,
                                    "minimum": 0,
                                    "maximum": 1,
                                    "options": {
                                        "infoText": "The rate of male calves when using sexed semen (default is 0.1)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 0.1,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "male_calf_rate_conventional_semen": {
                                    "title": "Male Calf Rate - Conventional Semen",
                                    "type": "number",
                                    "default": 0.53,
                                    "minimum": 0,
                                    "maximum": 1,
                                    "options": {
                                        "infoText": "The rate of male calves when using conventional semen (default is 0.53)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 0.53,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "keep_female_calf_rate": {
                                    "title": "Female Calf Rate",
                                    "type": "number",
                                    "default": 1,
                                    "minimum": 0,
                                    "maximum": 1,
                                    "options": {
                                        "infoText": "The rate female calves are kept and raised on-farm (default is 1)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 1,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "wean_day": {
                                    "title": "Wean Day (days)",
                                    "type": "number",
                                    "default": 60,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "Days the calf is fully weaned from milk or milk replace (default is 60)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 60,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "wean_length": {
                                    "title": "Wean Length (days)",
                                    "type": "number",
                                    "default": 7,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "Days weaning (default is 7)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 7,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "milk_type": {
                                    "title": "Milk Type (select one)",
                                    "type": "radio",
                                    "default": "whole",
                                    "enum": [
                                        "whole",
                                        "replacement"
                                    ],
                                    "options": {
                                        "infoText": "The type of milk that is used to feed calves (Whole or Replacer)",
                                        "grid_columns": 6,
                                    }
                                },
                            },
                        },
                        "repro": {
                            "type": "object",
                            "format": "grid",
                            "title": "Repro Management",
                            "properties": {
                                "voluntary_waiting_period": {
                                    "title": "Voluntary Waiting Period (days)",
                                    "type": "number",
                                    "default": 50,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "If 'TAI' (Timed Artificial Insemination) is chosen for cow, it is days after parturition when the 1st hormonal injection is made in TAI programs. If 'ED-TAI' is chosen for cow, it is days after parturition when estrus detection followed by AI in ED-TAI programs",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 50,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "conception_rate_decrease": {
                                    "title": "Conception Rate Decrease",
                                    "type": "number",
                                    "default": 0.026,
                                    "minimum": 0,
                                    "maximum": 0.1,
                                    "options": {
                                        "infoText": "the decrease of the conception rate for later breeding (default is 0.026)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 0.026,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "avg_gestation_len": {
                                    "title": "Average Gestation Length (days)",
                                    "type": "number",
                                    "default": 278,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "average length of gestations (default is 278)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 278,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "std_gestation_len": {
                                    "title": "Gestation Length Standard Deviation (days)",
                                    "type": "number",
                                    "default": 6,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "standard deviation of gestation length (default is 6)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 6,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "prefresh_day": {
                                    "title": "Prefresh Day (days)",
                                    "type": "number",
                                    "default": 30,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "length of period of the transition before calving (default is 30)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 21,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "calving_interval": {
                                    "title": "Calving Interval (days)",
                                    "type": "number",
                                    "default": 400,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "current average calving interval (days), used for initial bodyweight adjustment and other calculations",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 400,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "heifer_repro_programs": {
                                    "type": "object",
                                    "format": "grid",
                                    "title": "Heifer Reproductive programs",
                                    "minProperties": 6,
                                    "maxProperties": 6,
                                    "properties": {
                                        "estrus_detection_rate": {
                                            "title": "Estrus Detection Rate",
                                            "type": "number",
                                            "default": 0.6,
                                            "minimum": 0,
                                            "maximum": 1,
                                            "options": {
                                                "infoText": "The % of in-heat animalss that would be detected in the ED (Estrus Detection) programs (default is 0.6)",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "placeholder": 0.6,
                                                    "class": "text-primary  form-control"
                                                }
                                            }
                                        },
                                        "estrus_service_rate": {
                                            "title": "Estrus Service Rate",
                                            "type": "number",
                                            "default": 1,
                                            "minimum": 0,
                                            "maximum": 1,
                                            "options": {
                                                "infoText": "The % of detected in heat animals that would be serviced in the ED (Estrus Detection) programs (default is 1)",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "placeholder": 1,
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                        "ed_conception_rate": {
                                            "title": "ED Conception Rate",
                                            "type": "number",
                                            "default": 0.6,
                                            "minimum": 0,
                                            "maximum": 1,
                                            "options": {
                                                "infoText": "The % of serviced animals that would be concepted in the ED (Estrus Detection) programs (default is 0.6)",
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "placeholder": 0.6,
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                        "heifer_TAI_protocol": {
                                            "title": "Heifer TAI (Timed Artificial Insemination) Protocol (select one)",
                                            "links": [{
                                                "rel": "Source: DCRC",
                                                "href": "documents/Reproductive_Management_Strategies_Heifers.pdf",
                                                "class": "d-block"
                                            }],
                                            "type": "radio",
                                            "default": "md5CG2P",
                                            "enum": [
                                                "md5CG2P",
                                                "md5CGP"
                                            ],
                                            "options": {
                                                "infoText": "The breeding protocol for heifers (md5CG2P or md5CGP)",
                                                "grid_columns": 12,
                                            },
                                        },
                                        "md5CG2P_conception_rate": {
                                            "title": "Heifer Conception Rate for md5CG2P Protocol",
                                            "type": "number",
                                            "default": 0.6,
                                            "minimum": 0,
                                            "maximum": 1,
                                            "required": false,
                                            "options": {
                                                "infoText": "The conception rate for md5CG2P protocol in heifer TAI (Timed Artificial Insemination) program (default is 0.6)",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "placeholder": 0.6,
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                        "md5CGP_conception_rate": {
                                            "title": "Heifer Conception Rate for md5CGP Protocol",
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                            "default": 0.48,
                                            "required": false,
                                            "options": {
                                                "infoText": "The conception rate for md5CGP protocol in heifer TAI (Timed Artificial Insemination) program",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "placeholder": 0.48,
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                        "heifer_synchED_protocol": {
                                            "title": "Heifer SynchED Protocol (select one)",
                                            "type": "radio",
                                            "default": "2P",
                                            "enum": [
                                                "2P",
                                                "CP"
                                            ],
                                            "options": {
                                                "infoText": "2P: two injections of PGF (prostaglandin), watch for estrus after each injection with insemination upon heat detection; CP: 7 days CIDR implements, inject PGF upon removal, insemination upon heat detection",
                                                "grid_columns": 6,
                                            }
                                        },
                                        "estrus_detection_rate_h_synch": {
                                            "title": "ED Rate for SynchED Protocol",
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                            "default": 0.7,
                                            "options": {
                                                "infoText": "The estrus detection rate of the SynchED protocol.",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                    }
                                },
                                "cow_repro_programs": {
                                    "type": "object",
                                    "format": "grid",
                                    "title": "Cow Reproductive programs",
                                    "minProperties": 6,
                                    "maxProperties": 6,
                                    "properties": {
                                        "estrus_detection_rate": {
                                            "title": "Estrus Detection Rate",
                                            "type": "number",
                                            "default": 0.6,
                                            "minimum": 0,
                                            "maximum": 1,
                                            "options": {
                                                "infoText": "The % of in-heat animalss that would be detected in the ED (Estrus Detection) programs (default is 0.6)",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "placeholder": 0.6,
                                                    "class": "text-primary  form-control"
                                                }
                                            }
                                        },
                                        "estrus_service_rate": {
                                            "title": "Estrus Service Rate",
                                            "type": "number",
                                            "default": 1,
                                            "minimum": 0,
                                            "maximum": 1,
                                            "options": {
                                                "infoText": "The % of detected in heat animals that would be serviced in the ED (Estrus Detection) programs (default is 1)",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "placeholder": 1,
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                        "ed_conception_rate": {
                                            "title": "ED Conception Rate",
                                            "type": "number",
                                            "default": 0.6,
                                            "minimum": 0,
                                            "maximum": 1,
                                            "options": {
                                                "infoText": "The % of serviced animals that would be concepted in the ED (Estrus Detection) programs (default is 0.6)",
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "placeholder": 0.6,
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                        "cow_presynch_protocol": {
                                            "title": "Cow Presynch Protocol",
                                            "type": "string",
                                            "default": "Double OvSynch",
                                            "format": "select2",
                                            "required": true,
                                            "enum": [
                                                "Double OvSynch",
                                                "Presynch",
                                                "G6G"
                                            ],
                                            "options": {
                                                "infoText": "The preSynch protocol (1st breeding) for cow in TAI (Timed Artificial Insemination) program",
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                }
                                            },
                                            "links": [{
                                                "rel": "Source: DCRC",
                                                "href": "documents/Dairy_Cow_Protocol_Sheet_2018.pdf",
                                                "class": "d-block"
                                            }],
                                        },
                                        "cow_TAI_protocol": {
                                            "title": "Cow TAI (Timed Artificial Insemination) Protocol",
                                            "type": "string",
                                            "default": "OvSynch 56",
                                            "format": "select2",
                                            "required": true,
                                            "enum": [
                                                "OvSynch 56",
                                                "OvSynch 48",
                                                "CoSynch 72",
                                                "5d CoSynch"
                                            ],
                                            "options": {
                                                "infoText": "The timed AI protocol for cows in the TAI (Timed Artificial Insemination) program",
                                                "grid_columns": 12,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control",
                                                }
                                            }
                                        },
                                        "ovsynch56_conception_rate": {
                                            "title": "OvSynch56 Conception Rate",
                                            "type": "number",
                                            "default": 0.6,
                                            "minimum": 0,
                                            "maximum": 1,
                                            "required": false,
                                            "options": {
                                                "infoText": "The conception rate for OvSynch56 protocol (pre-breeding GnRH shot given 56hrs post prostaglandin) in cow TAI (Timed Artificial Insemination) program (default is 0.6)",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "placeholder": 0.6,
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                        "ovsynch48_conception_rate": {
                                            "title": "OvSynch48 Conception Rate",
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                            "default": 0.6,
                                            "required": false,
                                            "options": {
                                                "infoText": "The conception rate for OvSynch 48 protocol (pre-breeding GnRH shot given 48hrs post prostaglandin) in cow TAI (Timed Artificial Insemination) program",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "placeholder": 0.6,
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                        "cosynch72_conception_rate": {
                                            "title": "CoSynch72 Conception Rate",
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                            "default": 0.6,
                                            "required": false,
                                            "options": {
                                                "infoText": "The conception rate for CoSynch 72 protocol in cow TAI (Timed Artificial Insemination) program",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "placeholder": 0.6,
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                        "cosynch5d_conception_rate": {
                                            "title": "5d CoSynch Conception Rate",
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                            "default": 0.6,
                                            "required": false,
                                            "options": {
                                                "infoText": "The conception rate for 5d CoSynch protocol in cow TAI (Timed Artificial Insemination) program",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "placeholder": 0.6,
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                        "cow_resynch_protocol": {
                                            "title": "Cow Resynch Protocol",
                                            "type": "string",
                                            "default": "TAIafterPD",
                                            "format": "select2",
                                            "required": true,
                                            "enum": [
                                                "TAIafterPD",
                                                "TAIbeforePD",
                                                "PGFatPD"
                                            ],
                                            "options": {
                                                "infoText": "Resynch protocol for cow before/at/after pregnancy check day in the TAI (Timed Artificial Insemination) program",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control col-md-6"
                                                }
                                            }
                                        },
                                        "tai_program_start_day": {
                                            "title": "TAI program start day for ED-TAI protocol",
                                            "type": "number",
                                            "minimum": 0,
                                            "default": 72,
                                            "options": {
                                                "infoText": "The TAI program start day for ED-TAI protocol.",
                                                "grid_columns": 6,
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                }
                                            }
                                        },
                                    }
                                },
                            },
                        },
                        "bodyweight": {
                            "type": "object",
                            "format": "grid",
                            "title": "Bodyweight",
                            "properties": {
                                "birth_weight_avg_ho": {
                                    "title": "Average Holstein Birth Weight (kg/head)",
                                    "type": "number",
                                    "default": 43.9,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "The average birthweight for Holstein cows (default is 43.9)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 43.9,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "birth_weight_std_ho": {
                                    "title": "Holstein Birth Weight Standard Deviation (kg/head)",
                                    "type": "number",
                                    "default": 1,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "The standard deviation birthweight for Holstein cows (default is 1)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 1,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "birth_weight_avg_je": {
                                    "title": "Average Jersey Birth Weight (kg/head)",
                                    "type": "number",
                                    "default": 35,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "The average birthweight for Jersey cows (default is 35)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 35,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "birth_weight_std_je": {
                                    "title": "Jersey Birth Weight Standard Deviation (kg/head)",
                                    "type": "number",
                                    "default": 1,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "The standard deviation birthweight for Jersey cows (default is 1)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 1,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "target_heifer_preg_day": {
                                    "title": "Target Heifer Pregnancy Day (days)",
                                    "type": "number",
                                    "default": 420,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "The target pregnant age in days for heifers - for adjusting heifer body weight (default is 420)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 420,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "mature_body_weight_avg": {
                                    "title": "Average Mature Body Weight (kg/head)",
                                    "type": "number",
                                    "default": 740.1,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "The average mature body weight of cows (default is 740.1)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 740.1,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "mature_body_weight_std": {
                                    "title": "Mature Body Weight Standard Deviation (kg/head)",
                                    "type": "number",
                                    "default": 73.5,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "The standard deviation of mature body weight of cows (default is 73.5)",
                                        "grid_columns": 12,
                                        "inputAttributes": {
                                            "placeholder": 73.5,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                            },
                        },
                    },
                },
                "from_literature": {
                    "type": "object",
                    "title": "From Literature",
                    "properties": {
                        "repro": {
                            "type": "object",
                            "format": "grid",
                            "title": "Literature Repro Values",
                            "properties": {
                                "preg_check_day_1": {
                                    "title": "Pregnancy Check Day 1 (days)",
                                    "type": "number",
                                    "default": 32,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "Days Since Last Heat of pregnancy check 1 (default is 32)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 32,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "preg_loss_rate_1": {
                                    "title": "Pregnancy Loss Rate 1",
                                    "type": "number",
                                    "default": 0.02,
                                    "minimum": 0,
                                    "maximum": 0.1,
                                    "options": {
                                        "infoText": "The % of cows that abort their pregnancy before the 1st pregnancy check (default is 0.02)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 0.02,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "preg_check_day_2": {
                                    "title": "Pregnancy Check Day 2 (days)",
                                    "type": "number",
                                    "default": 60,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "Days Since Last Heat of pregnancy check 2 (default is 60)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 60,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "preg_loss_rate_2": {
                                    "title": "Pregnancy Loss Rate 2",
                                    "type": "number",
                                    "default": 0.096,
                                    "minimum": 0,
                                    "maximum": 0.1,
                                    "options": {
                                        "infoText": "% of cows that abort their pregnancy between the 1st and 2nd pregnancy check (default is 0.096)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 0.096,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "preg_check_day_3": {
                                    "title": "Pregnancy Check Day 3 (days)",
                                    "type": "number",
                                    "default": 200,
                                    "minimum": 0,
                                    "options": {
                                        "infoText": "DCC of pregnancy check 3 (default is 200)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 200,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "preg_loss_rate_3": {
                                    "title": "Pregnancy Loss Rate 3",
                                    "type": "number",
                                    "default": 0.017,
                                    "minimum": 0,
                                    "maximum": 0.1,
                                    "options": {
                                        "infoText": "The % of cows that abort their pregnancy between the 2nd and 3rd pregnancy check (default is 0.017)",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "placeholder": 0.017,
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "avg_estrus_cycle_return": {
                                    "title": "Average Estrus Cycle Return",
                                    "type": "number",
                                    "default": 23,
                                    "minimum": 1,
                                    "options": {
                                        "infoText": "Average days between calving and first estrus after calving.",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "std_estrus_cycle_return": {
                                    "title": "Estrus Cycle Return Standard Deviation",
                                    "type": "number",
                                    "default": 6,
                                    "minimum": 1,
                                    "options": {
                                        "infoText": "Standard deviation of days between calving and first estrus after calving.",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "avg_estrus_cycle_cow": {
                                    "title": "Cows Average Estrus Cycle",
                                    "type": "number",
                                    "default": 21,
                                    "minimum": 1,
                                    "options": {
                                        "infoText": "Average length of estrus cycle for cows.",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "std_estrus_cycle_cow": {
                                    "title": "Cows Estrus Cycle Standard Deviation",
                                    "type": "number",
                                    "default": 4,
                                    "minimum": 1,
                                    "options": {
                                        "infoText": "Standard deviation of the length of estrus cycle for cows.",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "avg_estrus_cycle_after_pgf": {
                                    "title": "Average Estrus Cycle after PGF",
                                    "type": "number",
                                    "default": 5,
                                    "minimum": 1,
                                    "options": {
                                        "infoText": "Average days between the injection of PGF and the occurrence of estrus in the ‘PGFatPD’ resynch protocol.",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                                "std_estrus_cycle_after_pgf": {
                                    "title": "Estrus Cycle after PGF Standard Deviation",
                                    "type": "number",
                                    "default": 2,
                                    "minimum": 1,
                                    "options": {
                                        "infoText": "Standard deviation of days between the injection of PGF and the occurrence of estrus in the ‘PGFatPD’ resynch protocol.",
                                        "grid_columns": 6,
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    }
                                },
                            },
                        },
                        "milking": {
                            "type": "object",
                            "format": "grid",
                            "title": "Literature Milking Values",
                            "options": {
                                "infoText": "Literature Milking Values",
                            },
                            "properties": {
                                "wood_l": {
                                    "title": "Wood L",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "infoText": "Parameter l in the Wood’s equation. It is a scale factor for the production level.",
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    },
                                    "items": {
                                        "title": "Wood L",
                                        "type": "array",
                                        "format": "table",
                                        "options": {
                                            "infoText": "Parameter l in the Wood’s equation. It is a scale factor for the production level.",
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            }
                                        },
                                        "items": {
                                            "title": "Wood L",
                                            "type": "number",
                                            "options": {
                                                "infoText": "Parameter l in the Wood’s equation. It is a scale factor for the production level.",
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                }
                                            },
                                        }
                                    }
                                },
                                "wood_m": {
                                    "title": "Wood M",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "infoText": "Parameter m in the Wood’s equation. It indicates the growth rate in milk yield until peak.",
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    },
                                    "items": {
                                        "title": "Wood M",
                                        "type": "array",
                                        "format": "table",
                                        "options": {
                                            "infoText": "Parameter m in the Wood’s equation. It indicates the growth rate in milk yield until peak.",
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            }
                                        },
                                        "items": {
                                            "title": "Wood M",
                                            "type": "number",
                                            "options": {
                                                "infoText": "Parameter m in the Wood’s equation. It indicates the growth rate in milk yield until peak.",
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                }
                                            },
                                        }
                                    }
                                },
                                "wood_n": {
                                    "title": "Wood N",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "infoText": "Parameter n in the Wood’s equation. It describes the rate of decline after the peak.",
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    },
                                    "items": {
                                        "title": "Wood N",
                                        "type": "array",
                                        "format": "table",
                                        "options": {
                                            "infoText": "Parameter n in the Wood’s equation. It describes the rate of decline after the peak.",
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            }
                                        },
                                        "items": {
                                            "title": "Wood N",
                                            "type": "number",
                                            "options": {
                                                "infoText": "Parameter n in the Wood’s equation. It describes the rate of decline after the peak.",
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                }
                                            },
                                        }
                                    }
                                },
                                "wood_l_std": {
                                    "title": "Wood L STD",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "infoText": "Standard deviation of parameter l.",
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    },
                                    "items": {
                                        "title": "Wood L STD",
                                        "type": "array",
                                        "format": "table",
                                        "options": {
                                            "infoText": "Standard deviation of parameter l.",
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            }
                                        },
                                        "items": {
                                            "title": "Wood L STD",
                                            "type": "number",
                                            "options": {
                                                "infoText": "Standard deviation of parameter l.",
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                }
                                            },
                                        }
                                    }
                                },
                                "wood_m_std": {
                                    "title": "Wood M STD",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "infoText": "Standard deviation of parameter m.",
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    },
                                    "items": {
                                        "title": "Wood M STD",
                                        "type": "array",
                                        "format": "table",
                                        "options": {
                                            "infoText": "Standard deviation of parameter m.",
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            }
                                        },
                                        "items": {
                                            "title": "Wood M STD",
                                            "type": "number",
                                            "options": {
                                                "infoText": "Standard deviation of parameter m.",
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                }
                                            },
                                        }
                                    }
                                },
                                "wood_n_std": {
                                    "title": "Wood N STD",
                                    "type": "array",
                                    "format": "grid",
                                    "options": {
                                        "infoText": "Standard deviation of parameter n.",
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    },
                                    "items": {
                                        "title": "Wood N STD",
                                        "type": "array",
                                        "format": "table",
                                        "options": {
                                            "infoText": "Standard deviation of parameter n.",
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            }
                                        },
                                        "items": {
                                            "title": "Wood N STD",
                                            "type": "number",
                                            "options": {
                                                "infoText": "Standard deviation of parameter n.",
                                                "inputAttributes": {
                                                    "class": "text-primary form-control"
                                                }
                                            },
                                        }
                                    }
                                },
                            },
                        },
                        "culling": {
                            "type": "object",
                            "format": "grid",
                            "title": "Literature Culling Values",
                            "options": {
                                "infoText": "Literature Culling Values",
                            },
                            "properties": {
                                "parity_death_prob": {
                                    "type": "array",
                                    "title": "Parity Death Probability",
                                    "options": {
                                        "infoText": "Death rate for first, second, third, and later lactations.",
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    },
                                    "items": {
                                        "type": "number",
                                        "title": "parity_death_prob",
                                        "options": {
                                            "infoText": "Death rate for first, second, third, and later lactations.",
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            }
                                        },
                                    }
                                },
                                "parity_cull_prob": {
                                    "type": "array",
                                    "title": "Parity Cull Probability",
                                    "options": {
                                        "infoText": "Culling rate for first, second, third, and later lactations.",
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    },
                                    "items": {
                                        "type": "number",
                                        "title": "parity_cull_prob",
                                        "options": {
                                            "infoText": "Culling rate for first, second, third, and later lactations.",
                                            "inputAttributes": {
                                                "class": "text-primary form-control"
                                            }
                                        },
                                    }
                                }
                            }
                        },
                        "life_cycle": {
                            "type": "object",
                            "format": "grid",
                            "title": "Literature Culling Values",
                            "options": {
                                "infoText": "Literature Culling Values",
                            },
                            "properties": {
                                "still_birth_rate": {
                                    "title": "Still Birth Rate",
                                    "type": "number",
                                    "options": {
                                        "infoText": "Still Birth Rate.",
                                        "inputAttributes": {
                                            "class": "text-primary form-control"
                                        }
                                    },
                                }
                            }
                        }
                    },
                },
            }
        },
        "methane_mitigation": {
            "type": "object",
            "format": "grid",
            "title": "Methane Mitigation",
            "minProperties": 2,
            "maxProperties": 2,
            "properties": {
                "methane_mitigation_method": {
                    "title": "Methane Mitigation Method",
                    "type": "string",
                    "format": "select2",
                    "required": true,
                    "default": "None",
                    "enum": [
                        "None",
                        "3-NOP",
                        "monensin",
                        "essential_oils",
                        "seaweed",
                    ],
                    "options": {
                        "infoText": "The type of enteric methane mitigation supplement that is fed to the lactating dairy cattle",
                        "grid_columns": 12,
                        "inputAttributes": {
                            "placeholder": "None",
                            "class": "text-primary form-control"
                        }
                    }
                },
                "3-NOP_additive_amount": {
                    "type": "number",
                    "title": "3-NOP Additive Amount (mg/kg DMI)",
                    "minimum": 40,
                    "maximum": 100,
                    "default": 70,
                    "required": false,
                    "options": {
                        "infoText": "The dosage of the 3-NOP mitigation additive (mg/kg DMI)",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        }
                    }
                },
                "monensin_additive_amount": {
                    "type": "number",
                    "title": "Monensin Additive Amount (mg/kg DMI)",
                    "minimum": 20,
                    "maximum": 36,
                    "default": 24,
                    "required": false,
                    "options": {
                        "infoText": "The dosage of the monensin mitigation additive (mg/kg DMI)",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        }
                    }
                },
                "essential_oils_additive_amount": {
                    "type": "number",
                    "title": "Essential Oils Additive Amount (mg/kg DMI)",
                    "minimum": 0,
                    "maximum": 100,
                    "default": 0,
                    "required": false,
                    "options": {
                        "infoText": "The dosage of the essential oils mitigation additive (mg/kg DMI)",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        }
                    }
                },
                "seaweed_additive_amount": {
                    "type": "number",
                    "title": "Seaweed Additive Amount (mg/kg DMI)",
                    "minimum": 0,
                    "maximum": 100,
                    "default": 0,
                    "required": false,
                    "options": {
                        "infoText": "The dosage of the seaweed mitigation additive (mg/kg DMI)",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        }
                    }
                },
            }
        },
        "housing": {
            "title": "Housing",
            "type": "string",
            "default": "barn",
            "enum": [
                "barn",
                "pasture",
                "drylot",
            ],
            "options": {
                "infoText": "The type of housing management for the herd.",
                "grid_columns": 6,
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            }
        },
        "pasture_concentrate": {
            "title": "Pasture Concentration",
            "type": "number",
            "minimum": 0,
            "default": 0,
            "required": false,
            "options": {
                "infoText": "Amount of concentrate supplementation provided if animals are housed on pasture. (kg)",
                "grid_columns": 6,
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            },
        },
        "methane_model": {
            "title": "Methane Model",
            "type": "string",
            "default": "IPCC",
            "enum": [
                "Mills",
                "Mutian",
                "IPCC",
            ],
            "options": {
                "infoText": "The method used to estimate enteric methane emissions.",
                "grid_columns": 12,
                "inputAttributes": {
                    "class": "text-primary form-control"
                }
            }
        },
        "ration": {
            "type": "object",
            "title": "Ration",
            "format": "grid",
            "options": {
                "infoText": "",
            },
            "properties": {
                "user_input": {
                    "title": "User Input",
                    "type": "boolean",
                    "default": false,
                    "format": "checkbox",
                    "options": {
                        "infoText": "A boolean value indicating if the user will provide the ration or diet formulation they would like to feed to the cattle (true) or not (false).",
                        "grid_columns": 6,
                    }
                },
                "formulation_interval": {
                    "title": "Formulation Interval",
                    "type": "number",
                    "minimum": 1,
                    "default": 30,
                    "options": {
                        "infoText": "The length of time in days between when the diets are reformulated.",
                        "grid_columns": 6,
                        "inputAttributes": {
                            "class": "text-primary form-control"
                        }
                    },
                },
            },

        },
        "pen_information": {
            "type": "array",
            "title": "Pen Information",
            "format": "grid",
            "options": {
                "infoText": "Add as many different pens as needed.",
            },
            "items": {
                "type": "object",
                "title": "Pen",
                "format": "grid",
                "properties": {
                    "id": {
                        "title": "Pen ID",
                        "type": "number",
                        "options": {
                            "infoText": "The index of the pen.",
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                    "pen_name": {
                        "title": "Pen Name",
                        "type": "string",
                        "options": {
                            "infoText": "The name or identifier of a given pen.",
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                    "animal_combination": {
                        "title": "Animal Combination",
                        "type": "string",
                        "enum": [
                            "CALF",
                            "GROWING",
                            "CLOSE_UP",
                            "LAC_COW",
                        ],
                        "options": {
                            "infoText": "The valid combinations of animal types that can be in a pen.",
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                    "vertical_dist_to_milking_parlor": {
                        "title": "Vertical Distance to Milking Parlor (m)",
                        "type": "number",
                        "minimum": 0,
                        "default": 0.1,
                        "options": {
                            "infoText": "The elevation gain (in meters) between the pen and the milking parlor.",
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                    "horizontal_dist_to_milking_parlor": {
                        "title": "Horizontal Distance to Milking Parlor (m)",
                        "type": "number",
                        "minimum": 0,
                        "default": 1.6,
                        "options": {
                            "infoText": "The distance (in meters) between the pen and the milking parlor.",
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                    "number_of_stalls": {
                        "title": "Number of Stalls",
                        "type": "number",
                        "minimum": 0,
                        "default": 1000,
                        "options": {
                            "infoText": "The number of stalls in the pen.",
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                    "housing_type": {
                        "title": "Housing Type",
                        "type": "string",
                        "enum": [
                            "open air barn"
                        ],
                        "default": "open air barn",
                        "options": {
                            "infoText": "The type of barn the pen is in.",
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                    "pen_type": {
                        "title": "Pen Type",
                        "type": "string",
                        "enum": [
                            "freestall",
                            "tilestall",
                            "drylot",
                        ],
                        "default": "freestall",
                        "options": {
                            "infoText": "The type of stalls the pen has.",
                            "grid_columns": 6,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                    "max_stocking_density": {
                        "title": "Max Stocking Density",
                        "type": "number",
                        "minimum": 0.5,
                        "maximum": 2,
                        "default": 1.2,
                        "options": {
                            "infoText": "The maximum ration between the number of animals in the pen and the number of stalls in the pen.",
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                    "manure_management_scenario_id": {
                        "title": "Manure Management Scenario ID",
                        "type": "number",
                        "minimum": 0,
                        "default": 0,
                        "options": {
                            "infoText": "The ID number of the manure management practices that are used for this pen.",
                            "grid_columns": 12,
                            "inputAttributes": {
                                "class": "text-primary form-control"
                            }
                        },
                    },
                },
            }
        }
    }
}