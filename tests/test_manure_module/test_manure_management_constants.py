from pytest import approx

from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants
def test_manure_constants() -> None:
    """Tests the manure constants in file manure_constants.py."""
    constants = ManureConstants
    assert constants.MANURE_DENSITY == approx(990.0)
    assert constants.UREA_MOLAR_MASS == approx(60.06)
    assert constants.UREA_DENSITY == approx(1.32)
    assert constants.TAN_MOLAR_MASS == approx(17.0306)
    assert constants.URINE_TAN_FACTOR == approx(0.45)
    assert constants.MANURE_SOLIDS_BEDDING_DENSITY == approx(400.0)


def test_gas_emission_constants() -> None:
    """Tests the gas emission constants in file gas_emission_constants.py."""
    constants = GasEmissionConstants
    assert constants.b1 == approx(1.0)
    assert constants.b2 == approx(0.01)
    assert constants.lnA == approx(43.33)
    assert constants.E == approx(112700)
    assert constants.R == approx(8.314)

    assert constants.Bo == approx(0.24)
    assert constants.MCF == approx(0.79)
    assert constants.MS == approx(1.0)
    assert constants.METHANE_FACTOR == approx(0.67)

    assert constants.METHANE_ENERGY_DENSITY == approx(55)
    assert constants.METHANE_DENSITY == approx(0.657)
    assert constants.METHANE_POTENTIAL_Go == approx(240.0)
    assert constants.POTENTIAL_METHANE_YIELD_OF_MANURE == approx(0.48)

    assert constants.DEFAULT_VOLATILE_SOLIDS_FRACTION == approx(0.68)
    assert constants.CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH == approx(3.1)
    assert constants.SPECIFIC_GROWTH_RATE == approx(0.637)

    assert constants.DEFAULT_HOUSING_SPECIFIC_CONSTANT == approx(260.0)
