"""
RUFAS: Ruminant Farm Systems Model
File name: test_animal_management.py
Description: Implements test cases for the AnimalManagement class
Author(s): Pooya Hekmati, sh2235@cornell.edu, Anchey Peng, ap724@cornell.edu
"""

import pytest
from unittest.mock import MagicMock, patch
from pytest_mock.plugin import MockerFixture

from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.output_manager import OutputManager

from typing import List, Dict, Union

import io
import sys

from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.pen import Pen


def create_mock_object_list(attribute_dicts: List[Dict]) -> List[MagicMock]:
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
            "vertical_dist_to_parlor": 1.0,
            "horizontal_dist_to_parlor": 2.0
        },
        {
            "vertical_dist_to_parlor": 5.0,
            "horizontal_dist_to_parlor": 10.0
        },
        {
            "vertical_dist_to_parlor": 4.0,
            "horizontal_dist_to_parlor": 8.0
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
            "pen_type": "freestall",
            "max_stocking_density": 1.2,
            "manure_management_scenario_id": 0
        },
        "pen1": {
            "id": 1,
            "animal_combination": "GROWING",
            "vertical_dist_to_milking_parlor": 0.1,
            "horizontal_dist_to_milking_parlor": 1.6,
            "number_of_stalls": 800,
            "housing_type": "open air barn",
            "pen_type": "freestall",
            "max_stocking_density": 1.2,
            "manure_management_scenario_id": 1
        },
        "pen2": {
            "id": 2,
            "animal_combination": "CLOSE_UP",
            "vertical_dist_to_milking_parlor": 0.1,
            "horizontal_dist_to_milking_parlor": 1.6,
            "number_of_stalls": 200,
            "housing_type": "open air barn",
            "pen_type": "tiestall",
            "max_stocking_density": 1.2,
            "manure_management_scenario_id": 2
        },
        "pen3": {
            "id": 3,
            "animal_combination": "LAC_COW",
            "vertical_dist_to_milking_parlor": 0.1,
            "horizontal_dist_to_milking_parlor": 1.6,
            "number_of_stalls": 850,
            "housing_type": "open air barn",
            "pen_type": "tiestall",
            "max_stocking_density": 1.2,
            "manure_management_scenario_id": 3
        }
    }


@pytest.fixture
def mock_manure_management_scenarios() -> List[Dict[str, Union[str, int]]]:
    return [
        {
            "scenario_id": 0,
            "bedding_type": "sawdust",
            "manure_handler": "manual scraping",
            "manure_separator": "none",
            "manure_treatment": "slurry storage underfloor"
        },
        {
            "scenario_id": 1,
            "bedding_type": "sawdust",
            "manure_handler": "manual scraping",
            "manure_separator": "none",
            "manure_treatment": "slurry storage outdoor"
        },
        {
            "scenario_id": 2,
            "bedding_type": "sawdust",
            "manure_handler": "manual scraping",
            "manure_separator": "screw press",
            "manure_treatment": "slurry storage outdoor"
        },
        {
            "scenario_id": 3,
            "bedding_type": "sawdust",
            "manure_handler": "flush system",
            "manure_separator": "none",
            "manure_treatment": "anaerobic lagoon"
        },
        {
            "scenario_id": 4,
            "bedding_type": "sand",
            "manure_handler": "flush system",
            "manure_separator": "sand lane",
            "manure_treatment": "anaerobic lagoon"
        },
        {
            "scenario_id": 5,
            "bedding_type": "sawdust",
            "manure_handler": "manual scraping",
            "manure_separator": "none",
            "manure_treatment": "anaerobic digestion and lagoon"
        },
        {
            "scenario_id": 6,
            "bedding_type": "sawdust",
            "manure_handler": "flush system",
            "manure_separator": "rotary screen",
            "manure_treatment": "anaerobic digestion and lagoon"
        },
        {
            "scenario_id": 7,
            "bedding_type": "sawdust",
            "manure_handler": "flush system",
            "manure_separator": "rotary screen",
            "manure_treatment": "anaerobic digestion and lagoon with split"
        }
    ]


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
                   mock_herd_data: Dict[str, Union[str, int, bool]],
                   mock_manure_management_scenarios: Dict[str, List[Dict[str, Union[str, int]]]],
                   mocker: MockerFixture) -> None:
    """Unit test for function init_pens in file routines/animal/animal_management.py"""
    # Arrange
    patch_for_init_default_pens = mocker.patch.object(animal_management, '_init_default_pens')

    # Act
    # More than the minimum num of pens - 4 pens
    animal_management.init_pens(mock_pen_data, mock_herd_data, mock_manure_management_scenarios)

    actual = len(animal_management.all_pens)
    expected = 4

    # Assert
    assert actual == expected
    patch_for_init_default_pens.assert_called_once_with(mock_herd_data['herd_num'])


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


def test_print_animal_num_warnings(animal_management: AnimalManagement, mocker: MockerFixture):
    """Unit test for function _print_animal_num_warnings in file routines/animal/animal_management.py"""
    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log, \
            patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:

        animal_keys = {"calf_num", "heiferI_num", "heiferII_num", "heiferIII_num", "cow_num"}
        herd_data = {
            "calf_num": 0,
            "heiferI_num": 0,
            "heiferII_num": 0,
            "heiferIII_num": 0,
            "cow_num": 0
        }

        expected_info_map = {
            "class": "AnimalManagement",
            "function": "_print_animal_num_warnings",
            "herd_data_animal_nums": {
                "calf_num": 0,
                "heiferI_num": 0,
                "heiferII_num": 0,
                "heiferIII_num": 0,
                "cow_num": 0
            },
            "simulate_animals": True
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
            expected_info_map['herd_data_animal_nums'][key] = 1
        expected_info_map['simulate_animals'] = False

        animal_management._print_animal_num_warnings(herd_data)

        for key in animal_keys:
            add_warning.assert_any_call(f"invalid_{key}_warning",
                                        f"Warning: simulate_animals is false, but {key} is not.",
                                        expected_info_map)

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
    expected = (10 / 3, 20 / 3)

    assert actual == pytest.approx(expected)


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/animal_management.py"""
    pass


def test_fully_update_id_pen():
    """Unit test for function fully_update_id_pen in file routines/animal/animal_management.py"""
    pass


def test_daily_update_id_pen():
    """Unit test for function daily_update_id_pen in file routines/animal/animal_management.py"""
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


@pytest.fixture
def mock_animals() -> List[MagicMock]:
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


def test_calc_p_conc(mock_animals: List[MagicMock]) -> None:
    """Unit test for function _calc_p_conc in file routines/animal/animal_management.py"""
    expected = 0
    actual = AnimalManagement._calc_p_conc([])
    assert actual == expected

    actual = AnimalManagement._calc_p_conc(mock_animals)
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


def test_get_lactating_cows(mocker: MockerFixture) -> None:
    """Unit test for function _get_lactating_cows in file routines/animal/animal_management.py"""
    # Arrange
    num_cows = 10
    num_lactating_cows = 5
    cows: List[Cow] = []
    for i in range(num_cows):
        cow = mocker.MagicMock(spec=Cow)
        cow.milking = i % 2 == 0
        cows.append(cow)

    # Act
    lactating_cows = AnimalManagement._get_lactating_cows(cows)

    # Assert
    assert len(lactating_cows) == num_lactating_cows
    for i in range(num_lactating_cows):
        assert lactating_cows[i] == cows[i * 2]


def test_get_dry_cows(mocker: MockerFixture) -> None:
    """Unit test for function _get_dry_cows in file routines/animal/animal_management.py"""
    # Arrange
    num_cows = 10
    num_dry_cows = 5
    cows: List[Cow] = []
    for i in range(num_cows):
        cow = mocker.MagicMock(spec=Cow)
        cow.milking = i % 2 == 0
        cows.append(cow)

    # Act
    dry_cows = AnimalManagement._get_dry_cows(cows)

    # Assert
    assert len(dry_cows) == num_dry_cows
    for i in range(num_dry_cows):
        assert dry_cows[i] == cows[i * 2 + 1]


def test_group_pens_by_animal_combination(mocker: MockerFixture) -> None:
    """Unit test for function group_pens_by_animal_combination in file routines/animal/animal_management.py"""
    # Arrange
    pens: List[Pen] = []
    animal_combinations = [
        Pen.AnimalCombination.CALF,
        Pen.AnimalCombination.GROWING,
        Pen.AnimalCombination.GROWING_AND_CLOSE_UP,
        Pen.AnimalCombination.LAC_COW,
        Pen.AnimalCombination.NONE,
        Pen.AnimalCombination.CLOSE_UP,
    ]
    num_groups = len(animal_combinations)
    num_pens_per_group = 3
    num_pens = num_groups * num_pens_per_group
    for i in range(num_pens):
        pen = mocker.MagicMock(spec=Pen)
        pen.animal_combination = animal_combinations[i % num_groups]
        pens.append(pen)

    # Act
    pen_groups = AnimalManagement._group_pens_by_animal_combination(pens)

    # Assert
    assert len(pen_groups) == num_groups
    for i in range(num_groups):
        assert len(pen_groups[animal_combinations[i]]) == num_pens_per_group
        for j in range(num_pens_per_group):
            assert pen_groups[animal_combinations[i]][j] == pens[j * num_groups + i]


def test_calculate_total_maximum_stocking_density(mocker: MockerFixture) -> None:
    """Unit test for function calculate_total_maximum_stocking_density in file routines/animal/animal_management.py"""
    # Arrange
    num_pens = 10
    pens: List[Pen] = []
    expected_total_maximum_stocking_density = 0
    for i in range(num_pens):
        pen = mocker.MagicMock(spec=Pen)
        pen.num_stalls = num_stalls = i + 1
        pen.max_stocking_density = max_stocking_density = (i + 2) * 1.5
        pens.append(pen)
        expected_total_maximum_stocking_density += num_stalls * max_stocking_density

    # Act
    total_maximum_stocking_density = AnimalManagement._calculate_total_maximum_stocking_density(pens)

    # Assert
    assert total_maximum_stocking_density == int(expected_total_maximum_stocking_density)


@pytest.mark.parametrize(
    'num_animals, total_max_stocking_density, expected_stall_shortage',
    [
        (100, 100, 0),
        (100, 101, -1),
        (100, 99, 1)
    ]
)
def test_calculate_stall_shortage(num_animals: int,
                                  total_max_stocking_density: int,
                                  expected_stall_shortage: int,
                                  mocker: MockerFixture) -> None:
    """Unit test for function calculate_stall_shortage in file routines/animal/animal_management.py"""
    # Arrange
    mock_pens = mocker.MagicMock(spec=List[Pen])
    patch_for_calculate_total_maximum_stocking_density = mocker.patch.object(
        AnimalManagement,
        '_calculate_total_maximum_stocking_density',
        return_value=total_max_stocking_density
    )

    # Act
    stall_shortage = AnimalManagement._calculate_stall_shortage(num_animals, mock_pens)

    # Assert
    assert stall_shortage == expected_stall_shortage
    patch_for_calculate_total_maximum_stocking_density.assert_called_once_with(mock_pens)


def test_calculate_stall_shortages_for_main_combinations(mocker: MockerFixture) -> None:
    """Unit test for function calculate_stall_shortages_for_main_combinations in file routines/animal/animal_management.py"""
    mock_calf_pens = mocker.MagicMock(spec=List[Pen])
    mock_growing_pens = mocker.MagicMock(spec=List[Pen])
    mock_close_up_pens = mocker.MagicMock(spec=List[Pen])
    mock_lac_cow_pens = mocker.MagicMock(spec=List[Pen])
    mock_pens_by_animal_combination = {
        Pen.AnimalCombination.CALF: mock_calf_pens,
        Pen.AnimalCombination.GROWING: mock_growing_pens,
        Pen.AnimalCombination.CLOSE_UP: mock_close_up_pens,
        Pen.AnimalCombination.LAC_COW: mock_lac_cow_pens,
    }

    num_calves = 10
    num_heiferIs = 20
    num_heiferIIs = 30
    num_heiferIIIs = 40
    num_dry_cows = 24
    num_lactating_cows = 26

    stall_shortages_dict = {
        (num_calves, mock_calf_pens): 11,
        (num_heiferIs + num_heiferIIs, mock_growing_pens): 21,
        (num_heiferIIIs + num_dry_cows, mock_close_up_pens): 31,
        (num_lactating_cows, mock_lac_cow_pens): 41,
    }

    expected_stall_shortages = {
        Pen.AnimalCombination.CALF: stall_shortages_dict[(num_calves, mock_calf_pens)],
        Pen.AnimalCombination.GROWING: stall_shortages_dict[(num_heiferIs + num_heiferIIs, mock_growing_pens)],
        Pen.AnimalCombination.CLOSE_UP: stall_shortages_dict[(num_heiferIIIs + num_dry_cows, mock_close_up_pens)],
        Pen.AnimalCombination.LAC_COW: stall_shortages_dict[(num_lactating_cows, mock_lac_cow_pens)],
    }

    patch_for_calculate_stall_shortage = mocker.patch.object(
        AnimalManagement,
        '_calculate_stall_shortage',
        side_effect=lambda num_animals, pens: stall_shortages_dict[(num_animals, pens)]
    )

    # Act
    actual_stall_storages = \
        AnimalManagement._calculate_stall_shortages_for_main_animal_combinations(
            mock_pens_by_animal_combination,
            num_calves,
            num_heiferIs,
            num_heiferIIs,
            num_heiferIIIs,
            num_dry_cows,
            num_lactating_cows,
        )

    # Assert
    assert actual_stall_storages == expected_stall_shortages
    patch_for_calculate_stall_shortage.assert_has_calls([
        mocker.call(num_animals=num_calves, pens=mock_calf_pens),
        mocker.call(num_animals=num_heiferIs + num_heiferIIs, pens=mock_growing_pens),
        mocker.call(num_animals=num_heiferIIIs + num_dry_cows, pens=mock_close_up_pens),
        mocker.call(num_animals=num_lactating_cows, pens=mock_lac_cow_pens),
    ])


@pytest.mark.parametrize(
    'animal_combination',
    [
        Pen.AnimalCombination.CALF,
        Pen.AnimalCombination.GROWING,
        Pen.AnimalCombination.CLOSE_UP,
        Pen.AnimalCombination.LAC_COW
    ]
)
def test_create_default_pen(animal_combination: Pen.AnimalCombination,
                            mocker: MockerFixture) -> None:
    """Unit test for function _create_default_pen() in file routines/animal/animal_management.py"""
    # Arrange
    num_stalls = 10
    pen_id = 1

    mock_pen = mocker.MagicMock(spec=Pen)
    patch_for_pen_init = mocker.patch(
        'RUFAS.routines.animal.animal_management.Pen',
        return_value=mock_pen
    )

    # Act
    pen = AnimalManagement._create_default_pen(pen_id, num_stalls, animal_combination)

    # Assert
    assert pen == mock_pen
    patch_for_pen_init.assert_called_once_with(
        pen_id=pen_id,
        vertical_dist_to_milking_parlor=0.1,
        horizontal_dist_to_milking_parlor=1.6,
        number_of_stalls=num_stalls,
        housing_type='open air barn',
        bedding_type='straw',
        pen_type='tiestall',
        manure_handling='manual_scraping',
        manure_separator='sedimentation',
        manure_storage='storage_pit',
        animal_combination=animal_combination,
        max_stocking_density=1.2
    )


def test_remove_items_from_dicts_by_id() -> None:
    """Unit test for function _remove_items_from_dicts_by_id() in file routines/animal/animal_management.py"""
    # Case 1: Given empty list of dictionaries, then nothing should be removed
    # Arrange
    item_id = 1
    dicts = []

    # Act
    AnimalManagement._remove_items_from_dicts_by_id(item_id, dicts)

    # Assert
    assert dicts == []

    # -------------------------------------------------------------------------
    # Case 2: Given list of dictionaries, then those dictionaries that contain
    #         the given item_id should be removed
    # Arrange
    item_id = 1
    dicts = [
        {1: 'a', 2: 'b'},
        {3: 'c', 4: 'd'},
        {1: 'e', 5: 'f'},
    ]

    # Act
    AnimalManagement._remove_items_from_dicts_by_id(item_id, dicts)

    # Assert
    assert dicts == [
        {2: 'b'},
        {3: 'c', 4: 'd'},
        {5: 'f'},
    ]

    # -------------------------------------------------------------------------
    # Case 3: Given list of dictionaries, if no dictionary contains the given
    #         item_id, then nothing should be removed
    # Arrange
    item_id = 1
    dicts = [
        {2: 'b'},
        {3: 'c', 4: 'd'},
        {5: 'f'},
    ]

    # Act
    AnimalManagement._remove_items_from_dicts_by_id(item_id, dicts)

    # Assert
    assert dicts == [
        {2: 'b'},
        {3: 'c', 4: 'd'},
        {5: 'f'},
    ]


@pytest.mark.parametrize(
    'animal_combination',
    [
        Pen.AnimalCombination.CALF,
        Pen.AnimalCombination.GROWING,
        Pen.AnimalCombination.CLOSE_UP,
        Pen.AnimalCombination.LAC_COW,
        Pen.AnimalCombination.NONE,
        Pen.AnimalCombination.GROWING_AND_CLOSE_UP
    ]
)
def test_update_stall_shortage_for_animal_combination(animal_combination: Pen.AnimalCombination,
                                                      mocker: MockerFixture) -> None:
    """Unit test for function _update_stall_shortage_for_animal_combination() in file routines/animal/animal_management.py"""
    mock_pen = mocker.MagicMock(spec=Pen)
    current_stall_shortage_for_calf = 20
    current_stall_shortage_for_growing = 30
    current_stall_shortage_for_close_up = 40
    current_stall_shortage_for_lac_cow = 50

    mock_stall_shortages = {
        Pen.AnimalCombination.CALF: current_stall_shortage_for_calf,
        Pen.AnimalCombination.GROWING: current_stall_shortage_for_growing,
        Pen.AnimalCombination.CLOSE_UP: current_stall_shortage_for_close_up,
        Pen.AnimalCombination.LAC_COW: current_stall_shortage_for_lac_cow,
    }
    mock_stall_shortages_copy = mock_stall_shortages.copy()

    total_max_stocking_density = 10
    patch_for_calculate_total_maximum_stocking_density = mocker.patch(
        'RUFAS.routines.animal.animal_management.AnimalManagement._calculate_total_maximum_stocking_density',
        return_value=total_max_stocking_density
    )

    all_expected_stall_shortages = {
        Pen.AnimalCombination.CALF: current_stall_shortage_for_calf - total_max_stocking_density,
        Pen.AnimalCombination.GROWING: current_stall_shortage_for_growing - total_max_stocking_density,
        Pen.AnimalCombination.CLOSE_UP: current_stall_shortage_for_close_up - total_max_stocking_density,
        Pen.AnimalCombination.LAC_COW: current_stall_shortage_for_lac_cow - total_max_stocking_density,
    }

    # Act
    updated_stall_shortages = AnimalManagement._update_stall_shortage_for_animal_combination(
        stall_shortages=mock_stall_shortages,
        animal_combination=animal_combination,
        pen=mock_pen
    )

    # Assert
    if animal_combination in mock_stall_shortages:
        assert updated_stall_shortages[animal_combination] == all_expected_stall_shortages[animal_combination]
        patch_for_calculate_total_maximum_stocking_density.assert_called_once_with([mock_pen])
    else:
        assert mock_stall_shortages == mock_stall_shortages_copy
        patch_for_calculate_total_maximum_stocking_density.assert_not_called()
