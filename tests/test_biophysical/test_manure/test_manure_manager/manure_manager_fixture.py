from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.manure_manager import ManureManager
from RUFAS.output_manager import OutputManager


@pytest.fixture
def manure_management_input_json() -> dict[str, list[dict[str, Any]]]:
    return {
        "anaerobic_digester": [
            {
                "name": "anaerobic_digester",
                "type": "ContinuousMix",
                "hydraulic_retention_time": 25,
                "top_cover_volume_fraction": 0.2,
                "evaporation_fraction": 0.02,
                "temperature_set_point": 37.5,
                "methane_leakage_fraction": 0.01,
            },
            {
                "name": "continuous_mix",
                "type": "ContinuousMix",
                "hydraulic_retention_time": 25,
                "top_cover_volume_fraction": 0.2,
                "evaporation_fraction": 0.02,
                "temperature_set_point": 37.5,
                "methane_leakage_fraction": 0.01,
            },
        ],
        "handler": [
            {
                "name": "alley_scraper",
                "type": "AlleyScraper",
                "handler_type": "AlleyScraper",
                "cleaning_water_use_amount": 0.0,
                "cleaning_water_recycle_fraction": 0.8,
                "use_parlor_flush": False,
            },
            {
                "name": "manual_scraper",
                "type": "ManualScraper",
                "handler_type": "ManualScraper",
                "cleaning_water_use_amount": 0.0,
                "cleaning_water_recycle_fraction": 0.8,
                "use_parlor_flush": False,
            },
            {
                "name": "flush_system",
                "type": "FlushSystem",
                "handler_type": "FlushSystem",
                "cleaning_water_use_amount": 0.0,
                "cleaning_water_recycle_fraction": 0.8,
                "use_parlor_flush": False,
            },
            {
                "name": "parlor_cleaning_handler",
                "type": "ParlorCleaningHandler",
                "handler_type": "ParlorCleaningHandler",
                "cleaning_water_use_amount": 0.0,
                "cleaning_water_recycle_fraction": 0.8,
                "use_parlor_flush": True,
            },
        ],
        "separator": [
            {
                "name": "rotary_screen",
                "type": "RotaryScreen",
                "separated_solids_dry_matter": 0.20,
                "total_solids_efficiency": 0.35,
                "volatile_solids_efficiency": 0.40,
                "nitrogen_efficiency": 0.30,
                "ammoniacal_nitrogen_efficiency": 0.15,
                "phosphorus_efficiency": 0.40,
                "potassium_efficiency": 0.15,
                "ash_efficiency": 0.20,
            },
            {
                "name": "screw_press",
                "type": "ScrewPress",
                "separated_solids_dry_matter": 0.35,
                "total_solids_efficiency": 0.25,
                "volatile_solids_efficiency": 0.30,
                "nitrogen_efficiency": 0.30,
                "ammoniacal_nitrogen_efficiency": 0.10,
                "phosphorus_efficiency": 0.20,
                "potassium_efficiency": 0.23,
                "ash_efficiency": 0.20,
            },
        ],
        "storage": [
            {
                "name": "slurry_storage_outdoor",
                "type": "SlurryStorageOutdoor",
                "capacity": None,
                "cover": "no cover",
                "storage_time_period": 120,
                "surface_area": None,
            },
            {
                "name": "slurry_storage_underfloor",
                "type": "SlurryStorageUnderfloor",
                "capacity": None,
                "cover": "cover",
                "storage_time_period": 120,
                "surface_area": None,
            },
            {
                "name": "anaerobic_lagoon",
                "type": "AnaerobicLagoon",
                "capacity": None,
                "cover": "no cover",
                "storage_time_period": 365,
                "surface_area": None,
            },
        ],
        "processor_connections": [
            {
                "processor_name": "alley_scraper",
                "destinations": [
                    {"receiving_processor_name": "rotary_screen", "proportion": 0.5},
                    {"receiving_processor_name": "anaerobic_digester", "proportion": 0.5},
                ],
            },
            {
                "processor_name": "flush_system",
                "destinations": [
                    {"receiving_processor_name": "screw_press", "proportion": 0.1},
                    {"receiving_processor_name": "parlor_cleaning_handler", "proportion": 0.8},
                    {"receiving_processor_name": "slurry_storage_outdoor", "proportion": 0.1},
                ],
            },
            {
                "processor_name": "parlor_cleaning_handler",
                "destinations": [
                    {"receiving_processor_name": "continuous_mix", "proportion": 0.18},
                    {"receiving_processor_name": "anaerobic_lagoon", "proportion": 0.68},
                    {"receiving_processor_name": "slurry_storage_outdoor", "proportion": 0.14},
                ],
            },
            {
                "processor_name": "anaerobic_digester",
                "destinations": [
                    {"receiving_processor_name": "flush_system", "proportion": 0.93},
                    {"receiving_processor_name": "screw_press", "proportion": 0.07},
                ],
            },
            {
                "processor_name": "continuous_mix",
                "destinations": [{"receiving_processor_name": "slurry_storage_outdoor", "proportion": 1.0}],
            },
            {"processor_name": "anaerobic_lagoon", "destinations": []},
            {"processor_name": "slurry_storage_outdoor", "destinations": []},
        ],
        "separator_connections": [
            {
                "processor_name": "rotary_screen",
                "liquid_output_destinations": [{"receiving_processor_name": "anaerobic_lagoon", "proportion": 1.0}],
                "solid_output_destinations": [
                    {"receiving_processor_name": "slurry_storage_outdoor", "proportion": 1.0}
                ],
            },
            {
                "processor_name": "screw_press",
                "liquid_output_destinations": [{"receiving_processor_name": "anaerobic_lagoon", "proportion": 1.0}],
                "solid_output_destinations": [
                    {"receiving_processor_name": "slurry_storage_outdoor", "proportion": 0.2},
                    {"receiving_processor_name": "continuous_mix", "proportion": 0.8},
                ],
            },
        ],
    }


@pytest.fixture
def manure_manager(mocker: MockerFixture) -> ManureManager:
    mocker.patch("RUFAS.biophysical.manure.manure_manager.ManureManager.__init__", return_value=None)
    manure_manager = ManureManager()

    manure_manager.all_processors, manure_manager._all_separators, manure_manager._adjacency_matrix = {}, {}, {}
    manure_manager._processing_order = []
    manure_manager._om = MagicMock(auto_spec=OutputManager)

    return manure_manager


@pytest.fixture
def expected_all_referenced_processor_names() -> list[str]:
    return [
        "alley_scraper",
        "flush_system",
        "parlor_cleaning_handler",
        "anaerobic_digester",
        "continuous_mix",
        "anaerobic_lagoon",
        "slurry_storage_outdoor",
        "rotary_screen",
        "screw_press",
    ]


@pytest.fixture
def expected_all_defined_processor_names() -> list[str]:
    return [
        "anaerobic_digester",
        "continuous_mix",
        "rotary_screen",
        "screw_press",
        "slurry_storage_outdoor",
        "slurry_storage_underfloor",
        "anaerobic_lagoon",
        "alley_scraper",
        "manual_scraper",
        "flush_system",
        "parlor_cleaning_handler",
    ]


@pytest.fixture
def expected_all_separator_names() -> list[str]:
    return ["rotary_screen", "screw_press"]


@pytest.fixture
def expected_adjacency_matrix() -> dict[str, dict[str, float]]:
    return {
        'alley_scraper': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.5,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.5,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'flush_system': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.8,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.1,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.1,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'parlor_cleaning_handler': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.18,
            'anaerobic_lagoon': 0.68,
            'slurry_storage_outdoor': 0.14,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'anaerobic_digester': {
            'alley_scraper': 0.0,
            'flush_system': 0.93,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.07,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'continuous_mix': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 1.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'anaerobic_lagoon': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'slurry_storage_outdoor': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'rotary_screen_input': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'rotary_screen_solid_output': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 1.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'rotary_screen_liquid_output': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 1.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'screw_press_input': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'screw_press_solid_output': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.8,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.2,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'screw_press_liquid_output': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 1.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        }
    }


@pytest.fixture
def expected_empty_adjacency_matrix() -> dict[str, dict[str, float]]:
    return {
        'alley_scraper': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'flush_system': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'parlor_cleaning_handler': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'anaerobic_digester': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'continuous_mix': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'anaerobic_lagoon': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'slurry_storage_outdoor': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'rotary_screen_input': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'rotary_screen_solid_output': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'rotary_screen_liquid_output': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'screw_press_input': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'screw_press_solid_output': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        },
        'screw_press_liquid_output': {
            'alley_scraper': 0.0,
            'flush_system': 0.0,
            'parlor_cleaning_handler': 0.0,
            'anaerobic_digester': 0.0,
            'continuous_mix': 0.0,
            'anaerobic_lagoon': 0.0,
            'slurry_storage_outdoor': 0.0,
            'rotary_screen_input': 0.0,
            'rotary_screen_solid_output': 0.0,
            'rotary_screen_liquid_output': 0.0,
            'screw_press_input': 0.0,
            'screw_press_solid_output': 0.0,
            'screw_press_liquid_output': 0.0,
        }
    }


@pytest.fixture
def expected_processing_order() -> list[str]:
    return []


@pytest.fixture
def expected_processor_definitions_by_name() -> dict[str, dict[str, Any]]:
    return {
        'anaerobic_digester': {
            'name': 'anaerobic_digester',
            'type': 'ContinuousMix',
            'hydraulic_retention_time': 25,
            'top_cover_volume_fraction': 0.2,
            'evaporation_fraction': 0.02,
            'temperature_set_point': 37.5,
            'methane_leakage_fraction': 0.01
        },
        "continuous_mix": {
            "name": "continuous_mix",
            "type": "ContinuousMix",
            "hydraulic_retention_time": 25,
            "top_cover_volume_fraction": 0.2,
            "evaporation_fraction": 0.02,
            "temperature_set_point": 37.5,
            "methane_leakage_fraction": 0.01,
        },
        "rotary_screen": {
            "name": "rotary_screen",
            "type": "RotaryScreen",
            "separated_solids_dry_matter": 0.2,
            "total_solids_efficiency": 0.35,
            "volatile_solids_efficiency": 0.4,
            "nitrogen_efficiency": 0.3,
            "ammoniacal_nitrogen_efficiency": 0.15,
            "phosphorus_efficiency": 0.4,
            "potassium_efficiency": 0.15,
            "ash_efficiency": 0.2,
        },
        "screw_press": {
            "name": "screw_press",
            "type": "ScrewPress",
            "separated_solids_dry_matter": 0.35,
            "total_solids_efficiency": 0.25,
            "volatile_solids_efficiency": 0.3,
            "nitrogen_efficiency": 0.3,
            "ammoniacal_nitrogen_efficiency": 0.1,
            "phosphorus_efficiency": 0.2,
            "potassium_efficiency": 0.23,
            "ash_efficiency": 0.2,
        },
        "slurry_storage_outdoor": {
            "name": "slurry_storage_outdoor",
            "type": "SlurryStorageOutdoor",
            "capacity": None,
            "cover": "no cover",
            "storage_time_period": 120,
            "surface_area": None,
        },
        "slurry_storage_underfloor": {
            "name": "slurry_storage_underfloor",
            "type": "SlurryStorageUnderfloor",
            "capacity": None,
            "cover": "cover",
            "storage_time_period": 120,
            "surface_area": None,
        },
        "anaerobic_lagoon": {
            "name": "anaerobic_lagoon",
            "type": "AnaerobicLagoon",
            "capacity": None,
            "cover": "no cover",
            "storage_time_period": 365,
            "surface_area": None,
        },
        "alley_scraper": {
            "name": "alley_scraper",
            "type": "AlleyScraper",
            "handler_type": "AlleyScraper",
            "cleaning_water_use_amount": 0.0,
            "cleaning_water_recycle_fraction": 0.8,
            "use_parlor_flush": False,
        },
        "manual_scraper": {
            "name": "manual_scraper",
            "type": "ManualScraper",
            "handler_type": "ManualScraper",
            "cleaning_water_use_amount": 0.0,
            "cleaning_water_recycle_fraction": 0.8,
            "use_parlor_flush": False,
        },
        "flush_system": {
            "name": "flush_system",
            "type": "FlushSystem",
            "handler_type": "FlushSystem",
            "cleaning_water_use_amount": 0.0,
            "cleaning_water_recycle_fraction": 0.8,
            "use_parlor_flush": False,
        },
        "parlor_cleaning_handler": {
            "name": "parlor_cleaning_handler",
            "type": "ParlorCleaningHandler",
            "handler_type": "ParlorCleaningHandler",
            "cleaning_water_use_amount": 0.0,
            "cleaning_water_recycle_fraction": 0.8,
            "use_parlor_flush": True,
        },
    }


@pytest.fixture
def expected_processor_connections_by_name() -> dict[str, dict[str, list[dict[str, Any]]]]:
    return {
        "alley_scraper": {
            "destinations": [
                {"proportion": 0.5, "receiving_processor_name": "rotary_screen"},
                {"proportion": 0.5, "receiving_processor_name": "anaerobic_digester"},
            ]
        },
        "anaerobic_digester": {
            "destinations": [
                {"proportion": 0.93, "receiving_processor_name": "flush_system"},
                {"proportion": 0.07, "receiving_processor_name": "screw_press"},
            ]
        },
        "anaerobic_lagoon": {"destinations": []},
        "continuous_mix": {"destinations": [{"proportion": 1.0, "receiving_processor_name": "slurry_storage_outdoor"}]},
        "flush_system": {
            "destinations": [
                {"proportion": 0.1, "receiving_processor_name": "screw_press"},
                {"proportion": 0.8, "receiving_processor_name": "parlor_cleaning_handler"},
                {"proportion": 0.1, "receiving_processor_name": "slurry_storage_outdoor"},
            ]
        },
        "parlor_cleaning_handler": {
            "destinations": [
                {"proportion": 0.18, "receiving_processor_name": "continuous_mix"},
                {"proportion": 0.68, "receiving_processor_name": "anaerobic_lagoon"},
                {"proportion": 0.14, "receiving_processor_name": "slurry_storage_outdoor"},
            ]
        },
        "rotary_screen": {
            "liquid_output_destinations": [{"proportion": 1.0, "receiving_processor_name": "anaerobic_lagoon"}],
            "solid_output_destinations": [{"proportion": 1.0, "receiving_processor_name": "slurry_storage_outdoor"}],
        },
        "screw_press": {
            "liquid_output_destinations": [{"proportion": 1.0, "receiving_processor_name": "anaerobic_lagoon"}],
            "solid_output_destinations": [
                {"proportion": 0.2, "receiving_processor_name": "slurry_storage_outdoor"},
                {"proportion": 0.8, "receiving_processor_name": "continuous_mix"},
            ],
        },
        "slurry_storage_outdoor": {"destinations": []},
    }


@pytest.fixture
def expected_all_processor_connections() -> list[dict[str, Any]]:
    return [
        {
            "processor_name": "alley_scraper",
            "destinations": [
                {"receiving_processor_name": "rotary_screen", "proportion": 0.5},
                {"receiving_processor_name": "anaerobic_digester", "proportion": 0.5},
            ],
        },
        {
            "processor_name": "flush_system",
            "destinations": [
                {"receiving_processor_name": "screw_press", "proportion": 0.1},
                {"receiving_processor_name": "parlor_cleaning_handler", "proportion": 0.8},
                {"receiving_processor_name": "slurry_storage_outdoor", "proportion": 0.1},
            ],
        },
        {
            "processor_name": "parlor_cleaning_handler",
            "destinations": [
                {"receiving_processor_name": "continuous_mix", "proportion": 0.18},
                {"receiving_processor_name": "anaerobic_lagoon", "proportion": 0.68},
                {"receiving_processor_name": "slurry_storage_outdoor", "proportion": 0.14},
            ],
        },
        {
            "processor_name": "anaerobic_digester",
            "destinations": [
                {"receiving_processor_name": "flush_system", "proportion": 0.93},
                {"receiving_processor_name": "screw_press", "proportion": 0.07},
            ],
        },
        {
            "processor_name": "continuous_mix",
            "destinations": [{"receiving_processor_name": "slurry_storage_outdoor", "proportion": 1.0}],
        },
        {"processor_name": "anaerobic_lagoon", "destinations": []},
        {"processor_name": "slurry_storage_outdoor", "destinations": []},
        {
            "processor_name": "rotary_screen",
            "liquid_output_destinations": [{"receiving_processor_name": "anaerobic_lagoon", "proportion": 1.0}],
            "solid_output_destinations": [{"receiving_processor_name": "slurry_storage_outdoor", "proportion": 1.0}],
        },
        {
            "processor_name": "screw_press",
            "liquid_output_destinations": [{"receiving_processor_name": "anaerobic_lagoon", "proportion": 1.0}],
            "solid_output_destinations": [
                {"receiving_processor_name": "slurry_storage_outdoor", "proportion": 0.2},
                {"receiving_processor_name": "continuous_mix", "proportion": 0.8},
            ],
        },
    ]


@pytest.fixture
def expected_adjacency_matrix_keys() -> list[str]:
    return ['alley_scraper', 'flush_system', 'parlor_cleaning_handler', 'anaerobic_digester', 'continuous_mix',
            'anaerobic_lagoon', 'slurry_storage_outdoor', 'rotary_screen_input', 'rotary_screen_solid_output',
            'rotary_screen_liquid_output', 'screw_press_input', 'screw_press_solid_output', 'screw_press_liquid_output']
