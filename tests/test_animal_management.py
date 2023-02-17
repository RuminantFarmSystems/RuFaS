"""
RUFAS: Ruminant Farm Systems Model
File name: test_animal_management.py
Description: Implements test cases for the AnimalManagement class
Author(s): Pooya Hekmati, sh2235@cornell.edu, Anchey Peng, ap724@cornell.edu
"""

from typing import List, Dict, Union, Any
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock.plugin import MockerFixture

from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.pen import Pen


def create_mock_object_list(attribute_dicts: List[Dict[str, Any]]) -> List[MagicMock]:
    mock_object_list = []

    for attribute_dict in attribute_dicts:
        mock_object = MagicMock()

        for attribute, value in attribute_dict.items():
            setattr(mock_object, attribute, value)

        mock_object_list.append(mock_object)

    return mock_object_list


@pytest.fixture
def mock_pens() -> List[MagicMock]:
    pen_attribute_dicts = [
        {
            "id": 0,
            "vertical_dist_to_parlor": 1.0,
            "horizontal_dist_to_parlor": 2.0,
            "stocking_density": 1.075,
            "num_stalls": 200,
            "animals_in_pen": [100000, 100001]
        },
        {
            "id": 1,
            "vertical_dist_to_parlor": 5.0,
            "horizontal_dist_to_parlor": 10.0,
            "stocking_density": 1.075,
            "num_stalls": 50,
            "animals_in_pen": [200000, 200001]
        },
        {
            "id": 2,
            "vertical_dist_to_parlor": 4.0,
            "horizontal_dist_to_parlor": 8.0,
            "stocking_density": 1.075,
            "num_stalls": 200,
            "animals_in_pen": [300000, 300001]
        },
        {
            "id": 3,
            "vertical_dist_to_parlor": 2.0,
            "horizontal_dist_to_parlor": 4.0,
            "stocking_density": 1.075,
            "num_stalls": 200,
            "animals_in_pen": [400000, 400001]
        },
    ]

    return create_mock_object_list(pen_attribute_dicts)


@pytest.fixture
def mock_pen_data() -> Dict[str, Dict[str, Union[str, float, int]]]:
    return {
        "pen0": {
            "id": 0,
            "animal_combination": "CALF",
            "vertical_dist_to_milking_parlor": 0.1,
            "horizontal_dist_to_milking_parlor": 1.6,
            "number_of_stalls": 110,
            "housing_type": "open air barn",
            "bedding_type": "sand",
            "pen_type": "freestall",
            "manure_handling": "manual_scraping",
            "manure_separator": "sedimentation",
            "manure_storage": "storage_pit",
            "max_stocking_density": 1.2
        },
        "pen1": {
            "id": 1,
            "animal_combination": "GROWING",
            "vertical_dist_to_milking_parlor": 0.1,
            "horizontal_dist_to_milking_parlor": 1.6,
            "number_of_stalls": 800,
            "housing_type": "open air barn",
            "bedding_type": "organic",
            "pen_type": "freestall",
            "manure_handling": "flush_system",
            "manure_separator": "sedimentation",
            "manure_storage": "storage_pit",
            "max_stocking_density": 1.2
        },
        "pen2": {
            "id": 2,
            "animal_combination": "CLOSE_UP",
            "vertical_dist_to_milking_parlor": 0.1,
            "horizontal_dist_to_milking_parlor": 1.6,
            "number_of_stalls": 200,
            "housing_type": "open air barn",
            "bedding_type": "organic",
            "pen_type": "tiestall",
            "manure_handling": "automatic_alley_scrapers",
            "manure_separator": "sedimentation",
            "manure_storage": "storage_pit",
            "max_stocking_density": 1.2
        },
        "pen3": {
            "id": 3,
            "animal_combination": "LAC_COW",
            "vertical_dist_to_milking_parlor": 0.1,
            "horizontal_dist_to_milking_parlor": 1.6,
            "number_of_stalls": 850,
            "housing_type": "open air barn",
            "bedding_type": "sand",
            "pen_type": "tiestall",
            "manure_handling": "manual_scraping",
            "manure_separator": "sedimentation",
            "manure_storage": "anaerobic_lagoon",
            "max_stocking_density": 1.2
        }
    }


@pytest.fixture()
def mock_animals_small() -> List[MagicMock]:
    animal_attribute_dicts = [
        {
            "body_weight": 5.0,
            "p_animal": 7.0
        },
        {
            "body_weight": 1.0,
            "p_animal": 8.0
        },
        {
            "body_weight": 2.0,
            "p_animal": 1.0
        },
    ]

    return create_mock_object_list(animal_attribute_dicts)


@pytest.fixture
def mock_herd_data() -> Dict[str, Union[str, int, bool]]:
    return {
        "calf_num": 80,
        "heiferI_num": 440,
        "heiferII_num": 380,
        "heiferIII_num": 50,
        "cow_num": 1000,
        "replace_num": 5000,
        "herd_num": 1000,
        "herd_init": False,
        "breed": "HO"
    }


@pytest.fixture
def animal_management() -> AnimalManagement:
    init_pens_patch = patch('RUFAS.routines.animal.animal_management.AnimalManagement.init_pens')
    init_animals_patch = patch('RUFAS.routines.animal.animal_management.AnimalManagement.init_animals')
    init_nutrient_rqmts_patch = patch('RUFAS.routines.animal.animal_management.AnimalManagement.init_nutrient_rqmts')
    init_allocate_all_pens_patch = patch('RUFAS.routines.animal.animal_management.AnimalManagement.allocate_all_pens')

    init_pens_patch.start()
    init_animals_patch.start()
    init_nutrient_rqmts_patch.start()
    init_allocate_all_pens_patch.start()

    data = MagicMock()
    config = MagicMock()
    feed = MagicMock()
    weather = MagicMock()
    time = MagicMock()

    animal_management = AnimalManagement(data, config, feed, weather, time)

    init_pens_patch.stop()
    init_animals_patch.stop()
    init_nutrient_rqmts_patch.stop()
    init_allocate_all_pens_patch.stop()

    return animal_management


@pytest.fixture
def animal_management_with_mock_pens(animal_management: AnimalManagement,
                                     mock_pens: List[MagicMock]) -> AnimalManagement:
    animal_management.all_pens = mock_pens
    return animal_management


def test_daily_animal_routine():
    """Unit test for function daily_animal_routine in file routines/animal/animal_management.py"""
    pass


def test_get_animal_config():
    """Unit test for function get_animal_config in file routines/animal/animal_management.py"""
    pass


def test_init_pens(animal_management: AnimalManagement, mock_pen_data: Dict[str, Dict[str, Union[str, float, int]]],
                   mock_herd_data: Dict[str, Union[str, int, bool]], mocker: MockerFixture) -> None:
    """Unit test for function init_pens in file routines/animal/animal_management.py"""

    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement._init_default_pens')

    # More than the minimum num of pens - 4 pens
    animal_management.init_pens(mock_pen_data, mock_herd_data)

    actual = len(animal_management.all_pens)
    expected = 4
    assert actual == expected

    animal_management._init_default_pens.assert_called_once()


def test_init_default_pens(animal_management: AnimalManagement) -> None:
    # Less than the minimum num of pens - 0 pens
    # MIN_NUM_PENS default pens should be created

    animal_management.all_pens = []
    animal_management._init_default_pens(1)

    actual = len(animal_management.all_pens)
    expected = animal_management.MIN_NUM_PENS
    assert actual == expected


def test_init_animals(animal_management: AnimalManagement, mocker: MockerFixture):
    """Unit test for function init_animals in file routines/animal/animal_management.py"""

    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.LifeCycleManager.initialize_herd',
                 return_value=[None, None, None, None, None])
    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement._print_animal_num_warnings')

    herd_data = MagicMock()
    config = MagicMock()

    animal_management.init_animals(herd_data, config)

    animal_management.life_cycle_manager.initialize_herd.assert_called_once()


def test_print_animal_num_warnings(animal_management: AnimalManagement):
    """Unit test for function _print_animal_num_warnings in file routines/animal/animal_management.py"""
    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log, \
            patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:

        animal_keys = {"calf_num", "heiferI_num", "heiferII_num", "heiferIII_num", "cow_num"}
        herd_data = dict()

        expected_info_map = {
            "class": "AnimalManagement",
            "function": "_print_animal_num_warnings",
            "herd_data": herd_data
        }

        # test for simulate_animals = True
        animal_management.simulate_animals = True
        animal_management._print_animal_num_warnings(herd_data)
        add_log.assert_called_once_with("simulate_animals_flag",
                                        "simulate_animals is true",
                                        expected_info_map)

        # test for warnings for every animal key and simulate_animals = False
        animal_management.simulate_animals = False
        for key in animal_keys:
            herd_data[key] = 1
        animal_management._print_animal_num_warnings(herd_data)

        for key in animal_keys:
            add_warning.assert_any_call(f"invalid_{key}_warning",
                                        f"Warning: herd_num is 0, but {key} is not.",
                                        expected_info_map)

        # question: how to reset assert_called_once with
        add_log.assert_any_call("num_warnings_associated_with_simulate_animals",
                                f"{len(animal_keys)} warnings were associated with simulate_animals",
                                expected_info_map)

        assert add_warning.call_count == len(animal_keys)
        assert add_log.call_count == 2


def test_init_nutrient_rqmts():
    """Unit test for function init_nutrient_rqmts in file routines/animal/animal_management.py"""
    pass


def test_avg_pen_dist(animal_management_with_mock_pens: AnimalManagement) -> None:
    """Unit test for function avg_pen_dist in file routines/animal/animal_management.py"""

    actual = animal_management_with_mock_pens.avg_pen_dist()
    expected = (12 / 4, 24 / 4)

    assert actual == pytest.approx(expected)


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/animal_management.py"""
    pass


def test_fully_update_animal_to_pen_id_map():
    """Unit test for function fully_update_animal_to_pen_id_map in file routines/animal/animal_management.py"""
    pass


@pytest.fixture()
def setup_dummy_animal(animal_id):
    args_dict = {'breed': 'dummy_breed', 'birth_date': 'dummy_birth_date', 'days_born': 'dummy_days_born',
                 'id': animal_id}
    config_dict = {'semen_type': 'dummy_semen_type'}

    AnimalBase.set_config(config_dict)
    dummy_animal = AnimalBase(args_dict)

    return dummy_animal


@pytest.fixture()
def setup_dummy_pen(pen_id, num_stalls, animal_list):
    dummy_pen_info_dict = {'vertical_dist_to_milking_parlor': 'dummy_vertical_dist_to_milking_parlor',
                           'horizontal_dist_to_milking_parlor': 'dummy_horizontal_dist_to_milking_parlor',
                           'housing_type': 'dummy_housing_type', 'bedding_type': 'dummy_bedding_type',
                           'pen_type': 'dummy_pen_type', 'manure_handling': 'dummy_manure_handling',
                           'manure_separator': 'dummy_manure_separator', 'manure_storage': 'dummy_manure_storage',
                           'animal_combination': 'dummy_animal_combination',
                           'max_stocking_density': 'dummy_max_stocking_density', 'id': pen_id,
                           'number_of_stalls': num_stalls}

    dummy_pen = Pen(dummy_pen_info_dict['id'], dummy_pen_info_dict['vertical_dist_to_milking_parlor'],
                    dummy_pen_info_dict['horizontal_dist_to_milking_parlor'],
                    dummy_pen_info_dict['number_of_stalls'],
                    dummy_pen_info_dict['housing_type'], dummy_pen_info_dict['bedding_type'],
                    dummy_pen_info_dict['pen_type'], dummy_pen_info_dict['manure_handling'],
                    dummy_pen_info_dict['manure_separator'], dummy_pen_info_dict['manure_storage'],
                    dummy_pen_info_dict['animal_combination'], dummy_pen_info_dict['max_stocking_density'])

    dummy_pen.animals_in_pen = animal_list

    return dummy_pen


def pen_removal_info_dicts():
    return [
        {
            "pen_data":
                {"pen0":
                     {"pen_id": 0, "ids_in_pen": [128382, 173829, 183920, 113803, 120462],
                      "expected_stocking_density": 0.5, "num_stalls": 8},
                 "pen1":
                     {"pen_id": 1, "ids_in_pen": [149495, 189237, 128193, 145927, 156253],
                      "expected_stocking_density": 0.5, "num_stalls": 8},
                 "pen2":
                     {"pen_id": 2, "ids_in_pen": [161832, 182729, 162719, 152394, 182938],
                      "expected_stocking_density": 0.5, "num_stalls": 8},
                 "pen3":
                     {"pen_id": 3, "ids_in_pen": [217892, 182738, 128374, 101239, 118389],
                      "expected_stocking_density": 0.5, "num_stalls": 8}
                 },
            "removal_set":
                {113803, 145927, 152394, 101239},
            "expected_map":
                {128382: 0, 173829: 0, 183920: 0, 120462: 0, 149495: 1, 189237: 1, 128193: 1, 156253: 1,
                 161832: 2, 182729: 2, 162719: 2, 182938: 2, 217892: 3, 182738: 3, 128374: 3, 118389: 3}
        }
    ]


@pytest.mark.parametrize("info_dict", pen_removal_info_dicts())
def test_remove_animals_from_herd(info_dict, animal_management) -> None:
    animals_removed = []
    pen_list = []
    for pen_num in info_dict['pen_data']:
        animal_list = []
        for animal_id in info_dict['pen_data'][pen_num]["ids_in_pen"]:
            dummy_animal = setup_dummy_animal(animal_id)
            animal_list.append(dummy_animal)
            animal_management.animal_to_pen_id_map[dummy_animal.id] = info_dict['pen_data'][pen_num]['pen_id']
            if dummy_animal.id in info_dict['removal_set']:
                animals_removed.append(dummy_animal)

        dummy_pen = setup_dummy_pen(info_dict['pen_data'][pen_num]['pen_id'],
                                    info_dict['pen_data'][pen_num]['num_stalls'],
                                    animal_list)

        dummy_pen.animals_in_pen = animal_list

        pen_list.append(dummy_pen)

    animal_management.all_pens = pen_list

    animal_management.remove_animals_from_herd(animals_removed)

    assert animal_management.animal_to_pen_id_map == info_dict['expected_map']
    assert animal_management.all_pens[0].stocking_density == info_dict['pen_data']['pen0']['expected_stocking_density']
    assert animal_management.all_pens[1].stocking_density == info_dict['pen_data']['pen1']['expected_stocking_density']
    assert animal_management.all_pens[2].stocking_density == info_dict['pen_data']['pen2']['expected_stocking_density']
    assert animal_management.all_pens[3].stocking_density == info_dict['pen_data']['pen3']['expected_stocking_density']


# pen_population_before_additions = [None] * len(self.all_pens)
#
# for index, pen in enumerate(self.all_pens):
#     pen_population_before_additions[index] = len(pen.animals_in_pen)
#
# return pen_population_before_additions


def test_track_former_pen_population(animal_management) -> None:
    """Unit test for function track_former_pen_population in file routines/animal/animal_management.py"""
    dummy_pen_info_dict = {
        'vertical_dist_to_milking_parlor': 'dummy_vertical_dist_to_milking_parlor',
        'horizontal_dist_to_milking_parlor': 'dummy_horizontal_dist_to_milking_parlor',
        'housing_type': 'dummy_housing_type',
        'bedding_type': 'dummy_bedding_type', 'pen_type': 'dummy_pen_type',
        'manure_handling': 'dummy_manure_handling', 'manure_separator': 'dummy_manure_separator',
        'manure_storage': 'dummy_manure_storage', 'animal_combination': 'dummy_animal_combination',
        'max_stocking_density': 'dummy_max_stocking_density'
    }

    pass


def test_calculate_pen_rations():
    """Unit test for function calculate_pen_rations in file routines/animal/animal_management.py"""
    pass


def test_daily_update_id_map():
    """Unit test for function daily_update_id_map in file routines/animal/animal_management.py"""
    pass


def test_allocate_all_pens():
    """Unit test for function allocate_all_pens in file routines/animal/animal_management.py"""
    pass


def test_clear_pens(animal_management_with_mock_pens: AnimalManagement) -> None:
    """Unit test for function clear_pens in file routines/animal/animal_management.py"""
    animal_management_with_mock_pens.clear_pens()

    for pen in animal_management_with_mock_pens.all_pens:
        pen.clear.assert_called_once()


def test_calc_avg_nutrient_rqmts():
    """Unit test for function calc_avg_nutrient_rqmts in file routines/animal/animal_management.py"""
    pass


def test_calc_ration():
    """Unit test for function calc_ration in file routines/animal/animal_management.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/animal_management.py"""
    pass


def test_calc_avg_growth(animal_management_with_mock_pens: AnimalManagement) -> None:
    """Unit test for function calc_avg_growth in file routines/animal/animal_management.py"""

    animal_management_with_mock_pens.calc_avg_growth()

    for pen in animal_management_with_mock_pens.all_pens:
        pen.calc_avg_growth.assert_called_once()

    pass


def test_record_pen_history():
    """Unit test for function record_pen_history in file routines/animal/animal_management.py"""
    pass


def test_calc_p_conc(mock_animals_small: List[MagicMock]) -> None:
    """Unit test for function _calc_p_conc in file routines/animal/animal_management.py"""
    expected = 0
    actual = AnimalManagement._calc_p_conc([])
    assert actual == expected

    actual = AnimalManagement._calc_p_conc(mock_animals_small)
    expected = (16.0 / 8.0) / 1000.0

    assert actual == pytest.approx(expected)


def test_calc_all_p_conc():
    """Unit test for function calc_all_p_conc in file routines/animal/animal_management.py"""
    pass


def test_calc_p_rqmts():
    """Unit test for function calc_p_rqmts in file routines/animal/animal_management.py"""
    pass


def test_daily_p_update():
    """Unit test for function daily_p_update in file routines/animal/animal_management.py"""
    pass


def test_daily_updates():
    """Unit test for function daily_updates in file routines/animal/animal_management.py"""
    pass


def test_end_ration_interval():
    """Unit test for function end_ration_interval in file routines/animal/animal_management.py"""
    pass


def test_annual_reset():
    """Unit test for function annual_reset in file routines/animal/animal_management.py"""
    pass


def test_generate_animal_output():
    """Unit test for function generate_animal_output in file routines/animal/animal_management.py"""
    pass


def test_get_life_cycle_output():
    """Unit test for function get_life_cycle_output in file routines/animal/animal_management.py"""
    pass


def test_get_initialize_db_summary():
    """Unit test for function get_initialize_db_summary in file routines/animal/animal_management.py"""
    pass
