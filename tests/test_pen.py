"""
RUFAS: Ruminant Farm Systems Model
File name: test_pen.py
Description: Implements test cases for the Pen class
Author(s): Pooya Hekmati, sh2235@cornell.edu, Anchey Peng, ap724@cornell.edu
"""

import pytest
from unittest.mock import MagicMock
from pytest_mock.plugin import MockerFixture
from typing import Set, List, Dict, Tuple
from statistics import mean
from pytest_lazyfixture import lazy_fixture

from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.pen import Pen


@pytest.fixture
def pen() -> Pen:
    id_number = 0
    vert_dist = 0.1
    horiz_dist = 1.6
    num_stalls = 100
    housing_type = 'open air barn'
    bedding_type = 'sand'
    pen_type = 'freestall'
    manure_handling = "manual_scraping"
    manure_separator = "sedimentation"
    manure_storage = "storage_pit"
    animal_combination = Pen.AnimalCombination.CALF
    max_stocking_density = 1.2

    pen = Pen(id_number, vert_dist, horiz_dist, num_stalls, housing_type, bedding_type, pen_type, manure_handling,
              manure_separator, manure_storage, animal_combination, max_stocking_density)

    return pen


@pytest.fixture
def mock_animal_list() -> List[MagicMock]:
    animal_i = MagicMock()
    animal_ii = MagicMock()
    animal_iii = MagicMock()

    return [animal_i, animal_ii, animal_iii]


@pytest.fixture
def mock_animal_list_ii() -> List[MagicMock]:
    animal_iv = MagicMock()
    animal_v = MagicMock()
    animal_vi = MagicMock()

    return [animal_iv, animal_v, animal_vi]


@pytest.fixture
def mock_animal_list_combined(mock_animal_list, mock_animal_list_ii) -> List[MagicMock]:
    return mock_animal_list + mock_animal_list_ii


@pytest.fixture
def pen_with_animals(pen: Pen, mock_animal_list: List[MagicMock]) -> Pen:
    pen.animals_in_pen = mock_animal_list

    return pen


def test_set_avg_nutrient_rqmts(pen: Pen):
    """Unit test for function set_avg_nutrient_rqmts in file routines/animal/pen.py"""
    avg_nutrient_rqmts = {'NEmaint': 22.739694446587276,
                          'NEa': 0,
                          'NEg': 0.0,
                          'NEpreg': 0.8809032714863911,
                          'NEl': 0,
                          'MP_req': 169.60219829211576,
                          'Ca_req': 8.551061771355254,
                          'P_req': 0.8978663353409345,
                          'DMIest': 0,
                          'avg_BW': 445.74074026264447}

    pen.set_avg_nutrient_rqmts(avg_nutrient_rqmts)

    assert pen.avg_nutrient_rqmts == avg_nutrient_rqmts


def test_set_milk_avgs(pen: Pen):
    """Unit test for function set_milk_avgs in file routines/animal/pen.py"""
    avg_milk = 40.362
    avg_CP_milk = 3.196

    pen.set_milk_avgs(avg_milk, avg_CP_milk)

    assert pen.avg_milk == avg_milk and pen.avg_CP_milk == avg_CP_milk


@pytest.mark.parametrize('pen_to_test, new_animals, expected_animals_in_pen',
                         [
                             (lazy_fixture('pen'), lazy_fixture('mock_animal_list'), lazy_fixture('mock_animal_list')),
                             (lazy_fixture('pen_with_animals'), lazy_fixture('mock_animal_list_ii'),
                              lazy_fixture('mock_animal_list_combined')),
                         ])
def test_add_new_animals(pen_to_test: Pen, mock_animal_list,
                         new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII],
                         expected_animals_in_pen: List[Calf | Cow | HeiferI | HeiferII | HeiferIII]):
    """Unit test for function add_new_animals in file routines/animal/pen.py"""

    pen_to_test.add_new_animals(new_animals)

    assert pen_to_test.animals_in_pen == expected_animals_in_pen


@pytest.mark.parametrize('pen_to_test, expected_pen_populated',
                         [
                             (lazy_fixture('pen'), False),
                             (lazy_fixture('pen_with_animals'), True),
                         ])
def test_update_pen_populated(pen_to_test: Pen, expected_pen_populated: bool):
    """Unit test for function update_pen_populated in file routines/animal/pen.py"""
    pen_to_test.update_pen_populated()

    assert pen_to_test.populated == expected_pen_populated


@pytest.mark.parametrize('pen_to_test, expected_stocking_density',
                         [
                             (lazy_fixture('pen'), 0),
                             (lazy_fixture('pen_with_animals'), 0.03),
                         ])
def test_update_stocking_density(pen_to_test: Pen, expected_stocking_density: float):
    """Unit test for function update_stocking_density in file routines/animal/pen.py"""
    pen_to_test.update_stocking_density()

    assert pen_to_test.stocking_density == expected_stocking_density


@pytest.mark.parametrize('animal_combination ',
                         [
                             Pen.AnimalCombination.CALF,
                             Pen.AnimalCombination.GROWING,
                             Pen.AnimalCombination.LAC_COW,
                             Pen.AnimalCombination.CLOSE_UP,
                             Pen.AnimalCombination.GROWING_AND_CLOSE_UP,
                         ])
def test_update_animal_combination(pen: Pen, animal_combination: Pen.AnimalCombination):
    """Unit test for function update_animal_combination in file routines/animal/pen.py"""
    pen.update_animal_combination(animal_combination)

    assert pen.animal_combination == animal_combination


def test_update_animals(pen: Pen, mocker: MockerFixture):
    """Unit test for function update_animals in file routines/animal/pen.py"""

    mocker.patch('RUFAS.routines.animal.pen.Pen.add_new_animals')
    mocker.patch('RUFAS.routines.animal.pen.Pen.update_pen_populated')
    mocker.patch('RUFAS.routines.animal.pen.Pen.update_stocking_density')
    mocker.patch('RUFAS.routines.animal.pen.Pen.update_animal_combination')
    mocker.patch('RUFAS.routines.animal.pen.Pen.calc_daily_walking_dist')
    mocker.patch('RUFAS.routines.animal.pen.Pen.update_classes_in_pen')

    pen.update_animals(MagicMock(), MagicMock())

    pen.add_new_animals.assert_called_once()
    pen.update_pen_populated.assert_called_once()
    pen.update_stocking_density.assert_called_once()
    pen.update_animal_combination.assert_called_once()
    pen.calc_daily_walking_dist.assert_called_once()
    pen.update_classes_in_pen.assert_called_once()


def test_call_animal_nutrient_rqmts():
    """Unit test for function call_animal_nutrient_rqmts in file routines/animal/pen.py"""
    pass


def test_calc_avg_nutrient_rqmts():
    """Unit test for function calc_avg_nutrient_rqmts in file routines/animal/pen.py"""
    pass


def test_calc_avg_stats():
    """Unit test for function calc_avg_stats in file routines/animal/pen.py"""
    pass


def test_calc_ration():
    """Unit test for function calc_ration in file routines/animal/pen.py"""
    pass


def test_calc_manure():
    """Unit test for function calc_manure in file routines/animal/pen.py"""
    pass


def test_reset_manure(pen: Pen) -> None:
    """Unit test for function reset_manure in file routines/animal/pen.py"""
    pen.manure = {}
    pen.calf_total = {}
    pen.heifer_total = {}
    pen.dry_total = {}
    pen.lactating_total = {}

    expected = AnimalManureExcretions(
        urea=0.0,
        urine=0.0,
        total_ammoniacal_nitrogen_concentration=0.0,
        urine_nitrogen=0.0,
        manure_nitrogen=0.0,
        manure_mass=0.0,
        total_solids=0.0,
        degradable_volatile_solids=0.0,
        non_degradable_volatile_solids=0.0,
        inorganic_phosphorus_fraction=0.0,
        organic_phosphorus_fraction=0.0,
        phosphorus=0.0,
        phosphorus_fraction=0.0,
        potassium=0.0,
        methane=0.0
    )

    pen.reset_manure()

    assert pen.manure == expected
    assert pen.calf_total == expected
    assert pen.heifer_total == expected
    assert pen.dry_total == expected
    assert pen.lactating_total == expected


@pytest.fixture
def mock_calves_with_daily_growth(calf_daily_growth_values: List[float]) -> List[MagicMock]:
    calves = [MagicMock() for i in range(3)]

    for calf, daily_growth in zip(calves, calf_daily_growth_values):
        calf.daily_growth = daily_growth

    return calves


@pytest.fixture
def calf_daily_growth_values() -> List[float]:
    return [0.7445883642358595,
            0.7254529863013488,
            0.7342433606191534,
            ]


@pytest.fixture
def avg_calf_daily_growth_values(calf_daily_growth_values: List[float]) -> float:
    return mean(calf_daily_growth_values)


@pytest.mark.parametrize('pen_animals, pen_populated, expected',
                         [
                             (lazy_fixture('mock_calves_with_daily_growth'), True,
                              lazy_fixture('avg_calf_daily_growth_values')),
                             ([], False, 0)
                         ])
def test_calc_avg_growth(pen: Pen, pen_animals, pen_populated, expected) -> None:
    """Unit test for function calc_avg_growth in file routines/animal/pen.py"""
    pen.animals_in_pen = pen_animals
    pen.populated = pen_populated
    pen.calc_avg_growth()

    actual = pen.avg_growth

    assert actual == expected


def test_calc_daily_walking_dist():
    """Unit test for function calc_daily_walking_dist in file routines/animal/pen.py"""
    pass


def test_call_p_rqmts():
    """Unit test for function call_p_rqmts in file routines/animal/pen.py"""
    pass


def test_daily_p_update():
    """Unit test for function daily_p_update in file routines/animal/pen.py"""


def test_set_up_new_animal():
    """Unit test for function set_up_new_animal in file routines/animal/pen.py"""
    pass


def test_clear(pen: Pen) -> None:
    """Unit test for function clear in file routines/animal/pen.py"""
    calves = [MagicMock()]
    pen.animals_in_pen = calves
    pen.populated = True
    pen.avg_p_animal = 1.0

    pen.clear()

    assert pen.animals_in_pen == []
    assert pen.populated is False
    assert pen.avg_p_animal == 0


def feed_allocations() -> Dict[Pen.AnimalCombination, Set[int]]:
    calf = {155, 156, 157}
    growing = {2, 51, 86, 136}
    close_up = {2, 26, 86, 118, 136, 139}
    lac_cow = {26, 86, 103, 118, 136, 139}

    return {
        Pen.AnimalCombination.CALF: calf,
        Pen.AnimalCombination.GROWING: growing,
        Pen.AnimalCombination.CLOSE_UP: close_up,
        Pen.AnimalCombination.GROWING_AND_CLOSE_UP: growing | close_up,
        Pen.AnimalCombination.LAC_COW: lac_cow,
    }


def dict_to_tuple_list(d: Dict) -> List[Tuple]:
    return list(d.items())


@pytest.mark.parametrize('test_animal_combination, expected_feed_allocation',
                         dict_to_tuple_list(feed_allocations()))
def test_subset_class_feeds(pen: Pen,
                            test_animal_combination: Pen.AnimalCombination,
                            expected_feed_allocation: Set[int]) -> None:
    """Unit test for function subset_class_feeds in file routines/animal/pen.py"""

    feed = MagicMock()
    feed.input_feed_combinations = feed_allocations()

    pen.animal_combination = test_animal_combination
    pen.subset_class_feeds(feed)
    assert pen.allocated_feeds == expected_feed_allocation
