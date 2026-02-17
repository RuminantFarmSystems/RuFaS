from collections.abc import Generator
import types
from typing import Any
import pytest
import pytest_mock

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    HeiferTAISubProtocol,
    HeiferSynchEDSubProtocol,
    CowReproductionProtocol,
    CowPreSynchSubProtocol,
    CowTAISubProtocol,
    CowReSynchSubProtocol,
)


@pytest.fixture(autouse=True)
def reset_animal_config_state() -> Generator[None, None, None]:
    """
    Snapshot AnimalConfig's non-callable class attributes before each test
    and restore them afterwards, so tests that call initialize_animal_config()
    don't leak global state into the rest of the suite.
    """
    original_attrs = {
        name: value
        for name, value in AnimalConfig.__dict__.items()
        if not name.startswith("__") and not isinstance(value, (types.FunctionType, classmethod, staticmethod))
    }
    original_names = set(original_attrs.keys())

    yield

    for name, value in list(AnimalConfig.__dict__.items()):
        if name.startswith("__"):
            continue
        if isinstance(value, (types.FunctionType, classmethod, staticmethod)):
            continue
        if name not in original_names:
            delattr(AnimalConfig, name)

    for name, value in original_attrs.items():
        setattr(AnimalConfig, name, value)


@pytest.mark.parametrize(
    "heifer_method, expected_subprogram_type",
    [
        ("TAI", HeiferTAISubProtocol),  # if branch
        ("SynchED", HeiferSynchEDSubProtocol),  # elif branch
        ("ED", HeiferTAISubProtocol),  # else fallback to default TAI subprogram
    ],
    ids=["heifer_tai", "heifer_synched", "heifer_other_fallback"],
)
def test_initialize_animal_config_heifer_subprogram_and_core_fields(
    mocker: pytest_mock.MockerFixture,
    heifer_method: str,
    expected_subprogram_type: type,
) -> None:
    mock_im_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.InputManager")
    mock_om_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.OutputManager")

    mock_im = mock_im_cls.return_value
    mock_om = mock_om_cls.return_value

    base_animal_config = {
        "management_decisions": {
            "breeding_start_day_h": 380,
            "heifer_repro_method": "SynchED",
            "cow_repro_method": "TAI",
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
                    "repro_sub_protocol": "2P",
                    "repro_sub_properties": {
                        "conception_rate": 0.6,
                        "estrus_detection_rate": 0.9,
                    },
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
    }

    base_animal_config["management_decisions"]["heifer_repro_method"] = heifer_method

    animal_data = {
        "animal_config": base_animal_config,
        "methane_model": {"dummy": "model"},
        "methane_mitigation": {
            "methane_mitigation_method": "None",
            "methane_mitigation_additive_amount": 0.0,
        },
    }

    def get_data_side_effect(key: str) -> Any:
        if key == "animal":
            return animal_data
        if key == "feed.milk_reduction_maximum":
            return 1.23
        raise KeyError(key)

    mock_im.get_data.side_effect = get_data_side_effect

    AnimalConfig.initialize_animal_config()

    assert AnimalConfig.wean_day == 60
    assert AnimalConfig.wean_length == 7
    assert AnimalConfig.semen_type == "conventional"
    assert AnimalConfig.milk_fat_percent == 4
    assert AnimalConfig.milk_reduction_maximum == 1.23

    assert AnimalConfig.heifer_reproduction_program == HeiferReproductionProtocol(heifer_method)
    assert isinstance(AnimalConfig.heifer_reproduction_sub_program, expected_subprogram_type)

    assert AnimalConfig.cow_reproduction_program == CowReproductionProtocol("TAI")
    assert AnimalConfig.cow_presynch_method == CowPreSynchSubProtocol("Double OvSynch")
    assert AnimalConfig.cow_tai_method == CowTAISubProtocol("OvSynch 56")
    assert AnimalConfig.cow_ovsynch_method == CowTAISubProtocol("OvSynch 56")
    assert AnimalConfig.cow_resynch_method == CowReSynchSubProtocol("TAIafterPD")

    mock_om.add_warning.assert_not_called()


def test_initialize_animal_config_adds_warning_when_third_check_after_or_on_dryoff(
    mocker: pytest_mock.MockerFixture,
) -> None:
    mock_im_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.InputManager")
    mock_om_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.OutputManager")

    mock_im = mock_im_cls.return_value
    mock_om = mock_om_cls.return_value

    animal_config = {
        "management_decisions": {
            "breeding_start_day_h": 380,
            "heifer_repro_method": "SynchED",
            "cow_repro_method": "TAI",
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
                    "repro_sub_protocol": "2P",
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
                "preg_check_day_3": 250,
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
    }

    animal_data = {
        "animal_config": animal_config,
        "methane_model": {"cow": {"lactating": "IPCC"}},
        "methane_mitigation": {
            "methane_mitigation_method": "None",
            "methane_mitigation_additive_amount": 0.0,
        },
    }

    def get_data_side_effect(key: str) -> Any:
        if key == "animal":
            return animal_data
        elif key == "feed.milk_reduction_maximum":
            return 2.5
        raise KeyError(key)

    mock_im.get_data.side_effect = get_data_side_effect

    AnimalConfig.initialize_animal_config()

    assert AnimalConfig.milk_reduction_maximum == 2.5

    mock_om.add_warning.assert_called_once()
    warning_args, warning_kwargs = mock_om.add_warning.call_args

    assert "3rd pregnancy check day >=" in warning_args[0]
