from typing import Any

import pytest
from mock.mock import MagicMock
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.feed.feed import Feed
from RUFAS.enums import AnimalCombination
from RUFAS.time import Time
from RUFAS.weather import Weather


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
    mock_set_animal_grouping_scenario = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.set_animal_grouping_scenario"
    )
    mock_user_defined_ration_init = mocker.patch(
        "RUFAS.biophysical.animal.ration.user_defined_ration.UserDefinedRationManager.__init__",
        return_value=None
    )
    mock_initialize_pens = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.initialize_pens"
    )
    mock_herd_factory_init = mocker.patch(
        "RUFAS.biophysical.animal.herd_factory.HerdFactory.__init__",
        return_value=None
    )
    mock_initialize_herd = mocker.patch(
        "RUFAS.biophysical.animal.herd_factory.HerdFactory.initialize_herd",
        return_value=[calves, heiferIs, heiferIIs, heiferIIIs, cows, replacement]
    )
    mock_initialize_nutrient_requirements = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.initialize_nutrient_requirements"
    )
    mock_allocate_animals_to_pens = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.allocate_animals_to_pens"
    )
    mock_print_animal_num_warnings = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._print_animal_num_warnings"
    )
    mock_purchased_feed_emissions_estimator_init = mocker.patch(
        "RUFAS.routines.animal.purchased_feed_emissions_estimator.PurchasedFeedEmissionsEstimator.__init__",
        return_value=None
    )

    return HerdManager(mock_feed, mock_weather, mock_time), {
        "mock_get_data": mock_get_data,
        "mock_initialize_animal_config": mock_initialize_animal_config,
        "mock_set_lactation_parameters": mock_set_lactation_parameters,
        "mock_set_animal_grouping_scenario": mock_set_animal_grouping_scenario,
        "mock_user_defined_ration_init": mock_user_defined_ration_init,
        "mock_initialize_pens": mock_initialize_pens,
        "mock_herd_factory_init": mock_herd_factory_init,
        "mock_initialize_herd": mock_initialize_herd,
        "mock_initialize_nutrient_requirements": mock_initialize_nutrient_requirements,
        "mock_allocate_animals_to_pens": mock_allocate_animals_to_pens,
        "mock_print_animal_num_warnings": mock_print_animal_num_warnings,
        "mock_purchased_feed_emissions_estimator_init": mock_purchased_feed_emissions_estimator_init
    }


def mock_animal(animal_type: AnimalType, mocker: MockerFixture) -> Animal:
    animal = mocker.MagicMock(auto_spec=Animal)
    animal.animal_type = animal_type
    if animal_type.is_cow:
        animal.is_milking = True if animal_type == AnimalType.LAC_COW else False
    return animal


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
    assert herd_manager.all_pens == []
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


def test_daily_routines(mocker: MockerFixture, mock_get_data_side_effect: list[Any]) -> None:
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

    mock_feed = mocker.MagicMock(auto_spec=Feed)
    mock_weather = mocker.MagicMock(auto_spec=Weather)
    mock_time = mocker.MagicMock(auto_spec=Time)

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
        "RUFAS.biophysical.animal.herd_manager.HerdManager._check_if_heifers_need_to_be_sold"
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
        "RUFAS.biophysical.animal.herd_manager.HerdManager.end_ration_interval"
    )
    mock_clear_pens = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.clear_pens"
    )
    mock_allocate_animals_to_pens = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.allocate_animals_to_pens"
    )
    mock_reformulate_ration_single_pen = mocker.patch(
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

    result = herd_manager.daily_routines(mock_feed, mock_weather, mock_time)
    assert result == {
        AnimalType.CALF: calves,
        AnimalType.HEIFER_I: heiferIs,
        AnimalType.HEIFER_II: heiferIIs,
        AnimalType.HEIFER_III: heiferIIIs,
        AnimalType.DRY_COW: dry_cow,
        AnimalType.LAC_COW: lac_cow,
    }
