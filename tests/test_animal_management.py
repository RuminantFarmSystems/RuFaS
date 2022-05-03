"""
RUFAS: Ruminant Farm Systems Model
File name: test_animal_management.py
Description: Implements test cases for the AnimalManagement class
Author(s): Pooya Hekmati, sh2235@cornell.edu, Anchey Peng, ap724@cornell.edu
"""

import pytest
from unittest.mock import MagicMock
from pytest_mock.plugin import MockerFixture

from RUFAS.routines.animal.animal_management import AnimalManagement

from typing import List, Dict


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
def animal_management(mocker: MockerFixture, mock_pens: MagicMock) -> AnimalManagement:
    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement.init_pens')
    mocker.patch('RUFAS.routines.animal.animal_management.AnimalManagement.init_animals')

    data = MagicMock()
    config = MagicMock()
    feed = MagicMock()
    weather = MagicMock()
    time = MagicMock()

    animalManagement = AnimalManagement(data, config, feed, weather, time)
    animalManagement.all_pens = mock_pens

    return animalManagement


def test_daily_animal_routine():
    """Unit test for function daily_animal_routine in file routines/animal/animal_management.py"""
    pass


def test_get_animal_config():
    """Unit test for function get_animal_config in file routines/animal/animal_management.py"""
    pass


def test_init_pens():
    """Unit test for function init_pens in file routines/animal/animal_management.py"""
    pass


def test_init_animals():
    """Unit test for function init_animals in file routines/animal/animal_management.py"""
    pass


def test_init_nutrient_rqmts():
    """Unit test for function init_nutrient_rqmts in file routines/animal/animal_management.py"""
    pass


def test_avg_pen_dist(animal_management: AnimalManagement) -> None:
    """Unit test for function avg_pen_dist in file routines/animal/animal_management.py"""

    actual = animal_management.avg_pen_dist()
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


def test_pen_allocation():
    """Unit test for function pen_allocation in file routines/animal/animal_management.py"""
    pass


def test_clear_pens(animal_management: AnimalManagement) -> None:
    """Unit test for function clear_pens in file routines/animal/animal_management.py"""
    animal_management.clear_pens()

    for pen in animal_management.all_pens:
        pen.clear.assert_called_once()
    pass


def test_calc_avg_nutrient_rqmts():
    """Unit test for function calc_avg_nutrient_rqmts in file routines/animal/animal_management.py"""
    pass


def test_calc_ration():
    """Unit test for function calc_ration in file routines/animal/animal_management.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/animal_management.py"""
    pass


def test_calc_avg_growth(animal_management: AnimalManagement) -> None:
    """Unit test for function calc_avg_growth in file routines/animal/animal_management.py"""

    animal_management.calc_avg_growth()

    for pen in animal_management.all_pens:
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


def test_calc_p_comp(mock_animals: List[MagicMock]) -> None:
    """Unit test for function _calc_p_comp in file routines/animal/animal_management.py"""
    expected = 0
    actual = AnimalManagement._calc_p_comp([])
    assert actual == expected

    actual = AnimalManagement._calc_p_comp(mock_animals)
    expected = (16.0 / 8.0)

    assert actual == pytest.approx(expected)


def test_calc_all_p_comp():
    """Unit test for function calc_all_p_comp in file routines/animal/animal_management.py"""
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
