"""
RUFAS: Ruminant Farm Systems Model
File name: test_pen.py
Description: Implements test cases for the Pen class
Author(s): Pooya Hekmati, sh2235@cornell.edu, Anchey Peng, ap724@cornell.edu
"""

import pytest
from mock.mock import MagicMock

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


def test_update_animals():
    """Unit test for function update_animals in file routines/animal/pen.py"""
    pass


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

    expected = {"U": 0,
                "TAN_s": 0,
                "MN": 0,
                "Mkg": 0,
                "TSd": 0,
                "VSd": 0,
                "VSnd": 0,
                "WIP_frac": 0,
                "WOP_frac": 0,
                "p_excrt_manure": 0,
                "p_frac": 0,
                "K_manure": 0,
                "CH4_manure": 0
                }

    pen.reset_manure()

    assert pen.manure == expected
    assert pen.calf_total == expected
    assert pen.heifer_total == expected
    assert pen.dry_total == expected
    assert pen.lactating_total == expected


@pytest.fixture
def calf_daily_growth_values() -> list[float]:
    return [0.7445883642358595,
            0.7254529863013488,
            0.7342433606191534,
            ]


@pytest.fixture
def mock_calves_with_daily_growth(calf_daily_growth_values: list[float]) -> list[MagicMock]:
    calves = [MagicMock() for i in range(3)]

    for calf, daily_growth in zip(calves, calf_daily_growth_values):
        calf.daily_growth = daily_growth

    return calves


def test_calc_avg_growth(pen: Pen, mock_calves_with_daily_growth: list[MagicMock],
                         calf_daily_growth_values) -> None:
    """Unit test for function calc_avg_growth in file routines/animal/pen.py"""
    pen.animals_in_pen = mock_calves_with_daily_growth
    pen.calc_avg_growth()

    actual = pen.avg_growth
    expected = sum(calf_daily_growth_values) / len(calf_daily_growth_values)

    assert actual == expected


def test_calc_daily_walking_dist():
    """Unit test for function calc_daily_walking_dist in file routines/animal/pen.py"""
    pass


def test_call_p_rqmts():
    """Unit test for function call_p_rqmts in file routines/animal/pen.py"""
    pass


def test_daily_p_update(pen):
    """Unit test for function daily_p_update in file routines/animal/pen.py"""


def test_set_up_new_animal():
    """Unit test for function set_up_new_animal in file routines/animal/pen.py"""
    pass


def test_clear(pen: Pen) -> None:
    """Unit test for function clear in file routines/animal/pen.py"""
    calves = [MagicMock()]
    pen.animals_in_pen = calves
    pen.pen_populated = True
    pen.avg_p_animal = 1.0

    pen.clear()

    assert pen.animals_in_pen == []
    assert pen.pen_populated is False
    assert pen.avg_p_animal == 0


@pytest.mark.parametrize('test_animal_combination, expected_feed_allocation', [
    (Pen.AnimalCombination.CALF, {155, 156, 157}),
    (Pen.AnimalCombination.GROWING, {2, 51, 86, 136}),
    (Pen.AnimalCombination.CLOSE_UP, {2, 26, 86, 118, 136, 139}),
    (Pen.AnimalCombination.GROWING_AND_CLOSE_UP, {2, 51, 86, 136, 26, 86, 118, 136, 139}),
    (Pen.AnimalCombination.LAC_COW, {26, 86, 103, 118, 136, 139}),
])
def test_subset_class_feeds(pen: Pen, test_animal_combination: Pen.AnimalCombination,
                            expected_feed_allocation: set[int]) -> None:
    """Unit test for function subset_class_feeds in file routines/animal/pen.py"""

    feed_combinations = {
        Pen.AnimalCombination.CALF: {155, 156, 157},
        Pen.AnimalCombination.GROWING: {2, 51, 86, 136},
        Pen.AnimalCombination.CLOSE_UP: {2, 26, 86, 118, 136, 139},
        Pen.AnimalCombination.GROWING_AND_CLOSE_UP: {2, 51, 86, 136} | {2, 26, 86, 118, 136, 139},
        Pen.AnimalCombination.LAC_COW: {26, 86, 103, 118, 136, 139},
    }

    feed = MagicMock()
    feed.input_feed_combinations = feed_combinations

    pen.animal_combination = test_animal_combination
    pen.subset_class_feeds(feed)
    assert pen.allocated_feeds == expected_feed_allocation
