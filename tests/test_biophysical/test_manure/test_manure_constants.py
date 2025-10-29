from pytest import approx

from RUFAS.biophysical.manure.manure_constants import ManureConstants


def test_manure_constants() -> None:
    """
    Unit test for the manure constants in file manure_constants.py.

    This function checks the accuracy of the constants based on predefined expected values.
    Assertions are arranged in the order the constants appear in the class definition.
    """

    # Assert
    assert ManureConstants.LIQUID_MANURE_DENSITY == approx(1000)
    assert ManureConstants.SLURRY_MANURE_DENSITY == approx(990)
    assert ManureConstants.SOLID_MANURE_DENSITY == approx(700)
    assert ManureConstants.DEFAULT_LAG_TIME == approx(2)
