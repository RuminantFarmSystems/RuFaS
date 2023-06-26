"""
RUFAS: Ruminant Farm Systems Model
File name: test_animal_management.py
Description: Implements test cases for the AnimalManagement class
Author(s): Pooya Hekmati, sh2235@cornell.edu, Anchey Peng, ap724@cornell.edu
"""

from typing import Any
from typing import List, Dict, Union
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock.plugin import MockerFixture

from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.feed.feed import Feed


def create_mock_object_list(attribute_dicts: List[Dict[str, Any]]) -> List[MagicMock]:
    mock_object_list = []

    for attribute_dict in attribute_dicts:
        mock_object = MagicMock()

        for attribute, value in attribute_dict.items():
            setattr(mock_object, attribute, value)

        mock_object_list.append(mock_object)

    return mock_object_list


@pytest.fixture
def pens_with_mock_animals() -> List[MagicMock]:
    mock_animal_1 = MagicMock()
    mock_animal_2 = MagicMock()
    mock_animal_3 = MagicMock()
    mock_animal_4 = MagicMock()
    mock_animals_in_pens = [
        {
            "id": 0,
            "animals_in_pen": [mock_animal_1, mock_animal_2]
        },
        {
            "id": 1,
            "animals_in_pen": [mock_animal_3, mock_animal_4]
        }
    ]

    return create_mock_object_list(mock_animals_in_pens)


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
    # init_allocate_all_pens_patch = patch('RUFAS.routines.animal.animal_management.AnimalManagement.allocate_all_pens')
    allocate_animals_to_pens_patch = patch(
        'RUFAS.routines.animal.animal_management.AnimalManagement.allocate_animals_to_pens'
    )

    init_pens_patch.start()
    init_animals_patch.start()
    init_nutrient_rqmts_patch.start()
    # init_allocate_all_pens_patch.start()
    allocate_animals_to_pens_patch.start()

    data = MagicMock()
    config = MagicMock()
    feed = MagicMock()
    weather = MagicMock()
    time = MagicMock()

    animal_management = AnimalManagement(data, config, feed, weather, time)

    init_pens_patch.stop()
    init_animals_patch.stop()
    init_nutrient_rqmts_patch.stop()
    # init_allocate_all_pens_patch.stop()
    allocate_animals_to_pens_patch.stop()

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


def test_print_animal_num_warnings(animal_management: AnimalManagement):
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
    expected = (12 / 4, 24 / 4)

    assert actual == pytest.approx(expected)


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/animal_management.py"""
    pass


def test_fully_update_animal_to_pen_id_map():
    """Unit test for function fully_update_animal_to_pen_id_map in file routines/animal/animal_management.py"""
    pass


def pens_test_data_dict() -> List[dict[Any]]:
    """
    A list of dictionaries containing the data needed to create several Pen objects for testing purposes.

    Creates a list of data dictionaries holding the data required for several unit tests below, where each
    dictionary is a separate test case due to the parametrization of test functions.

    Returns:
        Returns a list of dictionaries, where each dictionary contains the data needed for individual
        AnimalManagement test cases. The dictionaries include data needed to set up AnimalManagement
        instances for testing purposes, such as pen IDs and the animal IDs to be placed into pens. They also
        contain the expected results for various unit tests, such as the expected stocking density for a pen
        which is tested in test_remove_animals_from_herd()

    """

    return [
        {
            "pen_data":
                {"pen0":
                     {"pen_id": 0,
                      "cow_type_to_id_map": {
                          'Calf': [100283, 102779, 112701, 115078, 127686, 131248, 137254, 148550, 150007, 150905,
                                   151340, 154391, 154438, 156048, 157528, 165411, 169062, 170598, 182656,
                                   186570, 189951, 194172], 'HeiferI': [], 'HeiferII': [], 'HeiferIII': [],
                          'Dry_Cow': [], 'Lac_Cow': []},
                      "pen_animal_combination": Pen.AnimalCombination.CALF,
                      "post_removal_stocking_density": 0.50, "num_stalls": 40,
                      "ration": {"dummy_feed1": 205.0, "dummy_feed2": 0.0, "dummy_feed3": 18.25,
                                 "dummy_feed4": 72.0, "dummy_feed5": 45.0, "dummy_feed6": 146.0, "dummy_feed7": 170.0,
                                 "dummy_feed8": 5.0, "dummy_feed9": 0.0, "dummy_feed10": 200.0}},
                 "pen1":
                     {"pen_id": 1,
                      "cow_type_to_id_map": {'Calf': [], 'HeiferI': [100439, 106977, 111123, 111262, 111527, 112516],
                                             'HeiferII': [120348, 153413, 156414, 193126],
                                             'HeiferIII': [], 'Dry_Cow': [], 'Lac_Cow': []},
                      "pen_animal_combination": Pen.AnimalCombination.GROWING,
                      "post_removal_stocking_density": 0.25, "num_stalls": 36,
                      "ration": {"dummy_feed1": 0.0, "dummy_feed2": 56.0}}
                    ,
                 "pen2":
                     {"pen_id": 2,
                      "cow_type_to_id_map": {'Calf': [], 'HeiferI': [],
                                             'HeiferII': [],
                                             'HeiferIII': [115748, 118413, 129345, 139533, 148813, 156669, 158006,
                                                           161608,
                                                           162583, 163942,
                                                           176371],
                                             'Dry_Cow': [187817, 189760, 189801, 198331, 199999], 'Lac_Cow': []},
                      "pen_animal_combination": Pen.AnimalCombination.CLOSE_UP,
                      "post_removal_stocking_density": 0.10, "num_stalls": 150,
                      "ration": {"dummy_feed1": 10.0, "dummy_feed2": 35.0, "dummy_feed3": 0.0,
                                 "dummy_feed4": 84.0}},
                 "pen3":
                     {"pen_id": 3,
                      "cow_type_to_id_map": {'Calf': [],
                                             'HeiferI': [], 'HeiferII': [], 'HeiferIII': [], 'Dry_Cow': [],
                                             'Lac_Cow': [126963, 133132, 156958, 158639, 160697, 162375, 164238,
                                                         198542]},
                      "pen_animal_combination": Pen.AnimalCombination.LAC_COW,
                      "post_removal_stocking_density": 0.20, "num_stalls": 35,
                      "ration": {"dummy_feed1": 100.0, "status": "dummy_val"}}
                 },
            "animals_to_be_removed":
                {115078, 169062, 112516, 189801, 198542},
            "animal_to_pen_id_map_after_removals":
                {100283: 0, 102779: 0, 112701: 0, 127686: 0, 131248: 0, 137254: 0, 148550: 0, 150007: 0, 150905: 0,
                 151340: 0, 154391: 0, 154438: 0, 156048: 0, 157528: 0, 165411: 0, 170598: 0, 182656: 0, 186570: 0,
                 189951: 0, 194172: 0, 100439: 1, 106977: 1, 111123: 1, 111262: 1, 111527: 1, 120348: 1, 153413: 1,
                 156414: 1,
                 193126: 1, 115748: 2, 118413: 2, 129345: 2, 139533: 2, 148813: 2, 156669: 2, 158006: 2, 161608: 2,
                 162583: 2, 163942: 2, 176371: 2, 187817: 2, 189760: 2, 198331: 2, 199999: 2, 126963: 3, 133132: 3,
                 156958: 3,
                 158639: 3, 160697: 3, 162375: 3, 164238: 3},
            "new_calf_dict": {140735: 'Calf', 100055: 'Calf', 122469: 'Calf'},
            "new_cow_dict": {180081: 'HeiferI', 147361: 'HeiferII', 199813: 'HeiferIII', 148776: 'Dry_Cow',
                             164239: 'Lac_Cow'},
            "tracked_pen_population_list": [22, 10, 16, 8],
            "former_pen_populations": [20, 10, 20, 40],
            "updated_pen_rations": [{"dummy_feed1": 225.5, "dummy_feed2": 0.0, "dummy_feed3": 20.075,
                                     "dummy_feed4": 79.2, "dummy_feed5": 49.5, "dummy_feed6": 160.6,
                                     "dummy_feed7": 187.0,
                                     "dummy_feed8": 5.5, "dummy_feed9": 0.0, "dummy_feed10": 220.0},
                                    {"dummy_feed1": 0.0, "dummy_feed2": 56.0},
                                    {"dummy_feed1": 8.0, "dummy_feed2": 28.0, "dummy_feed3": 0.0,
                                     "dummy_feed4": 67.2},
                                    {"dummy_feed1": 20.0, 'status': 'dummy_val'}],
            "animal_to_pen_id_map_after_daily_update":
                {100055: 0, 100283: 0, 102779: 0, 112701: 0, 122469: 0, 127686: 0, 131248: 0, 137254: 0, 140735: 0,
                 148550: 0, 150007: 0, 150905: 0, 151340: 0, 154391: 0, 154438: 0, 156048: 0, 157528: 0, 165411: 0,
                 170598: 0, 182656: 0, 186570: 0, 189951: 0, 194172: 0, 100439: 1, 106977: 1, 111123: 1, 111262: 1,
                 111527: 1, 120348: 1, 147361: 1, 153413: 1, 156414: 1, 180081: 1, 193126: 1, 115748: 2, 118413: 2,
                 129345: 2, 139533: 2, 148776: 2, 148813: 2, 156669: 2, 158006: 2, 161608: 2, 162583: 2, 163942: 2,
                 176371: 2, 187817: 2, 189760: 2, 198331: 2, 199813: 2, 199999: 2, 126963: 3, 133132: 3, 156958: 3,
                 158639: 3, 160697: 3, 162375: 3, 164238: 3, 164239: 3}

        },
        {
            "pen_data":
                {"pen0":
                     {"pen_id": 0,
                      "cow_type_to_id_map": {'Calf': [120297, 122798, 123120, 124011, 125663, 139048, 141097, 151564,
                                                      152876, 162678, 100919, 101115, 112752, 119921, 172095, 178379,
                                                      181144, 185339, 186287, 192840, 194279, 195286, 196169, 199241,
                                                      199441],
                                             'HeiferI': [], 'HeiferII': [], 'HeiferIII': [], 'Dry_Cow': [],
                                             'Lac_Cow': []},
                      "pen_animal_combination": Pen.AnimalCombination.CALF,
                      "post_removal_stocking_density": 0.50, "num_stalls": 48,
                      "ration": {"status": "dummy_val", "dummy_feed2": 34.0, "dummy_feed3": 3.4,
                                 "dummy_feed4": 77.0, "dummy_feed5": 3.2, "dummy_feed6": 9.50, "dummy_feed7": 0.0,
                                 "dummy_feed8": 12.2, "dummy_feed9": 9.9, "dummy_feed10": 400.0}},
                 "pen1":
                     {"pen_id": 1,
                      "cow_type_to_id_map": {'Calf': [], 'HeiferI': [105602, 106140, 111756, 111796, 113310, 116100],
                                             'HeiferII': [117695, 118217, 118719, 120822, 128176, 135993, 137493,
                                                          142972, 143069, 144943, 146486, 147352, 159225, 161732,
                                                          164778, 164961, 186796, 190033, 193035],
                                             'HeiferIII': [], 'Dry_Cow': [], 'Lac_Cow': []},
                      "pen_animal_combination": Pen.AnimalCombination.GROWING,
                      "post_removal_stocking_density": 0.14, "num_stalls": 150,
                      "ration": {"objective": "dummy_val", "dummy_feed2": 4.0, "dummy_feed3": 20.0,
                                 "dummy_feed4": 362.0, "dummy_feed5": 3.8, "dummy_feed6": 800.0, "dummy_feed7": 0.0,
                                 "dummy_feed8": 1.0, "dummy_feed9": 104.0, "dummy_feed10": 0.0}},
                 "pen2":
                     {"pen_id": 2,
                      "cow_type_to_id_map": {'Calf': [],
                                             'HeiferI': [],
                                             'HeiferII': [],
                                             'HeiferIII': [100613, 113331, 113636, 119415, 120058, 121455, 124053,
                                                           140750, 148499, 150294, 158853, 168737, 175771, 176628,
                                                           177315, 178847],
                                             'Dry_Cow': [179190, 182657, 183755, 186898, 190988, 191700, 193955,
                                                         193975, 195540], 'Lac_Cow': []},
                      "pen_animal_combination": Pen.AnimalCombination.CLOSE_UP,
                      "post_removal_stocking_density": 0.35, "num_stalls": 60,
                      "ration": {"dummy_feed1": 44.4, "dummy_feed2": 21.2, "dummy_feed3": 9.0,
                                 "dummy_feed4": 56.8, "dummy_feed5": 2.0, "dummy_feed6": 650.0,
                                 "dummy_feed7": 1.0,
                                 "dummy_feed8": 0.0, "dummy_feed9": 0.0, "dummy_feed10": 300.0}},
                 "pen3":
                     {"pen_id": 3,
                      "cow_type_to_id_map": {'Calf': [],
                                             'HeiferI': [],
                                             'HeiferII': [],
                                             'HeiferIII': [],
                                             'Dry_Cow': [],
                                             'Lac_Cow': [101126, 101467, 113031, 117449, 118307, 119887, 130965,
                                                         132185, 135078, 135594, 141919, 144930, 145216, 145796,
                                                         149982, 151536, 155905, 164022, 167904, 178041, 181517,
                                                         181810, 184635, 189495, 191337]},
                      "pen_animal_combination": Pen.AnimalCombination.LAC_COW,
                      "post_removal_stocking_density": 0.10, "num_stalls": 210,
                      "ration": {"objective": "dummy_val", "dummy_feed2": 3.0, "dummy_feed3": 12.5,
                                 "dummy_feed4": 0.0, "dummy_feed5": 75.0, "dummy_feed6": 0.0,
                                 "dummy_feed7": 1.0,
                                 "dummy_feed8": 36.0, "dummy_feed9": 106.0, "dummy_feed10": 8.8}}
                 },
            "animals_to_be_removed":
                {112752, 113310, 137493, 142972, 193035, 150294, 168737, 175771, 191700, 145796, 181517, 189495,
                 191337},
            "animal_to_pen_id_map_after_removals":
                {120297: 0, 122798: 0, 123120: 0, 124011: 0, 125663: 0, 139048: 0, 141097: 0, 151564: 0,
                 152876: 0, 162678: 0, 100919: 0, 101115: 0, 119921: 0, 172095: 0, 178379: 0,
                 181144: 0, 185339: 0, 186287: 0, 192840: 0, 194279: 0, 195286: 0, 196169: 0, 199241: 0,
                 199441: 0, 105602: 1, 106140: 1, 111756: 1, 111796: 1, 116100: 1, 117695: 1, 118217: 1, 118719: 1,
                 120822: 1, 128176: 1, 135993: 1, 143069: 1, 144943: 1, 146486: 1, 147352: 1, 159225: 1, 161732: 1,
                 164778: 1, 164961: 1, 186796: 1, 190033: 1, 100613: 2, 113331: 2, 113636: 2, 119415: 2, 120058: 2,
                 121455: 2, 124053: 2, 140750: 2, 148499: 2, 158853: 2, 176628: 2, 177315: 2, 178847: 2, 179190: 2,
                 182657: 2, 183755: 2, 186898: 2, 190988: 2, 193955: 2, 193975: 2, 195540: 2, 101126: 3, 101467: 3,
                 113031: 3, 117449: 3, 118307: 3, 119887: 3, 130965: 3, 132185: 3, 135078: 3, 135594: 3, 141919: 3,
                 144930: 3, 145216: 3, 149982: 3, 151536: 3, 155905: 3, 164022: 3, 167904: 3, 178041: 3, 181810: 3,
                 184635: 3},
            "new_calf_dict": {123928: 'Calf', 138291: 'Calf', 149201: 'Calf', 187283: 'Calf', 188827: 'Calf',
                              199182: 'Calf', 199287: 'Calf'},
            "new_cow_dict": {},
            "tracked_pen_population_list": [25, 25, 25, 25],
            "former_pen_populations": [20, 25, 100, 50],
            "updated_pen_rations": [{"status": "dummy_val", "dummy_feed2": 42.5, "dummy_feed3": 4.25,
                                     "dummy_feed4": 96.25, "dummy_feed5": 4.0, "dummy_feed6": 11.875,
                                     "dummy_feed7": 0.0,
                                     "dummy_feed8": 15.25, "dummy_feed9": 12.375, "dummy_feed10": 500.0},
                                    {"objective": "dummy_val", "dummy_feed2": 4.0, "dummy_feed3": 20.0,
                                     "dummy_feed4": 362.0, "dummy_feed5": 3.8, "dummy_feed6": 800.0, "dummy_feed7": 0.0,
                                     "dummy_feed8": 1.0, "dummy_feed9": 104.0, "dummy_feed10": 0.0},
                                    {"dummy_feed1": 11.1, "dummy_feed2": 5.3, "dummy_feed3": 2.25,
                                     "dummy_feed4": 14.2, "dummy_feed5": 0.5, "dummy_feed6": 162.5,
                                     "dummy_feed7": 0.25,
                                     "dummy_feed8": 0.0, "dummy_feed9": 0.0, "dummy_feed10": 75.0},
                                    {"objective": "dummy_val", "dummy_feed2": 1.5, "dummy_feed3": 6.25,
                                     "dummy_feed4": 0.0, "dummy_feed5": 37.5, "dummy_feed6": 0.0,
                                     "dummy_feed7": 0.5,
                                     "dummy_feed8": 18.0, "dummy_feed9": 53.0, "dummy_feed10": 4.4}
                                    ],
            "animal_to_pen_id_map_after_daily_update":
                {123928: 0, 138291: 0, 149201: 0, 187283: 0, 188827: 0, 199182: 0, 199287: 0, 120297: 0, 122798: 0,
                 123120: 0, 124011: 0, 125663: 0, 139048: 0, 141097: 0, 151564: 0,
                 152876: 0, 162678: 0, 100919: 0, 101115: 0, 119921: 0, 172095: 0, 178379: 0,
                 181144: 0, 185339: 0, 186287: 0, 192840: 0, 194279: 0, 195286: 0, 196169: 0, 199241: 0,
                 199441: 0, 105602: 1, 106140: 1, 111756: 1, 111796: 1, 116100: 1, 117695: 1, 118217: 1, 118719: 1,
                 120822: 1, 128176: 1, 135993: 1, 143069: 1, 144943: 1, 146486: 1, 147352: 1, 159225: 1, 161732: 1,
                 164778: 1, 164961: 1, 186796: 1, 190033: 1, 100613: 2, 113331: 2, 113636: 2, 119415: 2, 120058: 2,
                 121455: 2, 124053: 2, 140750: 2, 148499: 2, 158853: 2, 176628: 2, 177315: 2, 178847: 2, 179190: 2,
                 182657: 2, 183755: 2, 186898: 2, 190988: 2, 193955: 2, 193975: 2, 195540: 2, 101126: 3, 101467: 3,
                 113031: 3, 117449: 3, 118307: 3, 119887: 3, 130965: 3, 132185: 3, 135078: 3, 135594: 3, 141919: 3,
                 144930: 3, 145216: 3, 149982: 3, 151536: 3, 155905: 3, 164022: 3, 167904: 3, 178041: 3, 181810: 3,
                 184635: 3}
        },
        {
            "pen_data":
                {"pen0":
                     {"pen_id": 0,
                      "cow_type_to_id_map": {
                          'Calf': [115259, 138228, 142905, 144752, 156434, 157064, 164638, 167179, 168371, 192382],
                          'HeiferI': [], 'HeiferII': [], 'HeiferIII': [], 'Dry_Cow': [], 'Lac_Cow': []},
                      "pen_animal_combination": Pen.AnimalCombination.CALF,
                      "post_removal_stocking_density": 0.20, "num_stalls": 50,
                      "ration": {"dummy_feed1": 200.0, "dummy_feed2": 0.0, "dummy_feed3": 8.5,
                                 "dummy_feed4": 98.0, "dummy_feed5": 3.5}},
                 "pen1":
                     {"pen_id": 1,
                      "cow_type_to_id_map": {'Calf': [], 'HeiferI': [112121, 117953, 138864, 144952],
                                             'HeiferII': [145016, 146409, 166665, 175830, 182621, 190070],
                                             'HeiferIII': [], 'Dry_Cow': [], 'Lac_Cow': []},
                      "pen_animal_combination": Pen.AnimalCombination.GROWING,
                      "post_removal_stocking_density": 0.10, "num_stalls": 100,
                      "ration": {"dummy_feed1": 1.0, "dummy_feed2": 100.0, "dummy_feed3": 77.23,
                                 "dummy_feed4": 60.5, "dummy_feed5": 42.0}}
                    ,
                 "pen2":
                     {"pen_id": 2,
                      "cow_type_to_id_map": {'Calf': [], 'HeiferI': [114067, 119819, 166593, 168618, 183594],
                                             'HeiferII': [133865, 142331, 155315, 193905, 197376, 198827],
                                             'HeiferIII': [], 'Dry_Cow': [], 'Lac_Cow': []},
                      "pen_animal_combination": Pen.AnimalCombination.GROWING,
                      "post_removal_stocking_density": 0.11, "num_stalls": 100,
                      "ration": {"dummy_feed1": 62.9, "dummy_feed2": 123.0, "dummy_feed3": 8.9,
                                 "dummy_feed4": 2222.0, "dummy_feed5": 0.0}},
                 "pen3":
                     {"pen_id": 3,
                      "cow_type_to_id_map": {'Calf': [], 'HeiferI': [], 'HeiferII': [],
                                             'HeiferIII': [107730, 126839, 142837, 143152, 152668, 162701],
                                             'Dry_Cow': [169688, 174053, 175698, 188017], 'Lac_Cow': []},
                      "pen_animal_combination": Pen.AnimalCombination.CLOSE_UP,
                      "post_removal_stocking_density": 0.5, "num_stalls": 20,
                      "ration": {"status": "dummy_value", "objective": "dummy_value", "dummy_feed1": 8.8,
                                 "dummy_feed2": 72.6, "dummy_feed3": 0.0, "dummy_feed4": 50.0, "dummy_feed5": 4.0}},
                 "pen4":
                     {"pen_id": 4,
                      "cow_type_to_id_map": {'Calf': [], 'HeiferI': [], 'HeiferII': [], 'HeiferIII': [], 'Dry_Cow': [],
                                             'Lac_Cow': [107891, 109102, 110776, 133967, 148657, 157455, 168534, 183607,
                                                         184783, 196284]},
                      "pen_animal_combination": Pen.AnimalCombination.LAC_COW,
                      "post_removal_stocking_density": 1.0, "num_stalls": 10,
                      "ration": {"dummy_feed1": 35.0, "dummy_feed2": 2.0, "dummy_feed3": 0.0,
                                 "dummy_feed4": 1200.0, "dummy_feed5": 82.50}}
                 },
            "animals_to_be_removed": {},
            "animal_to_pen_id_map_after_removals":
                {115259: 0, 138228: 0, 142905: 0, 144752: 0, 156434: 0, 157064: 0, 164638: 0, 167179: 0, 168371: 0,
                 192382: 0, 112121: 1, 117953: 1, 138864: 1, 144952: 1, 145016: 1, 146409: 1, 166665: 1, 175830: 1,
                 182621: 1, 190070: 1, 114067: 2, 119819: 2, 166593: 2, 168618: 2, 183594: 2, 133865: 2, 142331: 2,
                 155315: 2, 193905: 2, 197376: 2, 198827: 2, 107730: 3, 126839: 3, 142837: 3, 143152: 3, 152668: 3,
                 162701: 3, 169688: 3, 174053: 3, 175698: 3, 188017: 3, 107891: 4, 109102: 4, 110776: 4, 133967: 4,
                 148657: 4, 157455: 4, 168534: 4, 183607: 4, 184783: 4, 196284: 4},
            "new_calf_dict": {},
            "new_cow_dict": {100394: "HeiferI", 103171: "HeiferI", 110810: "HeiferII", 113905: "HeiferIII",
                             116462: "Dry_Cow", 122790: "Lac_Cow"},
            "tracked_pen_population_list": [10, 10, 11, 10, 10],
            "former_pen_populations": [20, 5, 22, 40, 100],
            "updated_pen_rations": [{"dummy_feed1": 100.0, "dummy_feed2": 0.0, "dummy_feed3": 4.25,
                                     "dummy_feed4": 49.0, "dummy_feed5": 1.75},
                                    {"dummy_feed1": 2.0, "dummy_feed2": 200.0, "dummy_feed3": 154.46,
                                     "dummy_feed4": 121.0, "dummy_feed5": 84.0},
                                    {"dummy_feed1": 31.45, "dummy_feed2": 61.5, "dummy_feed3": 4.45,
                                     "dummy_feed4": 1111.0, "dummy_feed5": 0.0},
                                    {"status": "dummy_value", "objective": "dummy_value", "dummy_feed1": 2.2,
                                     "dummy_feed2": 18.15, "dummy_feed3": 0.0, "dummy_feed4": 12.5, "dummy_feed5": 1.0},
                                    {"dummy_feed1": 3.50, "dummy_feed2": 0.20, "dummy_feed3": 0.0,
                                     "dummy_feed4": 120.0, "dummy_feed5": 8.25}
                                    ],
            "animal_to_pen_id_map_after_daily_update": {115259: 0, 138228: 0, 142905: 0, 144752: 0, 156434: 0,
                                                        157064: 0, 164638: 0, 167179: 0, 168371: 0, 192382: 0,
                                                        100394: 1, 103171: 1, 112121: 1, 117953: 1,
                                                        138864: 1, 144952: 1, 145016: 1, 146409: 1, 166665: 1,
                                                        175830: 1, 182621: 1, 190070: 1, 110810: 2,
                                                        114067: 2, 119819: 2, 166593: 2, 168618: 2, 183594: 2,
                                                        133865: 2, 142331: 2, 155315: 2, 193905: 2,
                                                        197376: 2, 198827: 2, 107730: 3, 113905: 3, 116462: 3,
                                                        126839: 3, 142837: 3, 143152: 3, 152668: 3,
                                                        162701: 3, 169688: 3, 174053: 3, 175698: 3, 188017: 3,
                                                        107891: 4, 109102: 4, 110776: 4, 122790: 4,
                                                        133967: 4, 148657: 4, 157455: 4, 168534: 4, 183607: 4,
                                                        184783: 4, 196284: 4}
        }
    ]


def setup_dummy_animal(animal_id: int, animal_type: str) -> AnimalBase:
    """
    Sets up a dummy AnimalBase object for testing purposes.

    Creates an AnimalBase object with filler required variables, except 'id,' which is passed in
    as an argument to the function.

    Args:
        animal_id: an integer animal ID number, uniquely signed to the AnimalBase object being made
        animal_type: the string type of the dummmy animal, ranging from a Calf, to one of three Heifer
            types, to lactating and dry cows

    Returns:
        An AnimalBase object that has the 'id' variable specified by the animal_id argument and dummy
        values for all other required variables.

    """

    args_dict = {'breed': 'dummy_breed', 'birth_date': 'dummy_birth_date', 'days_born': 'dummy_days_born',
                 'milking': 'dummy_milking_value', 'id': animal_id}
    config_dict = {'semen_type': 'dummy_semen_type'}

    AnimalBase.set_config(config_dict)
    dummy_animal = AnimalBase(args_dict)

    type_to_class_dict = {
        'Calf': Calf,
        'HeiferI': HeiferI,
        'HeiferII': HeiferII,
        'HeiferIII': HeiferIII,
        'Dry_Cow': Cow,
        'Lac_Cow': Cow
    }
    if animal_type == 'Dry_Cow':
        dummy_animal.milking = False
    elif animal_type == 'Lac_Cow':
        dummy_animal.milking = True

    dummy_animal.__class__ = type_to_class_dict[animal_type]

    return dummy_animal


def setup_dummy_pen(pen_id: int, num_stalls: int, animal_list: List[AnimalBase]) -> Pen:
    """
    Sets up a dummy Pen object for testing purposes.

    Creates a Pen object with filler required variables, except 'id' and 'number_of_stalls,' which are passed in
    as arguments to the function. The Pen's 'animals_in_pen' variable gets set to the animal_list passed in as
    an argument.

    Args:
        pen_id: an integer pen ID number, uniquely signed to the Pen object being made
        num_stalls: an integer pertaining to the number of stalls within the Pen being made
        animal_list: a list of AnimalBase objects that will be living inside the Pen

    Returns:
        A Pen object that has the 'id' and 'number_of_stalls' variable specified by the pen_id and num_stalls
        arguments and dummy values for all other required variables.
    """

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
    dummy_pen.stocking_density = len(animal_list) / num_stalls

    return dummy_pen


def setup_dummy_animal_management_with_pens(animal_management: AnimalManagement, info_dict: dict[Any],
                                            append_removals: bool = False) -> dict[Any]:
    """
    Prepares a dummy AnimalManagement object for testing purposes.

    Using the data held within the information dictionary passed in as input, this function populates several
    of the AnimalManagement object's variables. This is done by creating AnimalBase objects and placing them into
    Pen objects' 'animals_in_pen' variables, as well as configuring the Pen's ration variable before then
    appending individual Pen objects to the AnimalManagement object's 'all_pens' variable.


    Args:
        animal_management: An AnimalManagement object
        info_dict: A dictionary containing the data needed to fully create the
        append_removals: A boolean that is set to True if a list of animals to be removed needs to be true,
            False otherwise

    Returns:
        A dictionary containing the edited AnimalManagement object via the 'animal_management_object'
        key, and a list of AnimalBase objects to be removed via the 'animals_removed_list' key
    """

    animals_removed = []
    pen_list = []
    for pen_num, pen_dict in info_dict['pen_data'].items():
        animal_list = []
        for animal_type, animal_ids in pen_dict["cow_type_to_id_map"].items():
            for animal_id in animal_ids:
                dummy_animal = setup_dummy_animal(animal_id, animal_type)

                animal_list.append(dummy_animal)

                animal_management.animal_to_pen_id_map[dummy_animal.id] = pen_dict['pen_id']
                if append_removals and dummy_animal.id in info_dict['animals_to_be_removed']:
                    animals_removed.append(dummy_animal)

        dummy_pen = setup_dummy_pen(pen_dict['pen_id'], pen_dict['num_stalls'], animal_list)

        dummy_pen.ration = pen_dict['ration']

        dummy_pen.animals_in_pen = animal_list

        animal_management.pens_by_animal_combination[pen_dict['pen_animal_combination']].append(dummy_pen)

        pen_list.append(dummy_pen)

    animal_management.all_pens = pen_list

    return {'animal_management_object': animal_management, 'animals_removed_list': animals_removed}


@pytest.mark.parametrize("info_dict", pens_test_data_dict())
def test_remove_animals_from_herd(info_dict: dict[Any], animal_management: AnimalManagement) -> None:
    """Unit test for function remove_animals_from_herd in file routines/animal/animal_management.py"""

    dummy_animal_management = setup_dummy_animal_management_with_pens(animal_management, info_dict, True)[
        'animal_management_object']
    animals_removed = setup_dummy_animal_management_with_pens(animal_management, info_dict, True)[
        'animals_removed_list']

    dummy_animal_management.remove_animals_from_herd(animals_removed)

    assert dummy_animal_management.animal_to_pen_id_map == info_dict['animal_to_pen_id_map_after_removals']
    for idx, pen_dict in enumerate(info_dict['pen_data'].values()):
        assert dummy_animal_management.all_pens[idx].stocking_density == pen_dict['post_removal_stocking_density']
        assert set(dummy_animal_management.all_pens[idx].animals_in_pen) & set(animals_removed) == set()


@pytest.mark.parametrize("info_dict", pens_test_data_dict())
def test_track_former_pen_population(info_dict: dict[Any], animal_management: AnimalManagement) -> None:
    """Unit test for function track_former_pen_population in file routines/animal/animal_management.py"""

    dummy_animal_management = setup_dummy_animal_management_with_pens(animal_management, info_dict, False)[
        'animal_management_object']

    former_population_dictionary = dummy_animal_management.track_former_pen_population()

    assert former_population_dictionary == info_dict['tracked_pen_population_list']


@pytest.mark.parametrize("info_dict", pens_test_data_dict())
def test_calculate_pen_rations(info_dict: dict[Any], animal_management: AnimalManagement) -> None:
    """Unit test for function calculate_pen_rations in file routines/animal/animal_management.py"""

    dummy_animal_management = setup_dummy_animal_management_with_pens(animal_management, info_dict, False)[
        'animal_management_object']

    dummy_animal_management.calculate_pen_rations(info_dict['former_pen_populations'])

    for idx, pen in enumerate(dummy_animal_management.all_pens):
        assert pen.ration == info_dict['updated_pen_rations'][idx]


@pytest.mark.parametrize("info_dict", pens_test_data_dict())
def test_daily_update_id_map(info_dict: dict[Any], animal_management: AnimalManagement, mocker: MockerFixture):
    """Unit test for function daily_update_id_map in file routines/animal/animal_management.py"""

    mocker.patch("RUFAS.routines.feed.Feed.__init__", return_value=None)

    calf_addition_list = []
    animal_addition_list = []

    dummy_feed = Feed(data=mocker.MagicMock())

    dummy_object_and_removals = setup_dummy_animal_management_with_pens(animal_management, info_dict, True)
    dummy_animal_management = dummy_object_and_removals['animal_management_object']
    dummy_removal_list = dummy_object_and_removals['animals_removed_list']

    for animal_id, animal_type in info_dict["new_cow_dict"].items():
        new_cow = setup_dummy_animal(animal_id, animal_type)
        animal_addition_list.append(new_cow)

    for calf_id, calf_type in info_dict["new_calf_dict"].items():
        new_calf = setup_dummy_animal(calf_id, calf_type)
        calf_addition_list.append(new_calf)

    with patch("RUFAS.routines.animal.pen.Pen.set_up_new_animal") as set_up_new_animal:
        dummy_animal_management.daily_update_id_map(animal_addition_list, dummy_removal_list, calf_addition_list,
                                                    dummy_feed, 20.0)
        assert set_up_new_animal.call_count == len(info_dict["new_calf_dict"]) + len(info_dict["new_cow_dict"])

    assert dummy_animal_management.animal_to_pen_id_map == info_dict['animal_to_pen_id_map_after_daily_update']


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


def test_calc_all_p_conc():
    """Unit test for function calc_all_p_conc in file routines/animal/animal_management.py"""
    pass


def test_calc_p_rqmts():
    """Unit test for function calc_p_rqmts in file routines/animal/animal_management.py"""
    pass


def test_daily_p_update():
    """Unit test for function daily_p_update in file routines/animal/animal_management.py"""
    pass


def test_reset_milk_production_reduction(pens_with_mock_animals) -> None:
    """Unit test for function reset_milk_production_reduction in file routines/animal/animal_management.py"""

    # Set milk_production_reduction to some value
    for pen in pens_with_mock_animals:
        for animal in pen.animals_in_pen:
            animal.milk_production_reduction = 100.1

    # mock an animal_management object, but specifically so it returns a list of pens
    penlist = MagicMock()
    penlist.all_pens = pens_with_mock_animals
    for pen in penlist.all_pens:
        pen.animal_combination.name = "NOT_LAC_COW"
        for animal in pen.animals_in_pen:
            assert animal.milk_production_reduction == 100.1

    # call the function once on the list of pens
    AnimalManagement.reset_milk_production_reduction(penlist)

    # then assert that all animals in all pens are still 100.1
    for pen in penlist.all_pens:
        for animal in pen.animals_in_pen:
            assert animal.milk_production_reduction == 100.1

    # now set that they are LAC_COW
    for pen in penlist.all_pens:
        pen.animal_combination.name = "LAC_COW"

    # call the function again on the list of pens
    AnimalManagement.reset_milk_production_reduction(penlist)

    # then assert that all animals in all pens are now 0.0
    for pen in penlist.all_pens:
        for animal in pen.animals_in_pen:
            assert animal.milk_production_reduction == 0.0


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


@pytest.fixture
def cowlist():
    cowlist = [MagicMock(),
               MagicMock(),
               MagicMock()]
    return cowlist


def test_sum_daily_milk(animal_management, cowlist):
    """Unit test for function sum_daily_milk in file routines/animal/animal_management.py"""
    for cow in cowlist:
        cow.estimated_daily_milk_produced = 50.0
    result = AnimalManagement.sum_daily_milk(animal_management, cowlist)
    assert result == 150


def test_get_animals_snapshot(mocker: MockerFixture):
    """
    Unit test for function _get_animals_snapshot() in file animal_management.py

    This test checks that the function correctly creates a snapshot of the current state of all animals
    in the system, and additionally finds and stores the combination each animal belongs to.

    """
    # Arrange
    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement.__init__', return_value=None)
    animal_management = AnimalManagement(
        data=mocker.MagicMock(),
        config=mocker.MagicMock(),
        feed=mocker.MagicMock(),
        weather=mocker.MagicMock(),
        time=mocker.MagicMock()
    )
    old_animal_grouping_scenario = AnimalManagement.ANIMAL_GROUPING_SCENARIO
    mock_animal_grouping_scenario = mocker.MagicMock()
    num_animal_classes = 5
    num_animals_of_each_type = 10
    animal_id = 0
    mock_calves = []
    mock_heifer_Is = []
    mock_heifer_IIs = []
    mock_heifer_IIIs = []
    mock_cows = []
    animal_combination_by_id = {}
    for i in range(num_animals_of_each_type):
        mock_calves.append(mocker.MagicMock())
        mock_calves[i].id = animal_id
        animal_combination_by_id[animal_id] = f'calf_{i}'
        animal_id += 1

        mock_heifer_Is.append(mocker.MagicMock())
        mock_heifer_Is[i].id = animal_id
        animal_combination_by_id[animal_id] = f'heiferI_{i}'
        animal_id += 1

        mock_heifer_IIs.append(mocker.MagicMock())
        mock_heifer_IIs[i].id = animal_id
        animal_combination_by_id[animal_id] = f'heiferII_{i}'
        animal_id += 1

        mock_heifer_IIIs.append(mocker.MagicMock())
        mock_heifer_IIIs[i].id = animal_id
        animal_combination_by_id[animal_id] = f'heiferIII_{i}'
        animal_id += 1

        mock_cows.append(mocker.MagicMock())
        mock_cows[i].id = animal_id
        animal_combination_by_id[animal_id] = f'cow_{i}'
        animal_id += 1

    mock_animal_grouping_scenario.find_animal_combination = \
        mocker.MagicMock(side_effect=lambda animal: animal_combination_by_id[animal.id])

    animal_management.calves = mock_calves
    animal_management.heiferIs = mock_heifer_Is
    animal_management.heiferIIs = mock_heifer_IIs
    animal_management.heiferIIIs = mock_heifer_IIIs
    animal_management.cows = mock_cows
    AnimalManagement.ANIMAL_GROUPING_SCENARIO = mock_animal_grouping_scenario

    expected_snapshot = {
        'calves': set(mock_calves),
        'heiferIs': set(mock_heifer_Is),
        'heiferIIs': set(mock_heifer_IIs),
        'heiferIIIs': set(mock_heifer_IIIs),
        'cows': set(mock_cows),
        'animal_combination_by_id': animal_combination_by_id,
    }

    # Act
    actual_snapshot = animal_management._get_animals_snapshot()

    # Assert
    assert actual_snapshot == expected_snapshot
    assert mock_animal_grouping_scenario.find_animal_combination.call_count == \
           num_animal_classes * num_animals_of_each_type

    # Reset
    AnimalManagement.ANIMAL_GROUPING_SCENARIO = old_animal_grouping_scenario


def test_handle_removed_animals_after_update(mocker: MockerFixture):
    """
    Unit test for the function _handle_removed_animals_after_update() in file animal_management.py

    This test checks that the function correctly identifies the animals that have been removed after an update,
    and that it successfully calls the '_remove_animal_from_pen_and_id_map' method for each of these animals.

    """
    # Arrange
    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement.__init__', return_value=None)
    animal_management = AnimalManagement(data=mocker.MagicMock(), config=mocker.MagicMock(),
                                         feed=mocker.MagicMock(), weather=mocker.MagicMock(),
                                         time=mocker.MagicMock())

    num_animals_of_each_type = 10
    mock_calves = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_heifer_Is = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_heifer_IIs = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_heifer_IIIs = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_cows = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]

    animals_snapshot_before_update = {
        'calves': set(mock_calves),
        'heiferIs': set(mock_heifer_Is),
        'heiferIIs': set(mock_heifer_IIs),
        'heiferIIIs': set(mock_heifer_IIIs),
        'cows': set(mock_cows),
        'animal_combination_by_id': {}  # This is not used in this test
    }

    mock_calves_at_odd_indices = mock_calves[1::2]
    mock_heifer_Is_at_odd_indices = mock_heifer_Is[1::2]
    mock_heifer_IIs_at_odd_indices = mock_heifer_IIs[1::2]
    mock_heifer_IIIs_at_odd_indices = mock_heifer_IIIs[1::2]
    mock_cows_at_odd_indices = mock_cows[1::2]

    mock_calves_at_even_indices = mock_calves[::2]
    mock_heifer_Is_at_even_indices = mock_heifer_Is[::2]
    mock_heifer_IIs_at_even_indices = mock_heifer_IIs[::2]
    mock_heifer_IIIs_at_even_indices = mock_heifer_IIIs[::2]
    mock_cows_at_even_indices = mock_cows[::2]

    animals_snapshot_after_update = {
        'calves': set(mock_calves_at_odd_indices),
        'heiferIs': set(mock_heifer_Is_at_odd_indices),
        'heiferIIs': set(mock_heifer_IIs_at_odd_indices),
        'heiferIIIs': set(mock_heifer_IIIs_at_odd_indices),
        'cows': set(mock_cows_at_odd_indices),
        'animal_combination_by_id': {}  # This is not used in this test
    }

    removed_animals = set(mock_calves_at_even_indices + mock_heifer_Is_at_even_indices +
                          mock_heifer_IIs_at_even_indices + mock_heifer_IIIs_at_even_indices +
                          mock_cows_at_even_indices)
    patch_remove_animal_from_pen_and_id_map = mocker.patch.object(animal_management,
                                                                  '_remove_animal_from_pen_and_id_map')

    # Act
    animal_management._handle_removed_animals_after_update(animals_snapshot_before_update,
                                                           animals_snapshot_after_update)

    # Assert
    assert patch_remove_animal_from_pen_and_id_map.call_count == len(removed_animals)
    for animal in removed_animals:
        patch_remove_animal_from_pen_and_id_map.assert_any_call(animal)


def test_handle_animals_with_unchanged_class_and_changed_combination(mocker: MockerFixture):
    """
    Unit test for the function _handle_animals_with_unchanged_class_and_changed_combination() in file animal_management.py

    This test checks that the function correctly identifies the animals that didn't change their classes but changed their animal combination.
    It also verifies that the functions '_remove_animal_from_pen_and_id_map' and '_add_animal_to_pen_and_id_map' are called for these animals.

    """
    # Arrange
    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement.__init__', return_value=None)
    animal_management = AnimalManagement(data=mocker.MagicMock(), config=mocker.MagicMock(),
                                         feed=mocker.MagicMock(), weather=mocker.MagicMock(),
                                         time=mocker.MagicMock())

    num_animals_of_each_type = 10
    mock_calves = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_heifer_Is = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_heifer_IIs = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_heifer_IIIs = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_cows = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]

    animals = mock_calves + mock_heifer_Is + mock_heifer_IIs + mock_heifer_IIIs + mock_cows

    animals_snapshot_before_update = {
        'calves': set(mock_calves),
        'heiferIs': set(mock_heifer_Is),
        'heiferIIs': set(mock_heifer_IIs),
        'heiferIIIs': set(mock_heifer_IIIs),
        'cows': set(mock_cows),
        'animal_combination_by_id': {animal.id: 'combination1' for animal in animals}
    }

    animals_snapshot_after_update = {
        'calves': set(mock_calves),
        'heiferIs': set(mock_heifer_Is),
        'heiferIIs': set(mock_heifer_IIs),
        'heiferIIIs': set(mock_heifer_IIIs),
        'cows': set(mock_cows),
        'animal_combination_by_id': {animal.id: 'combination2' for animal in animals}
    }

    mock_feed = mocker.MagicMock()
    mock_temp = mocker.MagicMock()

    patch_remove_animal = mocker.patch.object(animal_management, '_remove_animal_from_pen_and_id_map')
    patch_add_animal = mocker.patch.object(animal_management, '_add_animal_to_pen_and_id_map')

    # Act
    animal_management._handle_animals_with_unchanged_class_and_changed_combination(animals_snapshot_before_update,
                                                                                   animals_snapshot_after_update,
                                                                                   mock_feed, mock_temp)

    # Assert
    assert patch_remove_animal.call_count == len(animals)
    assert patch_add_animal.call_count == len(animals)
    for animal in animals:
        patch_remove_animal.assert_any_call(animal)
        patch_add_animal.assert_any_call(animal, mock_feed, mock_temp)


def test_handle_graduated_animals(mocker: MockerFixture):
    """
    Unit test for the function _handle_graduated_animals() in file animal_management.py

    This test checks that the function correctly identifies the animals that have graduated to the next class.
    It also verifies that the function '_add_animal_to_pen_and_id_map' is called for these graduated animals.

    """
    # Arrange
    import random
    random.seed(42)  # Set seed to make test reproducible

    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement.__init__', return_value=None)
    animal_management = AnimalManagement(data=mocker.MagicMock(), config=mocker.MagicMock(),
                                         feed=mocker.MagicMock(), weather=mocker.MagicMock(),
                                         time=mocker.MagicMock())

    num_animals_of_each_type = 30  # To make easier to select a third of each class
    mock_calves = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_heifer_Is = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_heifer_IIs = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_heifer_IIIs = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]
    mock_cows = [mocker.MagicMock() for _ in range(num_animals_of_each_type)]

    # Randomly select a third of each class to graduate
    graduated_heifer_Is = random.sample(mock_calves, num_animals_of_each_type // 3)
    graduated_heifer_IIs = random.sample(mock_heifer_Is, num_animals_of_each_type // 3)
    graduated_heifer_IIIs = random.sample(mock_heifer_IIs, num_animals_of_each_type // 3)
    graduated_cows = random.sample(mock_heifer_IIIs, num_animals_of_each_type // 3)

    animals_snapshot_before_update = {
        'calves': set(mock_calves),
        'heiferIs': set(mock_heifer_Is),
        'heiferIIs': set(mock_heifer_IIs),
        'heiferIIIs': set(mock_heifer_IIIs),
        'cows': set(mock_cows),
        'animal_combination_by_id': {}
    }

    animals_snapshot_after_update = {
        'calves': set(mock_calves) - set(graduated_heifer_Is),
        'heiferIs': set(mock_heifer_Is).union(set(graduated_heifer_Is)) - set(graduated_heifer_IIs),
        'heiferIIs': set(mock_heifer_IIs).union(set(graduated_heifer_IIs)) - set(graduated_heifer_IIIs),
        'heiferIIIs': set(mock_heifer_IIIs).union(set(graduated_heifer_IIIs)) - set(graduated_cows),
        'cows': set(mock_cows).union(set(graduated_cows)),
        'animal_combination_by_id': {}
    }

    mock_feed = mocker.MagicMock()
    mock_temp = mocker.MagicMock()

    patch_add_animal = mocker.patch.object(animal_management, '_add_animal_to_pen_and_id_map')

    # Act
    animal_management._handle_graduated_animals(animals_snapshot_before_update,
                                                animals_snapshot_after_update,
                                                mock_feed, mock_temp)

    # Assert
    all_graduated_animals = graduated_heifer_Is + graduated_heifer_IIs + graduated_heifer_IIIs + graduated_cows
    assert patch_add_animal.call_count == len(all_graduated_animals)
    for animal in all_graduated_animals:
        patch_add_animal.assert_any_call(animal, mock_feed, mock_temp)


def test_handle_newly_added_animals(mocker: MockerFixture):
    """
    Unit test for the function _handle_newly_added_animals() in file animal_management.py

    This test checks that the function correctly handles newly added animals and adds them to
    the appropriate data structures.

    """
    # Arrange
    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement.__init__', return_value=None)
    animal_management = AnimalManagement(data=mocker.MagicMock(), config=mocker.MagicMock(),
                                         feed=mocker.MagicMock(), weather=mocker.MagicMock(),
                                         time=mocker.MagicMock())

    # MockAnimal class
    class MockAnimal:
        def __init__(self, animal_id):
            self.animal_id = animal_id

    num_new_animals = 10
    new_mock_animals = [MockAnimal(i) for i in range(num_new_animals)]

    mock_feed = mocker.MagicMock()
    mock_temp = mocker.MagicMock()

    patch_add_animal = mocker.patch.object(animal_management, '_add_animal_to_pen_and_id_map')

    # Set up property mock for animals_by_type
    mock_animals_by_type = {MockAnimal: []}
    mock_animals_by_type_property = mocker.patch.object(AnimalManagement, 'animals_by_type',
                                                        new_callable=mocker.PropertyMock)
    mock_animals_by_type_property.return_value = mock_animals_by_type

    # Act
    animal_management._handle_newly_added_animals(new_mock_animals, mock_feed, mock_temp)

    # Assert
    assert patch_add_animal.call_count == num_new_animals
    for animal in new_mock_animals:
        patch_add_animal.assert_any_call(animal, mock_feed, mock_temp)
        assert animal in animal_management.animals_by_type[MockAnimal]


def test_remove_animal_from_pen_and_id_map(mocker: MockerFixture):
    """
    Unit test for the function _remove_animal_from_pen_and_id_map() in file animal_management.py

    This test checks that the function correctly removes the animal from the pen it is in and
    from the animal_to_pen_id_map.

    """
    # Arrange
    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement.__init__', return_value=None)
    animal_management = AnimalManagement(data=mocker.MagicMock(), config=mocker.MagicMock(),
                                         feed=mocker.MagicMock(), weather=mocker.MagicMock(),
                                         time=mocker.MagicMock())

    mock_animal = mocker.MagicMock()
    mock_animal.id = 1

    mock_pen = mocker.MagicMock()
    mock_pen.remove_animal = mocker.MagicMock()

    mock_animal_to_pen_id_map = {mock_animal.id: 0}
    mock_all_pens = [mock_pen]

    animal_management.animal_to_pen_id_map = mock_animal_to_pen_id_map
    animal_management.all_pens = mock_all_pens

    # Act
    animal_management._remove_animal_from_pen_and_id_map(mock_animal)

    # Assert
    mock_pen.remove_animal.assert_called_once_with(mock_animal.id)
    assert mock_animal.id not in animal_management.animal_to_pen_id_map


def test_add_animal_to_pen_and_id_map(mocker: MockerFixture):
    """
    Unit test for the function _add_animal_to_pen_and_id_map() in file animal_management.py

    This test checks that the function correctly assigns an animal to a pen with the minimum stocking density,
    updates the pen's animal count and stocking density, and updates the animal_to_pen_id_map.

    """
    # Arrange
    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement.__init__', return_value=None)
    animal_management = AnimalManagement(data=mocker.MagicMock(), config=mocker.MagicMock(),
                                         feed=mocker.MagicMock(), weather=mocker.MagicMock(),
                                         time=mocker.MagicMock())

    mock_animal = mocker.MagicMock()
    mock_animal.id = 1

    mock_pen_1 = mocker.MagicMock()
    mock_pen_1.current_stocking_density = 10
    mock_pen_1.id = 1
    mock_pen_1.add_animal = mocker.MagicMock()

    mock_pen_2 = mocker.MagicMock()
    mock_pen_2.current_stocking_density = 5
    mock_pen_2.id = 2
    mock_pen_2.add_animal = mocker.MagicMock()

    mock_animal_combination = 'combination_1'
    mock_feed = mocker.MagicMock()
    mock_temp = mocker.MagicMock()

    mock_animal_grouping_scenario = mocker.MagicMock()
    mock_animal_grouping_scenario.find_animal_combination.return_value = mock_animal_combination

    mock_pens_by_animal_combination = {mock_animal_combination: [mock_pen_1, mock_pen_2]}

    original_ANIMAL_GROUPING_SCENARIO = AnimalManagement.ANIMAL_GROUPING_SCENARIO
    AnimalManagement.ANIMAL_GROUPING_SCENARIO = mock_animal_grouping_scenario
    animal_management.pens_by_animal_combination = mock_pens_by_animal_combination
    animal_management.phosphorus_concentration_by_animal_class = {type(mock_animal): 0.0}
    animal_management.animal_to_pen_id_map = {}

    # Act
    animal_management._add_animal_to_pen_and_id_map(mock_animal, mock_feed, mock_temp)

    # Assert
    mock_pen_1.add_animal.assert_not_called()
    mock_pen_2.add_animal.assert_called_once_with(mock_animal,
                                                  mock_animal_grouping_scenario,
                                                  mock_feed,
                                                  mock_temp,
                                                  0.0)
    assert animal_management.animal_to_pen_id_map[mock_animal.id] == mock_pen_2.id

    # Reset ANIMAL_GROUPING_SCENARIO
    AnimalManagement.ANIMAL_GROUPING_SCENARIO = original_ANIMAL_GROUPING_SCENARIO


@pytest.mark.parametrize(
    'is_end_ration_interval',
    [True, False]
)
def test_daily_updates(is_end_ration_interval: bool, mocker: MockerFixture) -> None:
    """
    Unit test for the function daily_updates() in file animal_management.py

    Test that the daily_updates() method of the AnimalManagement class correctly calls all required methods
    with correct parameters.

    """
    # Arrange
    mock_feed = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    temp = 25
    mock_weather.T_avg.__getitem__.return_value = [temp for _ in range(365)]
    mock_time = mocker.MagicMock()
    mock_time.year = 2023
    mock_time.day = 1

    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement.__init__', return_value=None)
    mock_animal_management = AnimalManagement(data=mocker.MagicMock(), config=mocker.MagicMock(),
                                              feed=mock_feed, weather=mock_weather,
                                              time=mock_time)

    mock_animal_management.simulate_animals = True
    mock_animal_management.simulation_day = 90
    mock_animal_management.calves = mock_calves = mocker.MagicMock()
    mock_animal_management.heiferIs = mock_heiferIs = mocker.MagicMock()
    mock_animal_management.heiferIIs = mock_heiferIIs = mocker.MagicMock()
    mock_animal_management.heiferIIIs = mock_heiferIIIs = mocker.MagicMock()
    mock_animal_management.cows = mock_cows = mocker.MagicMock()
    mock_animal_management.methane_model = mock_methane_model = mocker.MagicMock()
    patch_for_end_ration_interval = mocker.patch.object(
        AnimalManagement, 'end_ration_interval', return_value=is_end_ration_interval)
    patch_for_reset_milk_production_reduction = mocker.patch.object(
        AnimalManagement, 'reset_milk_production_reduction', return_value=None)
    mock_animal_snapshot_before_update = mocker.MagicMock()
    mock_animal_snapshot_after_update = mocker.MagicMock()
    patch_for_get_animals_snapshot = mocker.patch.object(
        AnimalManagement, '_get_animals_snapshot', side_effect=[mock_animal_snapshot_before_update,
                                                                mock_animal_snapshot_after_update])
    mock_animals_added = mocker.MagicMock()
    mock_animals_removed = mocker.MagicMock()
    mock_calves_born = mocker.MagicMock()
    mock_life_cycle_manager = mocker.MagicMock()
    mock_life_cycle_manager.daily_update.return_value = [mock_animals_added, mock_animals_removed,
                                                         mock_calves_born, []]
    mock_animal_management.life_cycle_manager = mock_life_cycle_manager

    patch_for_handle_removed_animals_after_update = mocker.patch.object(
        AnimalManagement, '_handle_removed_animals_after_update', return_value=None)
    patch_for_handle_unchanged_animals = mocker.patch.object(
        AnimalManagement, '_handle_animals_with_unchanged_class_and_changed_combination', return_value=None)
    patch_for_handle_graduated_animals = mocker.patch.object(
        AnimalManagement, '_handle_graduated_animals', return_value=None)
    patch_for_handle_newly_added_animals = mocker.patch.object(
        AnimalManagement, '_handle_newly_added_animals', return_value=None)

    patch_for_update_phosphorus_concentrations = mocker.patch.object(
        AnimalManagement, '_update_phosphorus_concentrations', return_value=None)
    patch_for_record_pen_history = mocker.patch.object(
        AnimalManagement, 'record_pen_history', return_value=None)

    num_pens = 5
    num_animals_per_pen = 10
    mock_all_pens = []
    for i in range(num_pens):
        mock_pen = mocker.MagicMock()
        mock_pen.animal_combination.name = 'LAC_COW'
        mock_pen.animals_in_pen = []
        for j in range(num_animals_per_pen):
            mock_animal = mocker.MagicMock()
            mock_animal.update_milk_production_history.return_value = None
            mock_pen.animals_in_pen.append(mock_animal)
        mock_all_pens.append(mock_pen)
    mock_animal_management.all_pens = mock_all_pens

    mock_classes_in_pen = mocker.MagicMock()
    patch_for_get_classes_in_pen = mocker.patch.object(
        AnimalManagement, '_get_classes_in_pen', return_value=mock_classes_in_pen)

    patch_for_calc_nutrient_rqmts = mocker.patch.object(
        AnimalManagement, 'calc_nutrient_rqmts', return_value=None)
    patch_for_clear_pens = mocker.patch.object(
        AnimalManagement, 'clear_pens', return_value=None)
    patch_for_allocate_animals_to_pens = mocker.patch.object(
        AnimalManagement, 'allocate_animals_to_pens', return_value=None)
    patch_for_calc_ration_at_interval = mocker.patch.object(
        AnimalManagement, '_calc_ration_at_interval', return_value=None)
    patch_for_calc_avg_growth = mocker.patch.object(
        AnimalManagement, 'calc_avg_growth', return_value=None)

    sum_daily_milk = 1000.0
    patch_for_sum_daily_milk = mocker.patch.object(
        AnimalManagement, 'sum_daily_milk', return_value=sum_daily_milk)

    # Act
    mock_animal_management.daily_updates(mock_feed, mock_weather, mock_time)

    # Assert
    assert patch_for_end_ration_interval.call_count == 2
    if is_end_ration_interval:
        patch_for_reset_milk_production_reduction.assert_called()

    mock_weather.T_avg.__getitem__.assert_called_with(mock_time.year - 1)

    patch_for_get_animals_snapshot.assert_has_calls([mocker.call(), mocker.call()])

    mock_life_cycle_manager.daily_update.assert_called_once_with(
        mock_animal_management.simulation_day, mock_calves, mock_heiferIs, mock_heiferIIs, mock_heiferIIIs, mock_cows)

    patch_for_handle_removed_animals_after_update.assert_called_once_with(
        mock_animal_snapshot_before_update, mock_animal_snapshot_after_update)

    patch_for_handle_unchanged_animals.assert_called_once_with(
        mock_animal_snapshot_before_update, mock_animal_snapshot_after_update, mock_feed, temp)

    patch_for_handle_graduated_animals.assert_called_once_with(
        mock_animal_snapshot_before_update, mock_animal_snapshot_after_update, mock_feed, temp)

    patch_for_handle_newly_added_animals.assert_called_once_with(
        list(mock_animals_added) + list(mock_calves_born), mock_feed, temp)

    patch_for_get_classes_in_pen.assert_has_calls([mocker.call(mock_pen) for mock_pen in mock_all_pens])

    for mock_pen in mock_all_pens:
        mock_pen.calc_total_manure.assert_called_once_with(mock_feed, mock_methane_model)
        mock_pen.call_p_rqmts.assert_called_once()
        mock_pen.daily_p_update.assert_called_once()

    patch_for_update_phosphorus_concentrations.assert_called_once()

    patch_for_record_pen_history.assert_called_once()

    if is_end_ration_interval:
        patch_for_reset_milk_production_reduction.assert_called()
        patch_for_calc_nutrient_rqmts.assert_called_once_with(mock_feed, temp)
        patch_for_clear_pens.assert_called_once()
        patch_for_allocate_animals_to_pens.assert_called_once()
        patch_for_calc_ration_at_interval.assert_called_once_with(mock_feed)
        patch_for_calc_avg_growth.assert_called_once()
        for mock_pen in mock_all_pens:
            for mock_animal in mock_pen.animals_in_pen:
                mock_animal.update_milk_production_history.assert_called_once_with(
                    mock_animal_management.simulation_day)

    patch_for_sum_daily_milk.assert_called_once_with(mock_cows)
    assert mock_animal_management.life_cycle_manager.daily_milk_production == sum_daily_milk
