from collections import defaultdict
from typing import Any, Callable

import pytest
from mock.mock import MagicMock, call
from numpy.ma.testutils import approx
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.feed.feed import Feed
from RUFAS.enums import AnimalCombination
from RUFAS.time import Time
from RUFAS.weather import Weather
from tests.animal_module_tests.test_animal import cow_a


@pytest.fixture
def config_json() -> dict[str, Any]:
    return {
    "start_date": "2012:244",
    "end_date": "2018:243",
    "random_seed": 42,
    "set_seed": True,
    "simulate_animals": True,
    "nutrient_standard": "NASEM",
    "FIPS_county_code": 55025,
    "include_detailed_values": True
}

@pytest.fixture
def animal_json() -> dict[str, Any]:
    return {
  "herd_information": {
    "calf_num": 8,
    "heiferI_num": 44,
    "heiferII_num": 38,
    "heiferIII_num_springers": 5,
    "cow_num": 100,
    "replace_num": 500,
    "herd_num": 100,
    "breed": "HO",
    "parity_fractions": {
      "1": 0.386,
      "2": 0.281,
      "3": 0.333
    },
    "annual_milk_yield": None
  },
  "herd_initialization": {
    "initial_animal_num": 10000,
    "simulation_days": 5000
  },
  "animal_config": {
    "management_decisions": {
      "breeding_start_day_h": 380,
      "heifer_repro_method": "ED",
      "cow_repro_method": "ED-TAI",
      "semen_type": "conventional",
      "days_in_preg_when_dry": 218,
      "heifer_repro_cull_time": 500,
      "do_not_breed_time": 185,
      "cull_milk_production": 30,
      "cow_times_milked_per_day": 3,
	    "milk_fat_percent": 4,
	    "milk_protein_percent": 3.2
    },
    "farm_level": {
      "calf": {
        "male_calf_rate_sexed_semen": 0.1,
        "male_calf_rate_conventional_semen": 0.53,
        "keep_female_calf_rate": 1,
        "wean_day": 60,
        "wean_length": 7,
        "milk_type": "whole"
      },
      "repro": {
        "voluntary_waiting_period": 50,
        "conception_rate_decrease": 0.026,
        "decrease_conception_rate_in_rebreeding": False,
        "decrease_conception_rate_by_parity": False,
        "avg_gestation_len": 276,
        "std_gestation_len": 6,
        "prefresh_day": 21,
        "calving_interval": 400,
        "heifers": {
            "estrus_detection_rate": 0.9,
            "estrus_conception_rate": 0.6,
            "repro_sub_protocol": "5dCG2P",
            "repro_sub_properties": {
                "conception_rate": 0.6,
                "estrus_detection_rate": 0.9
            }
        },
        "cows": {
            "estrus_detection_rate": 0.6,
            "ED_conception_rate": 0.5,
            "presynch_program": "Double OvSynch",
            "presynch_program_start_day": 50,
            "ovsynch_program": "OvSynch 56",
            "ovsynch_program_start_day": 64,
            "ovsynch_program_conception_rate": 0.6,
            "resynch_program": "TAIafterPD"
        }
			},
			"bodyweight": {
				"birth_weight_avg_ho": 43.9,
				"birth_weight_std_ho": 1,
				"birth_weight_avg_je": 27.2,
				"birth_weight_std_je": 1,
				"target_heifer_preg_day": 399,
				"mature_body_weight_avg": 740.1,
				"mature_body_weight_std": 73.5
			}
		},
		"from_literature": {
			"repro": {
				"preg_check_day_1": 32,
				"preg_loss_rate_1": 0.02,
				"preg_check_day_2": 60,
				"preg_loss_rate_2": 0.096,
				"preg_check_day_3": 200,
				"preg_loss_rate_3": 0.017,
				"avg_estrus_cycle_return": 23,
				"std_estrus_cycle_return": 6,
				"avg_estrus_cycle_heifer": 21,
				"std_estrus_cycle_heifer": 2.5,
				"avg_estrus_cycle_cow": 21,
				"std_estrus_cycle_cow": 4,
				"avg_estrus_cycle_after_pgf": 5,
				"std_estrus_cycle_after_pgf": 2
			},
			"culling": {
				"cull_day_count": [0, 5, 15, 45, 90, 135, 180, 225, 270, 330, 380, 430, 480, 530],
				"feet_leg_cull": {
					"probability": 0.1633,
					"cull_day_prob": [0, 0.03, 0.08, 0.16, 0.25, 0.36, 0.48, 0.59, 0.69, 0.78, 0.85, 0.90, 0.95, 1]
				},
				"injury_cull": {
					"probability": 0.2883,
					"cull_day_prob": [0, 0.08, 0.18, 0.28, 0.38, 0.47, 0.56, 0.64, 0.71, 0.78, 0.85, 0.90, 0.95, 1]
				},
				"mastitis_cull": {
					"probability": 0.2439,
					"cull_day_prob": [0, 0.06, 0.12, 0.19, 0.30, 0.43, 0.56, 0.68, 0.78, 0.85, 0.90, 0.94, 0.97, 1]
				},
				"disease_cull": {
					"probability": 0.1391,
					"cull_day_prob": [0, 0.04, 0.12, 0.24, 0.34, 0.42, 0.50, 0.57, 0.64, 0.72, 0.81, 0.89, 0.95, 1]
				},
				"udder_cull": {
					"probability": 0.0645,
					"cull_day_prob": [0, 0.12, 0.24, 0.33, 0.41, 0.48, 0.55, 0.62, 0.68, 0.76, 0.82, 0.89, 0.95, 1]
				},
				"unknown_cull": {
					"probability": 0.1009,
					"cull_day_prob": [0, 0.05, 0.11, 0.18, 0.27, 0.37, 0.45, 0.54, 0.62, 0.70, 0.77, 0.84, 0.92, 1]
				},
				"parity_death_prob": [0.039,0.056,0.085,0.117],
				"parity_cull_prob": [0.169, 0.233, 0.301, 0.408],
				"death_day_prob": [0, 0.18, 0.32, 0.42, 0.48, 0.54, 0.60, 0.65, 0.70, 0.77, 0.83, 0.89, 0.95, 1]
			},
			"life_cycle": {
				"still_birth_rate": 0.065
			}
		}
	},
	"methane_mitigation": {
		"methane_mitigation_method": "None",
		"methane_mitigation_additive_amount": 0,
		"3-NOP_additive_amount": 70,
		"monensin_additive_amount": 24,
		"essential_oils_additive_amount": 0,
		"seaweed_additive_amount": 0
	},
	"housing": "barn",
	"pasture_concentrate": 0,
	"methane_model": "IPCC",
	"ration": {
		"phosphorus_requirement_buffer": 0,
		"user_input": False,
		"formulation_interval": 30
	},
	"pen_information": [
		{
			"id": 0,
			"pen_name": "",
			"animal_combination": "CALF",
			"vertical_dist_to_milking_parlor": 0.1,
			"horizontal_dist_to_milking_parlor": 10,
			"number_of_stalls": 30,
			"housing_type": "open air barn",
			"pen_type": "freestall",
			"max_stocking_density": 1.2,
			"manure_management_scenario_id": 0
		},
		{
			"id": 1,
			"pen_name": "",
			"animal_combination": "GROWING",
			"vertical_dist_to_milking_parlor": 0.1,
			"horizontal_dist_to_milking_parlor": 10,
			"number_of_stalls": 125,
			"housing_type": "open air barn",
			"pen_type": "freestall",
			"max_stocking_density": 1.2,
			"manure_management_scenario_id": 1
		},
		{
			"id": 2,
			"pen_name": "",
			"animal_combination": "CLOSE_UP",
			"vertical_dist_to_milking_parlor": 0.1,
			"horizontal_dist_to_milking_parlor": 10,
			"number_of_stalls": 60,
			"housing_type": "open air barn",
			"pen_type": "freestall",
			"max_stocking_density": 1.2,
			"manure_management_scenario_id": 2
		},
		{
			"id": 3,
			"pen_name": "",
			"animal_combination": "LAC_COW",
			"vertical_dist_to_milking_parlor": 0.1,
			"horizontal_dist_to_milking_parlor": 10,
			"number_of_stalls": 150,
			"housing_type": "open air barn",
			"pen_type": "freestall",
			"max_stocking_density": 1.2,
			"manure_management_scenario_id": 5
		}
	]
}

@pytest.fixture
def manure_management_json() -> dict[str, Any]:
    return {
  "manure_management_scenarios": [
    {
      "scenario_id": 0,
      "bedding_type": "sawdust",
      "manure_handler": "manual scraping",
      "manure_separator": "none",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "anaerobic lagoon"
    },
    {
      "scenario_id": 1,
      "bedding_type": "sawdust",
      "manure_handler": "manual scraping",
      "manure_separator": "none",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "slurry storage outdoor"
    },
    {
      "scenario_id": 2,
      "bedding_type": "sawdust",
      "manure_handler": "manual scraping",
      "manure_separator": "screw press",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "slurry storage outdoor"
    },
    {
      "scenario_id": 3,
      "bedding_type": "sawdust",
      "manure_handler": "flush system",
      "manure_separator": "rotary screen",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "anaerobic lagoon"
    },
    {
      "scenario_id": 4,
      "bedding_type": "sand",
      "manure_handler": "flush system",
      "manure_separator": "none",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "anaerobic lagoon"
    },
    {
      "scenario_id": 5,
      "bedding_type": "sawdust",
      "manure_handler": "manual scraping",
      "manure_separator": "none",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "anaerobic digestion and lagoon"
    },
    {
      "scenario_id": 6,
      "bedding_type": "sawdust",
      "manure_handler": "flush system",
      "manure_separator": "rotary screen",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "anaerobic digestion and lagoon"
    },
    {
      "scenario_id": 7,
      "bedding_type": "sawdust",
      "manure_handler": "flush system",
      "manure_separator": "none",
      "manure_separator_after_digestion": "rotary screen",
      "manure_treatment": "anaerobic digestion and lagoon with separator"
    },
    {
      "scenario_id": 8,
      "bedding_type": "CBPB sawdust",
      "manure_handler": "tillage",
      "manure_separator": "none",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "compost bedded pack barn"
    },
    {
      "scenario_id": 9,
      "bedding_type": "none",
      "manure_handler": "harrowing",
      "manure_separator": "none",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "open lots"
    },
    {
      "scenario_id": 10,
      "bedding_type": "none",
      "manure_handler": "flush system",
      "manure_separator": "screw press",
      "manure_separator_after_digestion": "rotary screen",
      "manure_treatment": "anaerobic digestion and lagoon with separator"
    },
    {
      "scenario_id": 11,
      "bedding_type": "sawdust",
      "manure_handler": "alley scraper",
      "manure_separator": "none",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "composting"
    },
    {
      "scenario_id": 12,
      "bedding_type": "straw",
      "manure_handler": "manual scraping",
      "manure_separator": "none",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "composting"
    },
    {
      "scenario_id": 13,
      "bedding_type": "straw",
      "manure_handler": "alley scraper",
      "manure_separator": "none",
      "manure_separator_after_digestion": "none",
      "manure_treatment": "composting"
    }
  ],
  "bedding_configs": [
    {
      "name": "sawdust",
      "bedding_type": "sawdust",
      "bedding_mass_per_day": 1.97,
      "bedding_density": 250.0,
      "bedding_dry_matter_content": 0.9,
      "bedding_cleaned_fraction": 1.0,
      "bedding_carbon_fraction": 0.0,
      "bedding_phosphorus_content": 0.0,
      "sand_removal_efficiency": 0.0
    },
    {
      "name": "CBPB sawdust",
      "bedding_type": "CBPB sawdust",
      "bedding_mass_per_day": 12,
      "bedding_density": 350.0,
      "bedding_dry_matter_content": 0.9,
      "bedding_cleaned_fraction": 1.0,
      "bedding_carbon_fraction": 0.35,
      "bedding_phosphorus_content": 0.0,
      "sand_removal_efficiency": 0.0
    },
    {
      "name": "manure solids",
      "bedding_type": "manure solids",
      "bedding_mass_per_day": 2.50,
      "bedding_density": 400.0,
      "bedding_dry_matter_content": 0.9,
      "bedding_cleaned_fraction": 1.0,
      "bedding_carbon_fraction": 0.0,
      "bedding_phosphorus_content": 0.0,
      "sand_removal_efficiency": 0.0
    },
    {
      "name": "straw",
      "bedding_type": "straw",
      "bedding_mass_per_day": 1.97,
      "bedding_density": 100.0,
      "bedding_dry_matter_content": 0.9,
      "bedding_cleaned_fraction": 1.0,
      "bedding_carbon_fraction": 0.35,
      "bedding_phosphorus_content": 0.0,
      "sand_removal_efficiency": 0.0
    },
    {
      "name": "sand",
      "bedding_type": "sand",
      "bedding_mass_per_day": 25.0,
      "bedding_density": 1500.0,
      "bedding_dry_matter_content": 0.9,
      "bedding_cleaned_fraction": 1.0,
      "bedding_carbon_fraction": 0.0,
      "bedding_phosphorus_content": 0.0,
      "sand_removal_efficiency": 1.0
    },
    {
      "name": "none",
      "bedding_type": "none",
      "bedding_mass_per_day": 0.0,
      "bedding_density": 0.0,
      "bedding_dry_matter_content": 0.0,
      "bedding_cleaned_fraction": 0.0,
      "bedding_carbon_fraction": 0.0,
      "bedding_phosphorus_content": 0.0,
      "sand_removal_efficiency": 0.0
    }
  ],
  "manure_handler_configs": [
    {
      "name": "flush system",
      "manure_handler_type": "flush system",
      "cleaning_water_use_rate": 757.0,
      "minutes_per_cleaning": 8,
      "cleanings_per_day": 2,
      "daily_tillage_frequency": 0,
      "cleaning_water_recycle_fraction": 0.80
    },
    {
      "name": "manual scraping",
      "manure_handler_type": "manual scraping",
      "cleaning_water_use_rate": 10.0,
      "minutes_per_cleaning": 8,
      "cleanings_per_day": 2,
      "daily_tillage_frequency": 0,
      "cleaning_water_recycle_fraction": 0.10
    },
    {
      "name": "alley scraper",
      "manure_handler_type": "alley scraper",
      "cleaning_water_use_rate": 10.0,
      "minutes_per_cleaning": 8,
      "cleanings_per_day": 2,
      "daily_tillage_frequency": 0,
      "cleaning_water_recycle_fraction": 0.10
    },
    {
      "name": "tillage",
      "manure_handler_type": "tillage",
      "cleaning_water_use_rate": 0.0,
      "minutes_per_cleaning": 0.0,
      "cleanings_per_day": 0,
      "daily_tillage_frequency": 1,
      "cleaning_water_recycle_fraction": 0.0
    },
    {
      "name": "harrowing",
      "manure_handler_type": "harrowing",
      "cleaning_water_use_rate": 0.0,
      "minutes_per_cleaning": 0.0,
      "cleanings_per_day": 0,
      "daily_tillage_frequency": 0,
      "cleaning_water_recycle_fraction": 0.0
    }
  ],
  "manure_separator_configs": [
    {
      "name": "rotary screen",
      "manure_separator_type": "rotary screen",
      "percent_dry_solids": 0.20,
      "total_solids_removal_efficiency_for_separator": 0.35,
      "volatile_solids_removal_efficiency_for_separator": 0.40,
      "nitrogen_removal_efficiency_for_separator": 0.30,
      "total_ammoniacal_nitrogen_removal_efficiency_for_separator": 0.15,
      "phosphorus_removal_efficiency_for_separator": 0.40,
      "potassium_removal_efficiency_for_separator": 0.15
    },
    {
      "name": "screw press",
      "manure_separator_type": "screw press",
      "percent_dry_solids": 0.35,
      "total_solids_removal_efficiency_for_separator": 0.25,
      "volatile_solids_removal_efficiency_for_separator": 0.30,
      "nitrogen_removal_efficiency_for_separator": 0.30,
      "total_ammoniacal_nitrogen_removal_efficiency_for_separator": 0.10,
      "phosphorus_removal_efficiency_for_separator": 0.20,
      "potassium_removal_efficiency_for_separator": 0.23
    }
  ],
  "manure_treatment_configs": [
    {
      "name": "slurry storage underfloor",
      "manure_treatment_type": "slurry storage underfloor",
      "total_solids_removal_efficiency_for_treatment": 0.0,
      "volatile_solids_removal_efficiency_for_treatment": 0.0,
      "nitrogen_removal_efficiency_for_treatment": 0.0,
      "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.0,
      "phosphorus_removal_efficiency_for_treatment": 0.0,
      "potassium_removal_efficiency_for_treatment": 0.0,
      "storage_time_period": 120,
      "manure_cover": "crust"
    },
    {
      "name": "slurry storage outdoor",
      "manure_treatment_type": "slurry storage outdoor",
      "total_solids_removal_efficiency_for_treatment": 0.00,
      "volatile_solids_removal_efficiency_for_treatment": 0.0,
      "nitrogen_removal_efficiency_for_treatment": 0.0,
      "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.0,
      "phosphorus_removal_efficiency_for_treatment": 0.00,
      "potassium_removal_efficiency_for_treatment": 0.00,
      "storage_time_period": 120,
      "freeboard_input": 0.3048,
      "manure_cover": "crust"
    },
    {
      "name": "anaerobic lagoon",
      "manure_treatment_type": "anaerobic lagoon",
      "total_solids_removal_efficiency_for_treatment": 0.0,
      "volatile_solids_removal_efficiency_for_treatment": 0.0,
      "nitrogen_removal_efficiency_for_treatment": 0.0,
      "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.0,
      "phosphorus_removal_efficiency_for_treatment": 0.0,
      "potassium_removal_efficiency_for_treatment": 0.0,
      "hydraulic_retention_time": 365,
      "sludge_accumulation_period": 10.0,
      "sludge_accumulation_volume_fraction": 0.00,
      "storage_time_period": 365,
      "freeboard_input": 0.3048,
      "manure_cover": "cover"
    },
    {
      "name": "anaerobic digestion",
      "manure_treatment_type": "anaerobic digestion",
      "total_solids_removal_efficiency_for_treatment": 0.45,
      "volatile_solids_removal_efficiency_for_treatment": 0.40,
      "nitrogen_removal_efficiency_for_treatment": 0.0,
      "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.1,
      "phosphorus_removal_efficiency_for_treatment": 0.0,
      "potassium_removal_efficiency_for_treatment": 0.0,
      "hydraulic_retention_time": 25,
      "sludge_accumulation_period": 1.0,
      "sludge_accumulation_volume_fraction": 0.03,
      "top_cover_volume_fraction": 0.2,
      "evaporation_fraction": 0.02,
      "anaerobic_digestion_temperature_set_point": 37.5,
      "anaerobic_digestion_temperature_celsius": 37.5,
      "manure_cover": "N/A",
      "digester_methane_leakage_fraction": 0.01
    },
    {
      "name": "compost bedded pack barn",
      "manure_treatment_type": "compost bedded pack barn",
      "total_solids_removal_efficiency_for_treatment": 0.0,
      "nitrogen_removal_efficiency_for_treatment": 0.0,
      "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.0,
      "phosphorus_removal_efficiency_for_treatment": 0.0,
      "potassium_removal_efficiency_for_treatment": 0.0,
      "volatile_solids_removal_efficiency_for_treatment": 0.0,
      "hydraulic_retention_time": 365,
      "sludge_accumulation_period": 10.0,
      "sludge_accumulation_volume_fraction": 0.00251,
      "storage_time_period": 120,
      "freeboard_input": 0.3048
    },
    {
      "name": "open lots",
      "manure_treatment_type": "open lots",
      "total_solids_removal_efficiency_for_treatment": 0.0,
      "nitrogen_removal_efficiency_for_treatment": 0.0,
      "total_ammoniacal_nitrogen_removal_efficiency_for_treatment": 0.0,
      "phosphorus_removal_efficiency_for_treatment": 0.0,
      "potassium_removal_efficiency_for_treatment": 0.0,
      "volatile_solids_removal_efficiency_for_treatment": 0.0,
      "storage_time_period": 365
    },
    {
      "name": "composting",
      "manure_treatment_type": "composting",
      "composting_type": "intensive windrow",
      "storage_time_period": 365
    }
  ]
}

@pytest.fixture
def mock_get_data_side_effect(
        config_json: dict[str, Any],
        animal_json: dict[str, Any],
        manure_management_json: dict[str, Any]) -> list[Any]:
    return [
        config_json,
        animal_json,
        manure_management_json,
        True
    ]

@pytest.fixture
def mock_herd(mocker: MockerFixture) -> dict[str, list[Animal]]:
    calves = [
        mock_animal(AnimalType.CALF, mocker),
        mock_animal(AnimalType.CALF, mocker),
        mock_animal(AnimalType.CALF, mocker)
    ]
    heiferIs = [
        mock_animal(AnimalType.HEIFER_I, mocker),
        mock_animal(AnimalType.HEIFER_I, mocker),
        mock_animal(AnimalType.HEIFER_I, mocker)
    ]
    heiferIIs = [
        mock_animal(AnimalType.HEIFER_II, mocker),
        mock_animal(AnimalType.HEIFER_II, mocker),
        mock_animal(AnimalType.HEIFER_II, mocker)
    ]
    heiferIIIs = [
        mock_animal(AnimalType.HEIFER_III, mocker),
        mock_animal(AnimalType.HEIFER_III, mocker),
        mock_animal(AnimalType.HEIFER_III, mocker)
    ]
    dry_cows = [
        mock_animal(AnimalType.DRY_COW, mocker, days_in_milk=0, days_in_pregnancy=0),
        mock_animal(AnimalType.DRY_COW, mocker, days_in_milk=0, days_in_pregnancy=10),
        mock_animal(AnimalType.DRY_COW, mocker, days_in_milk=0, days_in_pregnancy=50),
    ]
    lac_cows = [
        mock_animal(AnimalType.LAC_COW, mocker),
        mock_animal(AnimalType.LAC_COW, mocker),
        mock_animal(AnimalType.LAC_COW, mocker),
    ]
    replacement = [mock_animal(AnimalType.DRY_COW, mocker)]

    return {
        "calves": calves,
        "heiferIs": heiferIs,
        "heiferIIs": heiferIIs,
        "heiferIIIs": heiferIIIs,
        "dry_cows": dry_cows,
        "lac_cows": lac_cows,
        "replacement": replacement
    }


def mock_herd_manager(
        calves: list[Animal],
        heiferIs: list[Animal],
        heiferIIs: list[Animal],
        heiferIIIs: list[Animal],
        cows: list[Animal],
        replacement: list[Animal],
        mocker: MockerFixture,
        mock_get_data_side_effect: list[Any]
) -> tuple[HerdManager, dict[str, MagicMock]]:
    mock_feed = mocker.MagicMock(auto_spec=Feed)
    mock_weather = mocker.MagicMock(auto_spec=Weather)
    mock_time = mocker.MagicMock(auto_spec=Time)

    mock_get_data = mocker.patch(
        "RUFAS.input_manager.InputManager.get_data",
        side_effect=mock_get_data_side_effect
    )
    mock_initialize_animal_config = mocker.patch(
        "RUFAS.biophysical.animal.animal_config.AnimalConfig.initialize_animal_config"
    )
    mock_set_lactation_parameters = mocker.patch(
        "RUFAS.biophysical.animal.milk.lactation_curve.LactationCurve.set_lactation_parameters"
    )
    mock_user_defined_ration_init = mocker.patch(
        "RUFAS.biophysical.animal.ration.user_defined_ration.UserDefinedRationManager.__init__",
        return_value=None
    )
    mocker.patch(
        "RUFAS.biophysical.animal.pen.Pen.update_animals",
        return_value=None
    )
    mock_herd_factory_init = mocker.patch(
        "RUFAS.biophysical.animal.herd_factory.HerdFactory.__init__",
        return_value=None
    )
    mock_initialize_herd = mocker.patch(
        "RUFAS.biophysical.animal.herd_factory.HerdFactory.initialize_herd",
        return_value=[calves, heiferIs, heiferIIs, heiferIIIs, cows, replacement]
    )
    mock_purchased_feed_emissions_estimator_init = mocker.patch(
        "RUFAS.routines.animal.purchased_feed_emissions_estimator.PurchasedFeedEmissionsEstimator.__init__",
        return_value=None
    )

    herd_manager = HerdManager(mock_feed, mock_weather, mock_time)
    # herd_manager.all_pens = []

    return herd_manager, {
        "mock_get_data": mock_get_data,
        "mock_initialize_animal_config": mock_initialize_animal_config,
        "mock_set_lactation_parameters": mock_set_lactation_parameters,
        "mock_user_defined_ration_init": mock_user_defined_ration_init,
        "mock_herd_factory_init": mock_herd_factory_init,
        "mock_initialize_herd": mock_initialize_herd,
        "mock_purchased_feed_emissions_estimator_init": mock_purchased_feed_emissions_estimator_init
    }


def mock_animal(
        animal_type: AnimalType,
        mocker: MockerFixture,
        days_in_milk: int = 0,
        days_in_pregnancy: int = 0
) -> Animal:
    animal = mocker.MagicMock(auto_spec=Animal)
    animal.animal_type = animal_type
    if animal_type.is_cow:
        animal.is_milking = True if animal_type == AnimalType.LAC_COW else False
        animal.days_in_milk = days_in_milk
    animal.is_pregnant = True if days_in_milk > 0 else False
    animal.days_in_pregnancy = days_in_pregnancy
    return animal


def mock_pen(animal_combination: AnimalCombination, mocker: MockerFixture) -> Pen:
    pen = mocker.MagicMock(auto_spec=Pen)
    pen.animal_combination = animal_combination
    return pen


def test_init(mocker: MockerFixture, mock_get_data_side_effect: list[Any]) -> None:
    herd_manager, mocking_methods = mock_herd_manager(
        calves=[],
        heiferIs=[],
        heiferIIs=[],
        heiferIIIs=[],
        cows=[],
        replacement=[],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )

    assert herd_manager.simulate_animals == True
    assert herd_manager.calves == []
    assert herd_manager.heiferIs == []
    assert herd_manager.heiferIIs == []
    assert herd_manager.heiferIIIs == []
    assert herd_manager.cows == []
    assert herd_manager.replacement_market == []
    assert herd_manager.heifers_sold == []
    assert herd_manager.cows_culled == []
    assert herd_manager.animal_to_pen_id_map == {}

    assert herd_manager.housing == "barn"
    assert herd_manager.pasture_concentrate == 0
    assert herd_manager.ration_user_input == False

    for key, mock_method in mocking_methods.items():
        if not key == "mock_get_data":
            mock_method.assert_called_once()


def test_animals_by_type(mocker: MockerFixture, mock_get_data_side_effect: list[Any]) -> None:
    calves = [mock_animal(AnimalType.CALF, mocker)]
    heiferIs = [mock_animal(AnimalType.HEIFER_I, mocker)]
    heiferIIs = [mock_animal(AnimalType.HEIFER_II, mocker)]
    heiferIIIs = [mock_animal(AnimalType.HEIFER_III, mocker)]
    dry_cow = [mock_animal(AnimalType.DRY_COW, mocker)]
    lac_cow = [mock_animal(AnimalType.LAC_COW, mocker)]
    replacement = [mock_animal(AnimalType.DRY_COW, mocker)]
    herd_manager, _ = mock_herd_manager(
        calves=calves,
        heiferIs=heiferIs,
        heiferIIs=heiferIIs,
        heiferIIIs=heiferIIIs,
        cows=dry_cow+lac_cow,
        replacement=replacement,
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )

    result = herd_manager.animals_by_type
    assert result == {
        AnimalType.CALF: calves,
        AnimalType.HEIFER_I: heiferIs,
        AnimalType.HEIFER_II: heiferIIs,
        AnimalType.HEIFER_III: heiferIIIs,
        AnimalType.DRY_COW: dry_cow,
        AnimalType.LAC_COW: lac_cow,
    }


def test_daily_routines(
        mocker: MockerFixture,
        mock_get_data_side_effect: list[Any],
        mock_herd: dict[str, list[Animal]]
) -> None:

    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"]+mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    herd_manager.all_pens = [
        mock_pen(AnimalCombination.CALF, mocker),
        mock_pen(AnimalCombination.GROWING, mocker),
        mock_pen(AnimalCombination.CLOSE_UP, mocker),
        mock_pen(AnimalCombination.LAC_COW, mocker)
    ]

    mock_feed = mocker.MagicMock(auto_spec=Feed)
    mock_weather = mocker.MagicMock(auto_spec=Weather)
    mock_time = mocker.MagicMock(auto_spec=Time)

    mock_animal_daily_routines_side_effect = [
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.LIFE_STAGE_CHANGED, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.SOLD, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.LIFE_STAGE_CHANGED, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.SOLD, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.LIFE_STAGE_CHANGED, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.SOLD, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.LIFE_STAGE_CHANGED, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.SOLD, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.NEW_CALF_BORN, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.NEW_CALF_BORN, animal_values={}),
        DailyRoutinesOutput(animal_status=AnimalStatus.SOLD, animal_values={})
    ]
    animals = (mock_herd["calves"] + mock_herd["heiferIs"] + mock_herd["heiferIIs"] + mock_herd["heiferIIIs"] +
               mock_herd["dry_cows"] + mock_herd["lac_cows"])
    graduated_animals: list[Animal] = []
    removed_animals: list[Animal] = []

    sold_heiferIIs: list[Animal] = []
    sold_and_died_cows: list[Animal] = []
    for animal in animals:
        return_value = mock_animal_daily_routines_side_effect.pop(0)
        animal.daily_routines = mocker.MagicMock(return_value=return_value)
        if return_value.animal_status in [
            AnimalStatus.DEAD, AnimalStatus.CULLED, AnimalStatus.SOLD
        ]:
            removed_animals.append(animal)
            if animal.animal_type == AnimalType.HEIFER_II:
                sold_heiferIIs.append(animal)
            elif animal.animal_type.is_cow:
                sold_and_died_cows.append(animal)
        elif return_value.animal_status == AnimalStatus.LIFE_STAGE_CHANGED:
            graduated_animals.append(animal)

    mock_animal_init = mocker.patch(
        "RUFAS.biophysical.animal.animal.Animal.__init__",
        return_value=None
    )

    mock_update_sold_and_died_cows = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._update_sold_and_died_cows"
    )
    mock_update_sold_heiferIIs = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._update_sold_heiferIIs"
    )
    mock_update_sold_newborn_calves = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._update_sold_newborn_calves"
    )
    mock_check_if_heifers_need_to_be_sold = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._check_if_heifers_need_to_be_sold",
        return_value=[]
    )
    mock_check_if_replacement_heifers_needed = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._check_if_replacement_heifers_needed"
    )
    mock_handle_graduated_animals = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._handle_graduated_animals"
    )
    mock_handle_newly_added_animals = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._handle_newly_added_animals"
    )
    mock_remove_animal_from_pen_and_id_map = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._remove_animal_from_pen_and_id_map"
    )
    mock_record_pen_history = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.record_pen_history"
    )
    mock_end_ration_interval = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.end_ration_interval",
        return_value=True
    )
    mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.clear_pens"
    )
    mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.allocate_animals_to_pens"
    )
    mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.reformulate_ration_single_pen"
    )
    mock_update_herd_statistics = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.update_herd_statistics"
    )
    mock_report_animal_module_manure = mocker.patch(
        "RUFAS.routines.animal.animal_module_reporter.AnimalModuleReporter.report_animal_module_manure"
    )
    mock_report_daily_reports = mocker.patch(
        "RUFAS.routines.animal.animal_module_reporter.AnimalModuleReporter.report_daily_reports"
    )

    herd_manager.daily_routines(mock_feed, mock_weather, mock_time)

    mock_animal_init.assert_called()
    mock_update_sold_and_died_cows.assert_called_once()
    mock_update_sold_heiferIIs.assert_called_once()
    mock_update_sold_newborn_calves.assert_called_once()
    mock_check_if_heifers_need_to_be_sold.assert_called_once()
    mock_check_if_replacement_heifers_needed.assert_called_once()
    mock_handle_graduated_animals.assert_called_once_with(
        graduated_animals,
        mock_feed,
        mock_weather.get_current_day_conditions().mean_air_temperature
    )
    mock_handle_newly_added_animals.assert_called()
    assert mock_remove_animal_from_pen_and_id_map.call_args_list == [
        call(animal) for animal in removed_animals
    ]
    mock_record_pen_history.assert_called_once()
    mock_end_ration_interval.assert_called()
    mock_update_herd_statistics.assert_called_once()
    mock_report_animal_module_manure.assert_called_once()
    mock_report_daily_reports.assert_called_once()


def test_initialize_pens(
        animal_json: dict[str, Any],
        manure_management_json: dict[str, Any],
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=[],
        heiferIs=[],
        heiferIIs=[],
        heiferIIIs=[],
        cows=[],
        replacement=[],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    herd_manager.all_pens = []

    herd_manager.initialize_pens(
        all_pen_data=animal_json["pen_information"],
        manure_management_scenarios=manure_management_json["manure_management_scenarios"]
    )

    expected_pen_configs = [
        {
            "pen_id": pen_config["id"],
            "pen_name": pen_config["pen_name"],
            "vertical_dist_to_milking_parlor": pen_config["vertical_dist_to_milking_parlor"],
            "horizontal_dist_to_milking_parlor": pen_config["horizontal_dist_to_milking_parlor"],
            "number_of_stalls": pen_config["number_of_stalls"],
            "housing_type": pen_config["housing_type"],
            "pen_type": pen_config["pen_type"],
            "max_stocking_density": pen_config["max_stocking_density"],
            "animal_combination": pen_config["animal_combination"],
            "bedding_type": manure_management_json["manure_management_scenarios"][
                pen_config["manure_management_scenario_id"]]["bedding_type"],
            "manure_handling": manure_management_json["manure_management_scenarios"][
                pen_config["manure_management_scenario_id"]]["manure_handler"],
            "manure_separator": manure_management_json["manure_management_scenarios"][
                pen_config["manure_management_scenario_id"]]["manure_separator"],
            "manure_separator_after_digestion": manure_management_json["manure_management_scenarios"][
                pen_config["manure_management_scenario_id"]]["manure_separator_after_digestion"],
            "manure_storage": manure_management_json["manure_management_scenarios"][
                pen_config["manure_management_scenario_id"]]["manure_treatment"]
        } for pen_config in animal_json["pen_information"]
    ]

    for pen_num in range(len(herd_manager.all_pens)):
        pen = herd_manager.all_pens[pen_num]
        assert pen.id == expected_pen_configs[pen_num]["pen_id"]
        assert pen.pen_name == expected_pen_configs[pen_num]["pen_name"]
        assert pen.vertical_dist_to_parlor == expected_pen_configs[pen_num]["vertical_dist_to_milking_parlor"]
        assert pen.horizontal_dist_to_parlor == expected_pen_configs[pen_num]["horizontal_dist_to_milking_parlor"]
        assert pen.num_stalls == expected_pen_configs[pen_num]["number_of_stalls"]
        assert pen.housing_type == expected_pen_configs[pen_num]["housing_type"]
        assert pen.pen_type == expected_pen_configs[pen_num]["pen_type"]
        assert pen.max_stocking_density == expected_pen_configs[pen_num]["max_stocking_density"]
        assert pen.animal_combination.name == expected_pen_configs[pen_num]["animal_combination"]
        assert pen.bedding_type == expected_pen_configs[pen_num]["bedding_type"]
        assert pen.manure_handling == expected_pen_configs[pen_num]["manure_handling"]
        assert pen.manure_separator == expected_pen_configs[pen_num]["manure_separator"]
        assert pen.manure_separator_after_digestion == expected_pen_configs[pen_num]["manure_separator_after_digestion"]
        assert pen.manure_storage == expected_pen_configs[pen_num]["manure_storage"]


def test_allocate_animals_to_pens(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    mock_allocate_animals_to_pens_helper = mocker.patch.object(herd_manager, "_allocate_animals_to_pens_helper")
    mock_fully_update_animal_to_pen_id_map = mocker.patch.object(herd_manager, "fully_update_animal_to_pen_id_map")

    herd_manager.allocate_animals_to_pens()

    assert mock_allocate_animals_to_pens_helper.call_args_list == [
        call(mock_herd["calves"], herd_manager.pens_by_animal_combination[AnimalCombination.CALF]),
        call(mock_herd["heiferIs"] + mock_herd["heiferIIs"],
             herd_manager.pens_by_animal_combination[AnimalCombination.GROWING]
             ),
        call(mock_herd["heiferIIIs"] + mock_herd["dry_cows"],
             herd_manager.pens_by_animal_combination[AnimalCombination.CLOSE_UP]
             ),
        call(mock_herd["lac_cows"], herd_manager.pens_by_animal_combination[AnimalCombination.LAC_COW]),
    ]
    mock_fully_update_animal_to_pen_id_map.assert_called_once()


def test_check_if_heifers_need_to_be_sold(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"]*33,
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    herd_manager.herd_statistics.heiferIII_num, herd_manager.herd_statistics.cow_num = (
        len(herd_manager.heiferIIIs), len(herd_manager.cows)
    )

    result = herd_manager._check_if_heifers_need_to_be_sold(simulation_day=0)

    expected_sold_heiferIIIs = mock_herd["heiferIIIs"][::-1][:2]
    expected_sold_heiferIIIs_info = [
        {
            "id": removed_heiferIII.id,
            "animal_type": removed_heiferIII.animal_type,
            "sold_at_day": removed_heiferIII.sold_at_day,
            "body_weight": removed_heiferIII.body_weight,
            "cull_reason": "NA",
            "days_in_milk": "NA",
            "parity": "NA",
        } for removed_heiferIII in expected_sold_heiferIIIs[:2]
    ]
    assert result == expected_sold_heiferIIIs
    assert herd_manager.herd_statistics.sold_heiferIIIs_info == expected_sold_heiferIIIs_info
    assert herd_manager.herd_statistics.heiferIII_num == 97
    assert herd_manager.herd_statistics.sold_heiferIII_oversupply_num == 2


def test_check_if_replacement_heifers_needed(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"]*31,
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"]*2,
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    herd_manager.herd_statistics.heiferIII_num, herd_manager.herd_statistics.cow_num = (
        len(herd_manager.heiferIIIs), len(herd_manager.cows)
    )
    herd_manager.herd_statistics.bought_heifer_num = 0

    result = herd_manager._check_if_replacement_heifers_needed(simulation_day=10)

    expected_bought_animals = mock_herd["replacement"]*2

    assert result == expected_bought_animals
    assert herd_manager.herd_statistics.bought_heifer_num == 2


def test_handle_graduated_animals(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    mock_add_animal_to_pen_and_id_map = mocker.patch.object(herd_manager, "_add_animal_to_pen_and_id_map")

    graduated_animals = [
        mock_animal(animal_type=AnimalType.HEIFER_I, mocker=mocker),
        mock_animal(animal_type=AnimalType.HEIFER_II, mocker=mocker),
        mock_animal(animal_type=AnimalType.HEIFER_III, mocker=mocker),
        mock_animal(animal_type=AnimalType.LAC_COW, mocker=mocker),
    ]
    mock_feed = mocker.MagicMock(auto_spec=Feed)

    herd_manager._handle_graduated_animals(graduated_animals, mock_feed, 15.0)

    assert mock_add_animal_to_pen_and_id_map.call_args_list == [
        call(animal, mock_feed, 15.0) for animal in graduated_animals
    ]


def test_handle_newly_added_animals(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    mock_add_animal_to_pen_and_id_map = mocker.patch.object(herd_manager, "_add_animal_to_pen_and_id_map")

    new_animals = [
        mock_animal(animal_type=AnimalType.HEIFER_I, mocker=mocker),
        mock_animal(animal_type=AnimalType.HEIFER_II, mocker=mocker),
        mock_animal(animal_type=AnimalType.HEIFER_III, mocker=mocker),
        mock_animal(animal_type=AnimalType.LAC_COW, mocker=mocker),
    ]
    mock_feed = mocker.MagicMock(auto_spec=Feed)

    herd_manager._handle_newly_added_animals(new_animals, mock_feed, 15.0)

    assert mock_add_animal_to_pen_and_id_map.call_args_list == [
        call(animal, mock_feed, 15.0) for animal in new_animals
    ]


def test_remove_animal_from_pen_and_id_map(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    animals = (mock_herd["calves"] + mock_herd["heiferIs"] + mock_herd["heiferIIs"] + mock_herd["heiferIIIs"] +
               mock_herd["dry_cows"] + mock_herd["lac_cows"])
    herd_manager.animal_to_pen_id_map = {
        animal.id: herd_manager.pens_by_animal_combination[
            herd_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
        ][0].id for animal in animals
    }

    mock_pen_remove_animals_by_ids = mocker.patch("RUFAS.biophysical.animal.pen.Pen.remove_animals_by_ids")

    for animal in animals:
        herd_manager._remove_animal_from_pen_and_id_map(animal)
        mock_pen_remove_animals_by_ids.assert_called_with([animal.id])

    assert herd_manager.animal_to_pen_id_map == {}


def test_add_animal_to_pen_and_id_map(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    animals = (mock_herd["calves"] + mock_herd["heiferIs"] + mock_herd["heiferIIs"] + mock_herd["heiferIIIs"] +
               mock_herd["dry_cows"] + mock_herd["lac_cows"])
    herd_manager.animal_to_pen_id_map = {}

    mock_pen_update_animals = mocker.patch("RUFAS.biophysical.animal.pen.Pen.update_animals")

    mock_feed = mocker.MagicMock(auto_spec=Feed)
    for animal in animals:
        herd_manager._add_animal_to_pen_and_id_map(animal, mock_feed, 15.0)
        mock_pen_update_animals.assert_called_with(
            [animal],
            herd_manager.ANIMAL_GROUPING_SCENARIO,
            mock_feed,
            15.0,
            herd_manager.phosphorus_concentration_by_animal_class[animal.animal_type]
        )

    assert herd_manager.animal_to_pen_id_map == {
            animal.id: herd_manager.pens_by_animal_combination[
                herd_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
            ][0].id for animal in animals
        }


def test_sort_cows_before_allocation(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    cow_a = mock_animal(AnimalType.LAC_COW, mocker, days_in_milk=10)
    cow_b = mock_animal(AnimalType.LAC_COW, mocker, days_in_milk=5)
    cow_c = mock_animal(AnimalType.LAC_COW, mocker, days_in_milk=15)
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + [cow_a, cow_b, cow_c],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )

    expected_cow_order = mock_herd["dry_cows"] + [cow_b, cow_a, cow_c]

    herd_manager._sort_cows_before_allocation()

    assert herd_manager.cows == expected_cow_order


def test_group_pens_by_animal_combination(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    expected_result = defaultdict(list)
    for animal_combination in [
        AnimalCombination.CALF, AnimalCombination.GROWING, AnimalCombination.CLOSE_UP, AnimalCombination.LAC_COW
    ]:
        expected_result[animal_combination].extend(herd_manager.pens_by_animal_combination[animal_combination])

    result = herd_manager._group_pens_by_animal_combination(herd_manager.all_pens)
    assert result == expected_result


def test_create_additional_pens_for_potential_space_shortage(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    expected_num_new_pens = {
        AnimalCombination.CALF: 1,
        AnimalCombination.GROWING: 1,
        AnimalCombination.CLOSE_UP: 0,
        AnimalCombination.LAC_COW: 2
    }
    expected_num_stalls_per_additional_pen = {
        AnimalCombination.CALF: 2,
        AnimalCombination.GROWING: 2,
        AnimalCombination.CLOSE_UP: 0,
        AnimalCombination.LAC_COW: 3
    }

    mock_calculate_animal_space_shortage = mocker.patch.object(
        herd_manager,
        "_calculate_animal_space_shortage",
        side_effect=list(expected_num_new_pens.values())
    )
    mock_calculate_max_animal_spaces_per_pen = mocker.patch.object(
        herd_manager,
        "_calculate_max_animal_spaces_per_pen",
        side_effect=[1, 1, 1]
    )

    for animal_combination, pens in herd_manager.pens_by_animal_combination.items():
        reference_pen = pens[0]
        expected_new_pens: list[Pen] = []
        num_new_pens = expected_num_new_pens[animal_combination]
        for i in range(num_new_pens):
            new_pen_id = reference_pen.id + i
            expected_new_pens.append(
                Pen(
                    pen_id=new_pen_id,
                    pen_name=str(new_pen_id),
                    vertical_dist_to_milking_parlor=reference_pen.vertical_dist_to_parlor,
                    horizontal_dist_to_milking_parlor=reference_pen.horizontal_dist_to_parlor,
                    number_of_stalls=expected_num_stalls_per_additional_pen[animal_combination],
                    housing_type=reference_pen.housing_type,
                    bedding_type=reference_pen.bedding_type,
                    pen_type=reference_pen.pen_type,
                    manure_handling=reference_pen.manure_handling,
                    manure_separator=reference_pen.manure_separator,
                    manure_separator_after_digestion=reference_pen.manure_separator_after_digestion,
                    manure_storage=reference_pen.manure_storage,
                    animal_combination=animal_combination,
                    max_stocking_density=reference_pen.max_stocking_density,
                )
            )
        result: list[Pen] = herd_manager._create_additional_pens_for_potential_space_shortage(
            num_animals=100,
            pens=pens,
            animal_combination=animal_combination,
            start_pen_id=reference_pen.id
        )

        if expected_num_new_pens[animal_combination] > 0:
            mock_calculate_animal_space_shortage.assert_called_with(num_animals=100, pens=pens)
            mock_calculate_max_animal_spaces_per_pen.assert_called_with(
                num_stalls=expected_num_stalls_per_additional_pen[animal_combination],
                max_stocking_density=reference_pen.max_stocking_density
            )

        for j in range(len(result)):
            result_pen: Pen = result[j]
            expected_pen: Pen = expected_new_pens[j] if j < len(expected_new_pens) else None
            assert result_pen.id == expected_pen.id
            assert result_pen.pen_name == expected_pen.pen_name
            assert result_pen.vertical_dist_to_parlor == expected_pen.vertical_dist_to_parlor
            assert result_pen.horizontal_dist_to_parlor == expected_pen.horizontal_dist_to_parlor
            assert result_pen.num_stalls == expected_pen.num_stalls
            assert result_pen.housing_type == expected_pen.housing_type
            assert result_pen.bedding_type == expected_pen.bedding_type
            assert result_pen.pen_type == expected_pen.pen_type
            assert result_pen.manure_handling == expected_pen.manure_handling
            assert result_pen.manure_separator == expected_pen.manure_separator
            assert result_pen.manure_separator_after_digestion == expected_pen.manure_separator_after_digestion
            assert result_pen.manure_storage == expected_pen.manure_storage
            assert result_pen.animal_combination == animal_combination
            assert result_pen.max_stocking_density == expected_pen.max_stocking_density


@pytest.mark.parametrize(
    "num_stalls, max_stocking_density, expected, raise_value_error", [
        (100, 1.2, 120, False),
        (7, 1.2, 8, False),
        (0, 1.1, 0, False),
        (100, 0, 0, False),
        (-1, 1.2, None, True),
        (100, -1, None, True)
    ]
)
def test_calculate_max_animal_spaces_per_pen(
        num_stalls: int,
        max_stocking_density: float,
        expected: int | None,
        raise_value_error: bool,
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    if raise_value_error:
        with pytest.raises(ValueError):
            herd_manager._calculate_max_animal_spaces_per_pen(num_stalls, max_stocking_density)
    else:
        result = herd_manager._calculate_max_animal_spaces_per_pen(num_stalls, max_stocking_density)
        assert result == expected

@pytest.mark.parametrize(
    "num_animals,num_stalls,max_stocking_density,expected",
    [
        # 1. Exact Match Capacity
        (10, [10], [1.0], 0),
        # 2. Insufficient Capacity
        (10, [10], [0.5], 5),
        # 3. Multiple Pens, Exact Match
        (10, [5, 5], [1.0, 1.0], 0),
        # 4. Multiple Pens, Surplus Capacity
        (10, [10, 10], [1.0, 1.0], -10),
        # 5. Mixed Densities and Multiple Pens
        (15, [5, 10], [1.0, 1.5], -5),
        # 6. Multiple Pens, Large Exact Match
        (50, [10, 20, 10], [1.0, 1.0, 2.0], 0),
        # 7. Large Shortage
        (100, [10, 20, 30], [1.0, 1.0, 1.0], 40),
        # 8. No Pens Provided
        (10, [], [], 10),
    ]
)
def test_calculate_animal_space_shortage(
        num_animals: int,
        num_stalls: list[int],
        max_stocking_density: list[float],
        expected: int | None,
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )

    mock_pens: list[Pen] = []
    for n in range(len(num_stalls)):
        dummy_pen = mocker.MagicMock(auto_spec=Pen)
        dummy_pen.num_stalls = num_stalls[n]
        dummy_pen.max_stocking_density = max_stocking_density[n]
        mock_pens.append(dummy_pen)

    result = herd_manager._calculate_animal_space_shortage(num_animals=num_animals, pens=mock_pens)

    assert result == expected


@pytest.mark.parametrize(
    "num_animals, num_spaces, expected, raise_value_error", [
        # Valid scenarios
        (0, 10, 0.0, False),  # No animals, positive spaces
        (10, 5, 2.0, False),  # More animals than spaces => density > 1
        (5, 10, 0.5, False),  # Fewer animals than spaces => density < 1
        (10, 10, 1.0, False),  # Equal animals and spaces => density = 1
        (100, 20, 5.0, False),  # Large numbers
        (1, 1, 1.0, False),  # Minimal positive values
        (50, 100, 0.5, False),  # Ratio less than 1 but valid

        # Error scenarios
        (-1, 10, None, True),  # Negative animals
        (10, 0, None, True),  # Zero spaces
        (10, -5, None, True),  # Negative spaces
    ]
)
def test_calculate_density(
        num_animals: int,
        num_spaces: int,
        expected: float,
        raise_value_error: bool,
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    if raise_value_error:
        with pytest.raises(ValueError):
            herd_manager._calculate_density(num_animals, num_spaces)
    else:
        result = herd_manager._calculate_density(num_animals, num_spaces)
        assert result == expected


def test_gather_pen_history(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    animals = (mock_herd["calves"] + mock_herd["heiferIs"] + mock_herd["heiferIIs"] + mock_herd["heiferIIIs"] +
               mock_herd["dry_cows"] + mock_herd["lac_cows"])
    herd_manager.animal_to_pen_id_map = {
        animal.id: herd_manager.pens_by_animal_combination[
            herd_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
        ][0].id for animal in animals
    }

    for animals in [
        herd_manager.calves,
        herd_manager.heiferIs,
        herd_manager.heiferIIs,
        herd_manager.heiferIIIs,
        herd_manager.cows
    ]:
        herd_manager.gather_pen_history(animals, simulation_day=10)
        for animal in animals:
            animal.update_pen_history.assert_called_once()


def test_record_pen_history(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    mock_gather_pen_history = mocker.patch.object(herd_manager, "gather_pen_history")

    herd_manager.record_pen_history(simulation_day=10)

    assert mock_gather_pen_history.call_args_list == [
        call(herd_manager.calves, 10),
        call(herd_manager.heiferIs, 10),
        call(herd_manager.heiferIIs, 10),
        call(herd_manager.heiferIIIs, 10),
        call(herd_manager.cows, 10),
    ]


def test_clear_pens(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    mock_clear_pen = mocker.patch("RUFAS.biophysical.animal.pen.Pen.clear")

    herd_manager.clear_pens()
    assert mock_clear_pen.call_args_list == [
        call() for _ in range(len(herd_manager.all_pens))
    ]

@pytest.mark.parametrize(
    "simulation_day, formulation_interval, expected", [
        # simulation_day == 0 scenario
        (0, 10, True),   # day=0 -> True regardless of interval

        # formulation_interval == 1 scenario
        (5, 1, True),    # interval=1 -> True for any simulation_day
        (10, 1, True),

        # simulation_day % formulation_interval == 1 scenario
        (7, 3, True),    # 7 % 3 = 1 -> True
        (1, 10, True),   # 1 % 10 = 1 -> True

        # None of the conditions met (should return False)
        (2, 2, False),   # 2 % 2 = 0, interval=2 != 1, day=2 !=0
        (10, 5, False),  # 10 % 5 = 0, interval=5 != 1, day=10 !=0
        (3, 4, False),   # 3 % 4 = 3, not 1; interval=4 != 1; day=3 !=0
    ]
)
def test_end_ration_interval(
        simulation_day: int,
        formulation_interval: int,
        expected: bool,
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    herd_manager.formulation_interval = formulation_interval

    result = herd_manager.end_ration_interval(simulation_day=simulation_day)

    assert result == expected


def test_update_herd_statistics(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    mock_calculate_herd_percentages = mocker.patch.object(
        herd_manager,
        "_calculate_herd_percentages"
    )
    mock_update_heifer_reproduction_statistics = mocker.patch.object(
        herd_manager,
        "_update_heifer_reproduction_statistics"
    )
    mock_update_cow_reproduction_statistics = mocker.patch.object(
        herd_manager,
        "_update_cow_reproduction_statistics"
    )
    mock_update_cow_milking_statistics = mocker.patch.object(
        herd_manager,
        "_update_cow_milking_statistics"
    )
    mock_update_cow_pregnancy_statistics = mocker.patch.object(
        herd_manager,
        "_update_cow_pregnancy_statistics"
    )
    mock_update_cow_parity_statistics = mocker.patch.object(
        herd_manager,
        "_update_cow_parity_statistics"
    )
    mock_calculate_cow_percentages = mocker.patch.object(
        herd_manager,
        "_calculate_cow_percentages"
    )
    mock_update_average_mature_body_weight = mocker.patch.object(
        herd_manager,
        "_update_average_mature_body_weight"
    )
    mock_update_average_cow_body_weight = mocker.patch.object(
        herd_manager,
        "_update_average_cow_body_weight"
    )
    mock_update_average_cow_parity = mocker.patch.object(
        herd_manager,
        "_update_average_cow_parity"
    )

    herd_manager.update_herd_statistics()

    assert herd_manager.herd_statistics.calf_num == len(herd_manager.calves)
    assert herd_manager.herd_statistics.heiferI_num == len(herd_manager.heiferIs)
    assert herd_manager.herd_statistics.heiferII_num == len(herd_manager.heiferIIs)
    assert herd_manager.herd_statistics.heiferIII_num == len(herd_manager.heiferIIIs)
    assert herd_manager.herd_statistics.cow_num == len(herd_manager.cows)

    mock_calculate_herd_percentages.assert_called_once_with()
    mock_update_heifer_reproduction_statistics.assert_called_once_with()
    mock_update_cow_reproduction_statistics.assert_called_once_with()
    mock_update_cow_milking_statistics.assert_called_once_with()
    mock_update_cow_pregnancy_statistics.assert_called_once_with()
    mock_update_cow_parity_statistics.assert_called_once_with()
    mock_calculate_cow_percentages.assert_called_once_with()
    mock_update_average_mature_body_weight.assert_called_once_with()
    mock_update_average_cow_body_weight.assert_called_once_with()
    mock_update_average_cow_parity.assert_called_once_with()


def test_calculate_herd_percentages(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    animals = (mock_herd["calves"] + mock_herd["heiferIs"] + mock_herd["heiferIIs"] + mock_herd["heiferIIIs"] +
               mock_herd["dry_cows"] + mock_herd["lac_cows"])

    herd_manager.herd_statistics.calf_num = len(herd_manager.calves)
    herd_manager.herd_statistics.heiferI_num = len(herd_manager.heiferIs)
    herd_manager.herd_statistics.heiferII_num = len(herd_manager.heiferIIs)
    herd_manager.herd_statistics.heiferIII_num = len(herd_manager.heiferIIIs)
    herd_manager.herd_statistics.cow_num = len(herd_manager.cows)

    herd_manager._calculate_herd_percentages()

    assert approx(herd_manager.herd_statistics.calf_percent, len(herd_manager.calves) / len(animals) * 100)
    assert approx(herd_manager.herd_statistics.heiferI_percent, len(herd_manager.heiferIs) / len(animals) * 100)
    assert approx(herd_manager.herd_statistics.heiferII_percent, len(herd_manager.heiferIIs) / len(animals) * 100)
    assert approx(herd_manager.herd_statistics.heiferIII_percent, len(herd_manager.heiferIIIs) / len(animals) * 100)
    assert approx(herd_manager.herd_statistics.cow_percent, len(herd_manager.cows) / len(animals) * 100)


def test_calculate_cow_percentages(
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )

    herd_manager.herd_statistics.cow_num = len(herd_manager.cows)
    herd_manager.herd_statistics.dry_cow_num = len(mock_herd["dry_cows"])
    herd_manager.herd_statistics.milking_cow_num = len(mock_herd["lac_cows"])
    herd_manager.herd_statistics.preg_cow_num = len([
        cow for cow in herd_manager.cows if cow.is_pregnant
    ])
    herd_manager.herd_statistics.open_cow_num = len([
        cow for cow in herd_manager.cows if not cow.is_pregnant
    ])

    herd_manager._calculate_cow_percentages()

    assert approx(
        herd_manager.herd_statistics.dry_cow_percent,
        (herd_manager.herd_statistics.dry_cow_num / herd_manager.herd_statistics.cow_num * 100)
    )
    assert approx(
        herd_manager.herd_statistics.milking_cow_percent,
        (herd_manager.herd_statistics.milking_cow_num / herd_manager.herd_statistics.cow_num * 100)
    )
    assert approx(
        herd_manager.herd_statistics.preg_cow_percent,
        (herd_manager.herd_statistics.preg_cow_num / herd_manager.herd_statistics.cow_num * 100)
    )
    assert approx(
        herd_manager.herd_statistics.non_preg_cow_percent,
        (herd_manager.herd_statistics.open_cow_num / herd_manager.herd_statistics.cow_num * 100)
    )


@pytest.mark.parametrize(
    "cull_reason_stats, cow_herd_exit_num, expected_cull_reason_stats_percent", [
        # 1. All zeros with cow_herd_exit_num = 0 -> denominator=1, all 0.0%
        (
            {
                animal_constants.DEATH_CULL: 0,
                animal_constants.LOW_PROD_CULL: 0,
                animal_constants.LAMENESS_CULL: 0,
                animal_constants.INJURY_CULL: 0,
                animal_constants.MASTITIS_CULL: 0,
                animal_constants.DISEASE_CULL: 0,
                animal_constants.UDDER_CULL: 0,
                animal_constants.UNKNOWN_CULL: 0,
            },
            0,
            {
                animal_constants.DEATH_CULL: 0.0,
                animal_constants.LOW_PROD_CULL: 0.0,
                animal_constants.LAMENESS_CULL: 0.0,
                animal_constants.INJURY_CULL: 0.0,
                animal_constants.MASTITIS_CULL: 0.0,
                animal_constants.DISEASE_CULL: 0.0,
                animal_constants.UDDER_CULL: 0.0,
                animal_constants.UNKNOWN_CULL: 0.0,
            },
        ),

        # 2. One reason has all culls, matches exit_num -> 100% that reason
        (
            {
                animal_constants.DEATH_CULL: 5,
                animal_constants.LOW_PROD_CULL: 0,
                animal_constants.LAMENESS_CULL: 0,
                animal_constants.INJURY_CULL: 0,
                animal_constants.MASTITIS_CULL: 0,
                animal_constants.DISEASE_CULL: 0,
                animal_constants.UDDER_CULL: 0,
                animal_constants.UNKNOWN_CULL: 0,
            },
            5,
            {
                animal_constants.DEATH_CULL: 100.0,
                animal_constants.LOW_PROD_CULL: 0.0,
                animal_constants.LAMENESS_CULL: 0.0,
                animal_constants.INJURY_CULL: 0.0,
                animal_constants.MASTITIS_CULL: 0.0,
                animal_constants.DISEASE_CULL: 0.0,
                animal_constants.UDDER_CULL: 0.0,
                animal_constants.UNKNOWN_CULL: 0.0,
            },
        ),

        # 3. Multiple reasons evenly split
        # Suppose total exit = 10, death=5, low_prod=5 -> each 50%
        (
            {
                animal_constants.DEATH_CULL: 5,
                animal_constants.LOW_PROD_CULL: 5,
                animal_constants.LAMENESS_CULL: 0,
                animal_constants.INJURY_CULL: 0,
                animal_constants.MASTITIS_CULL: 0,
                animal_constants.DISEASE_CULL: 0,
                animal_constants.UDDER_CULL: 0,
                animal_constants.UNKNOWN_CULL: 0,
            },
            10,
            {
                animal_constants.DEATH_CULL: 50.0,
                animal_constants.LOW_PROD_CULL: 50.0,
                animal_constants.LAMENESS_CULL: 0.0,
                animal_constants.INJURY_CULL: 0.0,
                animal_constants.MASTITIS_CULL: 0.0,
                animal_constants.DISEASE_CULL: 0.0,
                animal_constants.UDDER_CULL: 0.0,
                animal_constants.UNKNOWN_CULL: 0.0,
            },
        ),

        # 4. Partial distribution
        # total exit = 10, death=3, low=2, others=0 -> death=30%, low=20%
        (
            {
                animal_constants.DEATH_CULL: 3,
                animal_constants.LOW_PROD_CULL: 2,
                animal_constants.LAMENESS_CULL: 0,
                animal_constants.INJURY_CULL: 0,
                animal_constants.MASTITIS_CULL: 0,
                animal_constants.DISEASE_CULL: 0,
                animal_constants.UDDER_CULL: 0,
                animal_constants.UNKNOWN_CULL: 0,
            },
            10,
            {
                animal_constants.DEATH_CULL: 30.0,
                animal_constants.LOW_PROD_CULL: 20.0,
                animal_constants.LAMENESS_CULL: 0.0,
                animal_constants.INJURY_CULL: 0.0,
                animal_constants.MASTITIS_CULL: 0.0,
                animal_constants.DISEASE_CULL: 0.0,
                animal_constants.UDDER_CULL: 0.0,
                animal_constants.UNKNOWN_CULL: 0.0,
            },
        ),

        # 5. Non-zero exit, some reasons zero
        # total exit=10, death=2, disease=8
        # death=(2/10)*100=20%, disease=(8/10)*100=80%, rest=0%
        (
            {
                animal_constants.DEATH_CULL: 2,
                animal_constants.LOW_PROD_CULL: 0,
                animal_constants.LAMENESS_CULL: 0,
                animal_constants.INJURY_CULL: 0,
                animal_constants.MASTITIS_CULL: 0,
                animal_constants.DISEASE_CULL: 8,
                animal_constants.UDDER_CULL: 0,
                animal_constants.UNKNOWN_CULL: 0,
            },
            10,
            {
                animal_constants.DEATH_CULL: 20.0,
                animal_constants.LOW_PROD_CULL: 0.0,
                animal_constants.LAMENESS_CULL: 0.0,
                animal_constants.INJURY_CULL: 0.0,
                animal_constants.MASTITIS_CULL: 0.0,
                animal_constants.DISEASE_CULL: 80.0,
                animal_constants.UDDER_CULL: 0.0,
                animal_constants.UNKNOWN_CULL: 0.0,
            },
        ),
    ]
)
def test_calculate_cull_reason_stats_percent(
        cull_reason_stats: dict[str, int],
        cow_herd_exit_num: int,
        expected_cull_reason_stats_percent: dict[str, float],
        mock_get_data_side_effect: list[Any],
        mocker: MockerFixture,
        mock_herd: dict[str, list[Animal]]
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect
    )
    herd_manager.herd_statistics.cow_herd_exit_num = cow_herd_exit_num
    herd_manager.herd_statistics.cull_reason_stats = cull_reason_stats

    herd_manager._calculate_cull_reason_stats_percent()

    for key, value in herd_manager.herd_statistics.cull_reason_stats_percent.items():
        assert approx(value, expected_cull_reason_stats_percent[key])
