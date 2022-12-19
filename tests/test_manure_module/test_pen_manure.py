from dataclasses import fields

from pytest import approx

from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure


def test_pen_manure_init() -> None:
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
        'manure_urea': 1.0,
        'manure_urine': 2.0,
        'manure_urine_ammoniacal_nitrogen': 3.0,
        'manure_total_ammoniacal_nitrogen': 4.0,
        'manure_nitrogen': 5.0,
        'manure_mass': 6.0,
        'manure_total_solids': 7.0,
        'manure_degradable_volatile_solids': 8.0,
        'manure_non_degradable_volatile_solids': 9.0,
        'manure_inorganic_phosphorus_fraction': 10.0,
        'manure_organic_phosphorus_fraction': 11.0,
        'manure_phosphorus': 12.0,
        'manure_phosphorus_fraction': 13.0,
        'manure_potassium': 14.0,
        'manure_methane': 15.0
    }

    # Act
    manure = PenManure(**manure_data)

    # Assert
    assert manure.manure_urea == approx(1.0)
    assert manure.manure_urine == approx(2.0)
    assert manure.manure_urine_ammoniacal_nitrogen == approx(3.0)
    assert manure.manure_total_ammoniacal_nitrogen == approx(4.0)
    assert manure.manure_nitrogen == approx(5.0)
    assert manure.manure_mass == approx(6.0)
    assert manure.manure_volume == approx(manure.manure_mass / ManureConstants.MANURE_DENSITY)
    assert manure.manure_total_solids == approx(7.0)
    assert manure.manure_degradable_volatile_solids == approx(8.0)
    assert manure.manure_non_degradable_volatile_solids == approx(9.0)
    assert manure.manure_inorganic_phosphorus_fraction == approx(10.0)
    assert manure.manure_organic_phosphorus_fraction == approx(11.0)
    assert manure.manure_phosphorus == approx(12.0)
    assert manure.manure_phosphorus_fraction == approx(13.0)
    assert manure.manure_potassium == approx(14.0)
    assert manure.manure_methane == approx(15.0)

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
    assert manure.manure_urea == approx(animal_manure['U'] / num_animals)
    assert manure.manure_urine == approx(animal_manure['Urine'] / num_animals)
    assert manure.manure_urine_ammoniacal_nitrogen == approx(animal_manure['TAN_s'] * ManureConstants.URINE_TAN_FACTOR / num_animals)
    assert manure.manure_total_ammoniacal_nitrogen == approx(animal_manure['TAN_s'])
    assert manure.manure_nitrogen == approx(animal_manure['MN'])
    assert manure.manure_mass == approx(animal_manure['Mkg'])
    assert manure.manure_total_solids == approx(animal_manure['TSd'])
    assert manure.manure_degradable_volatile_solids == approx(animal_manure['VSd'])
    assert manure.manure_non_degradable_volatile_solids == approx(animal_manure['VSnd'])
    assert manure.manure_inorganic_phosphorus_fraction == approx(animal_manure['WIP_frac'] / num_animals)
    assert manure.manure_organic_phosphorus_fraction == approx(animal_manure['WOP_frac'] / num_animals)
    assert manure.manure_phosphorus == approx(animal_manure['p_excrt_manure'])
    assert manure.manure_phosphorus_fraction == approx(animal_manure['p_frac'] / num_animals)
    assert manure.manure_potassium == approx(animal_manure['K_manure'])
    assert manure.manure_methane == approx(animal_manure['CH4_manure'])
