import pytest
import numpy as np
from typing import Any, Dict
from unittest.mock import patch
from mock import MagicMock
from pytest_mock import MockerFixture

from pytest_lazyfixture import lazy_fixture
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents

from RUFAS.routines.animal.animal_types import AnimalType

from RUFAS.routines.animal.ration.animal_requirements import AnimalRequirements
from RUFAS.routines.animal.ration.ration_driver import AvailableFeeds
from RUFAS.routines.animal.ration.ration_driver import RationManager
from RUFAS.routines.animal.ration.ration_driver import RationReporter

from RUFAS.routines.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.routines.animal.ration.user_defined_ration import UserDefinedRationManager

import RUFAS.routines.animal.clustering_pen_grouping


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


def test_set_requirements(mocker: MockerFixture):
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
        }
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
    pen_mock.animals_in_pen = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    for i in range(0, 5):
        pen_mock.animals_in_pen[i].NEmaint_requirement = i
        pen_mock.animals_in_pen[i].NEg_requirement = i
        pen_mock.animals_in_pen[i].NEpreg_requirement = i
        pen_mock.animals_in_pen[i].NEl_requirement = i
        pen_mock.animals_in_pen[i].MP_requirement = i
        pen_mock.animals_in_pen[i].Ca_requirement = i
        pen_mock.animals_in_pen[i].P_requirement = i
        pen_mock.animals_in_pen[i].DMIest_requirement = i
        pen_mock.animals_in_pen[i].body_weight = i
        pen_mock.animals_in_pen[i].estimated_daily_milk_produced = i
        pen_mock.animals_in_pen[i].milk_production_reduction = i
        pen_mock.animals_in_pen[i].CP_milk = i
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
    assert pen_mock.animals_in_pen[-1].DNED_requirement == 2
    assert pen_mock.animals_in_pen[-1].DMDP_requirement == 1


def test_use_existing_requirements() -> None:
    pen_mock = MagicMock()
    pen_mock.animals_in_pen = [MagicMock(), MagicMock()]
    for i in range(0, 2):
        pen_mock.animals_in_pen[i].NEmaint_requirement = i
        pen_mock.animals_in_pen[i].NEg_requirement = i
        pen_mock.animals_in_pen[i].NEpreg_requirement = i
        pen_mock.animals_in_pen[i].NEl_requirement = i
        pen_mock.animals_in_pen[i].MP_requirement = i
        pen_mock.animals_in_pen[i].Ca_requirement = i
        pen_mock.animals_in_pen[i].P_requirement = i
        pen_mock.animals_in_pen[i].DMIest_requirement = i
        pen_mock.animals_in_pen[i].body_weight = i
        pen_mock.animals_in_pen[i].estimated_daily_milk_produced = i
        pen_mock.animals_in_pen[i].milk_production_reduction = i
        pen_mock.animals_in_pen[i].CP_milk = i
        pen_mock.animals_in_list[i].calc_daily_walking_dist = MagicMock()

    animal_grouping_scenario_mock = MagicMock()
    animal_grouping_scenario_mock.get_animal_type = MagicMock(side_effect=[AnimalType.HEIFER_I, AnimalType.LAC_COW])

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


@pytest.fixture
def mock_ration_config() -> MagicMock:
    ration_config = MagicMock()
    ration_config.price_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.n = 6
    ration_config.NEmaint_requirement = 1.0
    ration_config.NEa_requirement = 2.0
    ration_config.NEpreg_requirement = 3.0
    ration_config.NEl_requirement = 4.0
    ration_config.NEg_requirement = 5.0
    ration_config.MP_requirement = 6.0
    ration_config.C_requirement = 7.0
    ration_config.P_requirement = 8.0
    ration_config.TDN_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.DE_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.EE_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.is_fat_list = [True, True, True, False, False, False]
    ration_config.BW = 9.0
    ration_config.calcium_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.phosphorus_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.NDF_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.feed_type_list = ["Forage", "Conc", "Mineral", "Forage", "Conc", "Mineral"]
    ration_config.is_wetforage_list = [True, True, True, False, False, False]
    ration_config.Kd_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.N_A_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.N_B_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.CP_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.dRUP_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.feed_limit_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.lactating = True
    ration_config.DMIest_requirement = 10.0

    ration_config.NElact_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.MEact_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.NEgact_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.NEm_act_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.is_forage_list = [1, 1, 1, 0, 0, 0]
    ration_config.MPbact = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.RUP_diet = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.dP_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    ration_config.TDNact_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

    return ration_config


@pytest.fixture
def mock_random_ration_config() -> MagicMock:
    ration_config = MagicMock()
    ration_config.price_list = [2.615, 0.544, 3.847, 3.585, 2.881, 1.342]
    ration_config.n = 6
    ration_config.NEmaint_requirement = 1.423
    ration_config.NEa_requirement = 3.849
    ration_config.NEpreg_requirement = 2.223
    ration_config.NEl_requirement = 0.505
    ration_config.NEg_requirement = 3.375
    ration_config.MP_requirement = 2.207
    ration_config.C_requirement = 3.205
    ration_config.P_requirement = 1.17
    ration_config.TDN_list = [2.976, 0.19, 3.855, 4.415, 3.181, 4.065]
    ration_config.DE_list = [1.374, 4.783, 2.642, 4.42, 2.522, 2.397]
    ration_config.EE_list = [4.314, 4.227, 3.704, 4.897, 0.49, 1.59]
    ration_config.is_fat_list = [False, True, True, True, True, False]
    ration_config.BW = 2.227
    ration_config.calcium_list = [3.79, 4.242, 4.276, 0.676, 2.767, 0.907]
    ration_config.phosphorus_list = [3.275, 4.759, 0.653, 1.942, 0.914, 3.964]
    ration_config.NDF_list = [2.548, 2.382, 3.086, 4.709, 0.145, 3.554]
    ration_config.feed_type_list = ["Forage", "Conc", "Conc", "Conc", "Forage", "Mineral"]
    ration_config.is_wetforage_list = [False, True, False, False, True, True]
    ration_config.Kd_list = [2.548, 2.382, 3.086, 4.709, 0.145, 3.554]
    ration_config.N_A_list = [3.262, 2.552, 3.456, 2.377, 3.992, 4.561]
    ration_config.N_B_list = [3.453, 0.098, 2.109, 1.191, 4.602, 1.85]
    ration_config.CP_list = [3.489, 0.408, 4.415, 3.394, 2.497, 4.231]
    ration_config.dRUP_list = [2.281, 2.537, 2.186, 3.58, 1.436, 1.876]
    ration_config.feed_limit_list = [1.211, 0.908, 2.13, 3.851, 0.277, 4.266]
    ration_config.lactating = True
    ration_config.DMIest_requirement = 1.17

    ration_config.NElact_list = [4.433, 1.648, 3.986, 1.527, 4.815, 1.883]
    ration_config.MEact_list = [0.709, 1.781, 0.724, 3.533, 3.033, 4.017]
    ration_config.NEgact_list = [4.827, 0.161, 2.234, 2.955, 4.31, 3.584]
    ration_config.NEm_act_list = [3.757, 0.391, 0.259, 1.066, 0.782, 2.24]
    ration_config.is_forage_list = [3.053, 4.154, 2.636, 2.901, 2.095, 1.296]
    ration_config.MPbact = [2.47, 0.411, 1.933, 4.501, 2.679, 4.123]
    ration_config.RUP_diet = [1.124, 4.395, 4.673, 1.696, 1.469, 1.478]
    ration_config.dP_list = [4.678, 2.127, 4.902, 2.609, 3.125, 0.662]
    ration_config.TDNact_list = [3.249, 4.541, 0.663, 0.392, 1.745, 4.876]

    return ration_config


@pytest.fixture
def mock_ration_config_with_empty_NElact_list(mock_ration_config) -> MagicMock:
    mock_ration_config.NElact_list = np.empty(1)
    return mock_ration_config


@pytest.fixture
def mock_ration_config_with_empty_NEgact_list(mock_ration_config) -> MagicMock:
    mock_ration_config.NEgact_list = np.empty(1)
    return mock_ration_config


@pytest.fixture
def decision_vector() -> np.ndarray:
    return np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])


@pytest.fixture
def decision_vector_sum_zero() -> np.ndarray:
    return np.array([1.0, 2.0, 3.0, -3.0, -2.0 - 1.0])


@pytest.fixture
def mock_available_feeds() -> dict:
    available_feeds = dict()
    available_feeds["price"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["TDN"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["DE"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["EE"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["is_fat"] = [True, True, True, False, False, False]
    available_feeds["calcium"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["phosphorus"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["NDF"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["type"] = ["Forage", "Conc", "Mineral", "Forage", "Conc", "Mineral"]
    available_feeds["is_wetforage"] = [True, True, True, False, False, False]
    available_feeds["Kd"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["N_A"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["N_B"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["CP"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["dRUP"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    available_feeds["lactating_cow_limit"] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

    return available_feeds


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
def test_calculate_NRC_energy_maintenance_requirements(animal_dict: dict, expected: tuple) -> None:
    """Unit test for function calculate_NRC_energy_maintenance_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
    result_NEmaint, result_CW, result_CBW = req.calculate_NRC_energy_maintenance_requirements(
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
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
    result_NEg, result_ADG, result_EQSBW = req.calculate_NRC_energy_growth_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        conceptus_weight,
        animal_dict["animal_type"],
        animal_dict["parity"],
        animal_dict["calving_interval"],
        animal_dict["ADG_heifer"],
    )
    assert (result_NEg, result_ADG, result_EQSBW) == pytest.approx(expectedvalues, rel=1e-2)


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
def test_calculate_NRC_energy_pregnancy_requirements(animal_dict: dict, calf_birth_weight: float, expected: float):
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
    result_NEpreg = req.calculate_NRC_energy_pregnancy_requirements(animal_dict["day_of_pregnancy"], calf_birth_weight)
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
def test_calculate_NRC_energy_lactation_requirements(animal_dict: dict, expected: float) -> None:
    """Unit test for function calculate_NRC_energy_lactation_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
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
def test_calculate_NRC_protein_requirements(animal_dict: dict, TDNconc: float, expected: float) -> None:
    """Unit test for function calculate_NRC_protein_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
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
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
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
def test_calculate_NRC_phosphorus_requirements(animal_dict: dict, expected: float) -> None:
    """Unit test for function calculate_NRC_phosophorus_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
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
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
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
def test_calculate_NASEM_energy_lactation_requirements(animal_dict: dict, expected: float) -> None:
    """Unit test for function calculate_NASEM_energy_lactation_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
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
def test_calculate_NASEM_DMI(animal_dict: dict, lactating: bool, net_energy_lactation: float, expected: float) -> None:
    """Unit test for function calculate_NASEM_DMI in file routines/animal/ration/animal_requirements.py"""
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
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
        (lazy_fixture("heifer_b"), (6.3, 77.71, 10.25)),
    ],
)
def test_calculate_NASEM_energy_maintenance_requirements(animal_dict: dict, expected: tuple) -> None:
    """Unit test for function calculate_NASEM_energy_maintenance_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
    result_NEmaint, result_GrUterW, result_UterW = req.calculate_NASEM_energy_maintenance_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        animal_dict["day_of_pregnancy"],
        animal_dict["DIM"],
    )
    assert (result_NEmaint, result_GrUterW, result_UterW) == pytest.approx(expected, rel=1e-2)


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
def test_calculate_NASEM_energy_growth_requirements(animal_dict: dict, expected: tuple) -> None:
    """Unit test for function calculate_NASEM_energy_growth_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_NEg, result_ADG, result_frame_weight_gain = req.calculate_NASEM_energy_growth_requirements(
        animal_dict["body_weight"],
        animal_dict["mature_body_weight"],
        animal_dict["ADG_heifer"],
        animal_dict["animal_type"],
        animal_dict["parity"],
        animal_dict["calving_interval"],
    )
    assert (result_NEg, result_ADG, result_frame_weight_gain) == pytest.approx(expected, rel=1e-2)


@pytest.mark.parametrize(
    "animal_dict, expected",
    [
        (lazy_fixture("cow_a"), (0.4, 0.096)),
        (lazy_fixture("cow_b"), (4.2, 1.01)),
        (lazy_fixture("heifer_a"), (0, 0)),
        (lazy_fixture("heifer_b"), (4.9, 1.2)),
    ],
)
def test_calculate_NASEM_energy_pregnancy_requirements(animal_dict: dict, expected: tuple) -> None:
    """Unit test for function calculate_NASEM_energy_pregnancy_requirements in file
    routines/animal/ration/animal_requirements.py"""
    req = AnimalRequirements()
    result_NEpreg, result_GrUterWGain = req.calculate_NASEM_energy_pregnancy_requirements(
        animal_dict["lactating"], animal_dict["day_of_pregnancy"], animal_dict["DIM"], 49, 0.2
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
def test_calculate_NASEM_calcium_requirements(animal_dict: dict, expected: float) -> None:
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
def test_calculate_NASEM_phosphorus_requirements(animal_dict: dict, expected: float) -> None:
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


def test_norm():
    """Unit test for function norm in file routines/animal/clustering_pen_grouping.py"""

    def actual_func(act_func):
        return RUFAS.routines.animal.clustering_pen_grouping.norm(act_func)

    actual = actual_func([1, 2, 3])
    expected = np.array([0, 0.5, 1])
    assert actual.all() == expected.all()
    actual = actual_func([10.9, 120.1, 7])
    expected = np.array([0.03448276, 1, 0])
    assert actual.all() == expected.all()


def test_percentile_list():
    """Unit test for function percentile_list in file routines/animal/clustering_pen_grouping.py"""
    actual = RUFAS.routines.animal.clustering_pen_grouping.percentile_list([-2, 0, 4.7, 4.7])
    expected = [0.25, 0.5, 0.875, 0.875]
    assert actual == expected


def test_grouping():
    pass


def test_update_animals():
    """Unit test for function update_animals in file routines/animal/pen.py"""
    pass


def test_call_animal_nutrient_rqmts():
    """Unit test for function call_animal_nutrient_rqmts in file routines/animal/pen.py"""
    pass


def test_calc_avg_nutrient_rqmts():
    """Unit test for function calc_avg_nutrient_rqmts in file routines/animal/pen.py"""
    pass


def test_calc_manure():
    """Unit test for function calc_manure in file routines/animal/pen.py"""
    pass


def test_reset_manure():
    """Unit test for function reset_manure in file routines/animal/pen.py"""
    pass


def test_calc_avg_growth():
    """Unit test for function calc_avg_growth in file routines/animal/pen.py"""
    pass


def test_calc_daily_walking_dist():
    """Unit test for function calc_daily_walking_dist in file routines/animal/pen.py"""
    pass


def test_call_p_rqmts():
    """Unit test for function call_p_rqmts in file routines/animal/pen.py"""
    pass


def test_daily_pen_p_update():
    """Unit test for function daily_p_update in file routines/animal/pen.py"""
    pass


def test_set_up_new_animal():
    """Unit test for function set_up_new_animal in file routines/animal/pen.py"""
    pass


def test_clear():
    """Unit test for function clear in file routines/animal/pen.py"""
    pass


def test_set_nutrient_list():
    """Unit test for function set_nutrient_list in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_config():
    """Unit test for function set_config in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_default_nutrient_rqmts():
    """Unit test for function set_default_nutrient_rqmts in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_ration():
    """Unit test for function set_ration in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_p_intake():
    """Unit test for function set_p_intake in file routines/animal/life_cycle/animal_base.py"""
    pass


@pytest.fixture
def cow_fixture() -> AnimalBase:
    """simple AnimalBase fixture for use in animal tests"""
    initsetup = {
        "id": "1",
        "breed": "HO",
        "birth_date": "200",
        "days_born": "201",
        "semen_type": "conventional",
        "body_weight": 600,
        "pen_history": [],
    }
    AnimalBase.nutrients = {"dummy1": "dummyval1", "dummy2": "dummyval2"}
    AnimalBase.config = {"semen_type": "dummy"}
    cowfixture = AnimalBase(initsetup)
    return cowfixture


@pytest.mark.parametrize("dP_reserves,p_intake,p_req,expected", [(0, 1, 0, 0), (-10, 10, 1, -3.7), (10, 10, 1, 0)])
def test_daily_animal_p_update(dP_reserves, p_intake, p_req, expected, cow_fixture: AnimalBase) -> None:
    """Unit test for function daily_p_update in file routines/animal/life_cycle/animal_base.py"""
    cow_fixture.dP_reserves = dP_reserves
    cow_fixture.p_intake = p_intake
    cow_fixture.p_req = p_req
    cow_fixture.daily_p_update()
    assert cow_fixture.dP_reserves == expected


def test_calc_base_manure():
    """Unit test for function calc_base_manure in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_p_purchased():
    """Unit test for function set_p_purchased in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_update_pen_history(cow_fixture: AnimalBase) -> None:
    """Unit test for update_pen_history in file routines/animal/life_cycle/animal_base.py"""

    # Case 1
    # update hist with designated vals, using the time and the obj itself
    cow_fixture.update_pen_history(3, 2, ["Cow"])
    assert cow_fixture.pen_history[0].pen == 3
    assert cow_fixture.pen_history[-1].pen == 3
    assert cow_fixture.pen_history[-1].classes_in_pen == ["Cow"]
    assert cow_fixture.pen_history[-1].start_date == 2
    assert cow_fixture.pen_history[-1].end_date == 2

    # Case 2
    # check that it changes pens to 4
    cow_fixture.update_pen_history(4, 3, ["Cow"])
    # check previous history remains the same, then check newest
    assert cow_fixture.pen_history[0].pen == 3
    assert cow_fixture.pen_history[-1].pen == 4
    assert cow_fixture.pen_history[-1].classes_in_pen == ["Cow"]
    assert cow_fixture.pen_history[-1].start_date == 3
    assert cow_fixture.pen_history[-1].end_date == 3

    # Case 3
    # check that the start date remains the date of the change
    cow_fixture.update_pen_history(4, 4, ["Cow"])
    assert cow_fixture.pen_history[0].pen == 3
    assert cow_fixture.pen_history[-1].pen == 4
    assert cow_fixture.pen_history[-1].classes_in_pen == ["Cow"]
    assert cow_fixture.pen_history[-1].start_date == 3
    assert cow_fixture.pen_history[-1].end_date == 4


def test_update_body_weight_history(cow_fixture: AnimalBase) -> None:
    """Unit test for update_body_weight_history in file routines/animal/life_cycle/animal_base.py"""
    histories = [(1, 200, 650), (2, 300, 600), (3, 400, 550)]
    # use update function 3x
    for history in histories:
        sim_day = history[0]
        cow_fixture.days_born = history[1]
        cow_fixture.body_weight = history[2]
        cow_fixture.update_body_weight_history(sim_day)
    # asserts for each update
    for idx, history in enumerate(histories):
        assert cow_fixture.body_weight_history[idx].simulation_day == history[0]
        assert cow_fixture.body_weight_history[idx].days_born == history[1]
        assert cow_fixture.body_weight_history[idx].body_weight == history[2]


def test_init_from_string():
    """Unit test for function init_from_string in file routines/animal/life_cycle/animal_events.py"""
    A = AnimalEvents()
    A.init_from_string("3: simulation_day=0, event")
    assert A.events == {3: ["simulation_day=0, event"]}


def test_add_event() -> None:
    """Unit test for function add_event in file routines/animal/life_cycle/animal_events.py"""
    A = AnimalEvents()
    A.add_event(12, 212, "event1")
    A.add_event(12, 3, "event2")
    A.add_event(1, 345, "event3")
    assert A.events == {12: ["simulation_day=212", "event1", "event2"], 1: ["simulation_day=345", "event3"]}
    animal_event = AnimalEvents()
    # Case 0 check that no events are found
    assert animal_event.events == {}

    # Case 1: add an event
    animal_age = 100
    simulation_day = 200
    event_description = "dummy"
    animal_event.add_event(animal_age, simulation_day, event_description)
    assert animal_event.events[100] == ["simulation_day=200", "dummy"]

    # Case 2: another event on the next day
    animal_age = 101
    simulation_day = 201
    event_description = "dummy201"
    animal_event.add_event(animal_age, simulation_day, event_description)
    assert animal_event.events[101] == ["simulation_day=201", "dummy201"]

    # Case 3: another event on the first day
    animal_age = 100
    simulation_day = 200
    event_description = "dummy2"
    animal_event.add_event(animal_age, simulation_day, event_description)
    assert animal_event.events[100] == ["simulation_day=200", "dummy", "dummy2"]


def test___str__():
    """Unit test for function __str__ in file routines/animal/life_cycle/animal_events.py"""
    A = AnimalEvents()
    A.add_event(1000, 2000, "event")
    assert A.__str__().__eq__("\tdays born 1000: ['simulation_day=2000', 'event'] \n")


@pytest.mark.parametrize(
    "events_list, event_descriptions, expected_days",
    [
        ([], ["dummy"], [-1]),
        (
            [(1, 2, "event1"), (3, 4, "event2"), (5, 6, "event1"), (7, 8, "event3")],
            ["event1", "event2", "event3", "event0"],
            [5, 3, 7, -1],
        ),
    ],
)
def test_get_most_recent_date(events_list, event_descriptions, expected_days):
    """Unit test for function get_most_recent_date in file routines/animal/life_cycle/animal_events.py"""
    animal_event = AnimalEvents()
    for animal_age, simulation_day, event_description in events_list:
        animal_event.add_event(animal_age, simulation_day, event_description)

    for event_description, expected in zip(event_descriptions, expected_days):
        actual = animal_event.get_most_recent_date(event_description)
        assert actual == expected


def test_init_values():
    """Unit test for function init_values in file routines/animal/life_cycle/calf.py"""
    pass


def test_assign_calf_values():
    """Unit test for function assign_calf_values in file routines/animal/life_cycle/calf.py"""
    pass


def test_get_calf_values():
    """Unit test for function get_calf_values in file routines/animal/life_cycle/calf.py"""
    pass


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/calf.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/calf.py"""
    pass


def test_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/calf.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/calf.py"""
    pass


def test_update_milk_production_history():
    """Unit test for function update_milk_production_history in file routines/animal/life_cycle/cow.py"""
    pass


@pytest.mark.parametrize("days_in_milk,expected", [(1, 4.235874340457628),
                                                   (2, 4.235874340457628),
                                                   (3, 4.866603466869552)])
def test_calculate_fat_percent(days_in_milk, expected, mocker: MockerFixture):
    """Unit test for method calculate_fat_percent in routines/animal/life_cycle/cow.py"""
    animal_manager = mocker.MagicMock()
    fat_percent = RUFAS.routines.animal.life_cycle.cow.Cow.calculate_fat_percent(animal_manager, days_in_milk)
    assert fat_percent == expected


def test_cow_determine_param_value():
    """Unit test for function _determine_param_value in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_milking_update():
    """Unit test for function _milking_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_calc_daily_walking_dist():
    """Unit test for function calc_daily_walking_dist in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_get_bw_change():
    """Unit test for function get_bw_change in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_update():
    """Unit test for function update in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_determine_estrus_day():
    """Unit test for function _determine_estrus_day in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_restart_estrus():
    """Unit test for function _restart_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_later_estrus():
    """Unit test for function _later_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_return_estrus():
    """Unit test for function _return_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_after_ai_estrus():
    """Unit test for function _after_ai_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_after_abortion_estrus():
    """Unit test for function _after_abortion_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_ed_update():
    """Unit test for function _ed_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_determine_tai_program_day():
    """Unit test for function _determine_tai_program_day in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_tai_program_day_after_preg_check():
    """Unit test for function _tai_program_day_after_preg_check in file routines/animal/life_cycle/cow.py"""
    pass


def test__OvSynch56_update():
    """Unit test for function _OvSynch56_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_OvSynch48_update():
    """Unit test for function _OvSynch48_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_CoSynch72_update():
    """Unit test for function _CoSynch72_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_cow_5dCoSynch_update():
    """Unit test for function _5dCoSynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__user_defined_update():
    """Unit test for function _user_defined_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__determine_presynch_program_day():
    """Unit test for function _determine_presynch_program_day in file routines/animal/life_cycle/cow.py"""
    pass


def test__presynch_update():
    """Unit test for function _presynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__doubleovsynch_update():
    """Unit test for function _doubleovsynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__g6g_update():
    """Unit test for function _g6g_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__user_defined_presynch_update():
    """Unit test for function _user_defined_presynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__tai_update():
    """Unit test for function _tai_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__ed_tai_update():
    """Unit test for function _ed_tai_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__resynch_ed_tai():
    """Unit test for function _resynch_ed_tai in file routines/animal/life_cycle/cow.py"""
    pass


def test__open():
    """Unit test for function _open in file routines/animal/life_cycle/cow.py"""
    pass


def test__preg_update():
    """Unit test for function _preg_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__cull_update():
    """Unit test for function _cull_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_death_update():
    """Unit test for function death_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__health_cull_update():
    """Unit test for function _health_cull_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_get_heiferI_values():
    """Unit test for function get_heiferI_values in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_heiferI_calc_nutrient_rqmts_heiferI():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_calc_manure_excretion_heiferI():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_phosphorus_rqmts_heiferI():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_get_non_preg_bw_change_heiferI():
    """Unit test for function get_non_preg_bw_change in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_update_heiferI():
    """Unit test for function update in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_get_bw_change_heiferII():
    """Unit test for function get_bw_change in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_init_values_heiferII():
    """Unit test for function init_values in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_assign_heiferII_values():
    """Unit test for function assign_heiferII_values in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_get_heiferII_values():
    """Unit test for function get_heiferII_values in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_calc_heiferII_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_calc_heiferII_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_update():
    """Unit test for function update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_determine_estrus_day():
    """Unit test for function _determine_estrus_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_return_estrus():
    """Unit test for function _return_estrus in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_after_ai_estrus():
    """Unit test for function _after_ai_estrus in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_after_abortion_estrus():
    """Unit test for function _after_abortion_estrus in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_ed_update():
    """Unit test for function _ed_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_determine_tai_program_day():
    """Unit test for function _determine_tai_program_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_tai_program_day_after_abortion():
    """Unit test for function _tai_program_day_after_abortion in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_5dCG2P_update():
    """Unit test for function _5dCG2P_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_5dCGP_update():
    """Unit test for function _5dCGP_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_user_defined_update():
    """Unit test for function _user_defined_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_tai_update():
    """Unit test for function _tai_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_determine_synch_ed_program_day():
    """Unit test for function _determine_synch_ed_program_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_determine_synch_ed_estrus_day():
    """Unit test for function _determine_synch_ed_estrus_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_synch_ed_program_day_after_abortion():
    """Unit test for function _synch_ed_program_day_after_abortion in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_2P_update():
    """Unit test for function _2P_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_CP_update():
    """Unit test for function _CP_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_synch_ed_update():
    """Unit test for function _synch_ed_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_open():
    """Unit test for function _open in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_heiferII_preg_update():
    """Unit test for function _preg_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_get_heiferIII_values():
    """Unit test for function get_heiferIII_values in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_heiferIII_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_heiferIII_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_heiferIII_update():
    """Unit test for function update in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_initialize_herd():
    """Unit test for function initialize_herd in file routines/animal/life_cycle/life_cycle.py"""
    pass


def test_daily_update():
    """Unit test for function daily_update in file routines/animal/life_cycle/life_cycle.py"""
    pass


def test__calc_average():
    """Unit test for function _calc_average in file routines/animal/life_cycle/life_cycle.py"""
    pass


def test_calf_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/calf_manure_excretion.py"""
    pass


def test_cow_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/dry_cow_manure_excretion.py"""
    pass


def test_phosphorus_excreted():
    """Unit test for function phosphorus_excreted in file routines/animal/manure/general_manure.py"""
    pass


def test_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/growing_heifer_manure_excretion.py"""
    pass


def test_lactating_cow_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/lactating_cow_manure_excretion.py"""
    pass


def test_get_ration():
    """Unit test for function _get_ration in file routines/animal/ration/calf_ration.py"""
    actual = RUFAS.routines.animal.ration.calf_ration.CalfRationManager._get_ration()
    expected = {"202": 1, "216": 2, "status": "Optimal", "objective": 4.5}
    assert actual == expected


def test_optimize(mocker: MockerFixture):
    """Unit test for function optimize in file routines/animal/ration/calf_ration.
    Tests the optimize function to verify it returns a correctly optimized calf ration.py"""
    mocker.patch(
        "RUFAS.routines.animal.ration.calf_ration.CalfRationManager._get_ration", return_value="formulated_ration"
    )
    actual = RUFAS.routines.animal.ration.calf_ration.CalfRationManager.optimize()
    expected = "formulated_ration"
    assert actual == expected


def test_calc_requirements():
    """Unit test for function calc_requirements in file routines/animal/ration/calf_ration.py"""
    animal_intake = {
        "whole_milk_intake": 1,
        "milk_replacer_intake": 1,
        "starter_intake": 1,
        "wean_start": 1,
        "milk_reduction": 1,
        "milk_intake_wean": 1,
        "dm_intake": 1,
        "me_intake": 1,
        "cp_intake": 1,
        "adp_intake": 1,
        "milk_me_proportion": 1,
        "starter_me_proportion": 1,
        "milk_proportion": 1,
        "starter_proportion": 1,
    }
    feed = MagicMock()
    feed.calf_feeds = {
        202: {"DM": 1, "CP": 1, "DE": 1},
        203: {"DM": 1, "CP": 1, "DE": 1},
        216: {"DM": 1, "CP": 1, "DE": 1, "EE": 1},
    }

    calf = MagicMock()
    calf.days_born = 10
    calf.body_weight = 100
    temp = 25

    actual = RUFAS.routines.animal.ration.calf_ration.CalfRationManager.calc_requirements(
        calf, feed, temp, animal_intake
    )
    expected = {
        "ne_maint": {"op": "=", "val": 2.719558787744806},
        "me_maint": {"op": "=", "val": 1.1010359464553872},
        "bio_val": {"op": "=", "val": 0.023},
        "endo_urine_N": {"op": "=", "val": 6.324555320336759},
        "meta_fecal_N": {"op": "=", "val": 7.1000000000000005},
        "adp_maint": {"op": "=", "val": 3603.6019892219456},
        "me_gain": {"op": "=", "val": -0.10103594645538716},
        "ne_gain": {"op": "=", "val": -0.16557326346944443},
        "energy_allow_gain": {"op": "=", "val": 0},
        "adp_allow_gain": {"op": "=", "val": -0.4407438603835359},
        "live_weight_change": {"op": "=", "val": -0.4407438603835359},
    }
    assert actual == expected

    calf.days_born = 100
    actual = RUFAS.routines.animal.ration.calf_ration.CalfRationManager.calc_requirements(
        calf, feed, temp, animal_intake
    )
    expected = {
        "ne_maint": {"op": "=", "val": 2.719558787744806},
        "me_maint": {"op": "=", "val": 1.1010359464553872},
        "bio_val": {"op": "=", "val": 0.023},
        "endo_urine_N": {"op": "=", "val": 6.324555320336759},
        "meta_fecal_N": {"op": "=", "val": 7.1000000000000005},
        "adp_maint": {"op": "=", "val": 3603.6019892219456},
        "me_gain": {"op": "=", "val": -0.10103594645538716},
        "ne_gain": {"op": "=", "val": -0.16557326346944443},
        "energy_allow_gain": {"op": "=", "val": 0},
        "adp_allow_gain": {"op": "=", "val": -0.4407438603835359},
        "live_weight_change": {"op": "=", "val": -0.4407438603835359},
    }
    assert actual == expected


def test_calc_intake():
    """Unit test for function calc_intake in file routines/animal/ration/calf_ration.py"""

    calf = MagicMock()
    calf.birth_weight = 1
    calf.body_weight = 2

    feed = MagicMock()
    feed.calf_feeds = {
        202: {"DM": 1, "CP": 1, "DE": 1},
        203: {"DM": 1, "CP": 1, "DE": 1},
        216: {"DM": 1, "CP": 1, "DE": 1, "EE": 1},
    }

    milk_type = "whole"
    wean_day = 100
    wean_length = 10

    actual = RUFAS.routines.animal.ration.calf_ration.CalfRationManager.calc_intake(
        calf, feed, wean_day, wean_length, milk_type
    )
    expected = {
        "whole_milk_intake": 0.001,
        "milk_replacer_intake": 0.0,
        "starter_intake": -0.2379166,
        "wean_start": 89,
        "milk_reduction": 5,
        "milk_intake_wean": 0.0005454545454545455,
        "dm_intake": -0.2369166,
        "me_intake": -0.13008446328000003,
        "cp_intake": -0.0023691660000000002,
        "adp_intake": 749.2402389701692,
        "milk_me_proportion": -0.007379820585750122,
        "starter_me_proportion": 1.00737982058575,
        "milk_proportion": -0.004220894610170837,
        "starter_proportion": 1.004220894610171,
    }

    assert actual == expected

    milk_type = "not_whole"
    actual = RUFAS.routines.animal.ration.calf_ration.CalfRationManager.calc_intake(
        calf, feed, wean_day, wean_length, milk_type
    )
    expected = {
        "whole_milk_intake": 0.0,
        "milk_replacer_intake": 0.00015,
        "starter_intake": -0.2379166,
        "wean_start": 89,
        "milk_reduction": 5,
        "milk_intake_wean": 8.18181818181818e-05,
        "dm_intake": -0.2377666,
        "me_intake": -0.13090046328000002,
        "cp_intake": -0.002377666,
        "adp_intake": 749.8864432599029,
        "milk_me_proportion": -0.001100072500828203,
        "starter_me_proportion": 1.0011000725008283,
        "milk_proportion": -0.0006308707783178966,
        "starter_proportion": 1.000630870778318,
    }

    assert actual == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ([1, 2, 3, 4], [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]),
        (["1", "2", "3", "4"], ["1", "1", "1", "2", "2", "2", "3", "3", "3", "4", "4", "4"]),
    ],
)
def test_triple_values_in_list(input, expected) -> None:
    """Unit test for function triple_values_in_list in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()
    assert ration_optimizer.triple_values_in_list(input) == expected


def test_init_ration_optimizer():
    """Unit test for function __init__ in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    assert ration_optimizer.cow_cons == []
    assert ration_optimizer.heifer_cons == []
    assert ration_optimizer.constraint_functions == []


def test_set_constraints():
    """Unit test for function set_constraints in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()
    arguments = MagicMock()
    ration_optimizer.set_constraints(arguments)

    assert ration_optimizer.constraint_functions == [
        ration_optimizer.total_energy,
        ration_optimizer.NEmact_constraint,
        ration_optimizer.NEl_constraint,
        ration_optimizer.NEgact_constraint,
        ration_optimizer.calcium_constraint,
        ration_optimizer.phosphorus_constraint,
        ration_optimizer.protein_constraint,
        ration_optimizer.NDF_constraint_lower,
        ration_optimizer.NDF_constraint_upper,
        ration_optimizer.forage_NDF_constraint,
        ration_optimizer.fat_constraint,
        ration_optimizer.DMI_constraint_upper,
        ration_optimizer.DMI_constraint_lower,
    ]

    assert ration_optimizer.cow_cons == [
        {"type": "ineq", "fun": func, "args": arguments} for func in ration_optimizer.constraint_functions
    ]

    assert ration_optimizer.heifer_cons == [
        cons
        for cons in ration_optimizer.cow_cons
        if cons["fun"]
        not in [ration_optimizer.total_energy, ration_optimizer.NEl_constraint, ration_optimizer.DMI_constraint_lower]
    ]


def test_get_ration_vals():
    """Unit test for function get_ration_vals in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()
    decision_vector = [1.0, 2.0, 3.0, 4.0, 5.0]
    ration_config = MagicMock()
    ration_config.MEact_list = [6.0, 7.0, 8.0, 9.0, 10.0]

    actual = ration_optimizer.get_ration_vals(decision_vector, ration_config)

    expected = {"ME_total": 130.0}

    assert actual == expected


@pytest.mark.parametrize(
    "ration_config, expected",
    [(lazy_fixture("mock_ration_config"), 13.687246), (lazy_fixture("mock_random_ration_config"), 27.327894)],
)
def test_total_energy(ration_config, expected, decision_vector) -> None:
    """Unit test for function total_energy in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.total_energy(decision_vector, ration_config)

    assert actual == pytest.approx(expected)


def test_attempt_optimization(mocker: MockerFixture, mock_ration_config: MagicMock, mock_available_feeds: dict) -> None:
    """Unit test for function attempt_optimization in file routines/animal/ration/ration_optimizer.py"""

    def mock_triple_values_in_list(x):
        return x

    mock_RationConfig = mocker.patch("RUFAS.routines.animal.ration.ration_optimizer.RationConfig")
    mock_optimize = mocker.patch("RUFAS.routines.animal.ration.ration_optimizer.RationOptimizer.optimize")
    mocker.patch("RUFAS.routines.animal.ration.ration_optimizer.RationOptimizer.get_ration_vals")
    mocker.patch(
        "RUFAS.routines.animal.ration.ration_optimizer.RationOptimizer.triple_values_in_list",
        side_effect=mock_triple_values_in_list,
    )

    ration_optimizer = RationOptimizer()
    requirements = MagicMock()

    requirements.NEmaint_requirement = 1.0
    requirements.NEa_requirement = 2.0
    requirements.NEpreg_requirement = 3.0
    requirements.NEl_requirement = 4.0
    requirements.NEg_requirement = 5.0
    requirements.MP_requirement = 6.0
    requirements.C_requirement = 7.0
    requirements.P_requirement = 8.0
    requirements.avg_BW = 9.0
    requirements.DMIest_requirement = 10.0

    animal_combination = "AnimalCombination.LAC_COW"

    ration_optimizer.attempt_optimization(requirements, mock_available_feeds, animal_combination)

    mock_RationConfig.assert_called_once_with(
        mock_available_feeds["price"],
        requirements.NEmaint_requirement,
        requirements.NEa_requirement,
        requirements.NEpreg_requirement,
        requirements.NEl_requirement,
        requirements.NEg_requirement,
        requirements.MP_requirement,
        requirements.Ca_requirement,
        requirements.P_requirement,
        mock_available_feeds["TDN"],
        mock_available_feeds["DE"],
        mock_available_feeds["EE"],
        mock_available_feeds["is_fat"],
        requirements.avg_BW,
        mock_available_feeds["calcium"],
        mock_available_feeds["phosphorus"],
        mock_available_feeds["NDF"],
        mock_available_feeds["type"],
        mock_available_feeds["is_wetforage"],
        mock_available_feeds["Kd"],
        mock_available_feeds["N_A"],
        mock_available_feeds["N_B"],
        mock_available_feeds["CP"],
        mock_available_feeds["dRUP"],
        mock_available_feeds["lactating_cow_limit"],
        True,
        DMIest__requirement=requirements.DMIest_requirement,
    )

    ration_optimizer.optimize.assert_called_once_with(
        animal_combination, mock_available_feeds, mock_RationConfig.return_value
    )

    ration_optimizer.get_ration_vals.assert_called_once_with(
        mock_optimize.return_value.x, mock_RationConfig.return_value
    )


@pytest.mark.parametrize(
    "ration_config, expected",
    [(lazy_fixture("mock_ration_config"), 91.0), (lazy_fixture("mock_random_ration_config"), 52.041)],
)
def test_objective(ration_config, expected, decision_vector) -> None:
    """Unit test for function objective in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.objective(decision_vector, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, expected",
    [(lazy_fixture("mock_ration_config"), 88.0), (lazy_fixture("mock_random_ration_config"), 21.658)],
)
def test_NEmact_constraint(ration_config, expected, decision_vector) -> None:
    """Unit test for function NEmact_constraint in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.NEmact_constraint(decision_vector, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, expected",
    [
        (lazy_fixture("mock_ration_config"), 84.0),
        (lazy_fixture("mock_ration_config_with_empty_NElact_list"), 14.0),
        (lazy_fixture("mock_random_ration_config"), 58.44),
    ],
)
def test_NEl_constraint(ration_config, expected, decision_vector) -> None:
    """Unit test for function NEl_constraint in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.NEl_constraint(decision_vector, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, expected",
    [
        (lazy_fixture("mock_ration_config"), 86.0),
        # (lazy_fixture('mock_ration_config_with_empty_NEgact_list'),
        # 16.0),
        (lazy_fixture("mock_random_ration_config"), 63.349999999999994),
    ],
)
def test_NEgact_constraint(ration_config, expected, decision_vector) -> None:
    """Unit test for function NEgact_constraint in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.NEgact_constraint(decision_vector, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, expected",
    [(lazy_fixture("mock_ration_config"), 0.6455), (lazy_fixture("mock_random_ration_config"), 0.245465)],
)
def test_calcium_constraint(ration_config, expected, decision_vector) -> None:
    """Unit test for function calcium_constraint in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.calcium_constraint(decision_vector, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, expected",
    [(lazy_fixture("mock_ration_config"), 0.6638), (lazy_fixture("mock_random_ration_config"), 0.374025)],
)
def test_phosphorus_constraint(ration_config, expected, decision_vector) -> None:
    """Unit test for function phosphorus_constraint in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.phosphorus_constraint(decision_vector, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, expected",
    [(lazy_fixture("mock_ration_config"), 135.148700), (lazy_fixture("mock_random_ration_config"), 113.147389)],
)
def test_protein_constraint(ration_config, expected, decision_vector) -> None:
    """Unit test for function protein_constraint in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.protein_constraint(decision_vector, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, decision_vec, expected",
    [
        (lazy_fixture("mock_ration_config"), lazy_fixture("decision_vector"), -20.666667),
        (lazy_fixture("mock_random_ration_config"), lazy_fixture("decision_vector"), -22.264048),
        (lazy_fixture("mock_ration_config"), lazy_fixture("decision_vector_sum_zero"), None),
    ],
)
def test_NDF_constraint_lower(ration_config, decision_vec, expected) -> None:
    """Unit test for function test_NDF_constraint_lower in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.NDF_constraint_lower(decision_vec, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, decision_vec, expected",
    [
        (lazy_fixture("mock_ration_config"), lazy_fixture("decision_vector"), 40.666666),
        (lazy_fixture("mock_random_ration_config"), lazy_fixture("decision_vector"), 42.264047),
        (lazy_fixture("mock_ration_config"), lazy_fixture("decision_vector_sum_zero"), None),
    ],
)
def test_NDF_constraint_upper(ration_config, decision_vec, expected) -> None:
    """Unit test for function NDF_constraint_upper in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.NDF_constraint_upper(decision_vec, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, decision_vec, expected",
    [
        (lazy_fixture("mock_ration_config"), lazy_fixture("decision_vector"), -14.190476),
        (lazy_fixture("mock_random_ration_config"), lazy_fixture("decision_vector"), -14.844142),
        (lazy_fixture("mock_ration_config"), lazy_fixture("decision_vector_sum_zero"), None),
    ],
)
def test_forage_NDF_constraint(ration_config, decision_vec, expected) -> None:
    """Unit test for function forage_NDF_constraint in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.forage_NDF_constraint(decision_vec, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, decision_vec, expected",
    [
        (lazy_fixture("mock_ration_config"), lazy_fixture("decision_vector"), 2.666666),
        (lazy_fixture("mock_random_ration_config"), lazy_fixture("decision_vector"), 4.359142),
        (lazy_fixture("mock_ration_config"), lazy_fixture("decision_vector_sum_zero"), None),
    ],
)
def test_fat_constraint(ration_config, decision_vec, expected) -> None:
    """Unit test for function fat_constraint in file routines/animal/ration/ration_optimizer.py"""

    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.fat_constraint(decision_vec, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, expected",
    [(lazy_fixture("mock_ration_config"), 13.0), (lazy_fixture("mock_random_ration_config"), 20.064)],
)
def test_DMI_constraint(ration_config, expected, decision_vector) -> None:
    """Unit test for function DMI_constraint in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.DMI_constraint_lower(decision_vector, ration_config)

    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "ration_config, expected",
    [(lazy_fixture("mock_ration_config"), -9.0), (lazy_fixture("mock_random_ration_config"), -19.596)],
)
def test_DMI_constraint_upper(ration_config, expected, decision_vector) -> None:
    """Unit test for function DMI_constraint_upper in file routines/animal/ration/ration_optimizer.py"""
    ration_optimizer = RationOptimizer()

    actual = ration_optimizer.DMI_constraint_upper(decision_vector, ration_config)

    assert actual == pytest.approx(expected)


@pytest.fixture
def mock_cow_cons() -> MagicMock():
    return MagicMock(name="cow_cons")


@pytest.fixture
def mock_heifer_cons() -> MagicMock():
    return MagicMock(name="heifer_cons")


@pytest.fixture
def ration_optimizer(mock_cow_cons: MagicMock, mock_heifer_cons: MagicMock) -> RationOptimizer:
    ration_optimizer = RationOptimizer()

    def objective(x, _):
        sum(x)

    ration_optimizer.objective = objective
    ration_optimizer.cow_cons = mock_cow_cons
    ration_optimizer.heifer_cons = mock_heifer_cons

    return ration_optimizer


@pytest.mark.parametrize(
    "is_udr, animal_combination, expected_x0, expected_bounds, expected_constraints",
    [
        (
            True,
            "AnimalCombination.LAC_COW",
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
            [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6)],
            lazy_fixture("mock_cow_cons"),
        ),
        (
            True,
            "AnimalCombination.GROWING",
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
            [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6)],
            lazy_fixture("mock_heifer_cons"),
        ),
        (
            False,
            "AnimalCombination.LAC_COW",
            [1, 1, 1, 1, 1, 1],
            [
                (0, 0.3334333333333333),
                (0, 0.6667666666666666),
                (0, 1.0001),
                (0, 1.3334333333333332),
                (0, 1.6667666666666667),
                (0, 2.0001),
            ],
            lazy_fixture("mock_cow_cons"),
        ),
        (
            False,
            "AnimalCombination.GROWING",
            [1, 1, 1, 1, 1, 1],
            [
                (0, 0.3334333333333333),
                (0, 0.6667666666666666),
                (0, 1.0001),
                (0, 1.3334333333333332),
                (0, 1.6667666666666667),
                (0, 2.0001),
            ],
            lazy_fixture("mock_heifer_cons"),
        ),
    ],
)
def test_ration_optimizer_optimize(
    mocker: MockerFixture,
    mock_ration_config: MagicMock,
    mock_available_feeds: dict,
    ration_optimizer: RationOptimizer,
    is_udr: bool,
    animal_combination: str,
    expected_x0: list[float],
    expected_bounds: list[float],
    expected_constraints: MagicMock,
) -> None:
    """Unit test for function optimize in file routines/animal/ration/ration_optimizer.py"""

    mocker.patch("RUFAS.routines.animal.ration.ration_optimizer.udrm", MagicMock(is_udr=is_udr))
    mocker.patch("RUFAS.routines.animal.ration.ration_optimizer.RationOptimizer.set_constraints")
    mocker.patch(
        "RUFAS.routines.animal.ration.ration_optimizer.RationOptimizer.make_user_bounds",
        return_value=[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6)],
    )
    mock_ration_to_use = mocker.patch(
        "RUFAS.routines.animal.ration.user_defined_ration.UserDefinedRationManager.ration_to_use"
    )
    mock_minimize = mocker.patch("RUFAS.routines.animal.ration.ration_optimizer.minimize")
    mocker.patch("RUFAS.routines.animal.ration.ration_optimizer.random.random", return_value=0.1)

    assert (
        ration_optimizer.optimize(animal_combination, mock_available_feeds, mock_ration_config)
        == mock_minimize.return_value
    )

    ration_optimizer.set_constraints.assert_called_once_with(arguments=(mock_ration_config,))

    if is_udr:
        mock_ration_to_use.assert_called_once_with(animal_combination)

        ration_optimizer.make_user_bounds.assert_called_once_with(
            mock_ration_to_use.return_value, mock_ration_config.DMIest_requirement
        )

    mock_minimize.assert_called_once_with(
        ration_optimizer.objective,
        expected_x0,
        method="SLSQP",
        bounds=expected_bounds,
        constraints=expected_constraints,
        args=(mock_ration_config,),
    )


def test_ration_optimizer_optimize_value_error(
    mocker: MockerFixture, mock_ration_config: MagicMock, mock_available_feeds: dict, ration_optimizer: RationOptimizer
) -> None:
    """Unit test for value error in function optimize in file routines/animal/ration/ration_optimizer.py"""
    mocker.patch("RUFAS.routines.animal.ration.ration_optimizer.udrm", MagicMock(is_udr=False))
    mocker.patch("RUFAS.routines.animal.ration.ration_optimizer.RationOptimizer.set_constraints")

    animal_combination = "AnimalCombination.CALF"

    with pytest.raises(ValueError, match="Invalid animal combination: AnimalCombination.CALF"):
        ration_optimizer.optimize(animal_combination, mock_available_feeds, mock_ration_config)


def test_calc_rqmts():
    """Unit test for function calc_rqmts in file routines/animal/ration/animal_requirements.py"""
    test_requirements = AnimalRequirements()
    test_requirements.calculate_NRC_energy_maintenance_requirements = MagicMock(return_value=(1, 2, 3))
    test_requirements.calculate_NRC_energy_growth_requirements = MagicMock(return_value=(1, 2, 3))
    test_requirements.calculate_NRC_energy_pregnancy_requirements = MagicMock(return_value=1)
    test_requirements.calculate_NRC_energy_lactation_requirements = MagicMock(return_value=1)
    test_requirements.calculate_NRC_DMI = MagicMock(return_value=1)
    test_requirements.calculate_NRC_protein_requirements = MagicMock(return_value=1)
    test_requirements.calculate_NRC_calcium_requirements = MagicMock(return_value=1)
    test_requirements.calculate_NRC_phosphorus_requirements = MagicMock(return_value=1)
    test_requirements.calculate_NASEM_energy_maintenance_requirements = MagicMock(return_value=(4, 5, 6))
    test_requirements.calculate_NASEM_energy_growth_requirements = MagicMock(return_value=(4, 5, 6))
    test_requirements.calculate_NASEM_energy_pregnancy_requirements = MagicMock(return_value=(4, 5))
    test_requirements.calculate_NASEM_energy_lactation_requirements = MagicMock(return_value=2)
    test_requirements.calculate_NASEM_DMI = MagicMock(return_value=2)
    test_requirements.calculate_NASEM_protein_requirements = MagicMock(return_value=2)
    test_requirements.calculate_NASEM_calcium_requirements = MagicMock(return_value=2)
    test_requirements.calculate_NASEM_phosphorus_requirements = MagicMock(return_value=2)
    AnimalBase.config["nutrient_standard"] = "NRC"
    test_requirements.AnimalBase = AnimalBase
    # with patch.object('') as mocked:
    #     mocked.side
    actual = test_requirements.calc_rqmts(MagicMock(), MagicMock(), MagicMock(), MagicMock())
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
    actual = test_requirements.calc_rqmts(MagicMock(), MagicMock(), MagicMock(), MagicMock())
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
    result_energy_activity = req.energy_activity_rqmts(body_weight=400, housing="Grazing", distance=1)
    assert (result_energy_activity) == pytest.approx((294), rel=1e-2)

    result_energy_activity = req.energy_activity_rqmts(body_weight=400, housing="Not_Grazing", distance=1)
    assert (result_energy_activity) == pytest.approx((0), rel=1e-2)

    AnimalBase.config["nutrient_standard"] = "NRC"

    result_energy_activity = req.energy_activity_rqmts(body_weight=400, housing="Barn", distance=1)
    assert (result_energy_activity) == pytest.approx((0.18), rel=1e-2)

    result_energy_activity = req.energy_activity_rqmts(body_weight=400, housing="Grazing", distance=1)
    assert (result_energy_activity) == pytest.approx((0.66), rel=1e-2)

    result_energy_activity = req.energy_activity_rqmts(body_weight=400, housing="n e i t h e r", distance=1)
    assert (result_energy_activity) == pytest.approx((0.18), rel=1e-2)


def test_growing_heifer_ration_optimize():
    """Unit test for function optimize in file routines/animal/ration/growing_heifer_ration.py"""
    pass


def test_calculate_rqmts():
    """Unit test for function calculate_rqmts in file routines/animal/ration/growing_heifer_ration.py"""
    pass


# @pytest.mark.parameterize("udrm, om, expected", [MagicMock(), MagicMock(), True])
def test_formulate_ration() -> None:
    """Unit test for function formulate_ration in file routines/animal/ration/ration_driver.py"""
    pass


def test_calc_milk_average() -> None:
    """Unit test for function calc_milk_average in file routines/animal/ration/ration_driver.py"""
    mockpen = MagicMock()
    mockpen.animals_in_pen = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    production = [1, 2, 3, 4, 5]
    for i in range(len(production)):
        mockpen.animals_in_pen[i].estimated_daily_milk_produced = production[i]
    result = RationManager.calc_milk_average(mockpen)
    assert result == sum(production) / len(production)


def test_reduce_milk_production() -> None:
    """Unit test for function reduce_milk_production in file routines/animal/ration/ration_driver.py"""
    mockpen = MagicMock()
    mockpen.animals_in_pen = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    production = [1, 2, 3, 4, 5]
    reduced_predicted = [1, 2, 2, 3, 4]
    # assign production to mocked animals
    for i in range(len(production)):
        mockpen.animals_in_pen[i].estimated_daily_milk_produced = production[i]
    # assert all were reduced, but not reaching below 1.0 kg/day
    RationManager.reduce_milk_production(mockpen, 1.0)
    for i, animal in enumerate(mockpen.animals_in_pen):
        assert reduced_predicted[i] == animal.estimated_daily_milk_produced


def test_make_ration_from_solution():
    """Unit test for function make_ration_from_solution in file routines/animal/ration/ration_driver.py"""

    # make a mocked solution object - the critical component being the x
    mock_solution = MagicMock()
    mock_solution.x = [1, 1, 1, 2, 2, 2, 3, 3, 3]
    predicted = {"100": 3, "200": 6, "300": 9}
    predicted["status"] = "Optimal"
    predicted["objective"] = 0.0

    mock_avail_feeds = {}
    mock_avail_feeds["feed_id"] = [100, 200, 300]
    mock_avail_feeds["feed_key"] = ["100", "200", "300"]
    mock_avail_feeds["price"] = [0, 0, 0]
    result = RationManager.make_ration_from_solution(mock_avail_feeds, mock_solution)
    assert result == predicted


@pytest.mark.parametrize(
    "test_ration, expected",
    [
        ({"2": 3, "4": 6, "status": True, "objective": False}, [1, 1, 1, 2, 2, 2]),
        (
            {"2": 3, "status": True, "objective": False},
            [
                1,
                1,
                1,
            ],
        ),
        (
            {
                "2": 3,
                "4": 6,
            },
            [1, 1, 1, 2, 2, 2],
        ),
        (
            {
                "2": 3,
                "4": 12,
            },
            [1, 1, 1, 4, 4, 4],
        ),
    ],
)
def test_make_solution_from_fixed_ration(test_ration: Dict, expected: list):
    """Unit test for function make_solution_from_fixed_ration in file routines/animal/ration/ration_driver.py"""
    # test_ration = {'2' : 3, '4' : 6, 'status' : True, 'objective' : False}
    # expected = [1, 1, 1, 2, 2, 2]
    result = RationManager.make_solution_from_fixed_ration(test_ration)
    assert result == expected


def test_get_user_defined_ration():
    """Unit test for function get_user_defined_ration in file routines/animal/ration/ration_driver.py"""
    pass


def test_report_ration():
    """Unit test for function report_ration in file routines/animal/ration/ration_driver.py"""
    ration = {"1": 1, "2": 2, "3": 3, "121": 1, "122": 2, "155": 3, "157": 4}
    available_feeds = {
        "1": {
            "DM": 1,
            "as_fed": 1,
            "CP": 1,
            "ADF": 1,
            "NDF": 1,
            "lignin": 1,
            "ash": 1,
            "phosphorus": 1,
            "potassium": 1,
            "N": 1,
            "EE": 1,
            "starch": 1,
            "TDN": 1,
            "DE": 1,
            "calcium": 1,
        },
        "2": {
            "DM": 1,
            "as_fed": 1,
            "CP": 1,
            "ADF": 1,
            "NDF": 1,
            "lignin": 1,
            "ash": 1,
            "phosphorus": 1,
            "potassium": 1,
            "N": 1,
            "EE": 1,
            "starch": 1,
            "TDN": 1,
            "DE": 1,
            "calcium": 1,
        },
        "3": {
            "DM": 1,
            "as_fed": 1,
            "CP": 1,
            "ADF": 1,
            "NDF": 1,
            "lignin": 1,
            "ash": 1,
            "phosphorus": 1,
            "potassium": 1,
            "N": 1,
            "EE": 1,
            "starch": 1,
            "TDN": 1,
            "DE": 1,
            "calcium": 1,
        },
        "121": {
            "DM": 1,
            "as_fed": 1,
            "CP": 1,
            "ADF": 1,
            "NDF": 1,
            "lignin": 1,
            "ash": 1,
            "phosphorus": 1,
            "potassium": 1,
            "N": 1,
            "EE": 1,
            "starch": 1,
            "TDN": 1,
            "DE": 1,
            "calcium": 1,
        },
        "122": {
            "DM": 1,
            "as_fed": 1,
            "CP": 1,
            "ADF": 1,
            "NDF": 1,
            "lignin": 1,
            "ash": 1,
            "phosphorus": 1,
            "potassium": 1,
            "N": 1,
            "EE": 1,
            "starch": 1,
            "TDN": 1,
            "DE": 1,
            "calcium": 1,
        },
        "155": {
            "DM": 1,
            "as_fed": 1,
            "CP": 1,
            "ADF": 1,
            "NDF": 1,
            "lignin": 1,
            "ash": 1,
            "phosphorus": 1,
            "potassium": 1,
            "N": 1,
            "EE": 1,
            "starch": 1,
            "TDN": 1,
            "DE": 1,
            "calcium": 1,
        },
        "157": {
            "DM": 1,
            "as_fed": 1,
            "CP": 1,
            "ADF": 1,
            "NDF": 1,
            "lignin": 1,
            "ash": 1,
            "phosphorus": 1,
            "potassium": 1,
            "N": 1,
            "EE": 1,
            "starch": 1,
            "TDN": 1,
            "DE": 1,
            "calcium": 1,
        },
    }
    result = RationReporter.report_ration(ration, available_feeds)
    expected = (
        {
            "dm": 16,
            "as_fed": 1600,
            "CP": 0.16,
            "ADF": 0.16,
            "NDF": 0.16,
            "lignin": 0.16,
            "ash": 0.16,
            "phosphorus": 0.16,
            "potassium": 0.16,
            "N": 0.0256,
            "EE": 0.16,
            "starch": 0.16,
            "TDN": 0.16,
            "DE": 0.16,
            "calcium": 0.16,
        },
        {
            "dm": 1.0,
            "CP": 1.0,
            "ADF": 1.0,
            "NDF": 1.0,
            "lignin": 1.0,
            "ash": 1.0,
            "phosphorus": 1.0,
            "potassium": 1.0,
            "N": 0.16,
            "EE": 1.0,
            "starch": 1.0,
            "TDN": 1.0,
            "DE": 1.0,
            "calcium": 1.0,
        },
    )
    assert result == expected


def eq_constraint(x, ration_config):
    return np.sum(x) - 10  # This 'eq' constraint checks if the sum of x is equal to 10


def ineq_constraint(x, ration_config):
    return np.sum(x) - 10  # This 'ineq' constraint checks if the sum of x is greater than 10


@pytest.mark.parametrize(
    "solution_x,constraint,expected",
    [
        (
            np.array([2, 3, 5]),
            {"type": "eq", "fun": eq_constraint},
            False,
        ),  # Constraint not violated, hence expecting False
        (np.array([2, 3, 4]), {"type": "eq", "fun": eq_constraint}, True),
        (np.array([1, 3, 5]), {"type": "ineq", "fun": ineq_constraint}, True),
        (np.array([3, 4, 5]), {"type": "ineq", "fun": ineq_constraint}, False),
    ],
)
def test_is_constraint_violated(solution_x, constraint, expected):
    """Unit test for function is_constraint_violated in file routines/animal/ration/ration_driver.py"""
    ration_config = MagicMock()
    ration_optimizer = RationOptimizer()
    assert ration_optimizer.is_constraint_violated(solution_x, constraint, ration_config) == expected


@pytest.mark.parametrize(
    "mock_results, expected_result",
    [
        ([False, True, False], [1]),
        ([False, False, False], []),
        ([True, True, True], [0, 1, 2]),
    ],
)
def test_find_failed_constraints(mocker: MockerFixture, mock_results, expected_result):
    """Unit test for function find_failed_constraints in file routines/animal/ration/ration_driver.py"""
    # Arrange
    solution_x = MagicMock()
    constraints = [mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()]

    # The exact path depends on where is_constraint_violated() is 'used' (which may differ from where it is 'defined')
    # a common bug, so the path below may need to be adjusted
    mocker.patch(
        "RUFAS.routines.animal.ration.ration_optimizer.RationOptimizer.is_constraint_violated", side_effect=mock_results
    )

    # Act
    ration_config = MagicMock()
    ration_optimizer = RationOptimizer()
    failed_constraints = ration_optimizer.find_failed_constraints(solution_x, constraints, ration_config)
    failed_constraints_indices = []

    for i, constraint in enumerate(constraints):
        if constraint in failed_constraints:
            failed_constraints_indices.append(i)

    # Assert
    assert failed_constraints_indices == expected_result


def test_calc_pen_requirements():
    """Unit test for function set_pen_requirements in file routines/animal/ration/ration_driver.py"""
    req = RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements()
    req.calc_pen_requirements(
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        "mean",
    )
    attributelist = [
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
    for attribute in attributelist:
        assert getattr(req, attribute) == 2
    req.calc_pen_requirements(
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        [1, 2, 3],
        "percentile",
    )
    for attribute in attributelist:
        assert getattr(req, attribute) == 2.8


def test_feed_nutrients():
    """Unit test for function feed_nutrients in file routines/animal/ration/ration_driver.py"""
    feed_obj = MagicMock()
    feed_obj.available_feeds = {
        "1": {
            "rufas_id": 1,
            "TDN": 1,
            "DE": 1,
            "EE": 1,
            "is_fat": True,
            "calcium": 1,
            "phosphorus": 1,
            "NDF": 1,
            "feed_type": 1,
            "is_wetforage": True,
            "Kd": 1,
            "N_A": 1,
            "N_B": 1,
            "CP": 1,
            "dRUP": 1,
            "limit": {"lactating_cows": 1, "dry_cows": 2},
        },
        "2": {
            "rufas_id": 2,
            "TDN": 2,
            "DE": 2,
            "EE": 2,
            "is_fat": False,
            "calcium": 2,
            "phosphorus": 2,
            "NDF": 2,
            "feed_type": 2,
            "is_wetforage": False,
            "Kd": 2,
            "N_A": 2,
            "N_B": 2,
            "CP": 2,
            "dRUP": 2,
            "limit": 3,
        },
    }
    feed_obj.feed_costs = {"1": 1, "2": 2}

    available_feeds = AvailableFeeds()
    available_feeds.feed_nutrients(feed_obj)

    assert available_feeds.lactating_cow_limit == [1, 3]
    assert available_feeds.dry_cow_limit == [2, 3]
    assert available_feeds.CP == [1, 2]

    assert available_feeds.is_fat == [True, False]
    assert available_feeds.is_wetforage == [True, False]
    keylist = [
        "feed_id",
        "TDN",
        "DE",
        "EE",
        "calcium",
        "phosphorus",
        "NDF",
        "type",
        "Kd",
        "N_A",
        "N_B",
        "CP",
        "dRUP",
    ]
    for key in keylist:
        assert getattr(available_feeds, key) == [1, 2]
        assert len(getattr(available_feeds, key)) == 2


@pytest.fixture
def mock_cow_args() -> Dict[str, Any]:
    cow_args = {
        "birth_date": 0,
        "days_born": 0,
        "p_init": 0,
        "birth_weight": 0,
        "id": 1,
        "calf_birth_weight": 30,
        "repro_program": "ED",
        "presynch_method": "PreSynch",
        "tai_method_c": "OvSynch 56",
        "tai_method_h": "OvSynch 56",
        "resynch_method": "TAIafterPD",
        "synch_ed_method_h": "example",
        "wean_day": 4,
        "wood_l": 0,
        "wood_m": 0,
        "wood_n": 0,
    }
    return cow_args


@pytest.fixture
def mock_AnimalBase_config() -> AnimalBase.config:
    AnimalBase.config = MagicMock()
    AnimalBase.config.update({"lactation_curve": "wood"})
    AnimalBase.config.update(
        {
            "wood_l": [[16.13, 23.61, 23.81], [14.07, 19.26, 19.21]],
            "wood_m": [[0.235, 0.227, 0.244], [0.186, 0.173, 0.190]],
            "wood_n": [[0.0019, 0.0032, 0.0036], [0.0021, 0.0028, 0.0032]],
            "wood_l_std": [[0.28, 0.54, 0.51], [0.39, 0.49, 0.47]],
            "wood_m_std": [[0.0046, 0.0064, 0.0060], [0.0076, 0.0071, 0.0069]],
            "wood_n_std": [[3.77e-5, 5.82e-5, 5.54e-5], [6.60e-5, 6.69e-5, 6.53e-5]],
        }
    )
    return AnimalBase.config


@pytest.fixture
def mock_holstein(mock_AnimalBase_config: AnimalBase.config, mock_cow_args: Dict[str, Any]) -> Cow:
    AnimalBase.config = mock_AnimalBase_config
    mock_cow_args["breed"] = "HO"
    mock_holstein_cow = Cow(mock_cow_args)
    mock_holstein_cow.calves = 4
    mock_holstein_cow.lactation_curve = "wood"
    return mock_holstein_cow


@pytest.fixture
def mock_jersey(mock_AnimalBase_config: AnimalBase.config, mock_cow_args: Dict[str, Any]) -> Cow:
    AnimalBase.config = mock_AnimalBase_config
    mock_cow_args["breed"] = "JE"
    mock_jersey_cow = Cow(mock_cow_args)
    mock_jersey_cow.calves = 2
    mock_jersey_cow.lactation_curve = "wood"
    return mock_jersey_cow


@pytest.fixture
def mock_generic_cow(mock_AnimalBase_config: AnimalBase.config, mock_cow_args: Dict[str, Any]) -> Cow:
    AnimalBase.config = mock_AnimalBase_config
    mock_cow_args["breed"] = "Generic"
    mock_generic = Cow(mock_cow_args)
    mock_generic.calves = 1
    mock_generic.lactation_curve = "wood"
    return mock_generic


def test_set_breed_index(mock_holstein: Cow, mock_jersey: Cow, mock_generic_cow: Cow) -> None:
    """Unit test for function set_breed_index in file routines/animal/life_cycle/cow.py"""
    mock_holstein.set_breed_index()
    assert mock_holstein.breed == "HO"
    assert mock_holstein.breed_index == 0

    mock_jersey.set_breed_index()
    assert mock_jersey.breed == "JE"
    assert mock_jersey.breed_index == 1

    mock_generic_cow.set_breed_index()
    assert mock_generic_cow.breed != "HO"
    assert mock_generic_cow.breed != "JE"
    assert mock_generic_cow.breed_index == 0


def test_set_parity_index(mock_holstein: Cow, mock_jersey: Cow, mock_generic_cow: Cow) -> None:
    """Unit test for function set_parity_index in file routines/animal/life_cycle/cow.py"""
    mock_holstein.set_parity_index()
    assert mock_holstein.calves == 4
    assert mock_holstein.parity_index == 2

    mock_jersey.set_parity_index()
    assert mock_jersey.calves == 2
    assert mock_jersey.parity_index == 1

    mock_generic_cow.set_parity_index()
    assert mock_generic_cow.calves == 1
    assert mock_generic_cow.parity_index == 0


@pytest.mark.parametrize(
    "wood_l, wood_m, wood_n",
    [
        (25.0, 0.24, 0.0035),
    ],
)
def test_set_lactation_curve_params(wood_l, wood_m, wood_n, mock_cow_args) -> None:
    """Unit test for function set_lactation_curve_params in file routines/animal/life_cycle/cow.py"""

    with patch("numpy.random.normal") as mock_normal:
        mock_normal.side_effect = [wood_l, wood_m, wood_n]

        mock_cow_args["breed"] = "HO"
        mock_cow = Cow(mock_cow_args)
        mock_cow.calves = 3
        mock_cow.lactation_curve = "wood"

        AnimalBase.config = {
            "wood_l": [[1, 2], [3, 4]],
            "wood_l_std": [[0.1, 0.2], [0.3, 0.4]],
            "wood_m": [[5, 6], [7, 8]],
            "wood_m_std": [[0.5, 0.6], [0.7, 0.8]],
            "wood_n": [[9, 10], [11, 12]],
            "wood_n_std": [[0.9, 1.0], [1.1, 1.2]],
        }

        mock_cow.set_lactation_curve_params()

        assert mock_cow.wood_l == wood_l
        assert mock_cow.wood_m == wood_m
        assert mock_cow.wood_n == wood_n


@pytest.mark.parametrize(
    "lactation_curve, wood_l, wood_m, wood_n, days_in_milk, expected_milk",
    [
        ("wood", 16.13, 0.235, 0.0019, 100, 39.366),
        ("wood", 23.81, 0.244, 0.0036, 150, 47.120),
    ],
)
def test_calculate_daily_milk_produced(
    lactation_curve, wood_l, wood_m, wood_n, days_in_milk, expected_milk, mock_cow_args
) -> None:
    """Unit test for function set_lactation_curve_params in file routines/animal/life_cycle/cow.py"""
    AnimalBase.config = MagicMock()
    mock_cow_args["breed"] = "HO"
    mock_cow = Cow(mock_cow_args)
    mock_cow.calves = 3
    mock_cow.lactation_curve = lactation_curve
    mock_cow.wood_l = wood_l
    mock_cow.wood_m = wood_m
    mock_cow.wood_n = wood_n
    mock_cow.days_in_milk = days_in_milk

    daily_milk_produced = mock_cow.calculate_daily_milk_produced()

    assert np.isclose(daily_milk_produced, expected_milk, rtol=1e-3)


def test_get_feed_data_from_feed_ids() -> None:
    """Unit test for function get_feed_data_from_feed_ids in file routines/animal/ration/ration_driver.py"""

    # Arrange
    feed_ids = {155, 157}
    available_feeds = AvailableFeeds()
    available_feeds.feed_id = [136, 139, 155, 157]
    available_feeds.CP = [0, 0, 25.4, 18]
    available_feeds.DE = [0, 0, 5.59, 3.69]
    available_feeds.EE = [0, 0, 30.8, 3]
    available_feeds.Kd = [0, 0, 0, 0]
    available_feeds.NDF = [0, 0, 0, 0]
    available_feeds.N_A = [0, 0, 0, 0]
    available_feeds.N_B = [0, 0, 0, 0]
    available_feeds.TDN = [0, 0, 0, 0]
    available_feeds.calcium = [22, 34, 1, 0.7]
    available_feeds.dRUP = [0, 0, 0, 0]
    available_feeds.dry_cow_limit = [100, 100, 100, 100]
    available_feeds.feed_key = ["136", "139", "155", "157"]
    available_feeds.is_fat = [False, False, False, None]
    available_feeds.is_wetforage = [False, False, False, None]
    available_feeds.lactating_cow_limit = [100, 100, 100, 100]
    available_feeds.phosphorus = [19.3, 0, 0.75, 0.45]
    available_feeds.price = [0.1, 0.05, 0.82, 0.44]
    available_feeds.type = ["Mineral", "Mineral", "Milk", "Starter"]

    # Assert before
    assert len(available_feeds._feed_id_to_list_idx_dict) == 0

    # Act
    pen_specific_feed_data = available_feeds.get_feed_data_from_feed_ids(feed_ids)

    # Assert after
    expected_feed_id_to_list_idx_dict = {136: 0, 139: 1, 155: 2, 157: 3}
    assert available_feeds._feed_id_to_list_idx_dict == expected_feed_id_to_list_idx_dict

    expected_pen_specific_feed_data = {
        "feed_id": [155, 157],
        "heiferIII_limit": [],
        "heiferII_limit": [],
        "heiferI_limit": [],
        "calf_limit": [],
        "CP": [25.4, 18],
        "DE": [5.59, 3.69],
        "EE": [30.8, 3],
        "Kd": [0, 0],
        "NDF": [0, 0],
        "N_A": [0, 0],
        "N_B": [0, 0],
        "TDN": [0, 0],
        "calcium": [1, 0.7],
        "dRUP": [0, 0],
        "dry_cow_limit": [100, 100],
        "feed_key": ["155", "157"],
        "is_fat": [False, None],
        "is_wetforage": [False, None],
        "lactating_cow_limit": [100, 100],
        "phosphorus": [0.75, 0.45],
        "price": [0.82, 0.44],
        "type": ["Milk", "Starter"],
    }
    assert pen_specific_feed_data == expected_pen_specific_feed_data


@pytest.fixture
def mock_user_defined_ration_manager(mocker: MockerFixture) -> UserDefinedRationManager:
    user_defined_ration_manager = UserDefinedRationManager()
    return user_defined_ration_manager


def test_ration_to_use(mock_user_defined_ration_manager: UserDefinedRationManager):
    """Unit test for function ration_to_use in file routines/animal/ration/ration_driver.py"""

    # udrm = MagicMock()
    mock_user_defined_ration_manager.lactating_cow_ration = {"1": 100, "2": 200, "3": 300}
    mock_user_defined_ration_manager.close_up_ration = {"1": 10, "2": 20, "3": 30}
    mock_user_defined_ration_manager.growing_ration = {"1": 1, "2": 2, "3": 3}
    mock_user_defined_ration_manager.calf_ration = {"1": 0.1, "2": 0.2, "3": 0.3}

    pen_animal_combo = MagicMock()
    pen_animal_combo.name = "LAC_COW"

    fakefeeds_available = {}
    fakefeeds_available["feed_id"] = [1, 2, 3]

    result = UserDefinedRationManager.ration_to_use(pen_animal_combo)
    assert result == {"1": 100, "2": 200, "3": 300}

    pen_animal_combo.name = "GROWING"
    result = UserDefinedRationManager.ration_to_use(pen_animal_combo)
    assert result == {"1": 1, "2": 2, "3": 3}

    pen_animal_combo.name = "CLOSE_UP"
    result = UserDefinedRationManager.ration_to_use(pen_animal_combo)
    assert result == {"1": 10, "2": 20, "3": 30}

    pen_animal_combo.name = "CALF"
    result = UserDefinedRationManager.ration_to_use(pen_animal_combo)
    assert result == {"1": 0.1, "2": 0.2, "3": 0.3}


def test_make_user_bounds(mock_user_defined_ration_manager: UserDefinedRationManager):
    """Unit test for function make_user_bounds in file routines/animal/ration/ration_optimizer.py"""
    mock_user_defined_ration_manager.tolerance = 0.1
    ration_percents = {"1": 10, "2": 20}
    predicted = [
        [9 / 3, 11 / 3],
        [9 / 3, 11 / 3],
        [9 / 3, 11 / 3],
        [18 / 3, 22 / 3],
        [18 / 3, 22 / 3],
        [18 / 3, 22 / 3],
    ]
    result = RationOptimizer.make_user_bounds(ration_percents, 100)
    # assert that list output is those modified and repeated 3X
    for i in range(len(predicted)):
        assert predicted[i][0] == pytest.approx(result[i][0], 0.1)
        assert predicted[i][1] == pytest.approx(result[i][1], 0.1)


def test_report_ration_supply(mocker: MockerFixture) -> None:
    """Unit test for function report_ration_supply in file routines/animal/ration/ration_driver.py"""
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_ME", return_value=1.0)
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_DE", return_value=1.0)
    mocker.patch(
        "RUFAS.routines.animal.ration.ration_driver.RationReporter.get_NE_maintenance_and_activity", return_value=1.0
    )
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_NE_lactation", return_value=1.0)
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_NE_growth", return_value=1.0)
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_calcium", return_value=1.0)
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_phosphorus", return_value=1.0)
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_fat", return_value=1.0)
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_fat_percentage", return_value=1.0)
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_forage_NDF", return_value=1.0)
    mocker.patch(
        "RUFAS.routines.animal.ration.ration_driver.RationReporter.get_metabolizable_protein", return_value=1.0
    )

    ration = {"1": 1, "2": 2, "3": 3}
    available_feeds = {"1": {}, "2": {}, "3": {}}
    ration_report = {}
    body_weight = 1

    actual = RationReporter.report_ration_supply(ration, available_feeds, ration_report, body_weight)
    expected = {
        "ME": 3.0,
        "DE": 3.0,
        "NE_maintenance_and_activity": 3.0,
        "NE_lactation": 3.0,
        "NE_growth": 3.0,
        "calcium": 3.0,
        "phosphorus": 3.0,
        "fat": 3.0,
        "fat_percentage": 3.0,
        "forage_NDF": 3.0,
        "forage_NDF_percent": 0.5,
        "metabolizable_protein": 1.0,
    }
    assert actual == expected


@pytest.mark.parametrize(
    "ration_report,body_weight,expected",
    [
        ({"nutrient_amount": {"TDN": 0.0}, "nutrient_conc": {"TDN": 100}}, 100, 0.0),
        ({"nutrient_amount": {"TDN": 1}, "nutrient_conc": {"TDN": 100}}, 0.0, 0.0),
        ({"nutrient_amount": {"TDN": 1}, "nutrient_conc": {"TDN": 100}}, 100, 1.0),
        ({"nutrient_amount": {"TDN": 2}, "nutrient_conc": {"TDN": 61}}, 100, 0.9903),
        ({"nutrient_amount": {"TDN": 1}, "nutrient_conc": {"TDN": 59}}, 100, 1.0),
    ],
)
def test_get_TDN_discount(ration_report: dict, body_weight: float, expected: float) -> None:
    """Unit test for function get_TDN_discount in file routines/animal/ration/ration_driver.py"""
    actual = RationReporter.get_TDN_discount(ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


@pytest.mark.parametrize(
    "kg_fed,feed_item_info,ration_report,body_weight,expected",
    [
        ("dummy_variable", {"DE": 2}, "dummy_variable", "dummy_variable", 1.0),
        ("dummy_variable", {"DE": 1}, "dummy_variable", "dummy_variable", 0.5),
        ("dummy_variable", {"DE": 0}, "dummy_variable", "dummy_variable", 0.0),
    ],
)
def test_get_DE(
    kg_fed: float, feed_item_info: dict, ration_report: dict, body_weight: float, expected: float, mocker: MockerFixture
) -> None:
    """Unit test for function get_DE in file routines/animal/ration/ration_driver.py"""
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_TDN_discount", return_value=0.5)
    actual = RationReporter.get_DE(kg_fed, feed_item_info, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


@pytest.mark.parametrize(
    "kg_fed,feed_item_info,ration_report,body_weight,expected",
    [
        (0, {"feed_type": "Mineral"}, "dummy_variable", "dummy_variable", 0.0),
        (1, {"feed_type": "Mineral", "is_fat": True, "DE": 1}, "dummy_variable", "dummy_variable", 0.0),
        (1, {"feed_type": "not_mineral", "is_fat": True, "DE": 1}, "dummy_variable", "dummy_variable", 1.0),
        (1, {"feed_type": "not_mineral", "is_fat": "dummy", "EE": 4}, "dummy_variable", "dummy_variable", 1.5746),
        (1, {"feed_type": "not_mineral", "is_fat": "dummy", "EE": 1}, "dummy_variable", "dummy_variable", 1.57),
    ],
)
def test_get_ME(
    kg_fed: float, feed_item_info: dict, ration_report: dict, body_weight: float, expected: float, mocker: MockerFixture
) -> None:
    """Unit test for function get_ME in file routines/animal/ration/ration_driver.py"""
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_DE", return_value=2)
    actual = RationReporter.get_ME(kg_fed, feed_item_info, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


@pytest.mark.parametrize(
    "kg_fed,feed_item_info,ration_report,body_weight,expected",
    [
        (0, {"is_fat": "dummy"}, "dummy_variable", "dummy_variable", 0.0),
        (1, {"is_fat": True}, "dummy_variable", "dummy_variable", 1.6),
        (1, {"is_fat": False}, "dummy_variable", "dummy_variable", 1.152),
    ],
)
def test_get_NE_maintenance_and_activity(
    kg_fed: float, feed_item_info: dict, ration_report: dict, body_weight: float, expected: float, mocker: MockerFixture
) -> None:
    """Unit test for function get_NE_maintenance_and_activity in file routines/animal/ration/ration_driver.py"""
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_ME", return_value=2)
    actual = RationReporter.get_NE_maintenance_and_activity(kg_fed, feed_item_info, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


@pytest.mark.parametrize(
    "kg_fed,feed_item_info,ration_report,body_weight,expected",
    [
        (1, {"feed_type": "Mineral", "is_fat": "dummy"}, "dummy_variable", "dummy_variable", 0.0),
        (0, {"feed_type": "Mineral", "is_fat": "dummy"}, "dummy_variable", "dummy_variable", 0.0),
        (1, {"feed_type": "dummy", "is_fat": True}, "dummy_variable", "dummy_variable", 1.6),
        (1, {"feed_type": "dummy", "is_fat": False, "EE": 4}, "dummy_variable", "dummy_variable", 1.21996),
        (1, {"feed_type": "dummy", "is_fat": False, "EE": 1}, "dummy_variable", "dummy_variable", 1.216),
        (0, {"feed_type": "dummy", "is_fat": False, "EE": 1}, "dummy_variable", "dummy_variable", 0.0),
    ],
)
def test_get_NE_lactation(
    kg_fed: float, feed_item_info: dict, ration_report: dict, body_weight: float, expected: float, mocker: MockerFixture
) -> None:
    """Unit test for function get_NE_lactation in file routines/animal/ration/ration_driver.py"""
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_DE", return_value=2)
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_ME", return_value=2)
    actual = RationReporter.get_NE_lactation(kg_fed, feed_item_info, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


@pytest.mark.parametrize(
    "kg_fed,feed_item_info,ration_report,body_weight,expected",
    [
        (0, {"feed_type": "Mineral", "is_fat": "dummy"}, "dummy_variable", "dummy_variable", 0.000),
        (0, {"feed_type": "dummy", "is_fat": True}, "dummy_variable", "dummy_variable", 0.0),
        (1, {"feed_type": "Mineral", "is_fat": True}, "dummy_variable", "dummy_variable", 0.0),
        (1, {"feed_type": "dummy", "is_fat": True}, "dummy_variable", "dummy_variable", 1.1),
        (1, {"feed_type": "dummy", "is_fat": False}, "dummy_variable", "dummy_variable", 0.5916),
    ],
)
def test_get_NE_growth(
    kg_fed: float, feed_item_info: dict, ration_report: dict, body_weight: float, expected: float, mocker: MockerFixture
) -> None:
    """Unit test for function get_NE_growth in file routines/animal/ration/ration_driver.py"""
    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_ME", return_value=2)
    actual = RationReporter.get_NE_growth(kg_fed, feed_item_info, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


@pytest.mark.parametrize(
    "kg_fed,feed_item_info,ration_report,body_weight,expected",
    [
        (1, {"feed_type": "Forage", "calcium": 1}, "dummy_variable", "dummy_variable", 0.003),
        (1, {"feed_type": "Conc", "calcium": 1}, "dummy_variable", "dummy_variable", 0.006),
        (1, {"feed_type": "Mineral", "calcium": 1}, "dummy_variable", "dummy_variable", 0.0095),
        (1, {"feed_type": "Forage", "calcium": 0}, "dummy_variable", "dummy_variable", 0.000),
    ],
)
def test_get_calcium(
    kg_fed: float, feed_item_info: dict, ration_report: dict, body_weight: float, expected: float
) -> None:
    """Unit test for function get_Calcium in file routines/animal/ration/ration_driver.py"""
    actual = RationReporter.get_calcium(kg_fed, feed_item_info, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


@pytest.mark.parametrize(
    "kg_fed,feed_item_info,ration_report,body_weight,expected",
    [
        (1, {"feed_type": "Forage", "phosphorus": 1}, "dummy_variable", "dummy_variable", 0.0064),
        (1, {"feed_type": "Conc", "phosphorus": 1}, "dummy_variable", "dummy_variable", 0.007),
        (1, {"feed_type": "Mineral", "phosphorus": 1}, "dummy_variable", "dummy_variable", 0.008),
        (1, {"feed_type": "Forage", "phosphorus": 0}, "dummy_variable", "dummy_variable", 0.000),
    ],
)
def test_get_phosphorus(
    kg_fed: float, feed_item_info: dict, ration_report: dict, body_weight: float, expected: float
) -> None:
    """Unit test for function get_phosphorus in file routines/animal/ration/ration_driver.py"""
    actual = RationReporter.get_phosphorus(kg_fed, feed_item_info, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


@pytest.mark.parametrize(
    "kg_fed,feed_item_info,ration_report,body_weight,expected",
    [
        (1, {"EE": 1}, "dummy_variable", "dummy_variable", 1),
        (1, {"EE": 2}, "dummy_variable", "dummy_variable", 2),
        (2, {"EE": 2}, "dummy_variable", "dummy_variable", 4),
        (1, {"EE": 0}, "dummy_variable", "dummy_variable", 0.0),
    ],
)
def test_get_fat(kg_fed: float, feed_item_info: dict, ration_report: dict, body_weight: float, expected: float) -> None:
    """Unit test for function get_fat in file routines/animal/ration/ration_driver.py"""
    actual = RationReporter.get_fat(kg_fed, feed_item_info, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


@pytest.mark.parametrize(
    "kg_fed,feed_item_info,ration_report,body_weight,expected",
    [
        (1, {"EE": 1}, {"nutrient_amount": {"dm": 100}}, "dummy_variable", 0.01),
        (1, {"EE": 2}, {"nutrient_amount": {"dm": 1}}, "dummy_variable", 2),
        (2, {"EE": 2}, {"nutrient_amount": {"dm": 100}}, "dummy_variable", 0.04),
        (1, {"EE": 0}, {"nutrient_amount": {"dm": 100}}, "dummy_variable", 0.0),
    ],
)
def test_get_fat_percentage(
    kg_fed: float, feed_item_info: dict, ration_report: dict, body_weight: float, expected: float
) -> None:
    """Unit test for function get_fat_percentage in file routines/animal/ration/ration_driver.py"""
    actual = RationReporter.get_fat_percentage(kg_fed, feed_item_info, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


@pytest.mark.parametrize(
    "kg_fed,feed_item_info,ration_report,body_weight,expected",
    [
        (1, {"feed_type": "Forage", "NDF": 1}, "dummy_variable", "dummy_variable", 1),
        (1, {"feed_type": "Conc", "NDF": 2}, "dummy_variable", "dummy_variable", 0.0),
        (1, {"feed_type": "Forage", "NDF": 0}, "dummy_variable", "dummy_variable", 0.0),
        (1, {"feed_type": "Mineral", "NDF": 0}, "dummy_variable", "dummy_variable", 0.0),
    ],
)
def test_get_forage_NDF(
    kg_fed: float, feed_item_info: dict, ration_report: dict, body_weight: float, expected: float
) -> None:
    """Unit test for function get_forage_NDF in file routines/animal/ration/ration_driver.py"""
    actual = RationReporter.get_forage_NDF(kg_fed, feed_item_info, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)


def test_get_metabolizable_protein(mocker: MockerFixture) -> None:
    """Unit test for function get_metabolizable_protein in file routines/animal/ration/ration_driver.py"""
    feed_path_a1 = {"1": {"feed_type": "Conc", "Kd": 1, "N_A": 1, "N_B": 1, "CP": 1, "dRUP": 1}}
    feed_path_a2 = {"2": {"feed_type": "Conc", "Kd": -100, "N_A": 1, "N_B": 1, "CP": 1, "dRUP": 1}}
    feed_path_b1 = {
        "3": {"feed_type": "Forage", "Kd": 1, "N_A": 1, "N_B": 1, "CP": 1, "dRUP": 1, "is_wetforage": False, "NDF": 1}
    }
    feed_path_b2 = {
        "4": {"feed_type": "Forage", "Kd": -100, "N_A": 1, "N_B": 1, "CP": 1, "dRUP": 1, "is_wetforage": False,
              "NDF": 1}
    }
    feed_path_c1 = {
        "5": {"feed_type": "Forage", "Kd": 1, "N_A": 1, "N_B": 1, "CP": 1, "dRUP": 1, "is_wetforage": True, "NDF": 1}
    }
    feed_path_c2 = {
        "6": {"feed_type": "Forage", "Kd": -100, "N_A": 1, "N_B": 1, "CP": 1, "dRUP": 1, "is_wetforage": True, "NDF": 1}
    }
    feed_path_d1 = {
        "7": {"feed_type": "Dummy", "Kd": 1, "N_A": 1, "N_B": 1, "CP": 1, "dRUP": 1, "is_wetforage": False, "NDF": 1}
    }
    feed_path_d2 = {
        "8": {"feed_type": "Dummy", "Kd": -100, "N_A": 1, "N_B": 1, "CP": 1, "dRUP": 1, "is_wetforage": False, "NDF": 1}
    }
    available_feeds = (
        feed_path_a1
        | feed_path_b1
        | feed_path_c1
        | feed_path_d1
        | feed_path_a2
        | feed_path_b2
        | feed_path_c2
        | feed_path_d2
    )
    ration = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8}
    ration_report = {"nutrient_amount": {"TDN": 1}}
    body_weight = 100

    mocker.patch("RUFAS.routines.animal.ration.ration_driver.RationReporter.get_TDN_discount", return_value=1)
    expected = 171.1937767245963
    actual = RationReporter.get_metabolizable_protein(ration, available_feeds, ration_report, body_weight)
    assert np.isclose(actual, expected, rtol=1e-3)
