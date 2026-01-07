from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import SoldAnimalTypedDict, StillbornCalfTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
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
        "include_detailed_values": True,
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
            "parity_fractions": {"1": 0.386, "2": 0.281, "3": 0.333},
            "annual_milk_yield": None,
        },
        "herd_initialization": {"initial_animal_num": 10000, "simulation_days": 5000},
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
                "milk_protein_percent": 3.2,
            },
            "farm_level": {
                "calf": {
                    "male_calf_rate_sexed_semen": 0.1,
                    "male_calf_rate_conventional_semen": 0.53,
                    "keep_female_calf_rate": 1,
                    "wean_day": 60,
                    "wean_length": 7,
                    "milk_type": "whole",
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
                        "repro_sub_properties": {"conception_rate": 0.6, "estrus_detection_rate": 0.9},
                    },
                    "cows": {
                        "estrus_detection_rate": 0.6,
                        "ED_conception_rate": 0.5,
                        "presynch_program": "Double OvSynch",
                        "presynch_program_start_day": 50,
                        "ovsynch_program": "OvSynch 56",
                        "ovsynch_program_start_day": 64,
                        "ovsynch_program_conception_rate": 0.6,
                        "resynch_program": "TAIafterPD",
                    },
                },
                "bodyweight": {
                    "birth_weight_avg_ho": 43.9,
                    "birth_weight_std_ho": 1,
                    "birth_weight_avg_je": 27.2,
                    "birth_weight_std_je": 1,
                    "target_heifer_preg_day": 399,
                    "mature_body_weight_avg": 740.1,
                    "mature_body_weight_std": 73.5,
                },
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
                    "std_estrus_cycle_after_pgf": 2,
                },
                "culling": {
                    "cull_day_count": [0, 5, 15, 45, 90, 135, 180, 225, 270, 330, 380, 430, 480, 530],
                    "feet_leg_cull": {
                        "probability": 0.1633,
                        "cull_day_prob": [0, 0.03, 0.08, 0.16, 0.25, 0.36, 0.48, 0.59, 0.69, 0.78, 0.85, 0.90, 0.95, 1],
                    },
                    "injury_cull": {
                        "probability": 0.2883,
                        "cull_day_prob": [0, 0.08, 0.18, 0.28, 0.38, 0.47, 0.56, 0.64, 0.71, 0.78, 0.85, 0.90, 0.95, 1],
                    },
                    "mastitis_cull": {
                        "probability": 0.2439,
                        "cull_day_prob": [0, 0.06, 0.12, 0.19, 0.30, 0.43, 0.56, 0.68, 0.78, 0.85, 0.90, 0.94, 0.97, 1],
                    },
                    "disease_cull": {
                        "probability": 0.1391,
                        "cull_day_prob": [0, 0.04, 0.12, 0.24, 0.34, 0.42, 0.50, 0.57, 0.64, 0.72, 0.81, 0.89, 0.95, 1],
                    },
                    "udder_cull": {
                        "probability": 0.0645,
                        "cull_day_prob": [0, 0.12, 0.24, 0.33, 0.41, 0.48, 0.55, 0.62, 0.68, 0.76, 0.82, 0.89, 0.95, 1],
                    },
                    "unknown_cull": {
                        "probability": 0.1009,
                        "cull_day_prob": [0, 0.05, 0.11, 0.18, 0.27, 0.37, 0.45, 0.54, 0.62, 0.70, 0.77, 0.84, 0.92, 1],
                    },
                    "parity_death_prob": [0.039, 0.056, 0.085, 0.117],
                    "parity_cull_prob": [0.169, 0.233, 0.301, 0.408],
                    "death_day_prob": [0, 0.18, 0.32, 0.42, 0.48, 0.54, 0.60, 0.65, 0.70, 0.77, 0.83, 0.89, 0.95, 1],
                },
                "life_cycle": {"still_birth_rate": 0.065},
            },
        },
        "methane_mitigation": {
            "methane_mitigation_method": "None",
            "methane_mitigation_additive_amount": 0,
            "3-NOP_additive_amount": 70,
            "monensin_additive_amount": 24,
            "essential_oils_additive_amount": 0,
            "seaweed_additive_amount": 0,
        },
        "housing": "barn",
        "pasture_concentrate": 0,
        "methane_model": "IPCC",
        "ration": {
            "phosphorus_requirement_buffer": 0,
            "user_input": False,
            "formulation_interval": 30,
            "maximum_ration_reformulation_attempts": 250,
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
                "manure_management_scenario_id": 0,
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
                "manure_management_scenario_id": 1,
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
                "manure_management_scenario_id": 2,
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
                "manure_management_scenario_id": 5,
            },
        ],
    }


@pytest.fixture
def feed_json() -> dict[str, Any]:
    return {
        "calf_feeds": [202, 216],
        "growing_feeds": [2, 44, 51, 110, 167, 176, 231, 234],
        "close_up_feeds": [2, 44, 51, 100, 110, 167, 231, 234],
        "lac_cow_feeds": [2, 44, 51, 94, 110, 167, 231, 234],
        "purchased_feeds": [
            {"purchased_feed": 2, "purchased_feed_cost": 0.154},
            {"purchased_feed": 44, "purchased_feed_cost": 0.208},
            {"purchased_feed": 51, "purchased_feed_cost": 0.005},
            {"purchased_feed": 94, "purchased_feed_cost": 0.01},
            {"purchased_feed": 100, "purchased_feed_cost": 0.005},
            {"purchased_feed": 110, "purchased_feed_cost": 0.005},
            {"purchased_feed": 167, "purchased_feed_cost": 0.489},
            {"purchased_feed": 176, "purchased_feed_cost": 0.005},
            {"purchased_feed": 202, "purchased_feed_cost": 0.001},
            {"purchased_feed": 216, "purchased_feed_cost": 1.0},
            {"purchased_feed": 231, "purchased_feed_cost": 0.794},
            {"purchased_feed": 234, "purchased_feed_cost": 0.331},
        ],
        "farm_grown_feeds": [1],
        "storage_options": [
            {
                "storage_type": "Bunker Silo",
                "moisture": "Direct Cut",
                "additive": "preservative",
                "packing_density": 200,
                "inoculation": "heterofermentative",
                "bunk_type": "open_floor",
                "ventilation": True,
                "removal_rate": 6,
                "initial_dry_matter": 0,
            },
            {
                "storage_type": "Bunker Silo",
                "moisture": "Direct Cut",
                "additive": "preservative",
                "packing_density": 200,
                "inoculation": "heterofermentative",
                "bunk_type": "open_floor",
                "ventilation": True,
                "removal_rate": 6,
                "initial_dry_matter": 0,
            },
        ],
        "user_defined_ration_percentages": {
            "calf": [{"feed_type": 202, "ration_percentage": 50}, {"feed_type": 216, "ration_percentage": 50}],
            "growing": [
                {"feed_type": 2, "ration_percentage": 3.4},
                {"feed_type": 44, "ration_percentage": 4.2},
                {"feed_type": 51, "ration_percentage": 30.8},
                {"feed_type": 110, "ration_percentage": 36.3},
                {"feed_type": 167, "ration_percentage": 4.8},
                {"feed_type": 176, "ration_percentage": 17.5},
                {"feed_type": 231, "ration_percentage": 1.5},
                {"feed_type": 234, "ration_percentage": 1.5},
            ],
            "close_up": [
                {"feed_type": 2, "ration_percentage": 3.8},
                {"feed_type": 44, "ration_percentage": 4.1},
                {"feed_type": 51, "ration_percentage": 40.6},
                {"feed_type": 94, "ration_percentage": 22.2},
                {"feed_type": 110, "ration_percentage": 21.5},
                {"feed_type": 167, "ration_percentage": 5.7},
                {"feed_type": 231, "ration_percentage": 1.1},
                {"feed_type": 234, "ration_percentage": 1.0},
            ],
            "lac_cow": [
                {"feed_type": 2, "ration_percentage": 11.7},
                {"feed_type": 44, "ration_percentage": 11.2},
                {"feed_type": 51, "ration_percentage": 39.3},
                {"feed_type": 100, "ration_percentage": 7.5},
                {"feed_type": 110, "ration_percentage": 13.7},
                {"feed_type": 167, "ration_percentage": 13.1},
                {"feed_type": 231, "ration_percentage": 1.8},
                {"feed_type": 234, "ration_percentage": 1.7},
            ],
            "tolerance": 0.1,
            "milk_reduction_maximum": 0.5,
        },
        "allowances": [
            {
                "purchased_feed": 2,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 44,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 51,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 94,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 100,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 110,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 167,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 176,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 202,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 216,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 231,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
            {
                "purchased_feed": 234,
                "runtime_purchase_allowance": 1000.0,
                "advance_purchase_allowance": 1000.0,
                "planning_cycle_allowance": 1000.0,
            },
        ],
    }


@pytest.fixture
def mock_get_data_side_effect(
    config_json: dict[str, Any],
    animal_json: dict[str, Any],
    feed_json: dict[str, Any],
) -> list[Any]:
    return [config_json, animal_json, feed_json, feed_json["allowances"]]


@pytest.fixture
def mock_herd() -> dict[str, list[Animal]]:
    calves = [
        mock_animal(AnimalType.CALF, id=0),
        mock_animal(AnimalType.CALF, id=1),
        mock_animal(AnimalType.CALF, id=2),
    ]
    heiferIs = [
        mock_animal(AnimalType.HEIFER_I, id=3),
        mock_animal(AnimalType.HEIFER_I, id=4),
        mock_animal(AnimalType.HEIFER_I, id=5),
    ]
    heiferIIs = [
        mock_animal(AnimalType.HEIFER_II, id=6),
        mock_animal(AnimalType.HEIFER_II, id=7),
        mock_animal(AnimalType.HEIFER_II, id=8),
    ]
    heiferIIIs = [
        mock_animal(AnimalType.HEIFER_III, id=9),
        mock_animal(AnimalType.HEIFER_III, id=10),
        mock_animal(AnimalType.HEIFER_III, id=11),
        mock_animal(AnimalType.HEIFER_III, id=12),
    ]
    dry_cows = [
        mock_animal(AnimalType.DRY_COW, days_in_milk=0, days_in_pregnancy=0, id=13),
        mock_animal(AnimalType.DRY_COW, days_in_milk=0, days_in_pregnancy=10, id=14),
        mock_animal(AnimalType.DRY_COW, days_in_milk=0, days_in_pregnancy=50, id=15),
    ]
    lac_cows = [
        mock_animal(AnimalType.LAC_COW, id=16),
        mock_animal(AnimalType.LAC_COW, id=17),
        mock_animal(AnimalType.LAC_COW, id=18),
    ]
    replacement = [mock_animal(AnimalType.HEIFER_III, id=19)]

    return {
        "calves": calves,
        "heiferIs": heiferIs,
        "heiferIIs": heiferIIs,
        "heiferIIIs": heiferIIIs,
        "dry_cows": dry_cows,
        "lac_cows": lac_cows,
        "replacement": replacement,
    }


def mock_herd_manager(
    calves: list[Animal],
    heiferIs: list[Animal],
    heiferIIs: list[Animal],
    heiferIIIs: list[Animal],
    cows: list[Animal],
    replacement: list[Animal],
    mocker: MockerFixture,
    mock_get_data_side_effect: list[Any],
) -> tuple[HerdManager, dict[str, MagicMock]]:
    mock_feed = MagicMock(auto_spec=Feed)
    mock_weather = MagicMock(auto_spec=Weather)
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_available_feeds: list[Feed] = [mock_feed] * 8

    im = InputManager()
    mock_get_data: MagicMock = mocker.patch.object(im, "get_data", side_effect=mock_get_data_side_effect)
    mock_initialize_animal_config: MagicMock = mocker.patch(
        "RUFAS.biophysical.animal.animal_config.AnimalConfig.initialize_animal_config"
    )
    mock_set_lactation_parameters: MagicMock = mocker.patch(
        "RUFAS.biophysical.animal.milk.lactation_curve.LactationCurve.set_lactation_parameters"
    )
    mock_set_milk_quality: MagicMock = mocker.patch(
        "RUFAS.biophysical.animal.milk.milk_production.MilkProduction.set_milk_quality"
    )
    mocker.patch(
        "RUFAS.data_structures.feed_storage_to_animal_connection.AdvancePurchaseAllowance.__init__", return_value=None
    )
    mocker.patch("RUFAS.biophysical.animal.pen.Pen.update_animals", return_value=None)
    mocker.patch("RUFAS.biophysical.animal.pen.Pen._initialize_beddings", return_value=None)
    HerdFactory.set_post_animal_population(
        AnimalPopulation(
            calves=calves,
            heiferIs=heiferIs,
            heiferIIs=heiferIIs,
            heiferIIIs=heiferIIIs,
            cows=cows,
            replacement=replacement,
        )
    )

    herd_manager: HerdManager = HerdManager(mock_weather, mock_time, True, mock_available_feeds)

    return herd_manager, {
        "mock_get_data": mock_get_data,
        "mock_initialize_animal_config": mock_initialize_animal_config,
        "mock_set_lactation_parameters": mock_set_lactation_parameters,
        "mock_set_milk_quality": mock_set_milk_quality,
    }


def mock_animal(
    animal_type: AnimalType,
    days_in_milk: int = 0,
    days_in_pregnancy: int = 0,
    days_born: int = 0,
    id: int = 0,
    body_weight: float = 88.8,
    mature_body_weight: float = 100.0,
    total_phosphorus: float = 18.8,
    sold: bool = False,
    stillborn: bool = False,
    calves: int = 0,
    calving_interval: int = 0,
    calving_to_pregnancy_time: int = 0,
    most_recent_new_birth_age: int = 0,
    GnRH_injections: int = 0,
    PGF_injections: int = 0,
    CIDR_count: int = 0,
    pregnancy_diagnoses: int = 0,
    semen_number: int = 0,
    AI_times: int = 0,
    ED_days: int = 0,
    breeding_to_preg_time: int = 0,
    daily_milk_produced: float = 0.0,
    milk_fat_content: float = 0.0,
    milk_protein_content: float = 0.0,
    sold_at_day: int | None = None,
    dead_at_day: int | None = None,
    stillborn_day: int | None = None,
    cull_reason: str = "",
) -> Animal:
    animal = MagicMock(auto_spec=Animal)
    animal.id = id
    animal.animal_type = animal_type
    animal.days_born = days_born
    if animal_type.is_cow:
        animal.is_milking = True if animal_type == AnimalType.LAC_COW else False
        animal.days_in_milk = days_in_milk
    animal.is_pregnant = True if days_in_pregnancy > 0 else False
    animal.days_in_pregnancy = days_in_pregnancy
    animal.body_weight = body_weight
    animal.mature_body_weight = mature_body_weight
    animal.nutrients = MagicMock(auto_spec=Nutrients)
    animal.nutrients.total_phosphorus_in_animal = total_phosphorus
    animal.sold = sold
    animal.stillborn = stillborn
    animal.calves = calves
    animal.calving_interval = calving_interval
    animal.sold_at_day = sold_at_day
    animal.stillborn_day = stillborn_day
    animal.dead_at_day = dead_at_day
    animal.cull_reason = cull_reason

    animal.events = AnimalEvents()
    animal.events.add_event(most_recent_new_birth_age, 0, animal_constants.NEW_BIRTH)

    animal.reproduction = MagicMock(auto_spec=Reproduction)
    animal.reproduction.calves = calves
    animal.reproduction.calving_interval = calving_interval
    animal.reproduction.breeding_to_preg_time = breeding_to_preg_time

    animal.reproduction.reproduction_statistics = MagicMock(auto_spec=HerdReproductionStatistics)
    animal.reproduction.reproduction_statistics.calving_to_pregnancy_time = calving_to_pregnancy_time
    animal.reproduction.reproduction_statistics.GnRH_injections = GnRH_injections
    animal.reproduction.reproduction_statistics.PGF_injections = PGF_injections
    animal.reproduction.reproduction_statistics.CIDR_count = CIDR_count
    animal.reproduction.reproduction_statistics.pregnancy_diagnoses = pregnancy_diagnoses
    animal.reproduction.reproduction_statistics.semen_number = semen_number
    animal.reproduction.reproduction_statistics.AI_times = AI_times
    animal.reproduction.reproduction_statistics.ED_days = ED_days

    animal.milk_production = MagicMock(auto_spec=MilkProduction)
    animal.milk_production.daily_milk_produced = daily_milk_produced
    animal.milk_production.fat_content = milk_fat_content
    animal.milk_production.true_protein_content = milk_protein_content

    return animal


def mock_pen(pen_id: int, animal_combination: AnimalCombination) -> Pen:
    pen = Pen(
        pen_id=pen_id,
        pen_name=str(pen_id),
        vertical_dist_to_milking_parlor=0.0,
        horizontal_dist_to_milking_parlor=0.0,
        number_of_stalls=100,
        housing_type="",
        pen_type="",
        animal_combination=animal_combination,
        max_stocking_density=1.0,
        minutes_away_for_milking=120,
        first_parlor_processor=None,
        parlor_stream_name=None,
        manure_streams=[],
    )
    return pen


@pytest.fixture
def herd_manager(
    mock_herd: dict[str, list[Animal]], mock_get_data_side_effect: list[Any], mocker: MockerFixture
) -> HerdManager:
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect,
    )
    herd_manager.om = MagicMock(auto_spec=OutputManager)
    return herd_manager


@pytest.fixture
def mock_sold_animal_typed_dict() -> SoldAnimalTypedDict:
    return SoldAnimalTypedDict(
        id=0, animal_type="", sold_at_day=0, body_weight=0.0, cull_reason="NA", days_in_milk="NA", parity="NA"
    )


@pytest.fixture
def mock_stillborn_animal_typed_dict() -> StillbornCalfTypedDict:
    return StillbornCalfTypedDict(id=0, stillborn_day=23, birth_weight=12)
