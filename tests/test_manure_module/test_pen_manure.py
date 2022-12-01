from dataclasses import fields
from typing import Callable
from typing import Dict

from pytest import approx

from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.manure.pen_manure import PenManure


def test_manure_init() -> None:
    """Unit test for function __init__ in file pen_manure.py"""
    # Case 1: Given no arguments, a new PenManure object should have all attributes
    # initially set to 0.

    # Arrange
    pen_manure_attributes = [field.name for field in fields(PenManure)]

    # Act
    manure = PenManure()

    # Assert
    for attr in pen_manure_attributes:
        assert hasattr(manure, attr)
        assert getattr(manure, attr) == approx(0.0)

    # --------------------------------------------------------------------------- #

    # Case 2: Given a dictionary of arguments, a new PenManure object should have all attributes
    # initially set to the correct values.

    # Arrange
    manure_data = {
        'urea': 1.0,
        'urine': 2.0,
        'urine_TAN': 3.0,
        'TAN': 4.0,
        'N': 5.0,
        'manure_mass': 6.0,
        'TS': 7.0,
        'VSd': 8.0,
        'VSnd': 9.0,
        'WIP_frac': 10.0,
        'WOP_frac': 11.0,
        'P': 12.0,
        'P_frac': 13.0,
        'K': 14.0,
        'CH4': 15.0
    }

    # Act
    manure = PenManure(**manure_data)

    # Assert
    assert manure.urea == approx(1.0)
    assert manure.urine == approx(2.0)
    assert manure.urine_TAN == approx(3.0)
    assert manure.TAN == approx(4.0)
    assert manure.N == approx(5.0)
    assert manure.manure_mass == approx(6.0)
    assert manure.manure_volume == approx(manure.manure_mass / ManureConstants.MANURE_DENSITY)
    assert manure.TS == approx(7.0)
    assert manure.VSd == approx(8.0)
    assert manure.VSnd == approx(9.0)
    assert manure.WIP_frac == approx(10.0)
    assert manure.WOP_frac == approx(11.0)
    assert manure.P == approx(12.0)
    assert manure.P_frac == approx(13.0)
    assert manure.K == approx(14.0)
    assert manure.CH4 == approx(15.0)

    # --------------------------------------------------------------------------- #

    # Case 3: Given an animal manure data dictionary and number of animals, a PenManure
    # should be returned with internal attributes correctly calculated.

    # Arrange
    animal_manure = {
        'U': 1.0,
        'Urine': 2.0,
        'TAN_s': 3.0,
        'MN': 4.0,
        'Mkg': 5.0,
        'TSd': 6.0,
        'VSd': 7.0,
        'VSnd': 8.0,
        'WIP_frac': 9.0,
        'WOP_frac': 10.0,
        'p_excrt_manure': 11.0,
        'p_frac': 12.0,
        'K_manure': 13.0,
        'CH4_manure': 14.0
    }
    num_animals = 2

    # Act
    manure = PenManure.get_instance(animal_manure, num_animals)

    # Assert
    assert manure.urea == approx(animal_manure['U'] / num_animals)
    assert manure.urine == approx(animal_manure['Urine'] / num_animals)
    assert manure.urine_TAN == approx(animal_manure['TAN_s'] * ManureConstants.URINE_TAN_FACTOR / num_animals)
    assert manure.TAN == approx(animal_manure['TAN_s'])
    assert manure.N == approx(animal_manure['MN'])
    assert manure.manure_mass == approx(animal_manure['Mkg'])
    assert manure.TS == approx(animal_manure['TSd'])
    assert manure.VSd == approx(animal_manure['VSd'])
    assert manure.VSnd == approx(animal_manure['VSnd'])
    assert manure.WIP_frac == approx(animal_manure['WIP_frac'] / num_animals)
    assert manure.WOP_frac == approx(animal_manure['WOP_frac'] / num_animals)
    assert manure.P == approx(animal_manure['p_excrt_manure'])
    assert manure.P_frac == approx(animal_manure['p_frac'] / num_animals)
    assert manure.K == approx(animal_manure['K_manure'])
    assert manure.CH4 == approx(animal_manure['CH4_manure'])
