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


def _make_base_animal_config(repro_sub_protocol: str, heifer_repro_method: str) -> dict[str, Any]:
    """Builds the ``animal_config`` blob that ``AnimalConfig.initialize_animal_config()`` reads."""
    return {
        "management_decisions": {
            "breeding_start_day_h": 380,
            "heifer_repro_method": heifer_repro_method,
            "cow_repro_method": "TAI",
            "semen_type": "conventional",
            "days_in_preg_when_dry": 218,
            "heifer_repro_cull_time": 500,
            "calf_mortality_rate": 0,
            "heifer_mortality_rate": 0,
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
                "calf_retention_method": "rate",
                "annual_keep_female_calf_num": 0,
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
                    "repro_sub_protocol": repro_sub_protocol,
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
                "parity_death_prob": [0.039, 0.056, 0.085, 0.117],
                "parity_acute_sale_prob": [0.169, 0.233, 0.301, 0.408],
            },
            "life_cycle": {"still_birth_rate": 0.065},
        },
    }


@pytest.mark.parametrize(
    "heifer_method, repro_sub_protocol, expected_subprogram_type",
    [
        ("TAI", "5dCG2P", HeiferTAISubProtocol),  # if branch
        ("SynchED", "2P", HeiferSynchEDSubProtocol),  # elif branch
        ("ED", "5dCG2P", HeiferTAISubProtocol),  # else fallback to default TAI subprogram
    ],
    ids=["heifer_tai", "heifer_synched", "heifer_other_fallback"],
)
def test_initialize_animal_config_heifer_subprogram_and_core_fields(
    mocker: pytest_mock.MockerFixture,
    heifer_method: str,
    repro_sub_protocol: str,
    expected_subprogram_type: type,
) -> None:
    mock_im_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.InputManager")
    mock_om_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.OutputManager")

    mock_im = mock_im_cls.return_value
    mock_om = mock_om_cls.return_value

    base_animal_config = _make_base_animal_config(repro_sub_protocol, heifer_method)

    animal_data = {
        "animal_config": base_animal_config,
        "methane_model": {"dummy": "model"},
        "methane_mitigation": {
            "methane_mitigation_method": "None",
        },
        "herd_information": {"simulate_genetics": False},
    }

    def get_data_side_effect(key: str) -> Any:
        if key == "animal":
            return animal_data
        if key == "feed.ration_formulation_parameters.milk_reduction_maximum":
            return 1.23
        if key == "animal_mean_phenotype":
            return {}
        if key == "animal_top_listing_semen":
            return {}
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


@pytest.mark.parametrize(
    "methane_mitigation_method, expected_additive_amount",
    [
        ("None", 0.0),
        ("3-NOP", 90),
        ("Monensin", 30),
        ("Essential Oils", 50),
        ("Seaweed", 55),
        ("Unrecognized Additive", 0.0),
    ],
    ids=["none", "3nop", "monensin", "essential_oils", "seaweed", "unrecognized"],
)
def test_initialize_animal_config_selects_dose_of_chosen_mitigation_method(
    mocker: pytest_mock.MockerFixture,
    methane_mitigation_method: str,
    expected_additive_amount: float,
) -> None:
    """The dose fed to the mitigation equations comes from the selected method's own field."""
    mock_im_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.InputManager")
    mocker.patch("RUFAS.biophysical.animal.animal_config.OutputManager")

    mock_im = mock_im_cls.return_value

    animal_data = {
        "animal_config": _make_base_animal_config("5dCG2P", "TAI"),
        "methane_model": {"dummy": "model"},
        "methane_mitigation": {
            "methane_mitigation_method": methane_mitigation_method,
            "3-NOP_additive_amount": 90,
            "monensin_additive_amount": 30,
            "essential_oils_additive_amount": 50,
            "seaweed_additive_amount": 55,
        },
        "herd_information": {"simulate_genetics": False},
    }

    def get_data_side_effect(key: str) -> Any:
        if key == "animal":
            return animal_data
        if key == "feed.ration_formulation_parameters.milk_reduction_maximum":
            return 1.23
        if key in ("animal_mean_phenotype", "animal_top_listing_semen"):
            return {}
        raise KeyError(key)

    mock_im.get_data.side_effect = get_data_side_effect

    AnimalConfig.initialize_animal_config()

    assert AnimalConfig.methane_mitigation_method == methane_mitigation_method
    assert AnimalConfig.methane_mitigation_additive_amount == expected_additive_amount


def test_initialize_animal_config_warns_when_selected_mitigation_dose_field_is_missing(
    mocker: pytest_mock.MockerFixture,
) -> None:
    """A recognized method whose dose field is absent falls back to 0 and warns rather than raising."""
    mock_im_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.InputManager")
    mock_om_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.OutputManager")

    mock_im = mock_im_cls.return_value
    mock_om = mock_om_cls.return_value

    animal_data = {
        "animal_config": _make_base_animal_config("5dCG2P", "TAI"),
        "methane_model": {"dummy": "model"},
        # "3-NOP" is selected, but "3-NOP_additive_amount" is absent from the blob.
        "methane_mitigation": {"methane_mitigation_method": "3-NOP"},
        "herd_information": {"simulate_genetics": False},
    }

    def get_data_side_effect(key: str) -> Any:
        if key == "animal":
            return animal_data
        if key == "feed.ration_formulation_parameters.milk_reduction_maximum":
            return 1.23
        if key in ("animal_mean_phenotype", "animal_top_listing_semen"):
            return {}
        raise KeyError(key)

    mock_im.get_data.side_effect = get_data_side_effect

    AnimalConfig.initialize_animal_config()

    assert AnimalConfig.methane_mitigation_additive_amount == 0.0

    mock_om.add_warning.assert_called_once()
    warning_args, _ = mock_om.add_warning.call_args
    assert "Missing methane mitigation additive dose" in warning_args[0]
    assert "3-NOP_additive_amount" in warning_args[1]


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
            "calf_mortality_rate": 0,
            "heifer_mortality_rate": 0,
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
                "calf_retention_method": "rate",
                "annual_keep_female_calf_num": 0,
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
                "parity_death_prob": [0.039, 0.056, 0.085, 0.117],
                "parity_acute_sale_prob": [0.169, 0.233, 0.301, 0.408],
            },
            "life_cycle": {"still_birth_rate": 0.065},
        },
    }

    animal_data = {
        "animal_config": animal_config,
        "methane_model": {"cow": {"lactating": "IPCC"}},
        "methane_mitigation": {
            "methane_mitigation_method": "None",
        },
        "herd_information": {"simulate_genetics": False},
    }

    def get_data_side_effect(key: str) -> Any:
        if key == "animal":
            return animal_data
        elif key == "feed.ration_formulation_parameters.milk_reduction_maximum":
            return 2.5
        if key == "animal_mean_phenotype":
            return {}
        if key == "animal_top_listing_semen":
            return {}
        raise KeyError(key)

    mock_im.get_data.side_effect = get_data_side_effect

    AnimalConfig.initialize_animal_config()

    assert AnimalConfig.milk_reduction_maximum == 2.5

    mock_om.add_warning.assert_called_once()
    warning_args, warning_kwargs = mock_om.add_warning.call_args

    assert "3rd pregnancy check day >=" in warning_args[0]
