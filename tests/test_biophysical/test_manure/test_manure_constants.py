from pytest import approx

from RUFAS.biophysical.manure.manure_constants import ManureConstants


def test_manure_constants() -> None:
    """
    Unit test for the manure constants in file manure_constants.py.

    This function checks the accuracy of the constants based on predefined expected values.
    Assertions are arranged in the order the constants appear in the class definition.
    """

    # Assert
    assert ManureConstants.MANURE_DENSITY == approx(990.0)
    assert ManureConstants.MANURE_SOLIDS_BEDDING_DENSITY == approx(400.0)
    assert ManureConstants.LIQUID_MANURE_DENSITY == approx(1000)
    assert ManureConstants.SLURRY_MANURE_DENSITY == approx(990)
    assert ManureConstants.SOLID_MANURE_DENSITY == approx(700)
    assert ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_MANURE == approx(0.5)
    assert ManureConstants.EFFECTIVE_MICROBIAL_DECOMP_RATE == approx(2.37e-3)
    assert ManureConstants.DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP == approx(0.65)
    assert ManureConstants.DEFAULT_DAYS_SINCE_LAST_TILLAGE == approx(1)
    assert ManureConstants.DEFAULT_LAG_TIME == approx(2)
    assert ManureConstants.COMPOST_BEDDING_ORGANIC_NITROGEN_FRACTION == approx(0.952)
    assert ManureConstants.COMPOST_BEDDING_INORGANIC_NITROGEN_AMMONIUM_FRACTION == approx(0.5)
