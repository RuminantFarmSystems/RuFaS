from __future__ import annotations

from typing import List

import pytest
from mock import MagicMock
from pytest import approx
from pytest_lazyfixture import lazy_fixture
from pytest_mock import MockerFixture

from RUFAS.routines.animal.animal_types import AnimalType
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration.animal_requirements import AnimalRequirements


@pytest.fixture
def cow_a() -> dict:
    cow_a_dict = {
        "body_weight": 600,
        "mature_body_weight": 700,
        "day_of_pregnancy": 30,
        "animal_type": AnimalType.LAC_COW,
        "parity": 1,
        "calving_interval": 365,
        "milk_protein": 3.45,
        "Fat_Milk": 4,
        "Lactose_Milk": 4.9,
        "Milk": 30,
        "DIM": 120,
        "lactating": True,
        "BCS5": 3,
        "PrevTemp": None,
        "ADG_heifer": None,
        "daily_growth": None,
        "age": 1000,
        "distance": None,
        "NDF_conc": 0.3,
        "TDN_conc": 0.7,
        "net_energy_diet_concentration": 1.0,
        "days_born": 1000,
        "conceptus_weight": 22,
        "calf_birth_weight": 40,
        "net_energy_growth": 3,
        "average_daily_gain": 1,
        "equivalent_shrunk_body_weight": 220,
        "dry_matter_intake_estimate": 24,
    }
    return cow_a_dict


@pytest.fixture
def cow_b() -> dict:
    cow_b_dict = {
        "body_weight": 680,
        "mature_body_weight": 700,
        "day_of_pregnancy": 150,
        "animal_type": AnimalType.DRY_COW,
        "parity": 3,
        "calving_interval": 365,
        "milk_protein": 3.45,
        "Fat_Milk": 4,
        "Lactose_Milk": 4.9,
        "Milk": 25,
        "DIM": 240,
        "lactating": False,
        "BCS5": 3,
        "PrevTemp": None,
        "ADG_heifer": None,
        "daily_growth": None,
        "age": 1000,
        "distance": None,
        "NDF_conc": 0.3,
        "TDN_conc": 0.7,
        "net_energy_diet_concentration": 1.0,
        "days_born": 1000,
        "conceptus_weight": 0,
        "calf_birth_weight": 0,
        "net_energy_growth": 3,
        "average_daily_gain": 1,
        "equivalent_shrunk_body_weight": 0,
        "dry_matter_intake_estimate": 24,
    }
    return cow_b_dict


@pytest.fixture
def cow_c() -> dict:
    cow_c_dict = {
        "body_weight": 680,
        "mature_body_weight": 700,
        "day_of_pregnancy": 191,
        "animal_type": AnimalType.DRY_COW,
        "parity": 2,
        "calving_interval": 365,
        "milk_protein": 3.45,
        "Fat_Milk": 4,
        "Lactose_Milk": 4.9,
        "Milk": 25,
        "DIM": 240,
        "lactating": False,
        "BCS5": 3,
        "PrevTemp": None,
        "ADG_heifer": None,
        "daily_growth": None,
        "age": 1000,
        "distance": None,
        "NDF_conc": 0.3,
        "TDN_conc": 0.7,
        "net_energy_diet_concentration": 1.0,
        "days_born": 1000,
        "conceptus_weight": 0,
        "calf_birth_weight": 0,
        "net_energy_growth": 3,
        "average_daily_gain": 0,
        "equivalent_shrunk_body_weight": 479,
        "dry_matter_intake_estimate": 24,
    }
    return cow_c_dict


@pytest.fixture
def cow_d() -> dict:
    cow_d_dict = {
        "body_weight": 680,
        "mature_body_weight": 700,
        "day_of_pregnancy": 191,
        "animal_type": "dummy",
        "parity": 2,
        "calving_interval": 365,
        "milk_protein": 3.45,
        "Fat_Milk": 4,
        "Lactose_Milk": 4.9,
        "Milk": 25,
        "DIM": 240,
        "lactating": False,
        "BCS5": 3,
        "PrevTemp": None,
        "ADG_heifer": None,
        "daily_growth": None,
        "age": 1000,
        "distance": None,
        "NDF_conc": 0.3,
        "TDN_conc": 0.7,
        "net_energy_diet_concentration": 1.0,
        "days_born": 1000,
        "conceptus_weight": 0,
        "calf_birth_weight": 0,
        "net_energy_growth": 3,
        "average_daily_gain": 0,
        "equivalent_shrunk_body_weight": 479,
        "dry_matter_intake_estimate": 24,
    }
    return cow_d_dict


@pytest.fixture
def heifer_a() -> dict:
    heifer_a_dict = {
        "body_weight": 230,
        "mature_body_weight": 700,
        "day_of_pregnancy": None,
        "animal_type": AnimalType.HEIFER_I,
        "parity": 0,
        "calving_interval": None,
        "milk_protein": 0.0,
        "Fat_Milk": 0.0,
        "Lactose_Milk": 0.0,
        "Milk": 0.0,
        "DIM": None,
        "lactating": False,
        "BCS5": 3,
        "PrevTemp": 15,
        "ADG_heifer": 0.65,
        "daily_growth": None,
        "age": 210,
        "distance": None,
        "NDF_conc": 0.0,
        "TDN_conc": 0.0,
        "net_energy_diet_concentration": 0.0,
        "days_born": 100,
        "conceptus_weight": 22,
        "calf_birth_weight": 40,
        "net_energy_growth": 3,
        "average_daily_gain": 1,
        "equivalent_shrunk_body_weight": 220,
        "dry_matter_intake_estimate": 12,
    }
    return heifer_a_dict


@pytest.fixture
def heifer_b() -> dict:
    heifer_b_dict = {
        "body_weight": 340,
        "mature_body_weight": 700,
        "day_of_pregnancy": 1,
        "animal_type": AnimalType.HEIFER_I,
        "parity": 0,
        "calving_interval": None,
        "milk_protein": 0.0,
        "Fat_Milk": 0.0,
        "Lactose_Milk": 0.0,
        "Milk": 0.0,
        "DIM": None,
        "lactating": False,
        "BCS5": 3,
        "PrevTemp": 15,
        "ADG_heifer": 0.9,
        "daily_growth": None,
        "age": 365,
        "distance": None,
        "NDF_conc": 0.3,
        "TDN_conc": 0.7,
        "net_energy_diet_concentration": 1.0,
        "days_born": 400,
        "conceptus_weight": 0,
        "calf_birth_weight": 0,
        "net_energy_growth": 3,
        "average_daily_gain": 1,
        "equivalent_shrunk_body_weight": 0,
        "dry_matter_intake_estimate": 12,
    }
    return heifer_b_dict


def test_default_initialization() -> None:
    """
    Test the default initialization of the AnimalRequirements class.

    This test checks that when a AnimalRequirements object is instantiated without
    any parameters, all its attributes are correctly set to their default values.

    """

    # Act
    animal_requirements = AnimalRequirements()

    # Assert
    assert animal_requirements.NEmaint_requirement == 0
    assert animal_requirements.NEa_requirement == 0
    assert animal_requirements.NEg_requirement == 0
    assert animal_requirements.NEpreg_requirement == 0
    assert animal_requirements.NEl_requirement == 0
    assert animal_requirements.MP_requirement == 0
    assert animal_requirements.Ca_requirement == 0
    assert animal_requirements.P_requirement == 0
    assert animal_requirements.DMIest_requirement == 0
    assert animal_requirements.avg_BW == 0
    assert animal_requirements.avg_milk == 0
    assert animal_requirements.avg_CP_milk == 0
    assert animal_requirements.avg_milk_production_reduction is None


@pytest.mark.parametrize(
    "argument_lists, stat_method, expected",
    [
        (
            [
                [9, 10, 12, 13, 13, 13, 15, 15, 16, 16, 18, 22, 23, 24, 24, 25],
                [1, 8, 23, 29, 44, 82, 88, 99],
                [1, 4, 21, 29, 29, 74, 78, 82, 82, 84],
                [9, 45, 48, 65, 72, 73, 82, 91],
                [18, 37, 45, 47, 59, 74, 82, 87],
                [18, 27, 29, 39, 49, 64, 72, 72, 74, 84],
                [27, 29, 37, 53, 65, 71, 72, 84, 89, 93],
                [12, 17, 18, 19, 27, 34, 43, 54, 77, 81, 82, 83, 83, 91],
                [
                    24,
                    27,
                    28,
                    32,
                    34,
                    39,
                    54,
                    56,
                    57,
                    71,
                    74,
                    74,
                    75,
                    78,
                    79,
                    83,
                    88,
                    91,
                    91,
                    92,
                ],
                [17, 45, 71, 71, 72, 73, 73, 74, 74, 82, 83, 92, 92, 93, 98],
                [1, 1, 1, 2, 2, 2, 4, 4, 4, 5, 5, 7, 2003],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1, 4, 4, 4, 4, 4, 4, 4],
            ],
            "mean",
            [
                16.75,
                46.75,
                48.4,
                60.625,
                56.125,
                52.8,
                62.0,
                51.5,
                62.35,
                74.0,
                157.0,
                1.0,
                3.625,
            ],
        ),
        (
            [
                [9, 10, 12, 13, 13, 13, 15, 15, 16, 16, 18, 22, 23, 24, 24, 25],
                [1, 8, 23, 29, 44, 82, 88, 99],
                [1, 4, 21, 29, 29, 74, 78, 82, 82, 84],
                [9, 45, 48, 65, 72, 73, 82, 91],
                [18, 37, 45, 47, 59, 74, 82, 87],
                [18, 27, 29, 39, 49, 64, 72, 72, 74, 84],
                [27, 29, 37, 53, 65, 71, 72, 84, 89, 93],
                [12, 17, 18, 19, 27, 34, 43, 54, 77, 81, 82, 83, 83, 91],
                [
                    24,
                    27,
                    28,
                    32,
                    34,
                    39,
                    54,
                    56,
                    57,
                    71,
                    74,
                    74,
                    75,
                    78,
                    79,
                    83,
                    88,
                    91,
                    91,
                    92,
                ],
                [17, 45, 71, 71, 72, 73, 73, 74, 74, 82, 83, 92, 92, 93, 98],
                [1, 1, 1, 2, 2, 2, 4, 4, 4, 5, 5, 7, 2003],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1, 4, 4, 4, 4, 4, 4, 4],
            ],
            "median",
            [15.5, 36.5, 51.5, 68.5, 53.0, 56.5, 68.0, 48.5, 72.5, 74.0, 4.0, 1.0, 4.0],
        ),
        (
            [
                [9, 10, 12, 13, 13, 13, 15, 15, 16, 16, 18, 22, 23, 24, 24, 25],
                [1, 8, 23, 29, 44, 82, 88, 99],
                [1, 4, 21, 29, 29, 74, 78, 82, 82, 84],
                [9, 45, 48, 65, 72, 73, 82, 91],
                [18, 37, 45, 47, 59, 74, 82, 87],
                [18, 27, 29, 39, 49, 64, 72, 72, 74, 84],
                [27, 29, 37, 53, 65, 71, 72, 84, 89, 93],
                [12, 17, 18, 19, 27, 34, 43, 54, 77, 81, 82, 83, 83, 91],
                [
                    24,
                    27,
                    28,
                    32,
                    34,
                    39,
                    54,
                    56,
                    57,
                    71,
                    74,
                    74,
                    75,
                    78,
                    79,
                    83,
                    88,
                    91,
                    91,
                    92,
                ],
                [17, 45, 71, 71, 72, 73, 73, 74, 74, 82, 83, 92, 92, 93, 98],
                [1, 1, 1, 2, 2, 2, 4, 4, 4, 5, 5, 7, 2003],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1, 4, 4, 4, 4, 4, 4, 4],
            ],
            "percentile",
            [24.0, 91.3, 82.2, 84.7, 83.5, 75.0, 89.4, 83.0, 91.0, 92.6, 6.6, 1.0, 4.0],
        ),
        (
            [
                [12, 52, 71, 71, 72, 72, 73, 74, 81, 81, 82, 83, 84],
                [18, 37, 62, 65, 71, 72, 73, 74, 74, 81, 82, 92],
                [4, 12, 12, 23, 23, 23, 45, 54, 64, 72, 75, 81, 82, 91],
                [1, 12, 13, 34, 43, 45, 53, 82, 93],
                [12, 12, 23, 34, 48, 71, 74, 74, 81, 82, 82, 83, 91],
                [27, 28, 34, 34, 37, 56, 56, 64, 65, 73, 73, 75, 78],
                [12, 12, 27, 34, 43, 46, 47, 56, 64, 73, 73, 75, 98],
                [13, 23, 23, 32, 34, 34, 34, 43, 65, 67, 75, 78, 87, 88, 89, 97],
                [12, 12, 23, 34, 34, 51, 54, 56, 73, 74, 75, 78, 82, 86, 92, 94],
                [91, 20, 72, 19, 28, 47, 48, 95, 72, 56, 26, 78],
                [9, 12, 20, 23, 29, 34, 45, 45, 45, 49, 62, 63, 71, 76, 79, 83, 98],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [5, 5, 5, 5, 5, 5, 5, 5, 5, 19, 19, 19],
            ],
            "mean",
            [
                69.846,
                66.75,
                47.214,
                41.778,
                59.0,
                53.846,
                50.769,
                55.125,
                58.125,
                54.333,
                49.588,
                1.0,
                8.5,
            ],
        ),
        (
            [
                [12, 52, 71, 71, 72, 72, 73, 74, 81, 81, 82, 83, 84],
                [18, 37, 62, 65, 71, 72, 73, 74, 74, 81, 82, 92],
                [4, 12, 12, 23, 23, 23, 45, 54, 64, 72, 75, 81, 82, 91],
                [1, 12, 13, 34, 43, 45, 53, 82, 93],
                [12, 12, 23, 34, 48, 71, 74, 74, 81, 82, 82, 83, 91],
                [27, 28, 34, 34, 37, 56, 56, 64, 65, 73, 73, 75, 78],
                [12, 12, 27, 34, 43, 46, 47, 56, 64, 73, 73, 75, 98],
                [13, 23, 23, 32, 34, 34, 34, 43, 65, 67, 75, 78, 87, 88, 89, 97],
                [12, 12, 23, 34, 34, 51, 54, 56, 73, 74, 75, 78, 82, 86, 92, 94],
                [91, 20, 72, 19, 28, 47, 48, 95, 72, 56, 26, 78],
                [9, 12, 20, 23, 29, 34, 45, 45, 45, 49, 62, 63, 71, 76, 79, 83, 98],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [5, 5, 5, 5, 5, 5, 5, 5, 5, 19, 19, 19],
            ],
            "median",
            [
                73.0,
                72.5,
                49.5,
                43.0,
                74.0,
                56.0,
                47.0,
                54.0,
                64.5,
                52.0,
                45.0,
                1.0,
                5.0,
            ],
        ),
        (
            [
                [12, 52, 71, 71, 72, 72, 73, 74, 81, 81, 82, 83, 84],
                [18, 37, 62, 65, 71, 72, 73, 74, 74, 81, 82, 92],
                [4, 12, 12, 23, 23, 23, 45, 54, 64, 72, 75, 81, 82, 91],
                [1, 12, 13, 34, 43, 45, 53, 82, 93],
                [12, 12, 23, 34, 48, 71, 74, 74, 81, 82, 82, 83, 91],
                [27, 28, 34, 34, 37, 56, 56, 64, 65, 73, 73, 75, 78],
                [12, 12, 27, 34, 43, 46, 47, 56, 64, 73, 73, 75, 98],
                [13, 23, 23, 32, 34, 34, 34, 43, 65, 67, 75, 78, 87, 88, 89, 97],
                [12, 12, 23, 34, 34, 51, 54, 56, 73, 74, 75, 78, 82, 86, 92, 94],
                [91, 20, 72, 19, 28, 47, 48, 95, 72, 56, 26, 78],
                [9, 12, 20, 23, 29, 34, 45, 45, 45, 49, 62, 63, 71, 76, 79, 83, 98],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [5, 5, 5, 5, 5, 5, 5, 5, 5, 19, 19, 19],
            ],
            "percentile",
            [
                82.8,
                81.9,
                81.7,
                84.2,
                82.8,
                74.6,
                74.6,
                88.5,
                89.0,
                89.7,
                80.6,
                1.0,
                19.0,
            ],
        ),
        (
            [
                [55, 72, 84, 59, 35, 8, 48, 33, 47, 9],
                [16, 10, 99, 64, 73, 33, 24, 45, 1, 95, 43, 68],
                [61, 24, 17, 17, 94, 57, 76, 12, 90, 94, 46, 80, 87, 69, 76],
                [85, 19, 24, 82, 1, 54, 48, 84, 45, 28, 16],
                [29, 88, 95, 52, 73, 98, 59, 28, 45],
                [96, 65, 47, 98, 3, 72, 80, 74, 3, 96, 33, 6, 54, 88, 12],
                [8, 92, 42, 14, 31, 70, 30, 62, 24, 25, 26, 10, 56],
                [29, 31, 88, 42, 9, 27, 13, 42, 8, 99, 42, 97, 55, 16],
                [55, 25, 97, 17, 47, 54, 69, 70, 73, 59],
                [24, 79, 27, 91, 47, 77, 23, 34, 5, 47, 87, 5, 98, 58, 8, 42, 1],
                [14, 53, 63, 62, 76, 56, 91, 34, 25, 57, 68, 59, 4, 77],
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            ],
            "mean",
            [
                45.0,
                47.583,
                60.0,
                44.182,
                63.0,
                55.133,
                37.692,
                42.714,
                56.6,
                44.294,
                52.786,
                5.5,
                5.0,
            ],
        ),
        (
            [
                [55, 72, 84, 59, 35, 8, 48, 33, 47, 9],
                [16, 10, 99, 64, 73, 33, 24, 45, 1, 95, 43, 68],
                [61, 24, 17, 17, 94, 57, 76, 12, 90, 94, 46, 80, 87, 69, 76],
                [85, 19, 24, 82, 1, 54, 48, 84, 45, 28, 16],
                [29, 88, 95, 52, 73, 98, 59, 28, 45],
                [96, 65, 47, 98, 3, 72, 80, 74, 3, 96, 33, 6, 54, 88, 12],
                [8, 92, 42, 14, 31, 70, 30, 62, 24, 25, 26, 10, 56],
                [29, 31, 88, 42, 9, 27, 13, 42, 8, 99, 42, 97, 55, 16],
                [55, 25, 97, 17, 47, 54, 69, 70, 73, 59],
                [24, 79, 27, 91, 47, 77, 23, 34, 5, 47, 87, 5, 98, 58, 8, 42, 1],
                [14, 53, 63, 62, 76, 56, 91, 34, 25, 57, 68, 59, 4, 77],
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            ],
            "median",
            [
                47.5,
                44.0,
                69.0,
                45.0,
                59.0,
                65.0,
                30.0,
                36.5,
                57.0,
                42.0,
                58.0,
                5.5,
                5.0,
            ],
        ),
        (
            [
                [55, 72, 84, 59, 35, 8, 48, 33, 47, 9],
                [16, 10, 99, 64, 73, 33, 24, 45, 1, 95, 43, 68],
                [61, 24, 17, 17, 94, 57, 76, 12, 90, 94, 46, 80, 87, 69, 76],
                [85, 19, 24, 82, 1, 54, 48, 84, 45, 28, 16],
                [29, 88, 95, 52, 73, 98, 59, 28, 45],
                [96, 65, 47, 98, 3, 72, 80, 74, 3, 96, 33, 6, 54, 88, 12],
                [8, 92, 42, 14, 31, 70, 30, 62, 24, 25, 26, 10, 56],
                [29, 31, 88, 42, 9, 27, 13, 42, 8, 99, 42, 97, 55, 16],
                [55, 25, 97, 17, 47, 54, 69, 70, 73, 59],
                [24, 79, 27, 91, 47, 77, 23, 34, 5, 47, 87, 5, 98, 58, 8, 42, 1],
                [14, 53, 63, 62, 76, 56, 91, 34, 25, 57, 68, 59, 4, 77],
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            ],
            "percentile",
            [
                73.2,
                92.8,
                92.4,
                84.0,
                95.6,
                96.0,
                68.4,
                94.3,
                75.4,
                88.6,
                76.7,
                9.1,
                5.0,
            ],
        ),
    ],
)
def test_calc_pen_requirements(
    argument_lists: List[List[float]], stat_method: str, expected: List[float]
) -> None:
    """
    Test the calc_pen_requirement() method across varying statistical methods within the AnimalRequirements class.

    This test checks that when a calc_pen_requirements() function is called, the correct value is set for a pen's
    requirement based on some list of cow values and a statistical method.

    """
    animal_requirements = AnimalRequirements()
    animal_requirements.calc_pen_requirements(*argument_lists, stat_method)

    attr_list = [
        "NEmaint_requirement",
        "NEa_requirement",
        "NEg_requirement",
        "NEpreg_requirement",
        "NEl_requirement",
        "MP_requirement",
        "Ca_requirement",
        "P_requirement",
        "DMIest_requirement",
        "avg_BW",
        "avg_milk",
        "avg_CP_milk",
        "avg_milk_production_reduction",
    ]

    for attr_name, statistic in zip(attr_list, expected):
        assert getattr(animal_requirements, attr_name) == approx(statistic, abs=0.001)


def test_set_requirements(mocker: MockerFixture) -> None:
    """Unit test for function set_requirements in file routines/animal/ration/animal_requirements.py"""

    pen = MagicMock()
    animal_grouping_scenario = MagicMock()
    test_obj = AnimalRequirements()
    test_obj.recalculate_requirements = MagicMock(
        return_value={
            "NEmaint_requirement": [1, 2],
            "NEa_requirement": [2, 3],
            "NEg_requirement": [3, 4],
            "NEpreg_requirement": [
                4,
            ],
            "NEl_requirement": [
                5,
            ],
            "MP_requirement": [
                6,
            ],
            "Ca_requirement": [
                7,
            ],
            "P_requirement": [
                8,
            ],
            "DMIest_requirement": [
                9,
            ],
            "BW": [
                10,
            ],
            "milk": [
                11,
            ],
            "milk_production_reduction": [
                12,
            ],
            "CP_milk": [
                13,
            ],
        },
    )
    test_obj.use_existing_requirements = MagicMock(
        return_value={
            "NEmaint_requirement": [2, 2],
            "NEa_requirement": [3, 3],
            "NEg_requirement": [4, 4],
            "NEpreg_requirement": [5, 5],
            "NEl_requirement": [6, 6],
            "MP_requirement": [7, 7],
            "Ca_requirement": [8, 8],
            "P_requirement": [9, 9],
            "DMIest_requirement": [10, 10],
            "BW": [11, 11],
            "milk": [12, 12],
            "milk_production_reduction": [13, 13],
            "CP_milk": [14, 14],
        }
    )
    test_obj.calc_pen_requirements = MagicMock()

    recalc = True
    test_obj.set_requirements(pen, animal_grouping_scenario, recalc)
    test_obj.recalculate_requirements.assert_called_once()
    test_obj.calc_pen_requirements.assert_called_once()
    pen.set_milk_avgs.assert_called_once()
    pen.set_avg_nutrient_rqmts.assert_called_once()

    recalc = False
    test_obj.set_requirements(pen, animal_grouping_scenario, recalc)
    test_obj.use_existing_requirements.assert_called_once()


def test_recalculate_requirements() -> None:
    pen_mock = MagicMock()
    pen_mock.animals_in_pen = {
        0: MagicMock(),
        1: MagicMock(),
        2: MagicMock(),
        3: MagicMock(),
        4: MagicMock(),
    }
    animal_list = list(pen_mock.animals_in_pen.values())
    for i in range(0, 5):
        animal_list[i].NEmaint_requirement = i
        animal_list[i].NEg_requirement = i
        animal_list[i].NEpreg_requirement = i
        animal_list[i].NEl_requirement = i
        animal_list[i].MP_requirement = i
        animal_list[i].Ca_requirement = i
        animal_list[i].P_requirement = i
        animal_list[i].DMIest_requirement = i
        animal_list[i].body_weight = i
        animal_list[i].estimated_daily_milk_produced = i
        animal_list[i].milk_production_reduction = i
        animal_list[i].CP_milk = i
        pen_mock.animals_in_list[i].calc_daily_walking_dist = MagicMock()

    animal_grouping_scenario_mock = MagicMock()
    animal_grouping_scenario_mock.get_animal_type = MagicMock(
        side_effect=[
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.DRY_COW,
            AnimalType.LAC_COW,
        ]
    )

    requirements_lists_empty = {
        "NEmaint_requirement": [],
        "NEa_requirement": [],
        "NEg_requirement": [],
        "NEpreg_requirement": [],
        "NEl_requirement": [],
        "MP_requirement": [],
        "Ca_requirement": [],
        "P_requirement": [],
        "DMIest_requirement": [],
        "BW": [],
        "milk": [],
        "milk_production_reduction": [],
        "CP_milk": [],
    }
    requirements_list_expected = {
        "NEmaint_requirement": [1, 1, 1, 1, 1],
        "NEa_requirement": [0, 0, 0, 0, 100],
        "NEg_requirement": [1, 1, 1, 1, 1],
        "NEpreg_requirement": [1, 1, 1, 1, 1],
        "NEl_requirement": [1, 1, 1, 1, 1],
        "MP_requirement": [1, 1, 1, 1, 1],
        "Ca_requirement": [1, 1, 1, 1, 1],
        "P_requirement": [1, 1, 1, 1, 1],
        "DMIest_requirement": [1, 1, 1, 1, 1],
        "BW": [0, 1, 2, 3, 4],
        "milk": [4],
        "milk_production_reduction": [4],
        "CP_milk": [4],
    }

    requirements_mock = AnimalRequirements()
    requirements_mock.energy_activity_rqmts = MagicMock(return_value=100)
    requirements_mock.calc_rqmts = MagicMock(
        return_value={
            "NEmaint_requirement": 1,
            "NEa_requirement": 1,
            "NEg_requirement": 1,
            "NEpreg_requirement": 1,
            "NEl_requirement": 1,
            "MP_requirement": 1,
            "Ca_requirement": 1,
            "P_requirement": 1,
            "DMIest_requirement": 1,
        }
    )

    requirements_lists_actual = requirements_mock.recalculate_requirements(
        pen_mock, animal_grouping_scenario_mock, requirements_lists_empty
    )

    # Assertions
    requirements_mock.energy_activity_rqmts.assert_called_once()
    assert requirements_list_expected == requirements_lists_actual
    assert animal_list[-1].DNED_requirement == 2
    assert animal_list[-1].DMDP_requirement == 1


def test_use_existing_requirements() -> None:
    """Unit test for function use_existing_requirements() in file routines/animal/ration/animal_requirements.py"""

    pen_mock = MagicMock()
    pen_mock.animals_in_pen = {0: MagicMock(), 1: MagicMock()}
    animal_list = list(pen_mock.animals_in_pen.values())
    for i in range(0, 2):
        animal_list[i].NEmaint_requirement = i
        animal_list[i].NEg_requirement = i
        animal_list[i].NEpreg_requirement = i
        animal_list[i].NEl_requirement = i
        animal_list[i].MP_requirement = i
        animal_list[i].Ca_requirement = i
        animal_list[i].P_requirement = i
        animal_list[i].DMIest_requirement = i
        animal_list[i].body_weight = i
        animal_list[i].estimated_daily_milk_produced = i
        animal_list[i].milk_production_reduction = i
        animal_list[i].CP_milk = i
        pen_mock.animals_in_list[i].calc_daily_walking_dist = MagicMock()

    animal_grouping_scenario_mock = MagicMock()
    animal_grouping_scenario_mock.get_animal_type = MagicMock(
        side_effect=[AnimalType.HEIFER_I, AnimalType.LAC_COW]
    )

    requirements_lists_empty = {
        "NEmaint_requirement": [],
        "NEa_requirement": [],
        "NEg_requirement": [],
        "NEpreg_requirement": [],
        "NEl_requirement": [],
        "MP_requirement": [],
        "Ca_requirement": [],
        "P_requirement": [],
        "DMIest_requirement": [],
        "BW": [],
        "milk": [],
        "milk_production_reduction": [],
        "CP_milk": [],
    }
    requirements_list_expected = {
        "NEmaint_requirement": [0, 1],
        "NEa_requirement": [0, 1],
        "NEg_requirement": [0, 1],
        "NEpreg_requirement": [0, 1],
        "NEl_requirement": [0, 1],
        "MP_requirement": [0, 1],
        "Ca_requirement": [0, 1],
        "P_requirement": [0, 1],
        "DMIest_requirement": [0, 1],
        "BW": [0, 1],
        "milk": [1],
        "milk_production_reduction": [1],
        "CP_milk": [1],
    }

    requirements_mock = AnimalRequirements()
    requirements_mock.energy_activity_rqmts = MagicMock(return_value=i)

    requirements_lists_actual = requirements_mock.use_existing_requirements(
        pen_mock, animal_grouping_scenario_mock, requirements_lists_empty
    )

    # Assertions
    requirements_mock.energy_activity_rqmts.assert_called_once()
    assert requirements_list_expected == requirements_lists_actual
    # pen_mock.animals_in_list[1].calc_daily_walking_dist.assert_called_once()


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), (9.7, 0, 43.92)),
        (lazy_fixture("cow_b"), (10.65, 0, 43.92)),
        (lazy_fixture("cow_c"), (10.65, 18.22, 43.92)),
        (lazy_fixture("heifer_a"), (5.08, 0, 0)),
        (lazy_fixture("heifer_b"), (6.81, 0, 43.92)),
    ],
)
def test_calculate_NRC_energy_maintenance_requirements(
    animal_dict: dict, expected: tuple
) -> None:
    """Unit test for function calculate_NRC_energy_maintenance_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    (
        result_NEmaint,
        result_CW,
        result_CBW,
    ) = req.calculate_NRC_energy_maintenance_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        animal_dict["day_of_pregnancy"],
        animal_dict["BCS5"],
        animal_dict["PrevTemp"],
        animal_dict["animal_type"],
    )
    assert (result_NEmaint, result_CW, result_CBW) == pytest.approx(expected, rel=5e-1)


@pytest.mark.parametrize(
    "animal_dict, conceptus_weight, expectedvalues",
    [
        (lazy_fixture("cow_a"), 22, (0.77, 0.1841, 394.065)),
        (lazy_fixture("cow_b"), 0, (0.0, 0, 464.343)),
        (lazy_fixture("cow_c"), 0, (0.68, 0.147, 464.343)),
        (lazy_fixture("heifer_a"), 0, (1.533, 0.65, 157.057)),
        (lazy_fixture("heifer_b"), 0, (2.937, 0.9, 232.171)),
    ],
)
def test_calculate_NRC_energy_growth_requirements(
    animal_dict: dict, conceptus_weight: float, expectedvalues: tuple
) -> None:
    """Unit test for function calculate_NRC_energy_growth_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_NEg, result_ADG, result_EQSBW = req.calculate_NRC_energy_growth_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        conceptus_weight,
        animal_dict["animal_type"],
        animal_dict["parity"],
        animal_dict["calving_interval"],
        animal_dict["ADG_heifer"],
    )
    assert (result_NEg, result_ADG, result_EQSBW) == pytest.approx(
        expectedvalues, rel=1e-2
    )


@pytest.mark.parametrize(
    "animal_dict, calf_birth_weight, expected",
    [
        (lazy_fixture("cow_a"), 40, 0),
        (lazy_fixture("cow_b"), 40, 0),
        (lazy_fixture("cow_c"), 40, 2.33),
        (lazy_fixture("heifer_a"), 0, 0),
        (lazy_fixture("heifer_b"), 40, 0),
    ],
)
def test_calculate_NRC_energy_pregnancy_requirements(
    animal_dict: dict, calf_birth_weight: float, expected: float
):
    req = AnimalRequirements()
    result_NEpreg = req.calculate_NRC_energy_pregnancy_requirements(
        animal_dict["day_of_pregnancy"], calf_birth_weight
    )
    assert (result_NEpreg) == pytest.approx((expected), rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), 23),
        (lazy_fixture("cow_b"), 0.0),
        (lazy_fixture("heifer_a"), 0.0),
        (lazy_fixture("heifer_b"), 0.0),
    ],
)
def test_calculate_NRC_energy_lactation_requirements(
    animal_dict: dict, expected: float
) -> None:
    """Unit test for function calculate_NRC_energy_lactation_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_NEl = req.calculate_NRC_energy_lactation_requirements(
        animal_dict["animal_type"],
        animal_dict["Fat_Milk"],
        animal_dict["milk_protein"],
        animal_dict["Lactose_Milk"],
        animal_dict["Milk"],
    )
    assert (result_NEl) == pytest.approx((expected), rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, TDNconc, expected",
    [
        (lazy_fixture("cow_a"), 0.7, 2340),
        (lazy_fixture("cow_b"), 0.6, 786.12),
        (lazy_fixture("cow_c"), 0.6, 570.5),
        (lazy_fixture("heifer_a"), 0.7, 562),
        (lazy_fixture("heifer_b"), 0.7, 489),
        (lazy_fixture("heifer_b"), 0.5, 562.1),
    ],
)
def test_calculate_NRC_protein_requirements(
    animal_dict: dict, TDNconc: float, expected: float
) -> None:
    """Unit test for function calculate_NRC_protein_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_MP_req = req.calculate_NRC_protein_requirements(
        animal_dict["body_weight"],
        animal_dict["conceptus_weight"],
        animal_dict["day_of_pregnancy"],
        animal_dict["animal_type"],
        animal_dict["Milk"],
        animal_dict["milk_protein"],
        animal_dict["calf_birth_weight"],
        animal_dict["net_energy_growth"],
        animal_dict["average_daily_gain"],
        animal_dict["equivalent_shrunk_body_weight"],
        animal_dict["dry_matter_intake_estimate"],
        TDNconc,
    )
    assert (result_MP_req) == pytest.approx((expected), rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), 66),
        (lazy_fixture("cow_b"), 21.32),
        (lazy_fixture("cow_c"), 23.7),
        (lazy_fixture("heifer_a"), 16.806),
        (lazy_fixture("heifer_b"), 17.5),
    ],
)
def test_calculate_NRC_calcium_requirements(animal_dict: dict, expected: float) -> None:
    """Unit test for function calculate_NRC_calcium_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_Ca_req = req.calculate_NRC_calcium_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        animal_dict["day_of_pregnancy"],
        animal_dict["animal_type"],
        1,
        animal_dict["Milk"],
    )
    assert (result_Ca_req) == pytest.approx((expected), rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), 59),
        (lazy_fixture("cow_b"), 26.67),
        (lazy_fixture("cow_c"), 22.36),
        (lazy_fixture("heifer_a"), 17.47),
        (lazy_fixture("heifer_b"), 17.18),
    ],
)
def test_calculate_NRC_phosphorus_requirements(
    animal_dict: dict, expected: float
) -> None:
    """Unit test for function calculate_NRC_phosophorus_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_P_req = req.calculate_NRC_phosphorus_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        animal_dict["day_of_pregnancy"],
        animal_dict["Milk"],
        animal_dict["animal_type"],
        animal_dict["average_daily_gain"],
        animal_dict["dry_matter_intake_estimate"],
    )
    assert (result_P_req) == pytest.approx((expected), rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), 22.5),
        (lazy_fixture("cow_b"), 13.4),
        (lazy_fixture("cow_c"), 13.4),
        (lazy_fixture("heifer_a"), 6.36),
        (lazy_fixture("heifer_b"), 6.7),
    ],
)
def test_calculate_NRC_DMI(animal_dict: dict, expected: float) -> None:
    """Unit test for function calculate_NRC_DMI in file routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_DMIest = req.calculate_NRC_DMI(
        animal_dict["animal_type"],
        animal_dict["body_weight"],
        animal_dict["day_of_pregnancy"],
        animal_dict["DIM"],
        animal_dict["Milk"],
        animal_dict["Fat_Milk"],
        animal_dict["net_energy_diet_concentration"],
        animal_dict["days_born"],
    )
    assert (result_DMIest) == pytest.approx((expected), rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), 23),
        (lazy_fixture("cow_b"), 0.0),
        (lazy_fixture("heifer_a"), 0.0),
        (lazy_fixture("heifer_b"), 0.0),
    ],
)
def test_calculate_NASEM_energy_lactation_requirements(
    animal_dict: dict, expected: float
) -> None:
    """Unit test for function calculate_NASEM_energy_lactation_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_NEl = req.calculate_NASEM_energy_lactation_requirements(
        animal_dict["animal_type"],
        animal_dict["Fat_Milk"],
        animal_dict["milk_protein"],
        animal_dict["Lactose_Milk"],
        animal_dict["Milk"],
    )
    assert (result_NEl) == pytest.approx((expected), rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, lactating, net_energy_lactation, expected",
    [
        (lazy_fixture("cow_a"), True, 15, 19.4),
        (lazy_fixture("cow_b"), False, 15, 16),
        (lazy_fixture("cow_b"), True, 15, 21.26),
        (lazy_fixture("heifer_a"), False, 15, 9.19),
        (lazy_fixture("heifer_b"), False, 15, 11.5),
    ],
)
def test_calculate_NASEM_DMI(
    animal_dict: dict, lactating: bool, net_energy_lactation: float, expected: float
) -> None:
    """Unit test for function calculate_NASEM_DMI in file routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_DMIest = req.calculate_NASEM_DMI(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        animal_dict["DIM"],
        lactating,
        net_energy_lactation,
        animal_dict["parity"],
        animal_dict["BCS5"],
        animal_dict["NDF_conc"],
    )
    assert (result_DMIest) == pytest.approx((expected), rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), (11.12, 65.11, 0.204)),
        (lazy_fixture("cow_b"), (12.59, 48.52, 0.204)),
        (lazy_fixture("heifer_a"), (5.9, 0, 0)),
        (lazy_fixture("heifer_b"), (6.3, 77.71, 10.05)),
    ],
)
def test_calculate_NASEM_energy_maintenance_requirements(
    animal_dict: dict, expected: tuple
) -> None:
    """Unit test for function calculate_NASEM_energy_maintenance_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    (
        result_NEmaint,
        result_GrUterW,
        result_UterW,
    ) = req.calculate_NASEM_energy_maintenance_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        animal_dict["day_of_pregnancy"],
        animal_dict["DIM"],
    )
    assert (result_NEmaint, result_GrUterW, result_UterW) == pytest.approx(
        expected, rel=1e-2
    )


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), (1.12, 0.1841, 0.44)),
        (lazy_fixture("cow_b"), (0.0, 0.00001, 0.0)),
        (lazy_fixture("cow_c"), (0.97, 0.1472, 0.4705)),
        (lazy_fixture("cow_d"), (0.0, 0.00001, 0.0)),
        (lazy_fixture("heifer_a"), (2.5, 0.65, 0.31)),
        (lazy_fixture("heifer_b"), (4.1, 0.9, 0.35)),
    ],
)
def test_calculate_NASEM_energy_growth_requirements(
    animal_dict: dict, expected: tuple
) -> None:
    """Unit test for function calculate_NASEM_energy_growth_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    (
        result_NEg,
        result_ADG,
        result_frame_weight_gain,
    ) = req.calculate_NASEM_energy_growth_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        animal_dict["ADG_heifer"],
        animal_dict["animal_type"],
        animal_dict["parity"],
        animal_dict["calving_interval"],
    )
    assert (result_NEg, result_ADG, result_frame_weight_gain) == pytest.approx(
        expected, rel=1e-2
    )


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), (0.4, 0.096)),
        (lazy_fixture("cow_b"), (4.2, 1.01)),
        (lazy_fixture("heifer_a"), (0, 0)),
        (lazy_fixture("heifer_b"), (4.9, 1.2)),
    ],
)
def test_calculate_NASEM_energy_pregnancy_requirements(
    animal_dict: dict, expected: tuple
) -> None:
    """Unit test for function calculate_NASEM_energy_pregnancy_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    (
        result_NEpreg,
        result_GrUterWGain,
    ) = req.calculate_NASEM_energy_pregnancy_requirements(
        animal_dict["lactating"],
        animal_dict["day_of_pregnancy"],
        animal_dict["DIM"],
        49,
        0.2,
    )
    assert (result_NEpreg, result_GrUterWGain) == pytest.approx(expected, rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, frame_w_gain, gruter_w_gain, expected",
    [
        (lazy_fixture("cow_a"), 1, 0.1, 2044.23),
        (lazy_fixture("cow_b"), 1, 1, 912.7),
        (lazy_fixture("heifer_a"), 1, 1, 609.2),
        (lazy_fixture("heifer_b"), 1, 1, 647.8),
    ],
)
def test_calculate_NASEM_protein_requirements(
    animal_dict: dict, frame_w_gain: float, gruter_w_gain: float, expected: float
) -> None:
    """Unit test for function calculate_NASEM_protein_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_MP_req = req.calculate_NASEM_protein_requirements(
        animal_dict["lactating"],
        animal_dict["body_weight"],
        frame_w_gain,
        gruter_w_gain,
        animal_dict["dry_matter_intake_estimate"],
        animal_dict["milk_protein"],
        animal_dict["Milk"],
        animal_dict["NDF_conc"],
    )
    assert (result_MP_req) == pytest.approx(expected, rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), 55.78),
        (lazy_fixture("cow_b"), 51.38),
        (lazy_fixture("heifer_a"), 11.5),
        (lazy_fixture("heifer_b"), 11.45),
    ],
)
def test_calculate_NASEM_calcium_requirements(
    animal_dict: dict, expected: float
) -> None:
    """Unit test for function calculate_NASEM_calcium_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_Ca_req = req.calculate_NASEM_calcium_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        animal_dict["day_of_pregnancy"],
        animal_dict["average_daily_gain"],
        animal_dict["dry_matter_intake_estimate"],
        animal_dict["milk_protein"],
        animal_dict["Milk"],
        animal_dict["parity"],
    )
    assert (result_Ca_req) == pytest.approx((expected), rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), 59.28),
        (lazy_fixture("cow_b"), 33.18),
        (lazy_fixture("cow_d"), 0.0),
        (lazy_fixture("heifer_a"), 16.85),
        (lazy_fixture("heifer_b"), 16.44),
    ],
)
def test_calculate_NASEM_phosphorus_requirements(
    animal_dict: dict, expected: float
) -> None:
    """Unit test for function calculate_NASEM_phosphorus_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_P_req = req.calculate_NASEM_phosphorus_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        animal_dict["animal_type"],
        animal_dict["day_of_pregnancy"],
        animal_dict["average_daily_gain"],
        animal_dict["dry_matter_intake_estimate"],
        animal_dict["milk_protein"],
        animal_dict["Milk"],
        animal_dict["parity"],
    )
    assert (result_P_req) == pytest.approx((expected), rel=1e-2)


def test_calc_rqmts():
    """Unit test for function calc_rqmts in file routines/animal/ration/animal_requirements.py"""
    test_requirements = AnimalRequirements()
    test_requirements.calculate_NRC_energy_maintenance_requirements = MagicMock(
        return_value=(1, 2, 3)
    )
    test_requirements.calculate_NRC_energy_growth_requirements = MagicMock(
        return_value=(1, 2, 3)
    )
    test_requirements.calculate_NRC_energy_pregnancy_requirements = MagicMock(
        return_value=1
    )
    test_requirements.calculate_NRC_energy_lactation_requirements = MagicMock(
        return_value=1
    )
    test_requirements.calculate_NRC_DMI = MagicMock(return_value=1)
    test_requirements.calculate_NRC_protein_requirements = MagicMock(return_value=1)
    test_requirements.calculate_NRC_calcium_requirements = MagicMock(return_value=1)
    test_requirements.calculate_NRC_phosphorus_requirements = MagicMock(return_value=1)
    test_requirements.calculate_NASEM_energy_maintenance_requirements = MagicMock(
        return_value=(4, 5, 6)
    )
    test_requirements.calculate_NASEM_energy_growth_requirements = MagicMock(
        return_value=(4, 5, 6)
    )
    test_requirements.calculate_NASEM_energy_pregnancy_requirements = MagicMock(
        return_value=(4, 5)
    )
    test_requirements.calculate_NASEM_energy_lactation_requirements = MagicMock(
        return_value=2
    )
    test_requirements.calculate_NASEM_DMI = MagicMock(return_value=2)
    test_requirements.calculate_NASEM_protein_requirements = MagicMock(return_value=2)
    test_requirements.calculate_NASEM_calcium_requirements = MagicMock(return_value=2)
    test_requirements.calculate_NASEM_phosphorus_requirements = MagicMock(
        return_value=2
    )
    AnimalBase.config["nutrient_standard"] = "NRC"
    test_requirements.AnimalBase = AnimalBase
    actual = test_requirements.calc_rqmts(
        MagicMock(), MagicMock(), MagicMock(), MagicMock()
    )
    expected = {
        "NEmaint_requirement": 1,
        "NEg_requirement": 1,
        "NEpreg_requirement": 1,
        "NEl_requirement": 1,
        "MP_requirement": 1,
        "Ca_requirement": 1,
        "P_requirement": 1,
        "DMIest_requirement": 1,
    }
    assert actual == expected
    test_requirements.calculate_NRC_energy_maintenance_requirements.assert_called_once()
    test_requirements.calculate_NRC_energy_growth_requirements.assert_called_once()
    test_requirements.calculate_NRC_energy_pregnancy_requirements.assert_called_once()
    test_requirements.calculate_NRC_energy_lactation_requirements.assert_called_once()
    test_requirements.calculate_NRC_DMI.assert_called_once()
    test_requirements.calculate_NRC_protein_requirements.assert_called_once()
    test_requirements.calculate_NRC_calcium_requirements.assert_called_once()
    test_requirements.calculate_NRC_phosphorus_requirements.assert_called_once()

    expected = {
        "NEmaint_requirement": 2,
        "NEg_requirement": 2,
        "NEpreg_requirement": 2,
        "NEl_requirement": 2,
        "MP_requirement": 2,
        "Ca_requirement": 2,
        "P_requirement": 2,
        "DMIest_requirement": 2,
    }
    AnimalBase.config["nutrient_standard"] = "NASEM"
    actual = test_requirements.calc_rqmts(
        MagicMock(), MagicMock(), MagicMock(), MagicMock()
    )
    test_requirements.calculate_NASEM_energy_maintenance_requirements.assert_called_once()
    test_requirements.calculate_NASEM_energy_growth_requirements.assert_called_once()
    test_requirements.calculate_NASEM_energy_pregnancy_requirements.assert_called_once()
    test_requirements.calculate_NASEM_energy_lactation_requirements.assert_called_once()
    test_requirements.calculate_NASEM_DMI.assert_called_once()
    test_requirements.calculate_NASEM_protein_requirements.assert_called_once()
    test_requirements.calculate_NASEM_calcium_requirements.assert_called_once()
    test_requirements.calculate_NASEM_phosphorus_requirements.assert_called_once()


def test_energy_activity_rqmts():
    """Unit test for function energy_activity_rqmts in file routines/animal/ration/animal_requirements.py"""
    AnimalBase.config["nutrient_standard"] = "NASEM"
    req = AnimalRequirements()
    result_energy_activity = req.energy_activity_rqmts(
        body_weight=400, housing="Grazing", distance=1
    )
    assert (result_energy_activity) == pytest.approx((294), rel=1e-2)

    result_energy_activity = req.energy_activity_rqmts(
        body_weight=400, housing="Not_Grazing", distance=1
    )
    assert (result_energy_activity) == pytest.approx((0), rel=1e-2)

    AnimalBase.config["nutrient_standard"] = "NRC"

    result_energy_activity = req.energy_activity_rqmts(
        body_weight=400, housing="Barn", distance=1
    )
    assert (result_energy_activity) == pytest.approx((0.18), rel=1e-2)

    result_energy_activity = req.energy_activity_rqmts(
        body_weight=400, housing="Grazing", distance=1
    )
    assert (result_energy_activity) == pytest.approx((0.66), rel=1e-2)

    result_energy_activity = req.energy_activity_rqmts(
        body_weight=400, housing="n e i t h e r", distance=1
    )
    assert (result_energy_activity) == pytest.approx((0.18), rel=1e-2)
