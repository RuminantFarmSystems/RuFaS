from typing import Callable
from typing import Dict
from typing import List

from pytest import approx

from RUFAS.routines.manure.constants.constants import ManureManagementConstants
from RUFAS.routines.manure.manure.pen_manure import PenManure


def test_manure_init(pen_manure_attributes,
                     generate_animal_manure: Callable[[float], Dict[str, float]]) -> None:
    """Unit test for function __init__ in file pen_manure.py"""

    # Given no arguments, a new PenManure object should have all attributes
    # initially set to 0.
    manure = PenManure()
    for attr in pen_manure_attributes:
        assert hasattr(manure, attr)
        assert getattr(manure, attr) == approx(0.0)

    # Given a dictionary of arguments, a new PenManure object should have all attributes
    # initially set to the correct values.
    manure_data = generate_animal_manure(0.0)
    manure = PenManure.get_instance(manure_data, 1)
    for attr in pen_manure_attributes:
        assert hasattr(manure, attr)
        assert getattr(manure, attr) == approx(0.0)

    # Given one or more arguments, a new PenManure object should either set
    # the corresponding attributes to the given values or do some calculations.
    manure = PenManure(
            # The following attributes should be modified via unit conversion.
            urea=2.0,
            TAN=3.0,
            N=4.0,
            VSd=5.0,
            VSnd=6.0,
            P=7.0,
            K=8.0,

            # The following attributes should stay the same.
            # Only pick two as an example.
            manure_mass=10.0,
            CH4=10.0
    )
    # Currently, the following attributes are not modified via unit conversion.
    # constants = ManureManagementConstants
    # assert manure.urea == approx(2.0 * constants.UREA_MOLAR_MASS)
    # assert manure.TAN == approx(3.0 * constants.TAN_MOLAR_MASS)
    # assert manure.N == approx(4.0 * constants.GRAMS_TO_KG)
    # assert manure.VSd == approx(5.0 * constants.GRAMS_TO_KG)
    # assert manure.VSnd == approx(6.0 * constants.GRAMS_TO_KG)
    # assert manure.P == approx(7.0 * constants.GRAMS_TO_KG)
    # assert manure.K == approx(8.0 * constants.GRAMS_TO_KG)

    assert manure.manure_mass == approx(10.0)
    assert manure.CH4 == approx(10.0)

    # The remaining attributes should be set to the default value of 0.
    assert manure.TS == approx(0.0)
    assert manure.WIP_frac == approx(0.0)
    assert manure.WOP_frac == approx(0.0)
    assert manure.P_frac == approx(0.0)
